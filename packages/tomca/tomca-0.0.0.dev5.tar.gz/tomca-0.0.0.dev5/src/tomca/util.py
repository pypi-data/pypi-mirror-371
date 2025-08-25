"""functions which are general \b utilties for working with jcfg data types"""

import copy
from src import tomca


def verb(dispStr: str, currVerb: float, threshVerb:float):
    """Write output to the command prompt for tracability.

    Call with:
    verb(dispStr, jcfg['Expt']['verb'], threshVerb)

    Args:
        dispStr (_type_): String to put in terminal line
        currVerb (_type_): current verbose level
        threshVerb (_type_): threshold for displaying string
    """
    import numpy as np

    outStr = ""

    if dispStr == "":
        dispStr = "No Warning Written"

    # Add ticks according to level
    if currVerb >= threshVerb:
        for ii in np.arange(0, round(2 * threshVerb)):
            outStr = outStr + "-"
        # Display text
        print(outStr + " " + dispStr, flush=True)


def leaf_finder(rootDict: dict, tmpDict: dict, level, keys, leafs):
    """Function which goes through a dictionary and returns all the leaf entries (non-dicts)
    Call with: leafs= leafFinder(rootDict, rootDict, 0, [], {})

    Args:
        rootDict (dict): main dict
        tmpDict (dict): current branch dict
        level (int): counter to know if its finished
        keys (list): _description_
        leafs (item): _description_

    Returns:
        _type_: _description_
    """

    for ii in tmpDict:
        if isinstance(tmpDict[ii], dict) or ii == "Media":
            keys.append(ii)
            leaf_finder(rootDict, tmpDict[ii], level + 1, keys, leafs)
            keys.pop()
        else:
            tmp = copy.deepcopy(keys)
            tmp.append(ii)
            leafs[len(leafs)] = tmp
    if level == 0:
        return leafs


def leaf_value(rootDict, keys):
    """Returns "array" if the leaf of a dict as specified by list of dict keys is an array"""
    import numpy as np

    value = rootDict
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            try:
                if isinstance(value[key], dict):
                    value = value[key]
            except:
                return value
    if isinstance(value, np.ndarray):  # check if value is a list
        return "array"  # return the string "array"
    else:
        return value



class branch_builder(dict):
    """This lets you specify nested dict entry, even if the middle dicts are not defined, and it will fill them in.
    Implementation of perl's autovivification feature.

    intialize the changes dict with this,
    delta_cfg=branch_builder()
    # Next assign leaves
    delta_cfg["Optode"]["Source"]["spectProfile"]=ii
    # Convert to regular dict
    dict(delta_cfg)

    """

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


def convert_class_to_dicts(nested_dict):
    if isinstance(nested_dict, dict):
        new_dict = {}
        for key, value in nested_dict.items():
            new_dict[key] = convert_class_to_dicts(value)
        return new_dict
    elif isinstance(nested_dict, list):
        new_list = []
        for item in nested_dict:
            new_list.append(convert_class_to_dicts(item))
        return new_list
    else:
        return nested_dict


def update_jcfg(jcfg: dict, update_cfg: dict):
    """
    Updates the 'jcfg' dictionary or list with the values from 'update_cfg'.

    This function recursively traverses the 'update_cfg' dictionary or list and updates the corresponding
    entries in 'jcfg'. If a key in 'update_cfg' doesn't exist in 'jcfg', it will be added. If it does exist,
    its value will be updated. If 'update_cfg' is a list, 'jcfg' is expected to be a list as well, and its
    elements will be updated based on their index.

    Args:
        jcfg (dict or list): The dictionary or list to be updated.
        update_cfg (dict or list): The dictionary or list containing the updates.

    Raises:
        TypeError: If 'jcfg' and 'update_cfg' are not of the same type.
    """
    # if this is a dict,
    if isinstance(update_cfg, dict):
        for ii in update_cfg:
            # See if you're at the leaf keys
            if isinstance(update_cfg[ii], dict):
                try: 
                    update_jcfg(jcfg[int(ii)], update_cfg[ii])
                except:
                    update_jcfg(jcfg[ii], update_cfg[ii])
            else:
                # If you are at the leaf key, overwrite your jcfg leaf with the update leaf.
                jcfg[ii] = update_cfg[ii]
    elif isinstance(update_cfg, list):
        # check each list entry for dicts
        for ii in update_cfg:
            # if there's a dict in the list, it's a media list.  continue into the media list.
            if isinstance(update_cfg, dict):
                update_jcfg(update_cfg[ii], update_cfg[ii])
            # Otherwise, it's a list that should be assigned, so just assign it.
            else:
                jcfg[ii] = update_cfg[ii]
        pass

