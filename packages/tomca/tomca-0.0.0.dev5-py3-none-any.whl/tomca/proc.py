"""
functions which \b process simulation data  
"""

import copy
import sys
sys.path.append("C:\\dev\\python\\src")
import scipy.stats as st
from src import tomca
import pmcx
import numpy as np


def combine_jcfgs(jcfg_tmp: dict, jcfg_out: dict, rep):
    """Adds jcfg dict to jcfg_out dict, averaging fluxes and concatenating seeds, etc.  This takes the jcfg_out dict and updates with jcfg tmp values.  IT keeps all else from jcfg_out.

    Args:
        jcfg (dict): _description_
        jcfg_out (dict): _description_

    Returns:
        _type_: _description_
    """
    # Results Concatenation
    jcfg_out["res"]["seeds"] = np.concatenate(
        (jcfg_out["res"]["seeds"], jcfg_tmp["res"]["seeds"]), axis=1
    )
    jcfg_out["res"]["detp"] = np.concatenate(
        (jcfg_out["res"]["detp"], jcfg_tmp["res"]["detp"]), axis=1
    )
    jcfg_out["res"]["p"] = np.concatenate(
        (jcfg_out["res"]["p"], jcfg_tmp["res"]["p"]), axis=0
    )
    jcfg_out["res"]["x"] = np.concatenate(
        (jcfg_out["res"]["x"], jcfg_tmp["res"]["x"]), axis=0
    )
    jcfg_out["res"]["v"] = np.concatenate(
        (jcfg_out["res"]["v"], jcfg_tmp["res"]["v"]), axis=0
    )

    # Results Summation
    jcfg_out["res"]["stat"]["runtime"] = (
        jcfg_out["res"]["stat"]["runtime"] + jcfg_tmp["res"]["stat"]["runtime"]
    )
    jcfg_out["res"]["stat"]["nphoton"] = (
        jcfg_out["res"]["stat"]["nphoton"] + jcfg_tmp["res"]["stat"]["nphoton"]
    )
    jcfg_out["res"]["stat"]["energytot"] = (
        jcfg_out["res"]["stat"]["energytot"] + jcfg_tmp["res"]["stat"]["energytot"]
    )
    jcfg_out["res"]["stat"]["energyabs"] = (
        jcfg_out["res"]["stat"]["energyabs"] + jcfg_tmp["res"]["stat"]["energyabs"]
    )

    # Results Summation, weighted for repeats
    jcfg_out["res"]["flux"] = (
        jcfg_out["res"]["flux"] * (rep - 1) / rep +
        jcfg_tmp["res"]["flux"] / rep
    )

    ### Replay ###
    if jcfg_tmp["Expt"]["doReplay"]:
        # Replay Results Concatenation
        jcfg_out["res_replay"]["seeds"] = np.concatenate(
            (jcfg_out["res_replay"]["seeds"],
             jcfg_tmp["res_replay"]["seeds"]), axis=1
        )
        jcfg_out["res_replay"]["detp"] = np.concatenate(
            (jcfg_out["res_replay"]["detp"],
             jcfg_tmp["res_replay"]["detp"]), axis=1
        )

        # Replay Results Summation, weighted for repeats
        jcfg_out["res_replay"]["flux"] = (
            jcfg_out["res"]["flux"] * (rep - 1) /
            rep + jcfg_tmp["res"]["flux"] / rep
        )

        # Replay Results Summation
        jcfg_out["res_replay"]["stat"]["runtime"] = (
            jcfg_out["res_replay"]["stat"]["runtime"] +
            jcfg_tmp["res_replay"]["stat"]["runtime"]
        )
        jcfg_out["res_replay"]["stat"]["nphoton"] = (
            jcfg_out["res_replay"]["stat"]["nphoton"] +
            jcfg_tmp["res_replay"]["stat"]["nphoton"]
        )
        jcfg_out["res_replay"]["stat"]["energytot"] = (
            jcfg_out["res_replay"]["stat"]["energytot"] +
            jcfg_tmp["res_replay"]["stat"]["energytot"]
        )
        jcfg_out["res_replay"]["stat"]["energyabs"] = (
            jcfg_out["res_replay"]["stat"]["energyabs"] +
            jcfg_tmp["res_replay"]["stat"]["energyabs"]
        )
        
        tomca.util.verb('Finished combining state iteration '+ str(rep), jcfg_out['Expt']['verb'], 2)

    return jcfg_out
