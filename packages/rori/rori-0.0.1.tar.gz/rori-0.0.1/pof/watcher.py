"""Port forward health monitoring module."""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from pof.manager import PofManager
from pof.models import Pof, Status

logger = logging.getLogger(__name__)


@dataclass
class HealthCheck:
    """Health check result for a port forward."""

    pof_id: int
    pof_name: str
    port_to: int
    is_healthy: bool
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    checked_at: float = 0.0

    def __post_init__(self):
        if self.checked_at == 0.0:
            self.checked_at = time.time()


class PofWatcher:
    """Asynchronous port forward health monitoring service."""

    def __init__(
        self,
        pof_manager: PofManager,
        check_interval: float = 30.0,
        connection_timeout: float = 5.0,
        max_concurrent_checks: int = 10,
    ):
        """
        Initialize the port forward watcher.

        Args:
            pof_manager: PofManager instance
            check_interval: Time between health check cycles (seconds)
            connection_timeout: Timeout for individual port checks (seconds)
            max_concurrent_checks: Maximum concurrent health checks
        """
        self.pof_manager = pof_manager
        self.check_interval = check_interval
        self.connection_timeout = connection_timeout
        self.max_concurrent_checks = max_concurrent_checks

        # Health check results cache
        self.health_results: Dict[int, HealthCheck] = {}

        # Control flags
        self._running = False
        self._stop_event = asyncio.Event()

        # Semaphore to limit concurrent connections
        self._semaphore = asyncio.Semaphore(max_concurrent_checks)

    async def start_monitoring(self) -> None:
        """Start the monitoring loop."""
        if self._running:
            logger.warning("Watcher is already running")
            return

        self._running = True
        self._stop_event.clear()

        logger.info("Starting port forward health monitoring")

        try:
            await self._monitoring_loop()
        except asyncio.CancelledError:
            logger.info("Health monitoring was cancelled")
        except Exception as e:
            logger.error(f"Health monitoring failed: {e}")
        finally:
            self._running = False

    async def stop_monitoring(self) -> None:
        """Stop the monitoring loop."""
        if not self._running:
            return

        logger.info("Stopping port forward health monitoring")
        self._stop_event.set()

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self._running and not self._stop_event.is_set():
            try:
                # Get all active port forwards
                active_pofs = self.pof_manager.get_pofs(statuses=[Status.ACTIVE])

                if active_pofs:
                    logger.debug(
                        f"Checking health of {len(active_pofs)} active port forwards"
                    )

                    # Run health checks concurrently
                    tasks = [self._check_pof_health(pof) for pof in active_pofs]
                    health_results = await asyncio.gather(
                        *tasks, return_exceptions=True
                    )

                    # Process results
                    await self._process_health_results(health_results)
                else:
                    logger.debug("No active port forwards to monitor")

                # Wait for next check cycle or stop signal
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(), timeout=self.check_interval
                    )
                    break  # Stop event was set
                except asyncio.TimeoutError:
                    continue  # Normal cycle completion

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)

    async def _check_pof_health(self, pof: Pof) -> HealthCheck:
        """
        Check health of a single port forward.

        Args:
            pof: Port forward to check

        Returns:
            HealthCheck result
        """
        async with self._semaphore:  # Limit concurrent connections
            start_time = time.time()

            try:
                # Attempt to connect to the target port
                is_healthy = await self._check_port_connection(
                    host="localhost", port=pof.port_to, timeout=self.connection_timeout
                )

                response_time_ms = (time.time() - start_time) * 1000

                return HealthCheck(
                    pof_id=pof.hid,
                    pof_name=pof.name,
                    port_to=pof.port_to,
                    is_healthy=is_healthy,
                    response_time_ms=response_time_ms,
                    error=None if is_healthy else "Connection failed",
                )

            except Exception as e:
                response_time_ms = (time.time() - start_time) * 1000

                return HealthCheck(
                    pof_id=pof.hid,
                    pof_name=pof.name,
                    port_to=pof.port_to,
                    is_healthy=False,
                    response_time_ms=response_time_ms,
                    error=str(e),
                )

    async def _check_port_connection(
        self, host: str, port: int, timeout: float
    ) -> bool:
        """
        Check if a port is accepting connections.

        Args:
            host: Target host
            port: Target port
            timeout: Connection timeout

        Returns:
            True if port is accessible, False otherwise
        """
        try:
            # Create connection with timeout
            future = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(future, timeout=timeout)

            # Close the connection immediately
            writer.close()
            await writer.wait_closed()

            return True

        except (
            asyncio.TimeoutError,
            ConnectionRefusedError,
            ConnectionError,
            OSError,
        ) as e:
            logger.debug(f"Port {port} check failed: {e}")
            return False

    async def _process_health_results(self, results: List) -> None:
        """
        Process health check results and update cache.

        Args:
            results: List of HealthCheck results or exceptions
        """
        healthy_count = 0
        unhealthy_count = 0

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Health check task failed: {result}")
                continue

            if not isinstance(result, HealthCheck):
                logger.warning(f"Unexpected result type: {type(result)}")
                continue

            # Update cache
            self.health_results[result.pof_id] = result

            # Count results
            if result.is_healthy:
                healthy_count += 1
                logger.debug(
                    f"✅ {result.pof_name} (port {result.port_to}) - "
                    f"{result.response_time_ms:.1f}ms"
                )
            else:
                unhealthy_count += 1
                logger.warning(
                    f"❌ {result.pof_name} (port {result.port_to}) - "
                    f"Error: {result.error}"
                )

        if healthy_count + unhealthy_count > 0:
            logger.info(
                f"Health check completed: {healthy_count} healthy, "
                f"{unhealthy_count} unhealthy"
            )

    def get_health_status(self, pof_id: int) -> Optional[HealthCheck]:
        """
        Get the latest health status for a port forward.

        Args:
            pof_id: Port forward ID

        Returns:
            HealthCheck result or None if not found
        """
        return self.health_results.get(pof_id)

    def get_all_health_status(self) -> Dict[int, HealthCheck]:
        """Get health status for all monitored port forwards."""
        return self.health_results.copy()

    def get_unhealthy_pofs(self) -> List[HealthCheck]:
        """Get list of unhealthy port forwards."""
        return [
            health for health in self.health_results.values() if not health.is_healthy
        ]

    def clear_health_cache(self) -> None:
        """Clear the health check results cache."""
        self.health_results.clear()
        logger.info("Health check cache cleared")

    @property
    def is_running(self) -> bool:
        """Check if the watcher is currently running."""
        return self._running