def filter_dict(d, exclude_keys):
    """Recursively filters out excluded keys from nested dictionaries."""
    filtered = {}
    for k, v in d.items():
        if k not in exclude_keys:
            if isinstance(v, dict):
                filtered[k] = filter_dict(v, exclude_keys)
            elif isinstance(v, list):
                filtered[k] = [filter_dict(item, exclude_keys) if isinstance(item, dict) else item for item in v]
            else:
                filtered[k] = v
    return filtered

def prepare_state(jcfg, delta_cfg):
    """
    Prepares the jcfg for the new state evaluation, including a string representation of the current state based on changes to the model file.

    This function handles the maximum number of photons setting for mcx, and sets some replay flags for the first simulation. It then updates the 'stateName' key in the 'Expt' dictionary of `jcfg` with a string that reflects the changes
    made to the model file as specified in `delta_cfg`. It uses the `leaf_finder` utility to identify the leaf nodes
    in `delta_cfg` and appends their values from `jcfg` to the state string.

    Args:
        jcfg (dict): The input configuration dictionary containing the current state information.
        delta_cfg (dict): The configuration dictionary containing the changes to the model file.

    Returns:
        dict: The modified input configuration dictionary with the updated state name.
    """
    from .make import dir_state
    import json

    # Prepare state for nPhotons
    jcfg['Session']['maxdetphoton'] = jcfg['Session']['Photons']

    # Initialize fig save dict
    jcfg['fig']={}

    # Initialize jcfg for replay simulations
    if jcfg['Expt']['doReplay']:
        jcfg['Session']['DoSaveSeed']=1
        jcfg['Session']['DoPartialPath']=1

    # Update statename with changes to model file from delta_cfg
    leafs= leaf_finder(delta_cfg, delta_cfg, 0, [], {})
    if 'stateName' not in jcfg['Expt']:
        stateOut=""
        # for ii in leafs:
        #     stateOut+=" "+str(leafs[ii][-1])+"_"+str(tomca.util.leaf_value(jcfg, leafs[ii]))
        jcfg['Expt']['stateName']=stateOut
    jcfg['Expt']['DeltaCfg'] = delta_cfg
    #tomca.util.verb('Prepared state:'+stateOut, jcfg['Expt']['verb'], 0)

    jcfg = tomca.make.dir_state(jcfg)
    
    #any non-json serializable delta cfgs should be added to this list in the filtered dict.
    delta_cfg_tmp = filter_dict(copy.deepcopy(delta_cfg),['Pattern'])

    json_str = json.dumps(delta_cfg_tmp, sort_keys=True)
    tomca.util.verb('Prepared state: '+json_str, jcfg['Expt']['verb'], 0)

    return jcfg

