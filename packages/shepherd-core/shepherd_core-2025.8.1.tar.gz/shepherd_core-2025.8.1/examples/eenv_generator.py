"""Create a set of static artificial energy environments."""

from itertools import product
from pathlib import Path

import numpy as np
from tqdm import trange

from shepherd_core import Reader as ShpReader
from shepherd_core import Writer as ShpWriter
from shepherd_core.logger import log

# Config
voltages_V = [4.0, 2.0]
currents_A = [2e-3, 1e-3]
duration_s = 10
repetitions = 1

path_here = Path(__file__).parent.absolute()

for _v, _c in product(voltages_V, currents_A):
    v_str = f"{round(_v * 1000)}mV"
    c_str = f"{round(_c * 1000)}mA"
    t_str = f"{round(duration_s * repetitions)}s"
    name = f"eenv_static_{v_str}_{c_str}_{t_str}"
    file_path = path_here / f"{name}.h5"

    if file_path.exists():
        log.info("File exists, will skip: %s", file_path.name)
    else:
        with ShpWriter(file_path) as file:
            file.store_hostname("artificial")
            # values in SI units
            timestamp_vector = np.arange(0.0, duration_s, file.sample_interval_ns / 1e9)
            voltage_vector = np.linspace(_v, _v, int(file.samplerate_sps * duration_s))
            current_vector = np.linspace(_c, _c, int(file.samplerate_sps * duration_s))

            for idx in trange(repetitions, desc="generate", leave=False):
                timestamps = idx * duration_s + timestamp_vector
                file.append_iv_data_si(timestamps, voltage_vector, current_vector)

    with ShpReader(file_path) as file:
        file.save_metadata()
