"""
functions which \b offload simulations over the Azure cloud.
"""
# Standard library imports
import jdata

# Third party imports
import numpy as np
from pathlib import Path

# Local imports
from src import tomca


def batch(iterable: dict, size: int):
    length = len(iterable)
    for idx in range(0, length, size):
        yield iterable[idx: min(idx + size, length)]

# TODO: Is this method used anywhere ? #S.J
def process_sub_result(args):
    i, sub_result = args
    sub_result["Expt"]["verb"] = sub_result["Expt"]["verb_tmp"]
    jcfg = tomca.make.dir_state(sub_result, post_build=1, append_str="_" + str(i))
    jcfg = tomca.writ.jcfg_json(jcfg, desc="_jcfg_results")
    # We could consider also generating the plots here.
    return jcfg


def simulate(jcfg: dict, delta_cfgs: dict,
             offloader_cfg: dict = {"num_nodes": 2},
             use_octave: bool = False,
             detach: bool = False) -> list:
    from offloader import Offloader, OffloadSettings

    offload_idx = 0
    for delta_cfg in delta_cfgs:
        delta_cfg["offloader_index"] = offload_idx
        offload_idx += 1

    def pre(task_folder: Path, sub_delta_cfgs: list) -> None:
        # Function to be evaluated on local machine (not offloaded) before offloading
        jcfg["Expt"]["verb_tmp"] = jcfg["Expt"]["verb"]
        jcfg["Expt"]["verb"] = 1
        # Flag to reduce the size of the dict as it is evaluated
        jcfg["Expt"]["offload"] = 1
        # Set to 0 any key starting with fig_
        for key in jcfg["Expt"]["plot"]:
            if key.startswith("fig_"):
                jcfg["Expt"][key] = 0

        jdata.savet(jcfg, str(task_folder / "model_jcfg.json"), indent=4)
        # Write the sub_delta_cfgs.json file.  This is also the same across all offloaded computers, but the index(es) of the sub_delta_cfgs list used by each node is different.
        jdata.savet(sub_delta_cfgs, str(task_folder / "sub_delta_cfgs.json"), indent=4)

        # with open(str(task_folder/'sub_delta_cfgs.json'), 'w') as f:
        #     jdata.savet(sub_delta_cfgs, f)

    def post(task_folder: str, sub_delta_cfgs: dict):
        # Function to be evaluated on local machine (not offloaded) after offloading

        sub_results = jdata.loadt(f"{task_folder}/sub_results.json")

        # For each of the returned sub_results, create a local state folder
        # and write those results to a file in that folder
        for idx, sub_result in enumerate(sub_results):

            sub_result["Expt"]["verb"] = sub_result["Expt"]["verb_tmp"]
            sub_result.get("Expt")["makeStateDir"] = sub_result.get("Expt").get("write").get("state_results_json")
            if sub_result.get("Expt").get("makeStateDir") == 1:
                jcfg = tmcx.make.dir_state(sub_result,
                                           post_build=1,
                                           append_str="_" + str(idx) + str(np.random.randint(0, 10000)))
                jcfg = tmcx.writ.jcfg_json(jcfg, desc="_jcfg_results")
        return sub_results

    tmcx.util.verb("Setting up offloaded simulation", jcfg["Expt"]["verb"], 0)

    # Figure out which image to use
    if "MediaFormat" in jcfg["Domain"]:
        if "svmc" == jcfg["Domain"]["MediaFormat"]:
            use_octave = True

    # Evenly distribute over nodes
    if "num_tasks_per_node" not in offloader_cfg:
        offloader_cfg["num_tasks_per_node"] = int(np.ceil(len(delta_cfgs) / offloader_cfg["num_nodes"]))

    tomca.util.verb(
        "Sim States: "
        + str(len(delta_cfgs))
        + ", offloader nodes: "
        + str(offloader_cfg["num_nodes"])
        + ", tasks per node: "
        + str(offloader_cfg["num_tasks_per_node"]),
        jcfg["Expt"]["verb"],
        0,
    )

    tomca.util.verb(f"Sim States: {len(delta_cfgs)}, offloader nodes: {offloader_cfg['num_nodes']}, tasks per node: {offloader_cfg['num_tasks_per_node']}",
                   jcfg["Expt"]["verb"],
                   0)
    offloader = Offloader("offloadexperimental.offloader.nl")
    task_resources = {
        "requests": {"cpu": 1.0, "memory": "5Gi"},
        "limits": {"nvidia.com/gpu": 1},
    }

    if use_octave:
        image = "ci.tno.nl/tissue-optics/mcx:tmcx-octave"
    else:
        image = "ci.tno.nl/tissue-optics/mcx:tmcx"

    command = "python offload.py"
    settings = OffloadSettings(
        pre,
        image,
        command,
        post,
        name="tomca",
        task_resources=task_resources,
        auto_delete=False,
        stable=False,
        max_concurrent_tasks=offloader_cfg["num_nodes"],
        allow_failure=True,
    )
    settings.add_file(
        Path("c://dev/tomca/src/tomca/__init__.py"), Path("src/tomca")
    )
    settings.add_file(Path("c://dev/tomca/src/tomca/anly.py"), Path("src/tomca"))
    settings.add_file(Path("c://dev/tomca/src/tomca/buil.py"), Path("src/tomca"))
    settings.add_file(Path("c://dev/tomca/src/tomca/calc.py"), Path("src/tomca"))
    settings.add_file(Path("c://dev/tomca/src/tomca/conv.py"), Path("src/tomca"))
    settings.add_file(Path("c://dev/tomca/src/tomca/exec.py"), Path("src/tomca"))
    settings.add_file(Path("c://dev/tomca/src/tomca/grap.py"), Path("src/tomca"))
    settings.add_file(Path("c://dev/tomca/src/tomca/impo.py"), Path("src/tomca"))
    settings.add_file(Path("c://dev/tomca/src/tomca/make.py"), Path("src/tomca"))
    settings.add_file(Path("c://dev/tomca/src/tomca/modi.py"), Path("src/tomca"))
    settings.add_file(Path("c://dev/tomca/src/tomca/offl.py"), Path("src/tomca"))
    settings.add_file(Path("c://dev/tomca/src/tomca/proc.py"), Path("src/tomca"))
    settings.add_file(Path("c://dev/tomca/src/tomca/stas.py"), Path("src/tomca"))
    settings.add_file(Path("c://dev/tomca/src/tomca/util.py"), Path("src/tomca"))
    settings.add_file(Path("c://dev/tomca/src/tomca/writ.py"), Path("src/tomca"))
    settings.add_file(Path("c://dev/tomca/projects/offloader/offload.py"))
    settings.add_file(
        Path("c://dev/tomca/src/tomca/z_extras.py"), Path("src/tomca")
    )
    settings.retrieve_file(Path("sub_results.json"))

    tomca.util.verb(
        "Cutting DeltaConfigs into sub_DeltaConfigs batches...", jcfg["Expt"]["verb"], 1
    )
    tasks_parameters = [
        {"sub_delta_cfgs": sub_delta_cgfs}
        for sub_delta_cgfs in batch(delta_cfgs, offloader_cfg["num_tasks_per_node"])
    ]
    tomca.util.verb("Starting offload simulation", jcfg["Expt"]["verb"], 0)
    if detach is False:
        offload_result = offloader.run(settings, tasks_parameters)
        results = []
        for task in offload_result.all_tasks():
            for result in task.result:
                results.append(result)
        # results_list = []
        # order = []
        # for task in offload_result._tasks:
        #     for result in task.result:
        #         results_list.append(result)
        #         order.append(int(result['offloader_index']))
        # results_list = [result for _,result in sorted(zip(order, results_list))]
        return results

    if detach is True:
        run_id = offloader.start(settings, tasks_parameters)
        tomca.util.verb(
            "Detached offloader run with run_id: " + str(run_id),
            jcfg["Expt"]["verb"],
            0,
        )
        tomca.util.verb(
            "Check status with: offl.simulation_status(run_id, offloader)",
            jcfg["Expt"]["verb"],
            0,
        )
        tomca.util.verb(
            "Fetch results with: offl.simulation_fetch(run_id, offloader)",
            jcfg["Expt"]["verb"],
            0,
        )
        return [run_id, offloader]


