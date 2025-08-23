import logging
from pathlib import Path

from tqdm import tqdm
import numpy as np
import lightgbm as lgb
import pandas as pd
from scipy.interpolate import CloughTocher2DInterpolator
# Optimization related imports
import torch
from torch import Tensor
from botorch.models import SingleTaskGP
from botorch.fit import fit_gpytorch_mll
from botorch.acquisition import UpperConfidenceBound
from botorch.optim import optimize_acqf
from gpytorch.mlls import ExactMarginalLogLikelihood
from gpytorch.constraints import GreaterThan

from Software.tmcx.AIML.interface import DETECTOR_PARAMS, Interface, merge_data


LOGGER = logging.getLogger(__name__)


def regression(x, y, k=5, seed=None, num_leaves=21, num_round=30):
    """
    Expects features x to be NxM where M is number if features, and y to be a vector of N labels.
    it does k-fold cross validation. x has NoRelations columns and No Simulations with that configuration rows. Y is the biomarker value for each simulation.
    """
    n = len(x)
    if n < k:
        raise ValueError(f"Number of features n cannot be smaller than k, n={n}, k={k}")

    rng = np.random.default_rng(seed=seed)
    permutation = np.array([i for i in range(n)]) # Create a list of indexes
    rng.shuffle(permutation) # Shuffle the indexes

    validation_sets = np.array_split(permutation, k) # Split the indexes into k parts for k-fold cross validation
    costs = []

    train_data_param = {"min_data_in_bin": 1} 
    param = {'num_leaves': num_leaves, 'objective': 'regression', 'metric': ['rmse', 'l1'], 'verbose': -1,
             'min_data_in_leaf': 1, "min_data_in_bin": 1, 'tree_learner': "feature"} 
    for validation_set in validation_sets: # for current set of indexes
        train_set = list(set(permutation) - set(validation_set)) # Get the training indexes by removing the validation set indexes

        train_data = lgb.Dataset(data=x[train_set], label=y[train_set], params=train_data_param) # Extract the training data
        validation_data = lgb.Dataset(x[validation_set], label=y[validation_set])                # Extract the validation data

        bst = lgb.train(param, train_data, num_round, valid_sets=[validation_data], 
                        callbacks=[lgb.early_stopping(stopping_rounds=3, verbose=False),]) # Train the model to use the training data to predict the validation data and return the rmse and l1 metrics for the validation data performance.
        costs.append(bst.best_score['valid_0']["rmse"]) 
    return np.mean(costs), np.std(costs)


