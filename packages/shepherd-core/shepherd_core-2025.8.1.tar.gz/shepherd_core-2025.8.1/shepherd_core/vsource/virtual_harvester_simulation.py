"""Simulate behavior of virtual harvester algorithms.

The simulation recreates an observer-cape and the virtual harvester
- input = hdf5-file with an ivcurve
- output = optional as hdf5-file

The output file can be analyzed and plotted with shepherds tool suite.
"""

from contextlib import ExitStack
from pathlib import Path

from tqdm import tqdm

from shepherd_core.data_models.base.calibration import CalibrationHarvester
from shepherd_core.data_models.content.virtual_harvester import HarvesterPRUConfig
from shepherd_core.data_models.content.virtual_harvester import VirtualHarvesterConfig
from shepherd_core.reader import Reader
from shepherd_core.writer import Writer

from .virtual_harvester_model import VirtualHarvesterModel


def simulate_harvester(
    config: VirtualHarvesterConfig, path_input: Path, path_output: Path | None = None
) -> float:
    """Simulate behavior of virtual harvester algorithms.

    Fn return the harvested energy.
    """
    stack = ExitStack()
    file_inp = Reader(path_input, verbose=False)
    stack.enter_context(file_inp)
    cal_inp = file_inp.get_calibration_data()

    if path_output:
        cal_hrv = CalibrationHarvester()
        file_out = Writer(
            path_output, cal_data=cal_hrv, mode="harvester", verbose=False, force_overwrite=True
        )
        stack.enter_context(file_out)
        cal_out = file_out.get_calibration_data()
        file_out.store_hostname("hrv_sim_" + config.name)

    hrv_pru = HarvesterPRUConfig.from_vhrv(
        config,
        for_emu=True,
        dtype_in=file_inp.get_datatype(),
        window_size=file_inp.get_window_samples(),
        voltage_step_V=file_inp.get_voltage_step(),
    )
    hrv = VirtualHarvesterModel(hrv_pru)
    e_out_Ws = 0.0

    for _t, v_inp, i_inp in tqdm(
        file_inp.read(is_raw=True), total=file_inp.chunks_n, desc="Chunk", leave=False
    ):
        v_uV = cal_inp.voltage.raw_to_si(v_inp) * 1e6
        i_nA = cal_inp.current.raw_to_si(i_inp) * 1e9
        length = min(v_uV.size, i_nA.size)
        for _n in range(length):
            v_uV[_n], i_nA[_n] = hrv.ivcurve_sample(
                _voltage_uV=int(v_uV[_n]), _current_nA=int(i_nA[_n])
            )
        e_out_Ws += (v_uV * i_nA).sum() * 1e-15 * file_inp.sample_interval_s
        if path_output:
            v_out = cal_out.voltage.si_to_raw(v_uV / 1e6)
            i_out = cal_out.current.si_to_raw(i_nA / 1e9)
            file_out.append_iv_data_raw(_t, v_out, i_out)

    stack.close()
    return e_out_Ws
