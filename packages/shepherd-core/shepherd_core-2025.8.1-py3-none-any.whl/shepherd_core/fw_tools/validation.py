"""Helper-functions for firmware-validation.

TODO: Work in Progress.
    - Each arch should have its own file and
    - detection-functions that register in main validator.
"""

import shutil
import tempfile
from pathlib import Path

from intelhex import IntelHex
from intelhex import IntelHexError
from pydantic import validate_call

from shepherd_core.data_models.content.firmware_datatype import FirmwareDType
from shepherd_core.logger import log

from .converter_elf import elf_to_hex

try:
    from elftools.common.exceptions import ELFError
    from pwnlib.elf import ELF
except ImportError as e:
    ELF = None
    ELFError = None
    elf_error_text = (
        "Please install functionality with 'pip install shepherd-core[elf] -U' first, "
        f"underlying exception: {e.msg}"
    )


@validate_call
def is_hex(file: Path) -> bool:
    """Check if file is containing intel-hex data."""
    try:
        _ = IntelHex(file.as_posix())
    except ValueError:  # parsing
        return False
    except IntelHexError:  # structural errors
        return False
    return True


def is_hex_msp430(file: Path) -> bool:
    """Try to detect specifics for that MCU.

    Observations:
    - addresses begin at 0x4000
    - value @0xFFFE (IVT) is start_address (of pgm-code)
    """
    if is_hex(file):
        ih = IntelHex(file.as_posix())
        if ih.minaddr() != 0x4000:
            return False
        if 0xFFFE not in ih.addresses():
            return False
        value = int.from_bytes(ih.gets(0xFFFE, 2), byteorder="little", signed=False)
        if 0x4000 > value >= 0xFF80:
            return False

        # conservative test for now - should be well below 128 kB + 8kB for msp430fr5962
        return ih.get_memory_size() <= 270_000
    return False


def is_hex_nrf52(file: Path) -> bool:
    """Try to detect specifics for that MCU.

    Observations:
    - addresses begin mostly at 0x0 (no must)
    - only one segment (.get_segments), todo
    """
    if is_hex(file):
        ih = IntelHex(file.as_posix())
        # conservative test for now - should be between 0 and 1 MB + 256 kB,
        # but lately showed much higher values > 4 MB
        return ih.get_memory_size() > 0
    return False


# TODO: elf-workflow needs work -> construct experiments without external dependencies
#  - remove conversion to hex
#  - use elftools to verify magic-bytes and similar things done for the hex
#  https://github.com/eliben/pyelftools/wiki/User's-guide


@validate_call
def is_elf(file: Path) -> bool:
    """Check if file is an ELF file."""
    if ELF is None:
        raise RuntimeError(elf_error_text)
    if not file.is_file():
        return False
    try:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            # switcheroo that might prevent windows bug - overwrite fails in modify_symbol_value()
            file_tmp = Path(tmp) / file.name
            shutil.copy(file, file_tmp)
            elf = ELF(path=file_tmp)
            elf.close()
    except ELFError:
        log.debug("File %s is not ELF - Magic number does not match", file.name)
        return False
    return True


def is_elf_msp430(file: Path) -> bool:
    """Check if file is an ELF for that MCU.

    TODO: allow detection without conversion
    """
    if is_elf(file):
        with tempfile.TemporaryDirectory() as path:
            file_hex = Path(path) / "file.hex"
            file_hex = elf_to_hex(file, file_hex)
            if is_hex_msp430(file_hex):
                return True
        return False
    return False


def is_elf_nrf52(file: Path) -> bool:
    """Check if file is an ELF for that MCU.

    TODO: allow detection without conversion
    """
    if is_elf(file):
        with tempfile.TemporaryDirectory() as path:
            file_hex = Path(path) / "file.hex"
            file_hex = elf_to_hex(file, file_hex)
            if is_hex_nrf52(file_hex):
                return True
        return False
    return False


def determine_type(file: Path) -> FirmwareDType:
    """Figure out file-type (hex or elf)."""
    if not file.is_file():
        raise ValueError("Fn needs an existing file as input")
    if is_hex(file):
        return FirmwareDType.path_hex
    if is_elf(file):
        return FirmwareDType.path_elf
    msg = f"Type of file '{file.name}' could not be determined"
    raise ValueError(msg)


def determine_arch(file: Path) -> str:
    """Figure out arch (msp430 or nrf52)."""
    file_t = determine_type(file)
    if file_t == FirmwareDType.path_elf:
        if is_elf_msp430(file):
            return "msp430"
        if is_elf_nrf52(file):
            return "nrf52"
        msg = f"Arch of ELF '{file.name}' could not be determined"
        raise ValueError(msg)
    if file_t == FirmwareDType.path_hex:
        if is_hex_msp430(file):
            return "msp430"
        if is_hex_nrf52(file):
            return "nrf52"
        msg = f"Arch of HEX '{file.name}' could not be determined"
        raise ValueError(msg)
    msg = f"Arch of file '{file.name}' could not be determined"
    raise ValueError(msg)
