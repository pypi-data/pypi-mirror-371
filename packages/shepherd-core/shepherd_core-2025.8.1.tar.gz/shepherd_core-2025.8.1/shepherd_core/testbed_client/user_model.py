"""Model for user-management."""

import secrets
from hashlib import pbkdf2_hmac
from typing import Annotated
from typing import Any

from pydantic import EmailStr
from pydantic import Field
from pydantic import SecretBytes
from pydantic import SecretStr
from pydantic import StringConstraints
from pydantic import model_validator
from pydantic import validate_call

from shepherd_core.data_models.base.content import NameStr
from shepherd_core.data_models.base.content import SafeStr
from shepherd_core.data_models.base.content import id_default
from shepherd_core.data_models.base.shepherd import ShpModel


@validate_call
def hash_password(pw: Annotated[str, StringConstraints(min_length=20, max_length=100)]) -> bytes:
    """Generate a hash of a string.

    # NOTE: 1M Iterations need 25s on beaglebone
    # TODO: add salt of testbed -> this fn should be part of Testbed-Object
    """
    return pbkdf2_hmac(
        "sha512",
        password=pw.encode("utf-8"),
        salt=b"testbed_salt_TODO",
        iterations=1_000_000,
        dklen=128,
    )


class User(ShpModel):
    """meta-data representation of a testbed-component (physical object)."""

    id: int = Field(
        description="Unique ID",
        default_factory=id_default,
    )
    name: NameStr
    description: SafeStr | None = None
    comment: SafeStr | None = None

    name_full: NameStr | None = None
    group: NameStr
    email: EmailStr

    pw_hash: SecretBytes | None = None
    # ⤷ was hash_password("this_will_become_a_salted_slow_hash") -> slowed BBB down
    # ⤷ TODO (min_length=128, max_length=512)

    token: SecretStr
    # ⤷ TODO (min_length=128), request with: token.get_secret_value()
    active: bool = False

    @model_validator(mode="before")
    @classmethod
    def query_database(cls, values: dict[str, Any]) -> dict[str, Any]:
        # TODO:

        # post correction
        if values.get("token") is None:
            values["token"] = "shepherd_token_" + secrets.token_urlsafe(nbytes=128)

        return values
