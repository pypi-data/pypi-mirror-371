"""meta-data representation of a testbed-component (physical object)."""

from enum import Enum
from typing import Annotated
from typing import Any

from pydantic import Field
from pydantic import StringConstraints
from pydantic import model_validator
from typing_extensions import Self

from shepherd_core.data_models.base.content import IdInt
from shepherd_core.data_models.base.content import NameStr
from shepherd_core.data_models.base.content import SafeStr
from shepherd_core.data_models.base.shepherd import ShpModel
from shepherd_core.testbed_client import tb_client


class Direction(str, Enum):
    """Options for pin-direction."""

    Input = IN = "IN"
    Output = OUT = "OUT"
    Bidirectional = IO = "IO"


class GPIO(ShpModel, title="GPIO of Observer Node"):
    """meta-data representation of a testbed-component."""

    id: IdInt
    name: NameStr
    description: SafeStr | None = None
    comment: SafeStr | None = None

    direction: Direction = Direction.Input
    dir_switch: Annotated[str, StringConstraints(max_length=32)] | None = None

    reg_pru: Annotated[str, StringConstraints(max_length=10)] | None = None
    pin_pru: Annotated[str, StringConstraints(max_length=10)] | None = None
    reg_sys: Annotated[int, Field(ge=0)] | None = None
    pin_sys: Annotated[str, StringConstraints(max_length=10)] | None = None

    def __str__(self) -> str:
        return self.name

    @model_validator(mode="before")
    @classmethod
    def query_database(cls, values: dict[str, Any]) -> dict[str, Any]:
        values, _ = tb_client.try_completing_model(cls.__name__, values)
        return values

    @model_validator(mode="after")
    def post_validation(self) -> Self:
        # ensure that either pru or sys is used, otherwise instance is considered faulty
        no_pru = (self.reg_pru is None) or (self.pin_pru is None)
        no_sys = (self.reg_sys is None) or (self.pin_sys is None)
        if no_pru and no_sys:
            msg = (
                "GPIO-Instance is faulty -> "
                f"it needs to use pru or sys, content: {self.model_dump()}"
            )
            raise ValueError(msg)
        return self

    def user_controllable(self) -> bool:
        return ("gpio" in self.name.lower()) and (self.direction in {"IO", "OUT"})

    def user_recordable(self) -> bool:
        return (
            ("gpio" in self.name.lower())
            and (self.direction in {"IO", "IN"})
            and (self.pin_pru is not None)
        )
