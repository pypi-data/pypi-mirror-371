from pydantic import BaseModel
from typing import Callable, Union, Literal, Optional
from copy import deepcopy
from itertools import product
import time
from pathlib import Path
import os
import pickle
import json

import numpy as np
import pandas as pd
from scipy.stats.qmc import LatinHypercube
from tqdm import tqdm


CATEGORIES = ['optimization', 'tissue', 'hardware', 'simulation']
DONUT_WIDTHS = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
DETECTOR_PARAMS = ["pitch", "d_size"]
OUTPUT_PARAMS = ["time", "detected_photons"]
DEFAULT_DATA_PATH = r"/mnt/data/monte_carlo_tmp/"


def merge_data(df: Optional[pd.DataFrame] = None, path: Path | str = DEFAULT_DATA_PATH):
    """
    Load df if no dataframe is given. Saves df if no saved df exists yet. Merges df if both df is given a df exists.
    """
    path = Path(path)
    print(path)
    if path.exists():
        df_1 = pd.read_pickle(path)
        if df is None:
            df = df_1
        else:
            df = pd.concat([df, df_1], ignore_index=True)
    if df is not None:
        df.to_pickle(path)
    if df is not None:
        return df
    else:
        raise ValueError(f"Cannot save, load or merge, no dataframe provided and no dataframe stored at {path}!")


class ParameterConfig(BaseModel):
    min: float
    max: float
    res: float
    loc: tuple[Union[str, int], ...] = tuple()
    axis: Optional[str] = None


class SpaceConfig(BaseModel):
    optimization: ParameterConfig
    tissue: list[ParameterConfig] = []
    hardware: list[ParameterConfig] = []
    simulation: list[ParameterConfig] = []


class DeltaConfig(dict):
    """
    A container class used to store changes to default options of a config file.

    This class extends the functionalities of a dictionary and provides the following features:
    - Creates keys if they do noft exist
    - Supports setting items with tuples
    - Supports nested dictionaries of arbitrary depth (does not support lists)

    Usage:
    - To access an item, use the standard dictionary syntax: delta_config[key]

    Example:
    - delta_config = DeltaConfig()
    - delta_config['Session']['Photons'] = 1000
    - delta_config[('Domain', 'LengthUnit')] = '0.020'
    - print(delta_config[('Domain', 'LengthUnit')])
        
        '0.020'

    Note: This class is designed to be used in conjunction with the Interface class
    """

    def __getitem__(self, item):
        """
        Retrieves the value associated with the given item.

        If the item does not exist, it creates a new instance of DeltaConfig and returns it.

        Args:
        - item: The key to retrieve the value for.

        Returns:
        - The value associated with the given item.
        """

        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

    def __setitem__(self, key, value):
        """
        Sets the value associated with the given key.

        If the key is a tuple, it traverses the nested dictionaries and sets the value at the specified key.

        Args:
        - key: The key to set the value for.
        - value: The value to set.

        Returns:
        - None

        Example:
        delta_config = DeltaConfig()
        delta_config['Session']['Photons'] = 1000
        delta_config[('Domain', 'LengthUnit')] = '0.020'
        """
        target = self
        if isinstance(key, tuple):
            for k in key[:-1]:
                target = target[k]
            if isinstance(value, int):
                target[key[-1]] = int(value)
            else:
                target[key[-1]] = value
        else:
            if isinstance(value, int):
                super(DeltaConfig, self).__setitem__(key, int(value))
            else:
                super(DeltaConfig, self).__setitem__(key, value)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


