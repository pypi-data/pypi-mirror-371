"""Data models for port forwarding entries."""

import functools
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Optional, Self

from hapless.hap import Hap
from hapless.hap import Status as HapStatus

from pof import config


class PofError(ValueError):
    pass


# TODO: add starting status (when wait-ready is implemented)
class Status(StrEnum):
    """Enumeration for port forward entry statuses."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


def check_initialized(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._hap is None or self._db_entry is None:
            raise RuntimeError(
                f"Cannot get {func.__name__} on the uninitialized instance."
            )

        return func(self, *args, **kwargs)

    return wrapper


@dataclass
class PofDbEntry:
    """Port forwarding entry data model."""

    hid: int  # same as pof_id
    port_from: int = 0
    port_to: int = 0
    type_: str = "manual"  # kubernetes, docker, manual, etc.
    created_at: datetime = field(default_factory=datetime.now)
    # updated_at: datetime = field(default_factory=datetime.now)
    metadata: Optional[dict[str, str]] = None

    # def __post_init__(self):
    #     """Set updated_at timestamp."""
    #     if self.hid is not None:
    #         self.updated_at = datetime.now()


class Pof:
    def __init__(self):
        # Internal fields
        self._hap: Optional[Hap] = None
        self._db_entry: Optional[PofDbEntry] = None

    @property
    @check_initialized
    def hid(self) -> str:
        return self._hap.hid

    @property
    @check_initialized
    def name(self) -> str:
        return self._hap.name

    @property
    @check_initialized
    def uptime(self) -> str:
        if self.status == Status.ACTIVE:
            return self._hap.runtime
        return ""

    @property
    @check_initialized
    def logfile(self) -> str:
        return self._hap.stdout_path

    @property
    @check_initialized
    def command(self) -> str:
        return self._hap.cmd

    @property
    @check_initialized
    def restarts(self) -> int:
        return self._hap.restarts

    @property
    @check_initialized
    def pid(self) -> Optional[int]:
        return self._hap.pid

    @property
    @check_initialized
    def port_from(self) -> str:
        return self._db_entry.port_from

    @property
    @check_initialized
    def port_to(self) -> str:
        return self._db_entry.port_to

    @property
    @check_initialized
    def type_(self) -> str:
        return self._db_entry.type_

    @property
    @check_initialized
    def metadata(self) -> str:
        return self._db_entry.metadata

    @property
    @check_initialized
    def status(self) -> Status:
        status = Status.INACTIVE
        hap = self._hap
        if hap.proc is None and hap.rc is None:
            # hap was only created, not started
            return status

        match hap.status:
            # todo: add Hap status created
            case HapStatus.RUNNING:
                status = Status.ACTIVE
            case HapStatus.FAILED:
                status = Status.ERROR
            case HapStatus.SUCCESS | HapStatus.PAUSED:
                status = Status.INACTIVE

        return status

    @classmethod
    def compile(cls, pof_db_entry: PofDbEntry, pof_hap: Hap) -> Self:
        """
        Compile a Pof instance from database entry and hap instance.
        """
        instance = cls()
        instance._hap = pof_hap
        instance._db_entry = pof_db_entry
        return instance

    def __str__(self) -> str:
        return f"#{self.hid} ({self.name})"

    def __rich__(self) -> str:
        rich_text = f"pof {config.ICON_POFV}{self.hid} ([{config.COLOR_MAIN} bold]{self.name}[/])"
        # TODO: add info on the ports
        return rich_text