def pickle_out(jcfg: dict, filePath=None):
    """Write out a pickle file in binary to save the jcfg variable.
    "" Depends on an archive size variable in jcfg expt.

    Args:
        jcfg (dict): simulation state, at any stage.  Volume gets excluded.
    """
    import pickle
    from src import tomca
    
    # check if filePath exists, if not, create it folder by folder:
    if filePath is not None:
        if not os.path.exists(os.path.dirname(filePath)):
            os.makedirs(os.path.dirname(filePath))
    

    if filePath is None:
        if "Expt" in jcfg:
            filePath = (
                jcfg["Expt"]["pathState"]
                + "\\"
                + jcfg["Expt"]["time"]
                + jcfg["Expt"]["stateName"]
                + "_simulated_jcfg.pkl"
            )

        if "archiveSize" in jcfg['Expt']:
            if jcfg['Expt']['archiveSize'] == 'min':
                del jcfg['res']['p'], jcfg['res']['x'], jcfg['res']['v'], jcfg['res']['detp'], jcfg['res']['seeds'], jcfg['res']['flux'], jcfg['mcfg']['vol']

    else:
        pass


    # ChatGPT aided
    # Open a file and use dump()
    with open(filePath, "wb") as file:
        # A new file will be created
        pickle.dump(jcfg, file)

        verb("Wrote to pickle file at: " + filePath, 1, 2)

    return


def pickle_in(filePath: str):
    """Read from a pickle file in binary

    Args:
        filePath (str): Full path to pickle file

    Returns:
        jcfg: Anything in pickle file...
    """
    import pickle
    from src import tomca

    verb("Opening  pickle file at: " + filePath, 1, 2)

    with open(filePath, "rb") as file:
        jcfg = pickle.load(file)

    if "Expt" in jcfg:
        verb(f'Loaded pickle file: {os.path.join(*filePath.split(os.sep)[-3:])}', jcfg["Expt"]["verb"], 1)
    else:
        verb(f'Loaded pickle file: {os.path.join(*filePath.split(os.sep)[-3:])}', 1, 1)

    return jcfg


def find_pkl_files(folder_path):
    import os

    pkl_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".pkl"):
                pkl_files.append(os.path.join(root, file))
    return pkl_files


def custom_deepcopy(obj, _memo=None):
    """This deep copies figures as well as other types.  Needed for keeping figures accessible through jcfg"""
    import copy
    import matplotlib.pyplot as plt

    if _memo is None:
        _memo = {}

    obj_id = id(obj)
    if obj_id in _memo:
        return _memo[obj_id]

    if isinstance(obj, dict):
        copy_obj = {}
        _memo[obj_id] = copy_obj
        for key, value in obj.items():
            copy_obj[custom_deepcopy(key, _memo)] = custom_deepcopy(value, _memo)

    elif isinstance(obj, list):
        copy_obj = []
        _memo[obj_id] = copy_obj
        for item in obj:
            copy_obj.append(custom_deepcopy(item, _memo))

    elif isinstance(obj, plt.Figure):
        # If it's a matplotlib figure, use the figure's copy method
        copy_obj = obj.copy()

    else:
        # For other types, use the standard deepcopy
        copy_obj = copy.deepcopy(obj, _memo)

    return copy_obj


import os
import glob
import re
from collections import defaultdict

def collect_simulation_data(directory_path):
    data_dict = {
        "pklPaths": [],
        "varCombinations": defaultdict(lambda: defaultdict(list))
    }

    # Define a regular expression pattern to extract variable name and value pairs
    pattern = r' (\w+)_(\S+)'

    # Loop through subdirectories
    for subfolder in os.listdir(directory_path):
        subfolder_path = os.path.join(directory_path, subfolder)

        # Check if the subfolder is a directory
        if os.path.isdir(subfolder_path):
            # Extract the variable name and value pairs from the folder name
            var_vals = re.findall(pattern, subfolder)

            # Search for .pkl files in the subdirectory
            pkl_files = glob.glob(os.path.join(subfolder_path, '*.pkl'))

            # If .pkl files are found, add their paths to the list
            if pkl_files:
                data_dict["pklPaths"].extend(pkl_files)

            # If there are variable name and value pairs, organize the data
            if var_vals:
                var_combination = {}
                for var_name, var_val in var_vals:
                    var_combination[var_name] = var_val
                for var_name, var_val in var_combination.items():
                    data_dict["varCombinations"][var_name][var_val].extend(pkl_files)

    return data_dict["varCombinations"]

