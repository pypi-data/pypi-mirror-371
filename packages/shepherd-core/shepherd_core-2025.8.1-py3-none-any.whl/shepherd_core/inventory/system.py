"""System / OS related inventory model."""

import platform
import subprocess
import time
from collections.abc import Mapping
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any

from typing_extensions import Self

from shepherd_core.data_models.base.timezone import local_now
from shepherd_core.logger import log

try:
    import psutil
except ImportError:
    psutil = None

from pydantic import ConfigDict
from pydantic.types import PositiveInt

from shepherd_core.data_models import ShpModel


class SystemInventory(ShpModel):
    """System / OS related inventory model."""

    uptime: PositiveInt
    """ ⤷ seconds"""
    timestamp: datetime

    system: str
    release: str
    version: str

    machine: str
    processor: str

    ptp: str | None = None

    hostname: str

    interfaces: Mapping[str, Any] = MappingProxyType({})
    # ⤷ tuple with
    #   ip IPvAnyAddress
    #   mac MACStr

    fs_root: Sequence[str] = ()
    beagle: Sequence[str] = ()

    model_config = ConfigDict(str_min_length=0)

    @classmethod
    def collect(cls) -> Self:
        ts = local_now()

        if psutil is None:
            ifs2 = {}
            uptime = 0
            log.warning(
                "Inventory-Parameters will be missing. "
                "Please install functionality with "
                "'pip install shepherd_core[inventory] -U' first"
            )
        else:
            ifs1 = psutil.net_if_addrs().items()
            ifs2 = {name: (_if[1].address, _if[0].address) for name, _if in ifs1 if len(_if) > 1}
            uptime = time.time() - psutil.boot_time()

        fs_cmd = ["/usr/bin/df", "-h", "/"]
        fs_out = []
        if Path(fs_cmd[0]).is_file():
            reply = subprocess.run(  # noqa: S603
                fs_cmd, timeout=30, capture_output=True, check=False
            )
            fs_out = str(reply.stdout).split(r"\n")

        beagle_cmd = ["/usr/bin/beagle-version"]
        beagle_out = []
        if Path(beagle_cmd[0]).is_file():
            reply = subprocess.run(  # noqa: S603
                beagle_cmd, timeout=30, capture_output=True, check=False
            )
            beagle_out = str(reply.stdout).split(r"\n")

        ptp_cmd = ["/usr/sbin/ptp4l", "-v"]
        ptp_out = None
        if Path(ptp_cmd[0]).is_file():
            reply = subprocess.run(  # noqa: S603
                ptp_cmd, timeout=30, capture_output=True, check=False
            )
            ptp_out = f"{reply.stdout}, {reply.stderr}"
            # alternative: check_output - seems to be lighter

        model_dict = {
            "uptime": round(uptime),
            "timestamp": ts,
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "interfaces": ifs2,
            "fs_root": fs_out,
            "beagle": beagle_out,
            "ptp": ptp_out,
        }

        return cls(**model_dict)