class Interface:
    def __init__(self, config: dict, space_config: SpaceConfig,
                 simulate: Callable[[dict, DeltaConfig], dict], seed: float = None) -> None:
        """
        Initializes an instance of the Interface class.create_delta_configs

        Parameters:
        - config: A dictionary containing the configuration settings.
        - space_config: An instance of the SpaceConfig class that defines the parameter space.
        - simulate: A callable function that performs the simulation.
        - seed: An optional seed value for the random number generator.

        Returns:
        None
        """
        self.config = config
        self.space_config = space_config
        self.simulate = simulate
        self.rng = np.random.default_rng(seed=seed)

        # Create lookup table
        self.lookup = dict()
        for category in CATEGORIES:
            items = deepcopy(getattr(self.space_config, category))
            if not isinstance(items, list):
                items = [items]
            for item in items:
                item.axis = category
                self.lookup[tuple(item.loc)] = item

    def __call__(self, delta_configs: list[DeltaConfig], flattened_configs: list[dict],
                 name= "no_name", output_level: int = 0, offloader_cfg = 0, offloader_debug=0, save_csv=0):
        """
        Runs n simulations given n delta configs in a list of DeltaConfig class items. Returns data in a structured dataframe format.

        Parameters:
        - delta_configs: A list of DeltaConfig instances representing the configurations for each simulation.
        - flattened_configs: A list of dictionaries representing the flattened configurations.
        - name: A string representing the name of the simulation.
        - output_level: An integer representing the level of output verbosity.

        Returns:
        A pandas DataFrame containing the simulation results.

        Usage Example:
        ```
        delta_configs = [...]  # List of DeltaConfig instances
        flattened_configs = [...]  # List of dictionaries representing flattened configurations

        simulator = Simulator()
        result_df = simulator(delta_configs, flattened_configs, name="Simulation 1", output_level=2)
        print(result_df)
        ```
        """
        # Run the simulation for each delta config

        if offloader_cfg == 0:
            results = self.run_simulation(delta_configs, name=name, output_level=output_level)
            
        else:
            # if offloader_debug is 1, skip the simulation and load a previous simulation
            savePath=os.path.join(self.config['Expt']['dirResults'], "last_offload.pickle")
            if offloader_debug == 0:
                
                results, flattened_configs = self.run_simulation(delta_configs, name=name, output_level=output_level, offloader_cfg=offloader_cfg)
                # write out the workspace to a pickle file
                with open(savePath, 'wb') as f:
                    pickle.dump([results, flattened_configs, self], f)
                    
            else:
                # Read last offload results
                with open(savePath, 'rb') as f:
                    [results, flattened_configs, self]=pickle.load(f)
                    print('read old df')
                
            
                            
        # Initialize a dictionary to store the processed results
        processed_results = {
            DETECTOR_PARAMS[0]: [],
            DETECTOR_PARAMS[1]: [],
            OUTPUT_PARAMS[0]: [],
            OUTPUT_PARAMS[1]: []
        }

        # Create a DataFrame from the flattened configs
        df = pd.DataFrame(flattened_configs)
        
        repeats = []

        # Process the results for each flattened config
        for flattened_config, result in zip(flattened_configs, results):
            length_unit = flattened_config[('Domain', 'LengthUnit')]
            repeat = 0
            for i, donut_width in zip(range(len(result[OUTPUT_PARAMS[1]])), DONUT_WIDTHS):
                for j in range(len(result["detected_photons"][i])):
                    processed_results[DETECTOR_PARAMS[0]].append(j * length_unit + donut_width / 2)
                    processed_results[DETECTOR_PARAMS[1]].append(donut_width)
                    processed_results[OUTPUT_PARAMS[1]].append(result[OUTPUT_PARAMS[1]][i][j])
                    processed_results[OUTPUT_PARAMS[0]].append(result[OUTPUT_PARAMS[0]])
                    repeat += 1
            repeats.append(repeat)

        # Repeat the rows in the DataFrame based on the number of repeats
        df = df.loc[df.index.repeat(repeats)].reset_index(drop=True)
        
        # Add the processed results to the DataFrame
        df[DETECTOR_PARAMS[0]] = processed_results[DETECTOR_PARAMS[0]]
        df[DETECTOR_PARAMS[1]] = processed_results[DETECTOR_PARAMS[1]]
        df[OUTPUT_PARAMS[1]] = processed_results[OUTPUT_PARAMS[1]]
        df[OUTPUT_PARAMS[0]] = processed_results[OUTPUT_PARAMS[0]]

        if save_csv:
            # write the dataframe to a csv file located at self.config['Expt']['pathExpt']
            file_path = os.path.join(self.config['Expt']['pathExpt'], self.config['Expt']['time'] + '_' +  name + '_df.csv')
            df.to_csv(file_path)

        savePath=os.path.join(self.config['Expt']['pathExpt'], "df.pickle")
        merge_data(df, path = savePath)

        return df, self.config

    def run_simulation(self, delta_configs: list[DeltaConfig], name = "no_name", offloader_cfg = 0,  output_level: int = 0) -> list:
        """
        Runs the simulation for each delta config and returns the results.

        Parameters:
        - delta_configs: A list of DeltaConfig instances representing the configurations for each simulation.
        - name: A string representing the name of the simulation.
        - output_level: An integer representing the level of output verbosity.

        Returns:
        A list of dictionaries representing the simulation results.
        """
        from Software import tmcx
        self.config['Expt']['verb'] = output_level
        if name == 'repeatKey_noNewExptFolder':
             pass
        else:
            self.config['Expt']['exptName'] = name
            self.config['Expt']['pathExpt']=tmcx.make.dir_expt(self.config)['Expt']['pathExpt']

        results = []
        
        if offloader_cfg == 0:
            for delta_config in tqdm(delta_configs):
                print(delta_config)
                sim_result = self.simulate(deepcopy(self.config), delta_config)
                result = {
                    "n_photons": delta_config["Session"]["Photons"],
                    OUTPUT_PARAMS[1]: sim_result["res"]["imgDetectors"]["Avg"],
                    OUTPUT_PARAMS[0]: sim_result['Expt']['tf'] - sim_result['Expt']['t0']
                }
                results.append(result)
                
            return results

        else:
            flattened_configs=[]
            offload_results=tmcx.offl.simulate(self.config, delta_configs, offloader_cfg=offloader_cfg)
            for offload_result in offload_results:
                result = {
                    "n_photons": offload_result["Session"]["Photons"],
                    OUTPUT_PARAMS[1]: offload_result["res"]["imgDetectors"]["Avg"],
                    OUTPUT_PARAMS[0]: offload_result['Expt']['tf'] - offload_result['Expt']['t0']
                }
                delta_config=DeltaConfig()
                delta_config=offload_result['Expt']['DeltaCfg']
                flattened_configs.append(self.create_flattened_configs([delta_config])[0])
                results.append(result)
                
            return results, flattened_configs
        

    def list_locs(self, category: str = None):
        """
        Returns a list of locations for a given category.

        Parameters:
        - category: A string representing the category.

        Returns:
        A list of tuples representing the locations.
        """
        cats = CATEGORIES if category is None else [category]

        return [loc for loc in self.lookup.keys() if self.lookup[loc].axis in cats]

    def __getitem__(self, item: tuple[str, ...]):
        """
        Returns the parameter configuration for a given item.

        Parameters:
        - item: A tuple representing the item.

        Returns:
        The ParameterConfig instance for the given item.

        Usage Example:
        >>> interface = Interface()
        >>> config = interface[('Domain', 'LengthUnit')]
        >>> print(config.min)
        0.001
        """
        return self.lookup[item]

    def get_default_value(self, loc, config=None):
        """
        Retrieves the default value for a specific location.

        Parameters:
        - loc: A tuple representing the location.
        - config: A dictionary representing the configuration settings.

        Returns:
        The default value for the specified location.
        """
        config = config if config is not None else self.config
        if isinstance(config, dict) or isinstance(config, list):
            return self.get_default_value(loc[1:], config[loc[0]])
        else:
            return config

    def get_values(self, item: tuple[str, ...], n: int, method: Literal["equidistant", "uniform"] = "equidistant"):
        """
        Return n values given item properties using a method.

        Parameters:
        - item: A tuple representing the item.
        - n: An integer representing the number of values to generate.
        - method: A string representing the method to use for generating the values.

        Returns:
        A dictionary containing the generated values.
        """
        if n <= 0:
            raise ValueError(f"Please use a positive value for {n}!")
        if method == "equidistant":
            a = self[item].min
            b = self[item].max
            if n == 1:
                return [(b - a) / 2]
            else:
                return {item: list(np.linspace(a, b, n))}
        if method == "uniform":
            a = self[item].min
            b = self[item].max
            return {item: list(self.rng.random(n)*(b - a) + a)}

    def get_value(self, item: tuple[str, ...], x: float | np.ndarray):
        """
        Returns the value for a given item and input value.

        Parameters:
        - item: A tuple representing the item.
        - x: A float or numpy array representing the input value(s).

        Returns:
        The calculated value(s) based on the input value(s).
        """
        a = self[item].min
        b = self[item].max
        return a + (b - a) * x

    def divide_space(self, n: int, locs: list[tuple[str, ...]] = None,
                     method: Literal["equidistant", "uniform", "latin_hypercube"] = "latin_hypercube"):
        """
        Divides a specific dimension into n experiments.

        Parameters:
        - n: An integer representing the number of experiments.
        - locs: A list of tuples representing the locations to divide.
        - method: A string representing the method to use for dividing the space.

        Returns:
        An ordered dictionary containing the divided space.
        """
        space = dict()
        if locs is None:
            locs = self.list_locs()
        if method == "equidistant" or method == "uniform":
            for loc in locs:
                space = self.prod(space, self.get_values(loc, n, method))
        elif method == "latin_hypercube":
            m = len(locs)
            sampler = LatinHypercube(m, seed=self.rng)
            samples = sampler.random(n=n).T
            for sample, loc in zip(samples, locs):
                space[loc] = list(self.get_value(loc, sample))
        else:
            raise ValueError(f"Unknown specified method {method}!")
        return space

    def create_delta_configs(self, *spaces):
        """
        Creates delta configs for all combinations of all spaces.

        Parameters:
        - spaces: Variable number of dictionaries representing the parameter spaces.

        Returns:
        A tuple containing the delta configs and flattened configs.
        """
        # Initialize an empty dictionary to store the parameter space
        space = dict()
        
        # Iterate over each parameter space dictionary
        for space_b in spaces:
            # Generate all combinations of the current parameter space with the existing parameter space
            space = self.prod(space, space_b)

        # Initialize empty lists to store the delta configs and flattened configs
        delta_configs = []
        flattened_configs = []
        
        # Determine the number of combinations in the parameter space
        m = len(list(space.values())[0]) if space else 1

        # Generate delta configs and flattened configs for each combination in the parameter space
        for i in tqdm(range(m)):
            # Initialize a new DeltaConfig instance
            delta_config = DeltaConfig()
            flattened_config = dict()

            for loc in self.list_locs():
                # Check if the location exists in the current combination of the parameter space
                if loc in space:
                    # Set the value of the location in the delta config and flattened config
                    delta_config[loc] = space[loc][i]
                    flattened_config[loc] = space[loc][i]
                else:
                    # Set the default value for the location in the flattened config
                    flattened_config[loc] = self.get_default_value(loc)
            
            # Append the delta config and flattened config to their respective lists
            delta_configs.append(delta_config)
            flattened_configs.append(flattened_config)


        # Return the delta configs and flattened configs as a tuple
        return delta_configs, flattened_configs
    
    def create_delta_configs_lists(self, *spaces):
        """
        Creates delta configs for all combinations of all spaces.

        Parameters:
        - spaces: Variable number of dictionaries representing the parameter spaces.

        Returns:
        A tuple containing the delta configs and flattened configs.
        """
        # Initialize an empty dictionary to store the parameter space
        space = dict()
        
        # Iterate over each parameter space dictionary
        for space_b in spaces:
            # Generate all combinations of the current parameter space with the existing parameter space
            space = self.prod(space, space_b)

        # Initialize empty lists to store the delta configs and flattened configs
        delta_configs = []
        flattened_configs = []
        
        # Determine the number of combinations in the parameter space
        m = len(list(space.values())[0]) if space else 1

        # Generate delta configs and flattened configs for each combination in the parameter space
        for i in range(m):
            # Initialize a new DeltaConfig instance
            delta_config = self.config.copy()
            flattened_config = dict()

            for loc in self.list_locs():
                # Check if the location exists in the current combination of the parameter space
                if loc in space:
                    # Set the value of the location in the delta config and flattened config
                    value = space[loc][i]
                    self.update_jcfg(delta_config[loc], value)
                    self.update_jcfg(flattened_config[loc], value)
                else:
                    # Set the default value for the location in the flattened config
                    flattened_config[loc] = self.get_default_value(loc)
            
            # Append the delta config and flattened config to their respective lists
            delta_configs.append(delta_config)
            flattened_configs.append(flattened_config)

        # Return the delta configs and flattened configs as a tuple
        return delta_configs, flattened_configs

    def update_jcfg(self, jcfg: dict, update_cfg: dict):
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
                    self.update_jcfg(jcfg[ii], update_cfg[ii])
                else:
                    # If you are at the leaf key, overwrite your jcfg leaf with the update leaf.
                    jcfg[ii] = update_cfg[ii]
        elif isinstance(update_cfg, list):
            # check each list entry for dicts
            for ii in update_cfg:
                # if there's a dict in the list, it's a media list.  continue into the media list.
                if isinstance(update_cfg, dict):
                    self.update_jcfg(update_cfg[ii], update_cfg[ii])
                # Otherwise, it's a list that should be assigned, so just assign it.
                else:
                    jcfg[ii] = update_cfg[ii]
            pass
    
    def create_flattened_configs(self, delta_configs: list[DeltaConfig]) -> list[dict]:
        """
        Creates flattened configs for a given list of delta configs.

        Parameters:
        - delta_configs: A list of DeltaConfig instances representing the configurations for each simulation.

        Returns:
        A list of dictionaries representing the flattened configurations.  These are used as the individual row "keys" in the df.
        """
        from Software import tmcx  

        delta_flattened = []
        flattened_configs = []
        
        # Iterate over each delta config
        for delta_config in delta_configs:
            
            tmp=tmcx.util.leaf_finder(delta_config, delta_config, 0,[], {})
            flat=[]
            for loc in tmp:
                flat.append(tuple(tmp[loc]))
            # Append the flattened config to the list
            delta_flattened.append(flat)
    
        
            # Initialize an empty dictionary to store the flattened config
            flattened_config = dict()
            
            # Iterate over each location in the parameter space
            for config_loc in self.list_locs():
                # Check if the location exists in the current combination of the parameter space
                if config_loc in delta_flattened[-1]:
                    # Set the value of the config_location in the delta config and flattened config
                    flattened_config[config_loc] = tmcx.util.leaf_value(delta_config,config_loc)
                else:
                    # Set the default value for the config_location in the flattened config
                    flattened_config[config_loc] = self.get_default_value(config_loc)
        
            flattened_configs.append(flattened_config)
            
        return flattened_configs

    @staticmethod
    def prod(a: dict[tuple[str, ...], list[float]], b: dict[tuple[str, ...], list[float]]):
        """
        Returns all combinations of settings a with settings b.

        Parameters:
        - a: A dictionary representing the first set of settings.
        - b: A dictionary representing the second set of settings.

        Returns:
        A dictionary containing all combinations of settings a with settings b.
        """
        if len(a) == 0:
            return b
        if len(b) == 0:
            return a

        n = len(list(a.values())[0])
        m = len(list(b.values())[0])
        c = dict()

        combinations = np.array([x for x in product(range(n), range(m))]).T
        for k, v in a.items():
            c[k] = list(np.array(v)[combinations[0]])
        for k, v in b.items():
            c[k] = list(np.array(v)[combinations[1]])

        return c
