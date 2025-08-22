"""meta-data representation of a testbed-component (physical object)."""

from datetime import datetime
from typing import Annotated
from typing import Any

from pydantic import Field
from pydantic import model_validator

from shepherd_core.data_models.base.content import IdInt
from shepherd_core.data_models.base.content import NameStr
from shepherd_core.data_models.base.content import SafeStr
from shepherd_core.data_models.base.shepherd import ShpModel
from shepherd_core.testbed_client import tb_client

from .mcu import MCU

IdInt16 = Annotated[int, Field(ge=0, lt=2**16)]

MCUPort = Annotated[int, Field(ge=1, le=2)]


class Target(ShpModel, title="Target Node (DuT)"):
    """meta-data representation of a testbed-component (physical object)."""

    id: IdInt
    name: NameStr
    version: NameStr
    description: SafeStr

    comment: SafeStr | None = None

    active: bool = True
    created: datetime = Field(default_factory=datetime.now)

    testbed_id: IdInt16 | None = None
    """ ⤷ is derived from ID (targets are still selected by id!)"""
    mcu1: MCU | NameStr
    mcu2: MCU | NameStr | None = None

    # TODO: programming pins per mcu should be here (or better in Cape)

    def __str__(self) -> str:
        return self.name

    @model_validator(mode="before")
    @classmethod
    def query_database(cls, values: dict[str, Any]) -> dict[str, Any]:
        values, _ = tb_client.try_completing_model(cls.__name__, values)

        # post correction
        for _mcu in ["mcu1", "mcu2"]:
            if isinstance(values.get(_mcu), str):
                values[_mcu] = MCU(name=values[_mcu])
                # ⤷ this will raise if default is faulty
            elif isinstance(values.get(_mcu), dict):
                values[_mcu] = MCU(**values[_mcu])
        if values.get("testbed_id") is None:
            values["testbed_id"] = values.get("id") % 2**16

        return values
