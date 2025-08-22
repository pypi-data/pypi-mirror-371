import functools
import sys
from typing import Callable, Optional, TypedDict

import click

from pof import config
from pof.manager import PofManager
from pof.models import PofError
from pof.ui import ConsoleUI

pof_manager = PofManager(pof_dir=config.POF_DIR)
ui = ConsoleUI()


def handle_pof_errors(f: Callable) -> Callable:
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except PofError as e:
            # TODO: add logging
            ui.error(f"{e}")
            sys.exit(1)

    return wrapper


class AliasedGroup(click.Group):
    """A Click Group that supports command aliases."""

    def get_command(self, ctx, cmd_name):
        # Define aliases
        aliases = {
            # status
            "show": "status",
            "info": "status",
            "details": "status",
            # add
            "create": "add",
            "new": "add",
            "save": "add",
            # delete
            "remove": "delete",
            "rm": "delete",
            # forward
            "fwd": "forward",
            # start
            "resume": "start",
            "on": "start",
            "activate": "start",
            # stop
            "pause": "stop",
            "off": "stop",
            "deactivate": "stop",
        }

        # Check if it's an alias
        if cmd_name in aliases:
            cmd_name = aliases[cmd_name]

        return super().get_command(ctx, cmd_name)


name_option = click.option(
    "-n",
    "--name",
    help="provide alias for the configuration instead of a default one",
    required=False,
)
port_from_option = click.option(
    "--port-from",
    type=click.IntRange(1, 65535),
    help="remote port number",
)
port_to_option = click.option(
    "--port-to",
    type=click.IntRange(1, 65535),
    help="local port number",
)
interactive_option = click.option(
    "-i",
    "--interactive",
    is_flag=True,
    default=False,
    help="run command in interactive mode",
)
wait_option = click.option(
    "-w",
    "--wait-ready",
    is_flag=True,
    default=False,
)


def k8s_options(f):
    """Add common Kubernetes options to a command."""

    @port_from_option
    @port_to_option
    @click.option("--context", help="Kubernetes context")
    @click.option("--namespace", help="Kubernetes namespace")
    @click.option("--pod", help="Pod name")
    @click.option("--service", help="Service name")
    @functools.wraps(f)
    def wrapper(
        *args,
        port_from: Optional[int],
        port_to: Optional[int],
        context: Optional[str],
        namespace: Optional[str],
        pod: Optional[str],
        service: Optional[str],
        **kwargs,
    ):
        errors = []
        if not context:
            errors.append(f"option [bold {config.COLOR_ERROR}]--context[/] is required")

        if not namespace:
            errors.append(
                f"option [bold {config.COLOR_ERROR}]--namespace[/] is required"
            )

        if not service and not pod:
            errors.append(
                f"provide either [bold {config.COLOR_ERROR}]--service[/] or [bold {config.COLOR_ERROR}]--pod[/] option"
            )

        if not port_from or not port_to:
            errors.append(
                f"both [bold {config.COLOR_ERROR}]--port-from[/] and [bold {config.COLOR_ERROR}]--port-to[/] are required"
            )

        if errors:
            ui.handle_errors(errors)
            sys.exit(1)

        return f(
            *args,
            port_from=port_from,
            port_to=port_to,
            context=context,
            namespace=namespace,
            pod=pod,
            service=service,
            **kwargs,
        )

    return wrapper


def ssh_options(f):
    """Add common SSH options to a command."""

    @port_from_option
    @port_to_option
    @click.option("--host-from", help="target ssh host to forward from")
    @click.option("--remote-user", help="ssh user for the jump host")
    @click.option("--remote-server", help="ssh server for the jump host")
    @functools.wraps(f)
    def wrapper(
        *args,
        port_from: Optional[int],
        port_to: Optional[int],
        host_from: Optional[str],
        remote_user: Optional[str],
        remote_server: Optional[str],
        **kwargs,
    ):
        # TODO: add private key option
        errors = []
        if not host_from:
            errors.append(
                f"option [bold {config.COLOR_ERROR}]--host-from[/] is required"
            )

        if not remote_user:
            errors.append(
                f"option [bold {config.COLOR_ERROR}]--remote-user[/] is required"
            )

        if not remote_server:
            errors.append(
                f"option [bold {config.COLOR_ERROR}]--remote-server[/] is required"
            )

        if not port_from or not port_to:
            errors.append(
                f"both [bold {config.COLOR_ERROR}]--port-from[/] and [bold {config.COLOR_ERROR}]--port-to[/] are required"
            )

        if errors:
            ui.handle_errors(errors)
            sys.exit(1)

        return f(
            *args,
            port_from=port_from,
            port_to=port_to,
            host_from=host_from,
            remote_user=remote_user,
            remote_server=remote_server,
            **kwargs,
        )

    return wrapper
