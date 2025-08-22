"""Config for a Task programming the selected target."""

from collections.abc import Set as AbstractSet
from pathlib import Path
from pathlib import PurePosixPath
from typing import Annotated

from pydantic import Field
from pydantic import model_validator
from pydantic import validate_call
from typing_extensions import Self

from shepherd_core.data_models.base.content import IdInt
from shepherd_core.data_models.base.content import SafeStr
from shepherd_core.data_models.base.shepherd import ShpModel
from shepherd_core.data_models.content.firmware import suffix_to_DType
from shepherd_core.data_models.content.firmware_datatype import FirmwareDType
from shepherd_core.data_models.experiment.experiment import Experiment
from shepherd_core.data_models.testbed.cape import TargetPort
from shepherd_core.data_models.testbed.mcu import ProgrammerProtocol
from shepherd_core.data_models.testbed.target import MCUPort
from shepherd_core.data_models.testbed.testbed import Testbed

from .helper_paths import path_posix


class ProgrammingTask(ShpModel):
    """Config for a Task programming the selected target."""

    firmware_file: Path
    target_port: TargetPort = TargetPort.A
    mcu_port: MCUPort = 1
    mcu_type: SafeStr
    """ ⤷ must be either "nrf52" or "msp430" ATM, TODO: clean xp to tasks"""
    voltage: Annotated[float, Field(ge=1, lt=5)] = 3
    datarate: Annotated[int, Field(gt=0, le=1_000_000)] = 200_000
    protocol: ProgrammerProtocol
    # TODO: eradicate - should not exist. derive protocol from mcu_type

    simulate: bool = False

    verbose: Annotated[int, Field(ge=0, le=4)] = 2
    """ ⤷ 0=Errors, 1=Warnings, 2=Info, 3=Debug"""

    @model_validator(mode="after")
    def post_validation(self) -> Self:
        d_type = suffix_to_DType.get(self.firmware_file.suffix.lower())
        if d_type != FirmwareDType.base64_hex:
            msg = (f"Firmware is not intel-hex ({self.firmware_file.as_posix()})",)
            raise ValueError(msg)
        return self

    @classmethod
    @validate_call
    def from_xp(
        cls,
        xp: Experiment,
        tb: Testbed,
        tgt_id: IdInt,
        mcu_port: MCUPort,
        fw_path: Path,
    ) -> Self | None:
        obs = tb.get_observer(tgt_id)
        tgt_cfg = xp.get_target_config(tgt_id)

        fw = tgt_cfg.firmware1 if mcu_port == 1 else tgt_cfg.firmware2
        if fw is None:
            return None

        return cls(
            firmware_file=path_posix(fw_path),
            target_port=obs.get_target_port(tgt_id),
            mcu_port=mcu_port,
            mcu_type=fw.mcu.name,
            voltage=fw.mcu.prog_voltage,
            datarate=fw.mcu.prog_datarate,
            protocol=fw.mcu.prog_protocol,
        )

    def is_contained(self, paths: AbstractSet[PurePosixPath]) -> bool:
        """Limit paths to allowed directories."""
        return any(self.firmware_file.is_relative_to(path) for path in paths)