def simulation_fetch(run_id, offloader):
    """
    Fetches simulation results for a given run_id using the offloader.

    Parameters:
    - run_id (str): The ID of the simulation run.
    - offloader (Offloader): An instance of the Offloader class used for fetching the results.

    Returns:
    None
    """
    from offloader import Offloader, OffloadSettings, OffloadResult

    def post(task_folder, sub_delta_cfgs):
        """
        Function to be evaluated on the local machine (not offloaded) after offloading.

        Parameters:
        - task_folder (str): The path to the task folder.
        - sub_delta_cfgs (list): A list of sub_delta_cfgs.

        Returns:
        None
        """

        sub_results = jdata.loadt(str(task_folder / "sub_results.json"))

        # For each of the returned sub_results, create a local state folder and write those results to a file in that folder
        for i, sub_result in enumerate(sub_results):
            sub_result["Expt"]["verb"] = sub_result["Expt"]["verb_tmp"]

            if "makeStateDir" in sub_result["Expt"]:
                pass
            else:
                sub_result["Expt"]["makeStateDir"] = 1
            if sub_result["Expt"]["makeStateDir"] == 1:
                jcfg = tomca.make.dir_state(
                    sub_result, post_build=1, append_str="_" + str(i)
                )
                jcfg = tomca.writ.jcfg_json(jcfg, desc="_jcfg_results")

        return sub_results

    offload_result = offloader.fetch(run_id, post, auto_delete=False)

    results_list = []
    for task in offload_result._tasks:
        for result in task.result:
            results_list.append(result)
    return results_list


def simulation_status(run_id, offloader):
    """
    Checks the status of a workflow run.

    Parameters:
    - run_id (int): The ID of the workflow run to check.
    - offloader (Offloader): An instance of the Offloader class.

    Returns:
    - None

    This function calls the `is_workflow_finished` method of the `offloader` object
    to check if the specified workflow run with the given `run_id` has finished.
    """
    from offloader import Offloader, OffloadSettings

    return offloader.is_workflow_finished(run_id)
