"""In this module, the midas mv grid is defined and configured."""

import pandapower as pp
import pandapower.networks as pn


def build_grid(**kwargs):
    """Create the default midas mv grid."""
    # DERs are added manually
    grid = pn.create_cigre_network_mv(with_der="all")  # type: ignore[reportArgumentType]
    grid.load = grid.load[0:0]
    grid.sgen = grid.sgen[0:0]
    grid.storage = grid.storage[0:0]

    load_res = [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    load_com = [13, 14]
    sgen = [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    storage = [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    tap_changer = {
        0: {"min": -10, "max": 10, "mid": 0, "ts_size": 0.625},
        1: {"min": -10, "max": 10, "mid": 0, "ts_size": 0.625},
    }

    for bus_id in load_res:
        pp.create_load(
            grid,
            bus=bus_id,
            p_mw=0.0,
            q_mvar=0,
            name="LOAD_AGGRLV_{}".format(bus_id),
            scaling=1.0,
            in_service=True,
            controllable=False,
        )

    for bus_id in load_com:
        pp.create_load(
            grid,
            bus=bus_id,
            p_mw=0.0,
            q_mvar=0,
            name="LOAD_COMM_{}".format(bus_id),
            scaling=1.0,
            in_service=True,
            controllable=False,
        )

    for bus_id in sgen:
        pp.create_sgen(
            grid,
            bus=bus_id,
            p_mw=0.0,
            q_mvar=0,
            name="SGEN_{}".format(bus_id),
            scaling=1.0,
            type=None,  # type: ignore[reportArgumentType]
            in_service=True,
            controllable=False,
        )

    for bus_id in storage:
        pp.create_storage(
            grid,
            bus=bus_id,
            p_mw=0.0,
            max_e_mwh=1,
            q_mvar=0,
            name="STORAGE_{}".format(bus_id),
            scaling=1.0,
            type=None,
            in_service=True,
            controllable=False,
        )

    for trafo_id, trafo_config in tap_changer.items():
        grid.trafo.loc[trafo_id, "tap_side"] = "lv"
        grid.trafo.loc[trafo_id, "tap_min"] = trafo_config["min"]
        grid.trafo.loc[trafo_id, "tap_max"] = trafo_config["max"]
        grid.trafo.loc[trafo_id, "tap_neutral"] = trafo_config["mid"]
        grid.trafo.loc[trafo_id, "tap_step_percent"] = trafo_config["ts_size"]
        grid.trafo.loc[trafo_id, "tap_pos"] = trafo_config["mid"]

    num_loads = len(load_res) + len(load_com)
    num_sgens = len(sgen)
    num_storages = len(storage)

    if "constant_load_p_mw" in kwargs:
        grid.load.p_mw.values[:] = [
            kwargs["constant_load_p_mw"] for _ in range(num_loads)
        ]
    if "constant_load_q_mvar" in kwargs:
        grid.load.q_mvar.values[:] = [
            kwargs["constant_load_q_mvar"] for _ in range(num_loads)
        ]

    if "constant_sgen_p_mw" in kwargs:
        grid.sgen.p_mw.values[:] = [
            kwargs["constant_sgen_p_mw"] for _ in range(num_sgens)
        ]

    if "constant_sgen_q_mvar" in kwargs:
        grid.sgen.q_mvar.values[:] = [
            kwargs["constant_sgen_q_mvar"] for _ in range(num_sgens)
        ]
    if "constant_storage_p_mw" in kwargs:
        grid.storage.p_mw.values[:] = [
            kwargs["constant_storage_p_mw"] for _ in range(num_storages)
        ]
    if "constant_storage_q_mvar" in kwargs:
        grid.storage.q_mvar.values[:] = [
            kwargs["constant_storage_q_mvar"] for _ in range(num_storages)
        ]
    return grid
