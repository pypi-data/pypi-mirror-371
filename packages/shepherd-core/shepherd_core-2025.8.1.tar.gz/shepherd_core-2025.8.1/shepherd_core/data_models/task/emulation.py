"""Configuration for the Observer in Emulation-Mode."""

import copy
from collections.abc import Set as AbstractSet
from datetime import datetime
from datetime import timedelta
from enum import Enum
from pathlib import Path
from pathlib import PurePosixPath
from typing import Annotated

from pydantic import Field
from pydantic import model_validator
from pydantic import validate_call
from typing_extensions import Self

from shepherd_core.data_models.base.content import IdInt
from shepherd_core.data_models.base.shepherd import ShpModel
from shepherd_core.data_models.base.timezone import local_tz
from shepherd_core.data_models.content.virtual_source import VirtualSourceConfig
from shepherd_core.data_models.experiment.experiment import Experiment
from shepherd_core.data_models.experiment.observer_features import GpioActuation
from shepherd_core.data_models.experiment.observer_features import GpioTracing
from shepherd_core.data_models.experiment.observer_features import PowerTracing
from shepherd_core.data_models.experiment.observer_features import SystemLogging
from shepherd_core.data_models.experiment.observer_features import UartLogging
from shepherd_core.data_models.experiment.target_config import vsrc_neutral
from shepherd_core.data_models.testbed import Testbed
from shepherd_core.data_models.testbed.cape import TargetPort
from shepherd_core.logger import log

from .helper_paths import path_posix


class Compression(str, Enum):
    """Options for choosing a dataset-compression."""

    lzf = "lzf"  # not native hdf5
    gzip1 = gzip = default = 1  # higher compr & load
    null = None
    # NOTE: lzf & external file-compression (xz or zstd) work better than gzip
    #       -> even with additional compression


compressions_allowed: list = [None, "lzf", 1]
c_translate = {"lzf": "lzf", "1": 1, "None": None, None: None}


class EmulationTask(ShpModel):
    """Configuration for the Observer in Emulation-Mode."""

    # General config
    input_path: Path
    """ ⤷ hdf5 file containing harvesting data"""
    output_path: Path | None = None
    """ ⤷ dir- or file-path for storing the recorded data:

    - providing a directory -> file is named emu_timestamp.h5
    - for a complete path the filename is not changed except it exists and
      overwrite is disabled -> emu#num.h5
    TODO: should the output-path be mandatory?
    """
    force_overwrite: bool = False
    """ ⤷ Overwrite existing file"""
    output_compression: Compression | None = Compression.default
    """ ⤷ should be lzf, 1 (gzip level 1) or None (order of recommendation)"""
    time_start: datetime | None = None
    """ timestamp or unix epoch time, None = ASAP"""
    duration: timedelta | None = None
    """ ⤷ Duration of recording in seconds, None = till EOF"""

    # emulation-specific
    use_cal_default: bool = False
    """ ⤷ Use default calibration values, skip loading from EEPROM"""

    enable_io: bool = True
    # TODO: add direction of pins! also it seems error-prone when only setting _tracing
    """ ⤷ Switch the GPIO level converter to targets on/off

    pre-req for sampling gpio / uart,
    """
    io_port: TargetPort = TargetPort.A
    """ ⤷ Either Port A or B that gets connected to IO"""
    pwr_port: TargetPort = TargetPort.A
    """ ⤷ selected port will be current-monitored

    - main channel is nnected to virtual Source
    - the other port is aux
    """
    voltage_aux: Annotated[float, Field(ge=0, le=4.5)] | str = 0
    """ ⤷ aux_voltage options
    - 0-4.5 for specific const Voltage (0 V = disabled),
    - "buffer" will output intermediate voltage (storage cap of vsource),
    - "main" will mirror main target voltage
    """
    # sub-elements, could be partly moved to emulation
    virtual_source: VirtualSourceConfig = vsrc_neutral
    """ ⤷ Use the desired setting for the virtual source,

    provide parameters or name like BQ25570
    """

    power_tracing: PowerTracing | None = PowerTracing()
    gpio_tracing: GpioTracing | None = GpioTracing()
    uart_logging: UartLogging | None = UartLogging()
    gpio_actuation: GpioActuation | None = None
    sys_logging: SystemLogging | None = SystemLogging()

    verbose: Annotated[int, Field(ge=0, le=4)] = 2
    """ ⤷ 0=Errors, 1=Warnings, 2=Info, 3=Debug,

    TODO: just bool now, systemwide
    """

    @model_validator(mode="before")
    @classmethod
    def pre_correction(cls, values: dict) -> dict:
        # convert & add local timezone-data
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
        time_now = datetime.now().astimezone() - timedelta(hours=24)
        if self.time_start is not None and self.time_start < time_now:
            msg = (
                "Start-Time for Emulation can't be in the past "
                f"('{self.time_start}' vs '{time_now}'."
            )
            log.error(msg)  # do not raise anymore - server & clients do not have to match
        if self.duration and self.duration.total_seconds() < 0:
            raise ValueError("Task-Duration can't be negative.")
        if isinstance(self.voltage_aux, str) and self.voltage_aux not in {
            "main",
            "buffer",
        }:
            raise ValueError("Voltage Aux must be in float (0 - 4.5) or string 'main' / 'mid'.")
        if self.gpio_actuation is not None:
            raise ValueError("GPIO Actuation not yet implemented!")

        io_requested = any(
            _io is not None for _io in (self.gpio_actuation, self.gpio_tracing, self.uart_logging)
        )
        if self.enable_io and not io_requested:
            log.warning("Target IO enabled, but no feature requested IO")
        if not self.enable_io and io_requested:
            log.warning("Target IO not enabled, but a feature requested IO")
        return self

    @classmethod
    @validate_call
    def from_xp(cls, xp: Experiment, tb: Testbed, tgt_id: IdInt, root_path: Path) -> Self:
        obs = tb.get_observer(tgt_id)
        tgt_cfg = xp.get_target_config(tgt_id)
        io_requested = any(
            _io is not None
            for _io in (tgt_cfg.gpio_actuation, tgt_cfg.gpio_tracing, tgt_cfg.uart_logging)
        )

        return cls(
            input_path=path_posix(tgt_cfg.energy_env.data_path),
            output_path=path_posix(root_path / f"emu_{obs.name}.h5"),
            time_start=copy.copy(xp.time_start),
            duration=xp.duration,
            enable_io=io_requested,
            io_port=obs.get_target_port(tgt_id),
            pwr_port=obs.get_target_port(tgt_id),
            virtual_source=tgt_cfg.virtual_source,
            power_tracing=tgt_cfg.power_tracing,
            gpio_tracing=tgt_cfg.gpio_tracing,
            uart_logging=tgt_cfg.uart_logging,
            gpio_actuation=tgt_cfg.gpio_actuation,
            sys_logging=xp.sys_logging,
        )

    def is_contained(self, paths: AbstractSet[PurePosixPath]) -> bool:
        """Limit paths to allowed directories.

        TODO: could be added to validator (with a switch)
        """
        all_ok = any(self.input_path.is_relative_to(path) for path in paths)
        all_ok &= any(self.output_path.is_relative_to(path) for path in paths)
        return all_ok


# TODO: herdConfig
#  - store if path is remote (read & write)
#   -> so files need to be fetched or have a local path