def find_dict_differences(default_data:dict, non_default_data:dict):

    # Helper function to recursively find differences
    def find_differences(d1, d2, path=''):
        differences = []
        for key in d1:
            new_path = f"{path}.{key}" if path else key

            if key not in d2:
                differences.append((new_path, d1[key]))
            elif isinstance(d1[key], dict) and isinstance(d2[key], dict):
                differences.extend(find_differences(d1[key], d2[key], new_path))
            elif isinstance(d1[key], list) and isinstance(d2[key], list):
                for i, (item1, item2) in enumerate(zip(d1[key], d2[key])):
                    if isinstance(item1, dict) and isinstance(item2, dict):
                        differences.extend(find_differences(item1, item2, f"{new_path}[{i}]"))
                    elif item1 != item2:
                        differences.append((f"{new_path}[{i}]", item1))
            elif d1[key] != d2[key]:
                differences.append((new_path, d1[key], d2[key]))

        return differences

    # Find and return the differences
    differences = find_differences(default_data, non_default_data)
    return differences



def read_tiff_image(path_to_tiff):
    import tifffile as tiff
    import numpy as np

    try:
        with tiff.TiffFile(path_to_tiff) as tif:
            tiff_data = tif.asarray()
            return tiff_data
    except Exception as e:
        print(f"Error reading TIFF image: {e}")
        return None

def rebuild_state(jcfg, saveDir=None):
    import matplotlib.pyplot as plt

    # If saveDir is not specified, use the pathState from jcfg in the originally generated data save location.
    if saveDir is not None:
        jcfg['Expt']['pathState'] = str(saveDir)

    import src.tomca
    # Generate volume from jcfg parameters
    if 'vol' not in jcfg:
        jcfg = tomca.buil.vol_init(jcfg)
        jcfg = tomca.buil.vol_layers(jcfg)
        jcfg = tomca.buil.vol_vessel(jcfg)
        jcfg = tomca.conv.vol_svmc(jcfg)

    # Prepare simulation optics
    jcfg = tomca.buil.source(jcfg)
    jcfg = tomca.buil.detectors(jcfg)

    # Import Source Spectrum
    jcfg = tomca.buil.incident_spectrum(jcfg)

    # Evaluate optical properties
    jcfg = tomca.calc.mu_abs_scatt(jcfg)

    # Generate plots
    jcfg = tomca.grap.state_xsections(jcfg)

    # Evaluate imaginary image detectors, if any
    jcfg=tomca.calc.img_detectors(jcfg)

    # Save output files
    jcfg=tomca.writ.state_outputs(jcfg)

    tomca.util.verb('Finished state. '+ 'Save directory: ' + jcfg['Expt']['pathState'], jcfg['Expt']['verb'], 0)
    #tomca.util.verb(' ', jcfg['Expt']['verb'], 0)

    plt.close('all')
    
