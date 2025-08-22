"""Service layer for managing port forward entries."""

import subprocess
import time
from typing import List, Optional

import psutil

from pof.models import PortForwardDatabase, PortForwardEntry


class PortForwardService:
    """Service for managing port forward entries and processes."""

    def __init__(self):
        """Initialize the service."""
        self.db = PortForwardDatabase()

    def create_entry(
        self,
        name: str,
        port_from: int,
        port_to: int,
        entry_type: str = "manual",
        namespace: Optional[str] = None,
        resource_name: Optional[str] = None,
        context: Optional[str] = None,
        command: Optional[str] = None,
    ) -> PortForwardEntry:
        """Create a new port forward entry."""
        entry = PortForwardEntry(
            id_=1,
            name=name,
            port_from=port_from,
            port_to=port_to,
            type_=entry_type,
            namespace=namespace,
            resource_name=resource_name,
            context=context,
            status="inactive",
        )

        entry_id = self.db.add_entry(entry)
        return entry

    def start_port_forward(self, entry_id: int) -> bool:
        """Start a port forward process."""
        entry = self.db.get_entry(entry_id)
        if not entry:
            return False

        if entry.status == "active":
            return True  # Already active

        if not entry.command:
            return False  # No command to run

        try:
            # Start the process
            process = subprocess.Popen(
                entry.command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Update entry with process info
            self.db.update_status(entry_id, "active", process.pid)
            return True

        except Exception as e:
            print(f"❌ Failed to start port forward: {e}")
            return False

    def stop_port_forward(self, entry_id: int) -> bool:
        """Stop a port forward process."""
        entry = self.db.get_entry(entry_id)
        if not entry:
            return False

        if entry.status != "active" or not entry.pid:
            return True  # Already inactive

        try:
            # Try to terminate the process gracefully
            if psutil.pid_exists(entry.pid):
                process = psutil.Process(entry.pid)
                process.terminate()

                # Wait for process to terminate
                try:
                    process.wait(timeout=5)
                except psutil.TimeoutExpired:
                    # Force kill if it doesn't terminate
                    process.kill()

            # Update entry status
            self.db.update_status(entry_id, "inactive", None)
            return True

        except Exception as e:
            print(f"❌ Failed to stop port forward: {e}")
            return False

    def get_all_entries(self) -> List[PortForwardEntry]:
        """Get all port forward entries."""
        return self.db.get_all_entries()

    def get_active_entries(self) -> List[PortForwardEntry]:
        """Get only active port forward entries."""
        return self.db.get_entries_by_status("active")

    def get_entry(self, entry_id: int) -> Optional[PortForwardEntry]:
        """Get a specific entry by ID."""
        return self.db.get_entry(entry_id)

    def delete_entry(self, entry_id: int) -> bool:
        """Delete a port forward entry."""
        # Stop the process first if it's active
        entry = self.db.get_entry(entry_id)
        if entry and entry.status == "active":
            self.stop_port_forward(entry_id)

        return self.db.delete_entry(entry_id)

    def update_entry_uptime(self, entry_id: int) -> bool:
        """Update the uptime for an active entry."""
        entry = self.db.get_entry(entry_id)
        if not entry or entry.status != "active" or not entry.pid:
            return False

        try:
            if psutil.pid_exists(entry.pid):
                process = psutil.Process(entry.pid)
                uptime_seconds = time.time() - process.create_time()
                uptime = self._format_uptime(uptime_seconds)

                # Update the entry
                entry.uptime = uptime
                return self.db.update_entry(entry)
            else:
                # Process doesn't exist, mark as inactive
                self.db.update_status(entry_id, "inactive", None)
                return False

        except Exception:
            return False

    def sync_process_status(self) -> int:
        """Sync database status with actual process status."""
        active_entries = self.get_active_entries()
        updated_count = 0

        for entry in active_entries:
            if entry.id is None:
                continue

            if not entry.pid or not psutil.pid_exists(entry.pid):
                # Process is dead, mark as inactive
                self.db.update_status(entry.id, "inactive", None)
                updated_count += 1
            else:
                # Update uptime
                self.update_entry_uptime(entry.id)

        return updated_count

    def create_k8s_entry(
        self,
        namespace: str,
        resource_name: str,
        resource_type: str,
        local_port: int,
        remote_port: int,
        context: Optional[str] = None,
    ) -> PortForwardEntry:
        """Create a Kubernetes port forward entry."""
        name = f"{resource_type}-{resource_name}"

        # Build kubectl command
        cmd_parts = ["kubectl", "port-forward"]
        if context:
            cmd_parts.extend(["--context", context])
        cmd_parts.extend(["-n", namespace])
        cmd_parts.append(f"{resource_type}/{resource_name}")
        cmd_parts.append(f"{local_port}:{remote_port}")

        command = " ".join(cmd_parts)

        return self.create_entry(
            name=name,
            port_from=local_port,
            port_to=remote_port,
            entry_type="kubernetes",
            namespace=namespace,
            resource_name=resource_name,
            context=context,
            command=command,
        )

    def get_stats(self) -> dict:
        """Get service statistics."""
        db_stats = self.db.get_stats()

        # Add process-level stats
        active_processes = 0
        for entry in self.get_active_entries():
            if entry.pid and psutil.pid_exists(entry.pid):
                active_processes += 1

        db_stats["active_processes"] = active_processes
        return db_stats

    def cleanup_old_entries(self) -> int:
        """Clean up old inactive entries."""
        return self.db.cleanup_inactive_entries()

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        else:
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            return f"{days}d {hours}h" if hours > 0 else f"{days}d"
