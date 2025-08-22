import os
from pathlib import Path
from typing import Optional

from hapless.hap import Hap
from hapless.main import Hapless

from pof.command import CommandContext, CommandK8s, CommandSsh
from pof.db import PofDb
from pof.models import Pof, PofDbEntry, PofError, Status
from pof.utils import cat, tail


class PofManager:
    def __init__(self, pof_dir: Path | str):
        pof_dir = Path(pof_dir)
        if not pof_dir.exists():
            pof_dir.mkdir(parents=True, exist_ok=True)
            os.utime(pof_dir)
        self._pof_dir = pof_dir
        self._hapless = Hapless(pof_dir, quiet=True)
        self._db = PofDb(pof_dir / "pof.db")

    def create(self, name: Optional[str], context: CommandContext) -> Pof:
        """
        Create a new port forwarding configuration.
        """
        if not name:
            name = f"pof-{Hap.get_random_name()}"

        existing_pof = self._get_or_none(name)
        if existing_pof:
            raise PofError(f"entry with such a name already exists: {existing_pof}")

        pof_hap = self._hapless.create_hap(cmd=context.command, name=name)
        # check initial hap status
        pof_db_entry = PofDbEntry(
            hid=pof_hap.hid,
            port_from=context.port_from,
            port_to=context.port_to,
            type_=context.type_,
            metadata=context.metadata,
        )
        self._db.add(pof_db_entry)
        pof = Pof.compile(pof_db_entry, pof_hap)
        return pof

    def delete(self, pof: Pof, force: bool = False) -> None:
        if pof.status == Status.ACTIVE:
            raise PofError(f"cannot delete active forwarding {pof.name}")
        self._hapless._clean_one(pof._hap)
        self._db.delete(pof_id=pof.hid)

    def rename(self, pof: Pof, new_name: str) -> None:
        new_name = new_name.strip()
        if not new_name:
            raise PofError("new name cannot be empty")

        existing_pof = self._get_or_none(new_name)
        if existing_pof:
            raise PofError(f"entry with such a name already exists: {existing_pof}")

        self._hapless.rename_hap(pof._hap, new_name)

    def run_command(self, command: str):
        name: str = f"pof-{Hap.get_random_name()}"
        hap = self._hapless.create_hap(cmd=command, name=name, redirect_stderr=True)
        self._hapless.run_hap(hap)
        # os.exit(0) at this point, cannot log

    def start(self, pof: Pof):
        """
        Start the port forwarding process for the given entry.
        """
        if pof.status == Status.ACTIVE:
            raise PofError(f"port forwarding {pof.name} is already active")

        self._hapless.run_hap(pof._hap)

    def stop(self, pof: Pof):
        """
        Stop the port forwarding process for the given entry.
        """
        if pof.status != Status.ACTIVE:
            raise PofError(f"port forwarding {pof.name} is already inactive")

        command_context = self.restore_context(pof)
        self._hapless.signal(hap=pof._hap, sig=command_context.signal)

    def restart(self, pof: Pof):
        self._hapless.restart(pof._hap)

    def get_pof(self, pof_alias: str) -> Pof:
        pof_hap = self._hapless.get_hap(pof_alias)
        if pof_hap is None:
            raise PofError(f"no pof found for alias {pof_alias}")
        pof_db_entry = self._db.get(pof_id=pof_hap.hid)
        if pof_db_entry is None:
            raise PofError(f"no pof entry found in the database for id {pof_hap.hid}")

        pof = Pof.compile(pof_db_entry, pof_hap)
        return pof

    def _get_or_none(self, pof_alias: str) -> Optional[Pof]:
        try:
            return self.get_pof(pof_alias)
        except PofError:
            pass

    def get_pofs(self, statuses: Optional[list[Status]] = None) -> list[Pof]:
        """
        Retrieve the list of port forwarding configurations.
        """
        # Placeholder for actual implementation
        haps = self._hapless.get_haps()
        pofs = []
        for pof_hap in haps:
            pof_db_entry = self._db.get(pof_id=pof_hap.hid)
            if pof_db_entry is None:
                raise PofError(
                    f"no pof entry found in the database for id {pof_hap.hid}"
                )
            pofs.append(Pof.compile(pof_db_entry, pof_hap))
        return list(
            filter(lambda pof: statuses is None or pof.status in statuses, pofs)
        )

    def logs(self, pof: Pof, follow: bool = False):
        """
        Retrieve logs for a specific port forwarding entry.
        If `follow` is True, it should stream the logs.
        """
        if follow:
            return tail(pof.logfile, follow=True)

        return cat(pof.logfile)

    def restore_context(self, pof: Pof) -> CommandContext:
        """
        Restores a command context for the given port forwarding entry.
        """
        # TODO: actually restore context if we are going to use it
        match pof.type_:
            case "kubernetes":
                context = CommandK8s()
            case "ssh":
                context = CommandSsh()
            case _:
                raise PofError(f"unknown pof type: {pof.type_}")
        return context