def hash_dict(jcfg):
    """
    Generate a SHA-256 hash for a given dictionary.
    This function takes a dictionary, converts it to a JSON string with sorted keys,
    and then generates a SHA-256 hash of that JSON string.
    @param jcfg: The dictionary to be hashed.
    @type jcfg: dict
    @return: The SHA-256 hash of the dictionary as a hexadecimal string.
    @rtype: str
    """
    import hashlib
    import json

    # Convert the nested dict to a JSON string
    json_str = json.dumps(jcfg, sort_keys=True)

    # Create a hash object
    hash_obj = hashlib.sha256()

    # Update the hash object with the JSON string
    hash_obj.update(json_str.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hash_str = hash_obj.hexdigest()

    return hash_str

def hash_vol(jcfg, key='vol'):
    import hashlib
    import json
    import copy

    # Convert the vol to a bytes
    array=copy.deepcopy(jcfg[key])
    array_bytes = array.tobytes()

    # Create a hash object
    hash_obj = hashlib.sha256(array_bytes)

    # Get the hexadecimal representation of the hash
    hash_str = hash_obj.hexdigest()

    return hash_str

def dict_keys_sizes(jcfg):
    """
    @brief Computes and prints the sizes of all keys in a nested dictionary.
    
    This function takes a nested dictionary as input and computes the memory size of each key-value pair.
    It prints the size of each key in bytes. If a value is a dictionary, it recursively computes the sizes
    of the nested keys.
    
    @param jcfg The input nested dictionary whose keys' sizes are to be computed.
    @return None
    """
    from pympler import asizeof
    
    def get_dict_size(d, parent_key=''):
        sizes = {}
        for k, v in d.items():
            key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                sizes.update(get_dict_size(v, key))
            else:
                try:
                    sizes[key] = asizeof.asizeof(v)
                except Exception as e:
                    print(f"Error sizing {key}: {e}")
        return sizes

    sizes = get_dict_size(jcfg)
    for key, size in sizes.items():
        print(f"{key}: {size} bytes")
        
    
def compare_mcfg(mcfg1, mcfg2, verb=1):
    """!
    @brief Compare two configuration dictionaries (mcfg1 and mcfg2) and identify differences.
    @param mcfg1 The first configuration dictionary to compare.
    @param mcfg2 The second configuration dictionary to compare.
    @param verb Verbosity level for logging. Defaults to 1.
    @return A tuple containing:
        - differences: A dictionary of differences where keys are the differing keys and
        - err: Error code, 1 if important differences are found, 0 otherwise.
        
    Compare two configuration dictionaries (mcfg1 and mcfg2) and identify differences.
    This function compares the key-value pairs of two dictionaries. If the values are numpy arrays,
    it checks for array equality. It categorizes differences into important and unimportant based
    on a predefined list of unimportant keys. It logs the differences found and returns them along
    with an error code.
    Args:
        mcfg1 (dict): The first configuration dictionary to compare.
        mcfg2 (dict): The second configuration dictionary to compare.
        verb (int, optional): Verbosity level for logging. Defaults to 1.
    Returns:
        tuple: A tuple containing:
            - differences (dict): A dictionary of differences where keys are the differing keys and
              values are tuples of (value in mcfg1, value in mcfg2).
            - err (int): Error code, 1 if important differences are found, 0 otherwise.
    """
    import numpy as np
    differences = {}  # Initialize a dictionary to store differences
    for key in mcfg1:
        if key in mcfg2:
            if isinstance(mcfg1[key], np.ndarray) and isinstance(mcfg2[key], np.ndarray):
                # Check if both values are numpy arrays and if they are not equal
                if not np.array_equal(mcfg1[key], mcfg2[key]):
                    differences[key] = (mcfg1[key], mcfg2[key])
            else:
                # Check if values are not equal
                if mcfg1[key] != mcfg2[key]:
                    differences[key] = (mcfg1[key], mcfg2[key])
        else:
            # Key is in mcfg1 but not in mcfg2
            differences[key] = (mcfg1[key], None)
    for key in mcfg2:
        if key not in mcfg1:
            # Key is in mcfg2 but not in mcfg1
            differences[key] = (None, mcfg2[key])
    
    # List of keys considered unimportant
    unimportant_keys = ['srctype', 'srcpos', 'srcdir', 'srcparam1', 'srcparam2']
    # Filter out unimportant differences
    unimportant_differences = {key: differences[key] for key in unimportant_keys if key in differences}
    for key in unimportant_keys:
        if key in differences:
            del differences[key]
    
    err = 1  # Initialize error code
    if differences:
        # Log important differences
        tomca.util.verb('Compared mcfgs, important differences found for combining simulations : ' + str(differences), verb, 0)
    elif unimportant_differences:
        # Log unimportant differences
        tomca.util.verb('Compared mcfgs, unimportant differences found for combining simulations: ' + str(unimportant_differences), verb, 1)
        err = 0  # No error for unimportant differences
    else:
        # Log no differences found
        tomca.util.verb('Compared mcfgs, no differences found', verb, 1)
        err = 0  # No error if no differences found
        
    return differences, err  # Return differences and error code

