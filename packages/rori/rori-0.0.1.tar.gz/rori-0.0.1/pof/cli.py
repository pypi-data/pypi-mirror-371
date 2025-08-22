import os
import sys
from typing import Optional, TypedDict, Unpack

import click

from pof.cli_utils import (
    AliasedGroup,
    handle_pof_errors,
    interactive_option,
    k8s_options,
    name_option,
    pof_manager,
    ssh_options,
    ui,
)
from pof.command import CommandK8s, CommandSsh
from pof.models import Pof, PofError


@click.group(invoke_without_command=True, cls=AliasedGroup)
@click.version_option(message="pof, version %(version)s")
@click.option("-v", "--verbose", is_flag=True, default=False)
@click.pass_context
@handle_pof_errors
def cli(
    ctx,
    verbose: bool,
) -> None:
    if ctx.invoked_subcommand is None:
        _status(None, verbose=verbose)


@cli.command(short_help="show information about managed configurations")
@click.argument("pof_alias", metavar="pof", required=False)
@click.option("-v", "--verbose", is_flag=True, default=False)
@handle_pof_errors
def status(
    pof_alias: Optional[str],
    verbose: bool,
) -> None:
    _status(pof_alias, verbose)


def _status(
    pof_alias: Optional[str] = None,
    verbose: bool = False,
) -> None:
    if pof_alias is not None:
        pof = pof_manager.get_pof(pof_alias)
        ui.print(ui.render_one(pof, verbose=verbose))
        return
    pofs = pof_manager.get_pofs()
    ui.print(ui.render_all(pofs, verbose=verbose))


@cli.group(
    short_help="add new port forwarding configuration",
    invoke_without_command=True,
)
@interactive_option
@click.pass_context
@handle_pof_errors
def add(
    ctx,
    interactive: bool,
):
    ctx.ensure_object(dict)
    ctx.obj["start"] = False
    if interactive:
        ctx.obj["interactive"] = True
        raise PofError("interactive mode is not supported yet")


@add.command("kubernetes")
@name_option
@k8s_options
@click.pass_context
@handle_pof_errors
def add_kubernetes(
    ctx,
    name: Optional[str],
    port_from: int,
    port_to: int,
    context: str,
    namespace: str,
    service: Optional[str],
    pod: Optional[str],
) -> None:
    builder = CommandK8s()
    command = builder.build(
        context=context,
        namespace=namespace,
        pod=pod,
        service=service,
        port_from=port_from,
        port_to=port_to,
    )
    pof = pof_manager.create(name=name, context=command)
    # ctx.obj.get("start"):
    ui.info(f"added new configuration {pof.name}")


@add.command("ssh")
@name_option
@ssh_options
@click.pass_context
@handle_pof_errors
def add_ssh(
    ctx,
    name: Optional[str],
    port_from: int,
    port_to: int,
    host_from: str,
    remote_user: str,
    remote_server: str,
) -> None:
    command_builder = CommandSsh()
    command = command_builder.build(
        port_from=port_from,
        port_to=port_to,
        host_from=host_from,
        remote_user=remote_user,
        remote_server=remote_server,
    )
    pof = pof_manager.create(name=name, context=command)
    ui.info(f"added new configuration {pof.name}")


@cli.group(
    short_help="add new port forwarding and start it immediately",
    invoke_without_command=True,
)
@interactive_option
@click.pass_context
@handle_pof_errors
def forward(
    ctx,
    interactive: bool,
) -> None:
    ctx.ensure_object(dict)
    if interactive:
        ctx.obj["interactive"] = True
        raise PofError("interactive mode is not supported yet")


