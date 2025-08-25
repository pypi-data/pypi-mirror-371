"""
functions which \b execute simulations; includes the main function simulate

2022 - 2024 V Zoutenbier
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pmcx
from src import tomca
import copy
import sys
import time


def update_stat(jcfg, jcfg_tmp, inName='res'):
    """ Update the statistics of the simulation results
    """
    if 'stat' not in jcfg[inName]:
        jcfg[inName]['stat'] = {}
        jcfg[inName]['stat']['runtime'] = 0
        jcfg[inName]['stat']['nphoton'] = 0
        jcfg[inName]['stat']['energytot'] = 0
        jcfg[inName]['stat']['energyabs'] = 0
        jcfg[inName]['stat']['unitinmm'] = 0
    jcfg[inName]['stat']['runtime'] += jcfg_tmp[inName]['stat']['runtime']
    jcfg[inName]['stat']['nphoton'] += jcfg_tmp[inName]['stat']['nphoton']
    jcfg[inName]['stat']['energytot'] += jcfg_tmp[inName]['stat']['energytot']
    jcfg[inName]['stat']['energyabs'] += jcfg_tmp[inName]['stat']['energyabs']
    jcfg[inName]['stat']['unitinmm'] = jcfg_tmp[inName]['stat']['unitinmm']
    return jcfg


def mcx_with_replays_and_cycles(jcfg: dict):
    """
    Executes a Monte Carlo simulation with optional replays and
    processes the results.

    This function performs a series of state cycles as specified in
    the input configuration dictionary `jcfg`.
    For each cycle, it runs a simulation, optionally processes saved
    photon data, and performs a replay if enabled.
    The results are then used to create a CCD image and calculate the
    average flux over all cycles.

    The function modifies the input dictionary `jcfg` in-place to update
    the results with the averaged flux and CCD image.

    Original code by V Zoutenbier 2022
    Major rework by VZ 12/2024

    Args:
        jcfg (dict): The input configuration dictionary containing
        experiment parameters and result storage.

    Returns:
        dict: The modified input configuration dictionary with updated results.
    """

    # Prepare for simulation by creating pmcx cfg variable, called mcfg.
    # This is a dict key in jcfg
    jcfg = tomca.conv.json_to_mcx(jcfg)

    # Write the mcfg and full jcfg to files in the state folder
    tomca.writ.jcfg_json(jcfg)

    # Start a working copy of jcfg
    jcfg_tmp_init = copy.deepcopy(jcfg)

    # Repeat the simulation for the number of 'state cycles',
    # cycles which clear the GPU between evaluations
    for rep in np.arange(jcfg['Expt']['stateCycles']):

        tomca.util.verb('Starting state cycle: ' + str(rep+1) + ' of ' +
                       str(jcfg['Expt']['stateCycles']), jcfg['Expt']['verb'],
                       1)

        # Duplicate simulation warning
        if jcfg['Session']['RNGSeed'] != -1 and \
                jcfg['Expt']['stateCycles'] > 1:
            tomca.util.verb(
                'RNG seed not changing within multiple state cycles! Set '
                'jcfg[\'Session\'][\'RNGSeed\']=-1', jcfg['Expt']['verb'], 0)

        # Run primary simulation, starting with a pristine state jcfg_tmp_init.
        # jcfg_tmp is just the current rep of the simulation
        # jcfg remains the version that is updated with the results of
        # the simulation and written out at the end.
        jcfg_tmp = tomca.exec.mcx(copy.deepcopy(jcfg_tmp_init))

        # Parse saved photon info
        if 'SaveDataMask' in jcfg_tmp['Session']:
            jcfg_tmp = tomca.conv.savedetflags_to_dict(jcfg_tmp)

            # Mask detected photons if a mask or detection limits
            # or acceptance angle are used
            jcfg_tmp = tomca.modi.mask_detected_photons(jcfg_tmp)

        # Bin photons to make CCD image and flux map that can
        # be accumulated over cycles
        if rep == 0:
            jcfg['res'] = {}
            jcfg['res']['IM'] = 0
            if "flux" in jcfg_tmp['res']:
                jcfg['res']['flux'] = 0
            if 'hist' in jcfg['Optode']['Detector']:
                jcfg['res']['det_angles'] = 0
        # Bin photons to make CCD image and flux map that can
        # be accumulated over cycles

        if 'det_angles' in jcfg['res']:
            ccd_vals, angular_dist = tomca.stas.bin_voxels_tmcx(
                jcfg_tmp, inName='res')
            jcfg['res']['det_angles'] += angular_dist
            jcfg = tomca.grap.detector_angles_histogram(jcfg, inName='res')
        else:
            ccd_vals, _ = tomca.stas.bin_voxels_tmcx(
                jcfg_tmp, inName='res')
        jcfg['res']['IM'] += ccd_vals

        # Add sum of detected photons
        jcfg['res']['detected_photons_weighted'] = np.sum(jcfg['res']['IM'])
        # Flux is accumulated over cycles
        if "flux" in jcfg['res']:
            #  if true flux, convert its units with the time step
            if jcfg['Session']['OutputType'] != 'energy':
                jcfg_tmp['res']['flux'] *= jcfg_tmp['Forward']['Dt']
            jcfg['res']['flux'] += jcfg_tmp['res']['flux'] / \
                jcfg_tmp['Expt']['stateCycles']
        update_stat(jcfg, jcfg_tmp, inName='res')

        # checks if a mask is used to create detector(s), if this is the case,
        # the detectors get replayed once all together and then seperately
        if "Mask" in jcfg['Optode']['Detector']:
            # make list of detector combinations to replay, consists of
            # [[All detectors together], [detector 1], [detector 2], ...]
            if len(jcfg['Optode']['Detector']['Mask']) == 1:
                det_combos = [jcfg['Optode']['Detector']['Mask']]
            else:
                det_combos = [jcfg['Optode']['Detector']['Mask']] +\
                    [[i] for i in jcfg['Optode']['Detector']['Mask']]
        else:
            det_combos = ['default']

        det_combo_labels = []
        # Loop over the list of detectors; for each detector do a replay;
        # the masked photons are saved in seperate locations from each other
        # and from the unmasked photons
        if jcfg['Expt']['doReplay']:
            for i, det_combo in enumerate(det_combos):
                det_combo_label = f'res_replay{i}' if i != 0 else 'res_replay'
                det_combo_labels.append(det_combo_label)

                # Do the replays for all det combos; replay of all detectors
                # together is saved as res_replay and the individual detectors
                # as res_replay1, res_replay2, etc
                if jcfg_tmp['Expt']['doReplay']:
                    jcfg_tmp[det_combo_label] = copy.deepcopy(jcfg_tmp['res'])
                    jcfg_tmp = tomca.modi.mask_detected_photons(
                        jcfg_tmp, resName=det_combo_label, mask=det_combo)
                    jcfg_tmp = tomca.exec.mcx_replay(
                        jcfg_tmp, saveKey=det_combo_label)

                    # Parse photon info
                    if 'SaveDataMask' in jcfg_tmp['Session']:
                        jcfg_tmp = tomca.conv.savedetflags_to_dict(
                            jcfg_tmp, resName=det_combo_label)
                        jcfg_tmp = tomca.modi.mask_detected_photons(
                            jcfg_tmp, resName=det_combo_label, mask=det_combo)
                        if rep == 0:
                            jcfg[det_combo_label] = {}
                            jcfg[det_combo_label]['IM'] = 0
                            jcfg[det_combo_label]['flux'] = 0
                            if 'hist' in jcfg['Optode']['Detector']:
                                jcfg[det_combo_label]['det_angles'] = 0

                        # Bin photons to make CCD image and flux map that can
                        # be accumulated over cycles
                        ccd_vals, angular_dist = tomca.stas.bin_voxels_tmcx(
                            jcfg_tmp, inName=det_combo_label)
                        jcfg[det_combo_label]['IM'] += ccd_vals
                        if 'det_angles' in jcfg[det_combo_label]:
                            jcfg[det_combo_label]['det_angles'] += angular_dist
                            jcfg = tomca.grap.detector_angles_histogram(
                                jcfg, inName=det_combo_label)

                        # Add sum of detected photons for replay results
                        jcfg[det_combo_label]['detected_photons_weighted'] = np.sum(jcfg[det_combo_label]['IM'])
                        # Flux is accumulated over cycles
                        if "flux" in jcfg['res']:
                            # if true flux, convert its units
                            # with the time step
                            if jcfg['Session']['OutputType'] != 'energy':
                                jcfg_tmp[det_combo_label]['flux'] *= \
                                    jcfg_tmp['Forward']['Dt']
                            jcfg[det_combo_label]['flux'] += \
                                jcfg_tmp[det_combo_label]['flux']\
                                / jcfg_tmp['Expt']['stateCycles']
                    update_stat(jcfg, jcfg_tmp, inName=det_combo_label)

        jcfg['Optode']['Detector']['configs'] = det_combo_labels
        jcfg['Optode']['Detector']['configs_labels']=det_combo_labels

    # Remove unneeded data from jcfg to keep the size of the dict down as
    # much as possible.
    tomca.writ.try_del(jcfg, ['mcfg', 'vol'])
    tomca.writ.try_del(jcfg['res'], ['seeds'])
    if 'offload' in jcfg['Expt'] and jcfg['Expt']['offload']:
        tomca.writ.try_del(jcfg['res'], ['p'])
        tomca.writ.try_del(jcfg['res'], ['v'])
        tomca.writ.try_del(jcfg['res'], ['x'])
        tomca.writ.try_del(jcfg['res'], ['seeds_masked'])
        tomca.writ.try_del(jcfg['res'], ['detp'])
        tomca.writ.try_del(jcfg['res'], ['detp_masked'])
        tomca.writ.try_del(jcfg['res'], ['p_masked'])
        tomca.writ.try_del(jcfg['res'], ['v_masked'])
        tomca.writ.try_del(jcfg['res'], ['x_masked'])

    tomca.util.verb('Finished state cycles', jcfg['Expt']['verb'], 1)
    jcfg['Optode']['Detector']['configs'] = det_combos

    if jcfg['Session']['OutputType'] == 'energy':

        if det_combo_labels == []:
            if 'CalculateEnergy' in jcfg['Session']:
                if jcfg['Session']['CalculateEnergy']:
                    jcfg = tomca.calc.energy_per_media(
                        jcfg,  saveKey='res')
        for det_combo_label in det_combo_labels:
            if 'CalculateEnergy' in jcfg['Session']:
                if jcfg['Session']['CalculateEnergy']:
                    jcfg = tomca.calc.energy_per_media(
                        jcfg, saveKey=det_combo_label)

        if det_combo_labels == []:
            if 'CalculateEnergy' in jcfg['Session']:
                if jcfg['Session']['CalculateEnergy']:
                    jcfg = tomca.calc.energy_per_media(jcfg, saveKey='res')
        else:
            for det_combo_label in det_combo_labels:
                if 'CalculateEnergy' in jcfg['Session']:
                    if jcfg['Session']['CalculateEnergy']:
                        jcfg = tomca.calc.energy_per_media(
                            jcfg, saveKey=det_combo_label)

    for det_combo_label in det_combo_labels:
        if 'offload' in jcfg['Expt']:
            if jcfg['Expt']['offload']:
                if 'detp' in jcfg[det_combo_label]:
                    tomca.writ.try_del(jcfg[det_combo_label], ['detp'])
                if 'seeds' in jcfg[det_combo_label]:
                    tomca.writ.try_del(jcfg[det_combo_label], ['seeds'])
    tomca.writ.try_del(jcfg['mcfg'], ['detphotons'])
    tomca.writ.try_del(jcfg['mcfg'], ['seed'])

    return jcfg


def mcx(jcfg: dict, saveKey='res'):
    """Run the pmcx.run function, saving to the tomca dict structures

    Args:
        jcfg (dict): json style dict with mcfg key
        saveKey (str, optional): Key to save output to. Defaults to 'res',
        res_replay used as well.

    Returns:
        jcfg (dict): json style dict with res key appended
    """

    if saveKey != 'res':
        tomca.util.verb('Starting replay MCX evaluation for '+saveKey,
                       jcfg['Expt']['verb'], 1)
    else:
        tomca.util.verb('Starting primary MCX evaluation',
                       jcfg['Expt']['verb'], 1)

    # Save the original stdout so you can restore it later
    original_stdout = sys.stdout
    # Open a file for writing
    writeOut = 1

    if "write" in jcfg["Expt"]:
        if "mcx_output_file" in jcfg["Expt"]["write"]:
            writeOut = jcfg["Expt"]["write"]["mcx_output_file"]

    if writeOut:
        if "pathState" in jcfg["Expt"]:
            with open(
                Path(jcfg["Expt"]["pathState"]) /
                    (jcfg['Expt']['time'] + 'mcx_output.txt'), 'a') as file:

                # Redirect stdout to the file
                sys.stdout = file
                jcfg[saveKey] = pmcx.run(jcfg['mcfg'])
            # Restore the original stdout
            sys.stdout = original_stdout
        else:
            jcfg[saveKey] = pmcx.run(jcfg['mcfg'])
    else:
        jcfg[saveKey] = pmcx.run(jcfg['mcfg'])

    return jcfg


def mcx_replay(jcfg: dict, saveKey='res_replay'):
    """Append the seed and detp entries from the first run to mcfgSounds, then
    rerun simulation

    Args:
        jcfg (dict): json style dict with res key

    Returns:
        jcfg (dict): json style dict with res_replay key appended
    """

    # update the mcfg for the replay
    # one must define cfg['seed'] using the returned seeds
    jcfg['mcfg']['seed'] = jcfg[saveKey]['seeds']
    # one must define cfg['detphotons'] using the returned detp data
    jcfg['mcfg']['detphotons'] = jcfg[saveKey]['detp']

    jcfg = mcx(jcfg, saveKey=saveKey)

    return jcfg


def simulate(jcfg, delta_cfg=None, offloader_cfg=0):
    """
    Executes a simulation based on the given configuration and
    delta configuration.

    This function prepares the simulation by setting up the maximum number of
    detected photons, initializing the figure dictionary, and applying changes
    from `delta_cfg` to the default configuration `jcfg`. It then generates
    the volume from the parameters in `jcfg`, prepares the simulation optics,
    imports the source spectrum, evaluates optical properties, and builds a
    string with the simulation state parameters for figures.

    The function performs the simulation with repeats and cycles, generates
    plots if verbosity is enabled, evaluates imaginary image detectors, and
    saves output files. Finally, it logs the completion of the state simulation
    and returns the modified configuration dictionary.

    Args:
        jcfg (dict): The input configuration dictionary containing the
            simulation parameters.
        delta_cfg (dict): The configuration dictionary containing changes
            to apply to the default configuration.

    Returns:
        dict: The modified input configuration dictionary with the results of
            the simulation.
    """
    jcfg['Expt']['t0'] = time.time()
    if delta_cfg is None:
        delta_cfg = {}
    # Apply changes to default
    tomca.util.update_jcfg(jcfg, delta_cfg)
    jcfg = tomca.util.prepare_state(jcfg, delta_cfg)

    # Generate volume from jcfg parameters
    if 'vol' not in jcfg:
        jcfg = tomca.buil.vol_init(jcfg)
        jcfg = tomca.buil.vol_layers(jcfg)
        jcfg = tomca.buil.vol_modify_region(jcfg)
        jcfg = tomca.buil.vol_vessel(jcfg)
        jcfg = tomca.conv.vol_svmc(jcfg)

    # Prepare simulation optics
    jcfg = tomca.buil.source(jcfg)
    jcfg = tomca.buil.detectors(jcfg)

    # Import Source Spectrum
    jcfg = tomca.buil.incident_spectrum(jcfg)

    # Evaluate optical properties
    jcfg = tomca.calc.mu_abs_scatt(jcfg)

    # Build up a string with the interesting parameters from the simulation
    # state for figures
    jcfg = tomca.make.state_str(jcfg)

    # Do the simulation, with any repeats of the
    # state accumulated appropriately
    jcfg = tomca.exec.mcx_with_replays_and_cycles(jcfg)

    # Generate plots
    jcfg = tomca.grap.state_xsections(jcfg)

    # Evaluate imaginary image detectors, if any
    jcfg = tomca.calc.img_detectors(jcfg)

    jcfg['Expt']['tf'] = time.time()
    # Save output files
    jcfg = tomca.writ.state_outputs(jcfg, saveDesc='jcfg_results')

    tomca.util.verb('Finished state. ' + 'Save directory: ' +
                   jcfg['Expt']['pathState'], jcfg['Expt']['verb'], 0)
    # tomca.util.verb(' ', jcfg['Expt']['verb'], 0)

    plt.close('all')
    
    return jcfg


def simulate_multiSource(jcfg, delta_cfg=None, offloader_cfg=0):
    # Check if delta_cfg is a single state
    if delta_cfg is None:
        delta_cfg = {}
    if isinstance(delta_cfg, tomca.util.branch_builder) or isinstance(delta_cfg,
                                                                     dict):
        jcfg = simulate(jcfg, delta_cfg, offloader_cfg)
        return jcfg
    # check if it's a list of states
    elif isinstance(delta_cfg, list):
        nSoures = len(delta_cfg)
        tomca.util.verb(
            f'Starting multi-source simulation with {nSoures} sources',
            jcfg['Expt']['verb'], 1)
        jcfg_combined = []

        # Simulate each state
        for i in range(len(delta_cfg)):
            tomca.util.verb(f'Simulating source {i+1} of {nSoures}',
                           jcfg['Expt']['verb'], 1.5)
            jcfg_combined.append(simulate(copy.deepcopy(jcfg), delta_cfg[i],
                                          offloader_cfg))
        # combine the results
        jcfg_combined = tomca.modi.combine_n_sims(jcfg_combined)

        # Generate plots with multiple sources
        tomca.grap.state_xsection_CCD(jcfg_combined, resName='res_replay',
                                     desc='_combinedSources')
        tomca.grap.state_xsection_CCDx(jcfg_combined, resName='res_replay',
                                      desc='_combinedSources')
        tomca.grap.state_xsection_flux(jcfg_combined,
                                      desc='_combinedSources')
        tomca.grap.state_xsection_flux_replay(jcfg_combined,
                                             desc='_combinedSources')
        # Save combined sources jcfg
        tmp = tomca.writ.reduce_jcfg(jcfg_combined)

        tomca.writ.jcfg_json(tmp, desc='_combinedSources')

        if "offload" in tmp["Expt"]:
            if tmp["Expt"]["offload"]:
                return tmp

        return jcfg_combined
    else:
        print('delta_cfg is not a list or a dict')
