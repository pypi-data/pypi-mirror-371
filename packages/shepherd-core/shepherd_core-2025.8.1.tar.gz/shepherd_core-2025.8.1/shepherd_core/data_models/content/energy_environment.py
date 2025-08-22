"""Data-model for recorded eEnvs."""

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import PositiveFloat
from pydantic import model_validator

from shepherd_core.data_models.base.content import ContentModel
from shepherd_core.testbed_client import tb_client


class EnergyDType(str, Enum):
    """Data-Type-Options for energy environments."""

    ivtrace = ivsample = ivsamples = "ivsample"
    ivsurface = ivcurve = ivcurves = "ivcurve"
    isc_voc = "isc_voc"


class EnergyEnvironment(ContentModel):
    """Recording of meta-data representation of a testbed-component."""

    # General Metadata & Ownership -> ContentModel

    data_path: Path
    data_type: EnergyDType
    data_local: bool = True
    """ ⤷ signals that file has to be copied to testbed"""

    duration: PositiveFloat
    energy_Ws: PositiveFloat
    valid: bool = False

    # TODO: scale up/down voltage/current
    # TODO: multiple files for one env
    # TODO: mean power as energy/duration
    # TODO: harvester, transducer

    # additional descriptive metadata, TODO: these are very solar-centered -> generalize
    light_source: str | None = None
    weather_conditions: str | None = None
    indoor: bool | None = None
    location: str | None = None

    @model_validator(mode="before")
    @classmethod
    def query_database(cls, values: dict[str, Any]) -> dict[str, Any]:
        values, _ = tb_client.try_completing_model(cls.__name__, values)
        # TODO: figure out a way to crosscheck type with actual data
        return tb_client.fill_in_user_data(values)