@forward.command("ssh")
@interactive_option
@name_option
@ssh_options
@click.pass_context
@handle_pof_errors
def forward_ssh(
    ctx,
    interactive: bool,
    name: Optional[str],
    port_from: int,
    port_to: int,
    host_from: str,
    remote_user: str,
    remote_server: str,
) -> None:
    command_builder = CommandSsh()
    if interactive:
        command = command_builder.interactive()
    else:
        command = command_builder.build(
            port_from=port_from,
            port_to=port_to,
            host_from=host_from,
            remote_user=remote_user,
            remote_server=remote_server,
        )

    pof = pof_manager.create(name=name, context=command)
    pof_manager.start(pof)
    ui.info(f"saved {pof.name} and started forwarding: {pof.port_from}→{pof.port_to}")


@forward.command("kubernetes")
@interactive_option
@name_option
@k8s_options
@handle_pof_errors
def forward_kubernetes(
    interactive: bool,
    name: Optional[str],
    port_from: int,
    port_to: int,
    context: str,
    namespace: str,
    service: Optional[str],
    pod: Optional[str],
) -> None:
    non_interactive_options = [context, namespace, pod, service, port_from, port_to]
    if interactive and any(non_interactive_options):
        raise click.UsageError("Cannot use --interactive with other options")

    builder = CommandK8s()
    if interactive:
        # command = run_interactive_port_forward()
        command = builder.interactive()
    else:
        command = builder.build(
            port_from=port_from,
            port_to=port_to,
            context=context,
            namespace=namespace,
            pod=pod,
            service=service,
        )

    pof = pof_manager.create(name=name, context=command)
    pof_manager.start(pof)
    ui.info(f"saved {pof.name} and started forwarding: {pof.port_from}→{pof.port_to}")


@cli.command()
@click.argument("pof_alias", metavar="pof")
@click.option("-f", "--follow", is_flag=True, default=False)
@handle_pof_errors
def logs(
    pof_alias: str,
    follow: bool,
) -> None:
    pof = pof_manager.get_pof(pof_alias)
    lines = pof_manager.logs(pof, follow=follow)
    if follow:
        ui.info(f"streaming logs for {pof.name} from {pof.logfile}")
    else:
        ui.info(f"printing logs for {pof.name} from {pof.logfile}")
    for line in lines:
        ui.print(line)


@cli.command()
@click.argument("pof_alias", metavar="pof")
@handle_pof_errors
def start(
    pof_alias: str,
) -> None:
    pof = pof_manager.get_pof(pof_alias)
    pof_manager.start(pof)
    ui.info(f"started forwarding for {pof.name}: {pof.port_from}→{pof.port_to}")


@cli.command()
@click.argument("pof_alias", metavar="pof")
@handle_pof_errors
def stop(
    pof_alias: str,
) -> None:
    pof = pof_manager.get_pof(pof_alias)
    pof_manager.stop(pof)
    ui.info(f"forwarding for {pof.name} stopped")


@cli.command(short_help="stops the port forwarding process and starts it again")
@click.argument("pof_alias", metavar="pof", required=True)
@handle_pof_errors
def restart(pof_alias: str):
    pof = pof_manager.get_pof(pof_alias)
    pof_manager.restart(pof)
    ui.info(f"{pof.name} has been restarted")


@cli.command(short_help="sets a new name/alias for the existing entry")
@click.argument("pof_alias", metavar="pof", required=True)
@click.argument("new_name", metavar="new-name", required=True)
@handle_pof_errors
def rename(
    pof_alias: str,
    new_name: str,
) -> None:
    pof = pof_manager.get_pof(pof_alias)
    name = pof.name
    pof_manager.rename(pof, new_name)
    ui.info(f"renamed entry {name} to {new_name}")


@cli.command()
@click.argument("pof_alias", metavar="pof")
@click.option("-f", "--force", is_flag=True, default=False)
@handle_pof_errors
def delete(
    pof_alias: str,
    force: bool,
) -> None:
    pof = pof_manager.get_pof(pof_alias)
    name = pof.name
    pof_manager.delete(pof, force=force)
    ui.info(f"deleted entry {name}")


if __name__ == "__main__":
    cli()
