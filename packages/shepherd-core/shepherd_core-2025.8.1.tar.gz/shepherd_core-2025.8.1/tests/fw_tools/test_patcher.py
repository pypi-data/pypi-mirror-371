import os
import shutil
from pathlib import Path

import pytest

from shepherd_core import fw_tools

from .conftest import files_elf


@pytest.mark.elf
@pytest.mark.parametrize("path_elf", files_elf)
def test_sym_finding(path_elf: Path) -> None:
    assert fw_tools.find_symbol(path_elf, "SHEPHERD_NODE_ID")


@pytest.mark.elf
@pytest.mark.parametrize("path_elf", files_elf)
def test_sym_reading(path_elf: Path) -> None:
    assert fw_tools.read_symbol(path_elf, "SHEPHERD_NODE_ID", 2)


@pytest.mark.elf
@pytest.mark.parametrize("path_elf", files_elf)
def test_sym_mod(path_elf: Path, tmp_path: Path) -> None:
    value = 0xCAFE
    sym = "SHEPHERD_NODE_ID"
    path_new = tmp_path / path_elf.name
    shutil.copy(path_elf, path_new)
    path_gen = fw_tools.modify_symbol_value(path_new, sym, value, overwrite=False)
    assert path_gen.is_file()
    assert path_gen.as_posix() != path_new.as_posix()
    value_new = fw_tools.read_symbol(path_gen, sym, 2)
    assert value == value_new
    value_old = fw_tools.read_symbol(path_elf, sym, 2)
    assert value_new != value_old


@pytest.mark.elf
@pytest.mark.parametrize("path_elf", files_elf)
def test_sym_mod_overwrite(path_elf: Path, tmp_path: Path) -> None:
    value = 0xCAFE
    sym = "SHEPHERD_NODE_ID"
    assert tmp_path.exists()
    path_new = tmp_path / path_elf.name
    shutil.copy(path_elf, path_new)
    path_gen = fw_tools.modify_symbol_value(path_new, sym, value, overwrite=True)
    if path_gen is None and os.name == "nt":
        # TODO: overwriting fails ATM on WinOS (at least in tmp-dir)
        return
    assert path_gen.is_file()
    assert path_gen.as_posix() == path_new.as_posix()
    value_new = fw_tools.read_symbol(path_gen, sym, 2)
    assert value == value_new
    value_old = fw_tools.read_symbol(path_elf, sym, 2)
    assert value_new != value_old


@pytest.mark.elf
@pytest.mark.parametrize("path_elf", files_elf)
def test_id_mod(path_elf: Path, tmp_path: Path) -> None:
    value = 0xCAFE
    path_new = tmp_path / path_elf.name
    shutil.copy(path_elf, path_new)
    path_gen = fw_tools.modify_uid(path_new, value)
    if path_gen is None and os.name == "nt":
        # TODO: overwriting fails ATM on WinOS (at least in tmp-dir)
        return
    assert path_gen.as_posix() == path_new.as_posix()
    value_new = fw_tools.read_symbol(path_gen, "SHEPHERD_NODE_ID", 2)
    assert value == value_new
