from functools import reduce
from importlib.metadata import version

from hapless.hap import Status as HapStatus
from rich import box
from rich.console import Console, ConsoleOptions, Group, RenderableType
from rich.measure import measure_renderables
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pof import config
from pof.models import Pof, Status

STATUS_COLORS = {
    Status.ACTIVE: "#4aad52",
    # Status.ACTIVE: config.COLOR_ACCENT,
    # Status.INACTIVE: "#f79824",
    Status.INACTIVE: "",
    Status.ERROR: config.COLOR_ERROR,
}

get_color = lambda status: STATUS_COLORS[status]

console = Console(highlight=False)


class ConsoleUI:
    def __init__(self):
        self.console = Console(highlight=False)

    def print(self, *args, **kwargs):
        return self.console.print(*args, **kwargs)

    def error(self, message: str):
        return self.console.print(
            f"{config.ICON_ERROR} {message}",
            style=f"{config.COLOR_ERROR} bold",
            overflow="ignore",
            crop=False,
        )

    def handle_errors(self, errors: list[str]):
        for message in errors:
            self.console.print(
                f"{config.ICON_MULTI_ERROR} {message}",
                overflow="ignore",
                crop=False,
            )

    def info(self, message: str):
        return self.console.print(
            f"{config.ICON_INFO} {message}",
            style=f"{config.COLOR_ACCENT} bold",
            overflow="ignore",
            crop=False,
        )

    def render_all(self, pofs: list[Pof], verbose: bool = False) -> Table:
        package_version = version(__package__)
        active_count = reduce(
            lambda acc, pof: acc + (1 if pof.status == Status.ACTIVE else 0), pofs, 0
        )

        table = Table(
            show_header=True,
            header_style=f"{config.COLOR_MAIN} bold",
            box=box.ROUNDED,
            caption_style="dim",
            caption_justify="right",
        )
        table.add_column("#", style="dim", min_width=2)
        table.add_column("name")
        table.add_column("port from")
        table.add_column("port to")
        table.add_column("status")
        table.add_column("type")
        if active_count:
            table.add_column("uptime", justify="right")

        for pof in pofs:
            status_text = get_status_text(pof)
            port_text = get_port_text(pof)
            row = [
                f"{pof.hid}",
                f"{pof.name}",
                f"{pof.port_from}",
                port_text,
                status_text,
                f"{pof.type_}",
            ]
            if active_count:
                row.append(f"{pof.uptime}")

            table.add_row(*row, style="dim" if pof.status == Status.INACTIVE else "")

        if verbose:
            table.title = f"{config.ICON_POF} pof, {package_version}"
            table.caption = f"{active_count} active / {len(pofs)} total"

        return table

    def render_one(self, pof: Pof, verbose: bool = False) -> RenderableType:
        column_min_width = 12
        table_min_width = 40
        status_table = Table(
            show_header=False,
            show_footer=False,
            expand=True,
            width=48,
            box=None,
        )
        status_table.add_column("lefside", justify="right", style="dim")
        status_table.add_column("rightside", justify="left")

        status_text = get_status_text(pof)
        color = STATUS_COLORS.get(pof.status)
        status_table.add_row("name", f"{pof.name}")
        status_table.add_row(
            "status", Text(f"{config.ICON_STATUS} {pof.status}", style=f"bold {color}")
        )
        if pof.status == Status.ACTIVE:
            status_table.add_row("uptime", f"{pof.uptime}")

        status_table.add_row("")
        status_table.add_row("port from", f"{pof.port_from}")
        status_table.add_row("port to", f"{pof.port_to}")
        status_table.add_row("")

        if not verbose:
            status_table.add_row("type", Text(f"{pof.type_}"))

        if verbose:
            status_table.add_row(
                "command", Text(f"{pof.command}", style=f"{config.COLOR_ACCENT} bold")
            )
            if pof.status == Status.ACTIVE:
                status_table.add_row("pid", f"{pof.pid}")
                status_table.add_row("restarts", f"{pof.restarts}")
            status_table.add_row("")
            status_table.add_row("logs", Text(f"{pof.logfile}"))

        # start_time = pof.start_time
        # end_time = pof.end_time
        # if verbose and start_time:
        #     status_table.add_row("Start time:", f"{start_time}")

        # if verbose and end_time:
        #     status_table.add_row("End time:", f"{end_time}")

        status_panel = Panel(
            status_table,
            expand=False,
            # min_width=panel_width,
            title=f"pof {config.ICON_POF} {pof.hid}",
            border_style=config.COLOR_MAIN,
        )
        result = Group(status_panel)

        # if verbose:
        info_table = Table(
            show_header=False,
            show_footer=False,
            expand=True,
            box=None,
            # min_width=panel_width,
        )
        info_table.add_column(
            "leftside", justify="right", style="dim", min_width=column_min_width
        )
        info_table.add_column("rightside", justify="left", style=config.COLOR_ACCENT)

        for key, value in pof.metadata.items():
            info_table.add_row(key, Text(value, overflow="fold"))

        info_panel = Panel(
            info_table,
            expand=False,
            # width=panel_width,
            title=f"{pof.type_} info",
            # border_style=config.COLOR_MAIN,
        )
        result = Group(status_panel, info_panel)
        # options = ConsoleOptions()
        measure = measure_renderables(
            console=console,
            options=console.options,
            renderables=[status_panel, info_panel],
        )
        if verbose:
            status_table.width = measure.maximum
            info_table.width = measure.maximum

        return result


def get_status_text(entry: Pof):
    status: Status = entry.status
    status_text = Text()
    status_text.append(config.ICON_STATUS, style=get_color(status))
    status_text.append(f" {status}", style=get_color(status))
    return status_text


def get_port_text(entry: Pof):
    style = ""
    match entry.status:
        case Status.ACTIVE:
            style = f"bold {get_color(entry.status)}"
        case Status.ERROR:
            style = f"{get_color(entry.status)}"

    return Text(f"{entry.port_to}", style=style)