class Framework:
    """
    The Framework class represents a framework for optimization in retinal imaging.
    
    Usage:
    1. Initialize the Framework object with an Interface object:
        framework = Framework(interface)
        
    2. Set the hardware configuration using the set_hardware_config() method:
        framework.set_hardware_config(relations=((0, 0), (1, 1)))
        
    3. Get the simulation settings using the get_simulation_settings() method:
        framework.get_simulation_settings(n=5)
        
    4. Perform an initial low resolution sweep using the initial_sweep() method:
        df = framework.initial_sweep(biomarker=10, tissue=10, wavelength=10, voxel_size=0.05, photons=10**7)
        
    5. Add hardware table data using the add_hardware_table_data() method:
        framework.add_hardware_table_data(df)
        
    6. Calculate hardware costs using the calculate_hardware_costs() method:
        framework.calculate_hardware_costs(num_round=50)
    """
    
    def __init__(self, interface: Interface):
        self.interface = interface

        # Set parameters inherited from framework
        self.source_params = self.interface.list_locs("hardware")
        self.biomarker = self.interface.list_locs("optimization")[0]
        self.tissue_params = self.interface.list_locs("tissue")
        self.simulation_params = self.interface.list_locs("simulation")
        self.detector_params = DETECTOR_PARAMS
        LOGGER.info(f"Target to optimize for is {self.biomarker}.")

        # Parameters to be set
        self.df = None
        self.simulation_time = None
        self.simulation_error = None

        # parameters to be set related to hardware configuration
        self.source_ids = None
        self.detector_ids = None
        self.relations = None
        self.hardware_design_source = None
        self.hardware_design = None

    def __call__(self):
        pass

    def set_hardware_config(self, relations=((0, 0), (1, 1))):
        """
        Calling this will reset any previous set hardware configuration.
        """
        self.source_ids = np.unique(np.array(relations)[:, 0])
        self.detector_ids = np.unique(np.array(relations)[:, 1])
        self.relations = relations

        # Create hardware design tables
        source_column_structure = [(a, b) for i in self.source_ids for a, b in
                                   zip([f"source_{i}"] * len(self.source_params), self.source_params)]
        self.hardware_design_source = pd.DataFrame(columns=pd.MultiIndex.from_tuples(source_column_structure))
        detector_column_structure = []
        for d_id in self.detector_ids:
            # For each relation a different pitch
            for rel in self.relations:
                if rel[1] == d_id:
                    detector_column_structure.append((f"detector_{d_id}", f"{self.detector_params[0]}_{rel[0]}"))
            # For each detector a size
            detector_column_structure.append((f"detector_{d_id}", self.detector_params[1]))
        df_detectors = pd.DataFrame(columns=pd.MultiIndex.from_tuples(detector_column_structure))
        self.hardware_design = self.hardware_design_source.merge(df_detectors, how='cross').reset_index(drop=True)
        self.hardware_design_source[["cost", "std"]] = None
        self.hardware_design[["cost", "std"]] = None

        LOGGER.info(f"Hardware configuration initialized with sources {self.source_ids} and detectors "
                    f"{self.detector_ids} having {len(self.relations)} relations.")

    def get_simulation_settings(self, n=5, offloader_cfg = 0):
        """
        Perform a set of simulations over the simulation parameter space, n times, to be able to
        1) estimate how much a set of experiments will approximately take
        2) estimate the variation in the detected photons
        Both estimates are rough estimates and can probably be improved for example by adding more variety in the
        simulations or running more of them.
        """
        LOGGER.info("Performing simulations in order to get the simulation settings.")
        simulation_space = self.interface.divide_space(5, self.interface.list_locs("simulation"), method="equidistant")
        delta_configs, flattened_config = self.interface.create_delta_configs(simulation_space)
        dfs = []

        if offloader_cfg == 0:
            for i in range(n):
                df, last_config = self.interface(delta_configs, flattened_config, name= "gen_sim_settings")
                dfs.append(df)
           
        else: 
            for i in range(n):
                if i==0:
                    name= "gen_sim_settings"
                else:
                    name= "repeatKey_noNewExptFolder"
                df, last_config = self.interface(delta_configs, flattened_config, name= name, offloader_cfg = offloader_cfg)
                dfs.append(df)
        
        df = pd.concat(dfs)

        # Get function to calculate time given simulation settings
        df_simulation = df[self.simulation_params].drop_duplicates().reset_index(drop=True)
        t, t_std = [], []
        for i in range(len(df_simulation)):
            values = df_simulation.iloc[i].values
            df_sub = df[(df[self.simulation_params] == values).all(axis=1)]
            t.append(np.mean(df_sub["time"].values))
            t_std.append(np.std(df_sub["time"].values))
        df_simulation["t"] = t
        df_simulation["t_std"] = t_std
        xy = df_simulation.values[:, :2]
        z = t
        self.simulation_time = CloughTocher2DInterpolator(xy, z)

        # Get function to approximate std given photons on detector (simple least squares)
        x = np.mean(dfs, axis=0)[:, -2]
        y = np.std(dfs, axis=0)[:, -2][:, None]
        A = np.vstack([x, np.ones(len(x))]).T
        alpha = np.dot((np.dot(np.linalg.inv(np.dot(A.T, A)), A.T)), y)
        self.simulation_error = lambda v: v*alpha[0] + alpha[1]

        

    def initial_sweep(self, biomarker: int = 10, tissue: int = 10, wavelength: int = 10, voxel_size: float = 0.05,
                      photons: float = 10**7, output_path: Path = None, offloader_cfg = 0):
        """
        Initial low resolution sweep over the wavelengths, varying tissue and biomarker.
        """
        tissue_space = self.interface.divide_space(tissue, self.tissue_params)#, method="equidistant")
        biomarker_space = self.interface.divide_space(biomarker, [self.biomarker], method="equidistant")
        hardware_space_0 = self.interface.divide_space(wavelength, [('Optode', 'Source', 'mu')],
                                                       method="equidistant")
        hardware_space_1 = {
            ('Optode', 'Source', 'Size'): [float(.5)]
        }
        hardware_space_2 = {
            ('Optode', 'Source', 'sig'): [float(12)]
        }
        exp_space = {
            ('Session', 'Photons'): [float(photons)],
            ('Domain', 'LengthUnit'): [float(voxel_size)]
        }
        delta_configs, flattened_configs = self. interface.create_delta_configs(hardware_space_0, hardware_space_1,
                                                                                hardware_space_2, biomarker_space,
                                                                                exp_space, tissue_space)
        self.get_expected_time(flattened_configs)

        # Run experiments
        df, last_config = self.interface(delta_configs, flattened_configs, name= "initial_sweep", offloader_cfg=offloader_cfg)
        if output_path is None:
            output_path = Path(last_config['Expt']['pathExpt'],'initialSweepData.pickle')
        df = merge_data(df, output_path)
        self.df = df
        return df

    def get_expected_time(self, flattened_config):
        if self.simulation_time is not None:
            time_estimate = np.sum([self.simulation_time(x[('Session', 'Photons')], x[('Domain', 'LengthUnit')])
                                    for x in flattened_config])
            LOGGER.info(f"Estimates time is {time_estimate} seconds or {time_estimate / 60} minutes.")
            print(f"Estimates time is {time_estimate} seconds or {time_estimate / 60} minutes.")
        else:
            LOGGER.info("Cannot estimate time. Run 'get_simulation_settings' first.")

    def add_hardware_table_data(self, df, source_slice=np.s_[::1], detector_slice=np.s_[::1]):
        """
        Adds hardware design data to the hardware design table by calculating all permutations of unique source and detector configurations from the given dataframe.
        """
        if self.relations is None:
            raise ValueError(f"Cannot process new data, set hardware config first!")

        # Calculate the hardware design source table
        df_sources = None
        hardware_columns = self.interface.list_locs("hardware")                                                     # get the source parameters
        unique_source_values = df[hardware_columns].drop_duplicates()[source_slice]                                 # find the unique values of the source parameters
        for i in self.source_ids:                                                                                   # loop over the sources
            df_source = unique_source_values
            df_source = pd.DataFrame(df_source.values, columns=pd.MultiIndex.from_tuples(
                [(a, b) for a, b in zip([f"source_{i}"] * len(hardware_columns), hardware_columns)]))               # make a source column with the parameters
            if df_sources is None:
                df_sources = df_source                                                                              # if this is the first source, start a source table
            else:
                df_sources = df_sources.merge(df_source, how='cross')                                               # Else merge the source table with the new source creating every permutation of the sources
        hardware_design_source = pd.DataFrame(df_sources.values, columns=self.hardware_design_source.columns[:-2])  # make a dataframe of the source table
        self.hardware_design_source = pd.concat([self.hardware_design_source, hardware_design_source])              # add the source table to the hardware design table in the framework object !!

        # Calculate the hardware design detector table
        detector_ids, detector_counts = np.unique(np.array(self.relations)[:, 1], return_counts=True)               # get the detector ids and the number of detectors.  detector counts is the number of times that detector is referenced in this cfg.
        df_detectors = None
        unique_detector_values = df[DETECTOR_PARAMS].drop_duplicates()[detector_slice]                             # get the unique detector values in the df, thats combinations of pitch and size
        r_i = 0
        for i, c in zip(detector_ids, detector_counts): # for this detector id and the number of times it is referenced in the cfg
            det_df = unique_detector_values 
            for j in range(1, c): # for the number of times this detector is referenced in the cfg
                r_i += 1 
                det_df = det_df.merge(unique_detector_values, how="cross", suffixes=(f'_{j}', f'_{0}')) # merge the detector values with itself to create all possible combinations of the detector values
                det_df = det_df[det_df.iloc[:, -3] == det_df.iloc[:, -1]] # require that the same detector be the same size
                det_df = det_df.drop(det_df.columns[-3], axis=1) 
            if df_detectors is None:
                df_detectors = det_df
            else:
                df_detectors = df_detectors.merge(det_df, how='cross') # merge the detector table with the new detector table creating every permutation of the detectors allowed
            r_i += 1
        df_detectors = pd.DataFrame(data=df_detectors.values,
                                    columns=self.hardware_design.iloc[:, 3*len(self.source_ids):-2].columns) # make a dataframe of the detector table

        # Combine both tables into one large table
        hardware_design = pd.DataFrame(df_sources.merge(df_detectors, how='cross').reset_index(drop=True).values,
                                       columns=self.hardware_design.columns[:-2]) # merge the source and detector tables to create a hardware design table with every permutation of source and detector
        self.hardware_design = pd.concat([self.hardware_design, hardware_design])

    def calculate_hardware_costs(self, num_round=50):
        self._hardware_table_check()

        costs = []
        stds = []

        to_calculate = pd.isna(self.hardware_design["cost"]).copy()
        #to_calculate = pd.Series(True, index=self.hardware_design.index).copy() # find indexes to calculate

        df_sub_h = self.hardware_design[to_calculate]  # Should we do all, instead of to_calculate?  Right now it just does new entry combinations.
        hardware_parameters = self.source_params + self.detector_params 
        LOGGER.info(f"Calculating cost for updated hardware design table of length {len(df_sub_h)}.")
        
        for i in tqdm(range(len(df_sub_h))): # Loop over every ROW / configuration in the hardware design table
            features = []
            for r in self.relations: # relations r are (source, detector) pairs
                values = np.hstack([df_sub_h[f"source_{r[0]}"].values[i], df_sub_h[f"detector_{r[1]}"][
                    [f"{DETECTOR_PARAMS[0]}_{r[0]}", DETECTOR_PARAMS[1]]].values[i]]) # concatinate source [size, mu, sig] and detector values [pitch, size]
                df_sub = self.df[np.all((self.df[hardware_parameters] == values), axis=1)] # find the data in the df that corresponds to this hardware configuration # ** see printout below
                x = df_sub["detected_photons"].values[:, None] # Number of photons detected for this HW configuration
                features.append(x)
            y = df_sub[self.interface.list_locs("optimization")[0]].values # SpO2 values in simulation data for this HW configuration
            x = np.concatenate(features, axis=1)

            cost, std = regression(x, y, num_round=num_round)
            costs.append(cost)
            stds.append(std)

        # Rescale costs with the biomarker range
        biomarker_config = self.interface[self.interface.list_locs("optimization")[0]]
        self.hardware_design.loc[to_calculate, "cost"] = np.array(costs) / (biomarker_config.max - biomarker_config.min)
        self.hardware_design.loc[to_calculate, "std"] = np.array(stds) / (biomarker_config.max - biomarker_config.min)
        
            # ** print(r, values)
            # (0, 0) [  0.5 420.   12.    0.5   0.5]
            # (1, 0) [  0.5 420.   12.    0.5   0.5]
            # (1, 1) [  0.5 420.   12.    3.5   0.5]
    
    
    def calculate_hardware_costs_parallel(self, num_round=50):
        self._hardware_table_check()

        costs = []
        stds = []

        to_calculate = pd.isna(self.hardware_design["cost"]).copy()
        #to_calculate = pd.Series(True, index=self.hardware_design.index).copy()

        df_sub_h = self.hardware_design[to_calculate]  # Should we do all, instead of to_calculate?  Right now it just does new entry combinations.
        hardware_parameters = self.source_params + self.detector_params
        LOGGER.info(f"Calculating cost for updated hardware design table of length {len(df_sub_h)}.")

        import concurrent.futures
        from tqdm import tqdm
        import numpy as np

        def process_row(i, df_sub_h, relations, df, hardware_parameters, DETECTOR_PARAMS, interface, num_round):
            features = []
            for r in relations:
                # Find the hardware design that's being calculated
                values = np.hstack([df_sub_h[f"source_{r[0]}"].values[i], df_sub_h[f"detector_{r[1]}"][
                    [f"{DETECTOR_PARAMS[0]}_{r[0]}", DETECTOR_PARAMS[1]]].values[i]])
                # Find the corresponding data in the df
                df_sub = df[np.all((df[hardware_parameters] == values), axis=1)]
                x = df_sub["detected_photons"].values[:, None]
                features.append(x)
            x = np.concatenate(features, axis=1)
            y = df_sub[interface.list_locs("optimization")[0]].values # this is pulling the values of the biomarker from the subdf

            cost, std = regression(x, y, num_round=num_round) # Regression between detected photons and the biomarker value for this configuraiton of hardware
            return cost, std

        costs = []
        stds = []

        print('starting parallel processing')
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor: # optimized for PC-28113.  use os.cpu_count()
            futures = [executor.submit(process_row, i, df_sub_h, self.relations, self.df, hardware_parameters, DETECTOR_PARAMS, self.interface, num_round) for i in range(len(df_sub_h))]
            for idx, future in enumerate(concurrent.futures.as_completed(futures)):
                if idx % 100 == 0:
                    print(f"Processing row {idx} of {len(df_sub_h)}")
                cost, std = future.result()
                costs.append(cost)
                stds.append(std)

        # Rescale costs with the biomarker range
        biomarker_config = self.interface[self.interface.list_locs("optimization")[0]]
        self.hardware_design.loc[to_calculate, "cost"] = np.array(costs) / (biomarker_config.max - biomarker_config.min)
        self.hardware_design.loc[to_calculate, "std"] = np.array(stds) / (biomarker_config.max - biomarker_config.min)

    def _hardware_table_check(self):
        if self.relations is None:
            raise ValueError(f"Please first set the hardware configuration!")
        if len(self.hardware_design_source) == 0:
            raise ValueError(f"Hardware table is empty, please run at least some simulations and update"
                             f" the hardware table!")

    def get_next_simulations(self, num_points=10, offloader_cfg = 0):
        """
        Given a hardware source table with calculated costs for different hardware design, return the next simulations
        to run.
        """
        self._hardware_table_check()
        #check there are no NaN values in the cost column
        if self.hardware_design["cost"].isnull().values.any():
            raise ValueError(f"Hardware design table has NaN values in the cost column. Please calculate costs first using calculate_hardware_costs_parallel() method.")

        # Calculate how to scale such that all columns are between 0 and 1
        hardware_columns = self.interface.list_locs("hardware")
        # # get min and max values for each hardware parameter
        source_min = np.array(
            [self.interface[hardware_columns[i]].min for i in range(len(hardware_columns))] * len(self.source_ids))
        source_max = np.array(
            [self.interface[hardware_columns[i]].max for i in range(len(hardware_columns))] * len(self.source_ids))

        # Calculate costs per hardware source design
        costs = []
        stds = []
        for i in range(len(self.hardware_design_source)): # each row is a specific source configuration
            df_sub = self.hardware_design[np.all(
                self.hardware_design.iloc[:, :3 * len(self.source_ids)] == self.hardware_design_source.iloc[
                                                                             i,
                                                                             :3 * len(self.source_ids)].values,
                axis=1)] # this is finding the rows in the hardware design table that match all entries of the source configuration
            index = np.argmin(df_sub[["cost"]])
            costs.append(df_sub.iloc[index]["cost"][0])
            stds.append(df_sub.iloc[index]["std"][0])
        self.hardware_design_source["cost"] = costs
        self.hardware_design_source["std"] = stds

        # Get thedata for bayesian optimization
        data = self.hardware_design_source.values
        # # Normalizes the feature columns (excluding the last two columns for cost and standard deviation).
        train_x = Tensor((data[:, :-2] - source_min[None]) / (source_max[None] - source_min[None]))
        # # Sets the target values for optimization. The 1 - transformation is used to convert costs to a maximization problem (since lower costs are better).
        train_y = 1-Tensor(data[:, -2][:, None])
        # # Sets the variance of the target values.
        train_yvar = Tensor(data[:, -1][:, None])

        # Uses Bayesian optimization to find the next candidate hardware design.
        candidate = 1 - self.get_next_candidate(train_x, train_y, train_yvar)

        candidate = candidate * (source_max[None] - source_min[None]) + source_min[None]
        candidate = candidate.reshape(len(self.source_ids), 3)
        LOGGER.info(f"Next candidate found: {candidate}")
        print(f"Next candidate found: {candidate}")

        # Create next set of simulations
        tissue_space = self.interface.divide_space(num_points, self.tissue_params)
        biomarker_space = self.interface.divide_space(num_points, [self.biomarker], method="equidistant")
        hardware_space = {
            ('Optode', 'Source', 'Size'): candidate[:, 0],
            ('Optode', 'Source', 'mu'): candidate[:, 1],
            ('Optode', 'Source', 'sig'): candidate[:, 2]
        }
        exp_space = {
            ('Session', 'Photons'): [float(10 ** 7)],
            ('Domain', 'LengthUnit'): [0.050]
        }
        delta_configs, flattened_configs = self.interface.create_delta_configs(hardware_space, biomarker_space, exp_space,
                                                                          tissue_space)

        new_df, last_config = self.interface(delta_configs, flattened_configs, "next_simulations", offloader_cfg = offloader_cfg)
        return new_df

    def get_next_candidate(self, train_x, train_y, train_yvar, num_candidates=1):
        """
        Expects input already to be normalized.
        """
        gp = SingleTaskGP(train_x, train_y, train_Yvar=train_yvar)

        UCB = UpperConfidenceBound(gp, beta=0.4)

        bounds = torch.stack([torch.zeros(train_x.shape[1]), torch.ones(train_x.shape[1])])
        candidate, acq_value = optimize_acqf(
            UCB, bounds=bounds, q=num_candidates, num_restarts=5, raw_samples=20,
        )
        return candidate
