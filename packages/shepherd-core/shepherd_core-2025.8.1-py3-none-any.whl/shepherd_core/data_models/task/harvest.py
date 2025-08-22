"""Config for the Observer in Harvest-Mode to record IV data from a harvesting-source."""

from collections.abc import Set as AbstractSet
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from pathlib import PurePosixPath
from typing import Annotated

from pydantic import Field
from pydantic import model_validator
from typing_extensions import Self

from shepherd_core.data_models.base.shepherd import ShpModel
from shepherd_core.data_models.base.timezone import local_tz
from shepherd_core.data_models.content.virtual_harvester import VirtualHarvesterConfig
from shepherd_core.data_models.experiment.observer_features import PowerTracing
from shepherd_core.data_models.experiment.observer_features import SystemLogging

from .emulation import Compression


class HarvestTask(ShpModel):
    """Config for the Observer in Harvest-Mode to record IV data from a harvesting-source."""

    # General config
    output_path: Path
    """ ⤷ dir- or file-path for storing the recorded data:

    - providing a directory -> file is named hrv_timestamp.h5
    - for a complete path the filename is not changed except it exists and
      overwrite is disabled -> name#num.h5
    """
    force_overwrite: bool = False
    """ ⤷ Overwrite existing file"""
    output_compression: Compression | None = Compression.default
    """ ⤷ should be 1 (level 1 gzip), lzf, or None (order of recommendation)"""

    time_start: datetime | None = None
    """ timestamp or unix epoch time, None = ASAP"""
    duration: timedelta | None = None
    """ ⤷ Duration of recording in seconds, None = till EOFSys"""

    # emulation-specific
    use_cal_default: bool = False
    """ ⤷ Use default calibration values, skip loading from EEPROM"""

    virtual_harvester: VirtualHarvesterConfig = VirtualHarvesterConfig(name="mppt_opt")
    """ ⤷ Choose one of the predefined virtual harvesters or configure a new one
    """
    power_tracing: PowerTracing = PowerTracing()
    sys_logging: SystemLogging | None = SystemLogging()

    verbose: Annotated[int, Field(ge=0, le=4)] = 2
    """ ⤷ 0=Errors, 1=Warnings, 2=Info, 3=Debug"""

    # TODO: there is an unused DAC-Output patched to the harvesting-port

    @model_validator(mode="before")
    @classmethod
    def pre_correction(cls, values: dict) -> dict:
        # convert & add local timezone-data, TODO: used twice, refactor
        has_time = values.get("time_start") is not None
        if has_time and isinstance(values["time_start"], (int, float)):
            values["time_start"] = datetime.fromtimestamp(values["time_start"], tz=local_tz())
        if has_time and isinstance(values["time_start"], str):
            values["time_start"] = datetime.fromisoformat(values["time_start"])
        if has_time and values["time_start"].tzinfo is None:
            values["time_start"] = values["time_start"].astimezone()
        return values

    @model_validator(mode="after")
    def post_validation(self) -> Self:
        # TODO: limit paths
        has_time = False  # TODO: deactivated, self.time_start is not None
        time_now = datetime.now().astimezone()
        if has_time and self.time_start < time_now:
            msg = (
                f"Start-Time for Harvest can't be in the past ('{self.time_start}' vs '{time_now}'."
            )
            raise ValueError(msg)
        if self.duration and self.duration.total_seconds() < 0:
            raise ValueError("Task-Duration can't be negative.")
        return self

    def is_contained(self, paths: AbstractSet[PurePosixPath]) -> bool:
        """Limit paths to allowed directories."""
        return any(self.output_path.is_relative_to(path) for path in paths)