# Convenience function for standalone usage
async def watch_port_forwards(
    pof_manager: PofManager,
    check_interval: float = 30.0,
    connection_timeout: float = 5.0,
    max_concurrent_checks: int = 10,
) -> None:
    """
    Start monitoring port forwards (convenience function).

    Args:
        pof_manager: PofManager instance
        check_interval: Time between health check cycles (seconds)
        connection_timeout: Timeout for individual port checks (seconds)
        max_concurrent_checks: Maximum concurrent health checks
    """
    watcher = PofWatcher(
        pof_manager=pof_manager,
        check_interval=check_interval,
        connection_timeout=connection_timeout,
        max_concurrent_checks=max_concurrent_checks,
    )

    try:
        await watcher.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        await watcher.stop_monitoring()


async def main():
    from pathlib import Path

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create PofManager
    pof_dir = Path.home() / ".pof"
    pof_manager = PofManager(pof_dir)

    # Start monitoring
    print("Starting port forward health monitoring...")
    print("Press Ctrl+C to stop")

    await watch_port_forwards(
        pof_manager=pof_manager,
        check_interval=15.0,  # Check every 15 seconds
        connection_timeout=3.0,  # 3 second timeout
        max_concurrent_checks=5,  # Max 5 concurrent checks
    )


if __name__ == "__main__":
    asyncio.run(main())
