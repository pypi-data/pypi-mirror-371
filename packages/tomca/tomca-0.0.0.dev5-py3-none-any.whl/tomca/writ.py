
"""
functions which \b write our standard formats of data; includes functions to
write out jdat, json, and figures with logging in tomca.
"""


def try_del(dict, nested_keys):
    """Try to delete a leaf key in a dictionary, if it exists."""
    try:
        for key in nested_keys[:-1]:
            dict = dict[key]
        del dict[nested_keys[-1]]
    except KeyError:
        pass


def vol_out(cfg, vol):
    """write out the volume file"""

    if cfg['Expt']['verb'] >= 1:
        print("- Write volume out function unfinished")

    return (cfg)


def json(jcfg):
    import jdata
    import os

    jcfg['vol'] = []

    jdata.savet(jcfg, os.path.join(jcfg['Expt']['pathState'], 'sim.json'))
    print('- Wrote out JSON to: ' + os.path.join(jcfg['Expt']['pathState'],
                                                 'sim.json'))


def mcfg_json(jcfg):
    import jdata
    import copy
    from src import tomca
    import os

    tmp = copy.deepcopy(jcfg['mcfg'])
    if 'vol' in tmp:
        del tmp['vol']
    del tmp['prop']
    jdata.savet(tmp,
                outFile := os.path.join(
                    jcfg['Expt']['pathState'],
                    jcfg['Expt']['time']+'_mcfg.json'
                    ),
                indent=4)
    tomca.util.verb('Saved ' + '_mcfg' + '.json file @: ' + outFile,
                   jcfg['Expt']['verb'], 1)
    return jcfg


def reduce_jcfg(jcfg):
    import copy

    tmp = copy.deepcopy(jcfg)

    # Setup
    keepVol = 0
    if "write" in tmp['Expt']:
        if "jcfg_vol" in tmp['Expt']['write']:
            keepVol = tmp['Expt']['write']['jcfg_vol']
    if not keepVol:
        try:
            del tmp['vol']
        except:
            pass

    try:
        del tmp['mcfg']['vol']
    except:
        pass
    try:
        del tmp['vol_svmc']
    except:
        pass

    # Delete keys from the main dictionary
    def delete_keys(d, keys):
        """
        Delete a list of keys from a dictionary if they exist.
        Args:
            d (dict): The dictionary to delete keys from.
            keys (list): List of keys to delete.
        """
        for k in keys:
            try:
                del d[k]
            except Exception:
                pass

    # Define keys to check for deletion
    del_keys = ['detp', 'p', 'x', 'v', 'w', 'detp_masked', 'p_masked',
                'x_masked', 'v_masked', 'w_masked',
                'angles', 'flux']
            
    # Delete keys from mcfg
    delete_keys(tmp.get('mcfg', {}), del_keys)
    
    if "json_res_IM" in jcfg['Expt']['write']:
        if jcfg['Expt']['write']['json_res_IM'] == 0:
            del_keys.append('IM')

    # Delete keys from default results
    delete_keys(tmp.get('res', {}), del_keys)
    
    # Delete keys from replay results
    clear_replay = 0
    if 'doReplay' in tmp['Expt']: 
        if tmp['Expt']['doReplay']:
            clear_replay = 1
            if 'Mask' in tmp['Optode']['Detector']:
                if tmp['Optode']['Detector']['Mask'] != [[]]:
                    clear_replay = 0
    if clear_replay:   
        delete_keys(tmp.get('res_replay', {}), del_keys)  

    # Delete keys from replay results
    if 'Mask' in tmp['Optode']['Detector']:
        if 'configs_labels' in tmp['Optode']['Detector']:
            for replay_key in tmp['Optode']['Detector']['configs_labels']:
                delete_keys(tmp.get(replay_key, {}), del_keys)

    savePlotPlanes = tmp['Expt']['write'].get('json_res_plotPlanes', 0)
    if savePlotPlanes == 0:
        try:
            del tmp['res']['plot_planes']
            if 'Mask' in tmp['Optode']['Detector']:
                if 'configs_labels' in tmp['Optode']['Detector']:
                    for replay_key in tmp['Optode']['Detector']['configs_labels']:
                        del tmp[replay_key]['plot_planes']
        except:
            pass

    if 'Spectrum' in tmp['Optode']['Source']:
        # Want to keep the wavelength and intensity of your source?
        # uncomment these two lines!

        # tmp['Optode']['Source']['wls'] = tmp['Optode']['Source']['Spectrum'].iloc[:,  0].values
        # tmp['Optode']['Source']['intNorm'] = (tmp['Optode']['Source']['Spectrum'].iloc[:,  1].values)/sum(tmp['Optode']['Source']['Spectrum'].iloc[:,  1].values)
        del tmp['Optode']['Source']['Spectrum']
    if 'Pattern' in tmp['Optode']['Source']:
        del tmp['Optode']['Source']['Pattern']

    def convert_tuples_to_lists(d):
        if isinstance(d, dict):
            return {k: convert_tuples_to_lists(v) for k, v in d.items()}
        elif isinstance(d, (list, tuple)):
            return [convert_tuples_to_lists(i) for i in d]
        else:
            return d

    convert_tuples_to_lists(tmp)
    return tmp


def jcfg_json(jcfg, multi=0, desc='_jcfg'):
    import jdata
    from src import tomca
    import os
    from copy import deepcopy

    tmp = reduce_jcfg(deepcopy(jcfg))
    if multi == 0:
        jdata.savet(tmp, outFile := os.path.join(tmp['Expt']['pathState'],
                    tmp['Expt']['time'] + desc + '.json'), indent=4)
    else:
        jdata.savet(tmp, outFile := os.path.join(tmp['Expt']['pathState'],
                    tmp['Expt']['time'] + desc + '.json'), indent=4)
    tomca.util.verb('Saved ' + desc + '.json file @: ' + outFile,
                   jcfg['Expt']['verb'], 1)

    return jcfg


def fig(jcfg, fig, filename, location='state'):
    """
    Save a matplotlib figure as an SVG file at state/exp folder location.

    This function saves the specified matplotlib figure as an SVG file with
    the given filename.

    Args:
        jcfg (dict): A dictionary containing configuration settings.
        fig (matplotlib.figure.Figure): The matplotlib figure to be saved.
        filename (str): The name of the file to be saved (without the
        file extension).
        location (str, optional): The state parameter indicating the type of
        file to be saved.
            Defaults to 'state' folder.

    Returns:
        None
    """
    import os
    from src import tomca
    import matplotlib.pyplot as plt

    plt.figure(fig)

    if location == 'Expt':
        savepath = jcfg['Expt']['pathExpt']
    else:
        savepath = jcfg['Expt']['pathState']

    # Ensure the directory exists
    os.makedirs(savepath, exist_ok=True)

    savepath = os.path.join(savepath, filename + ".svg")

    # Debugging: Print the savepath to check for issues
    # print(f"Saving figure to: {savepath}")

    if "plot" in jcfg['Expt']:
        if "writeFigs" not in jcfg['Expt']['plot']:
            jcfg['Expt']['plot']['writeFigs'] = 1

        if jcfg['Expt']['plot']['writeFigs']:
            try:
                plt.savefig(savepath, format="svg", dpi=800, bbox_inches='tight')
                tomca.util.verb('Wrote plot: ' + filename, jcfg['Expt']['verb'], 1)
            except Exception as e:
                tomca.util.verb(f'Failed to write plot {filename}: {e}', jcfg['Expt']['verb'], 1)
        else:
            tomca.util.verb('Did not write plot ' + filename + '. Toggle with jcfg[\'Expt\'][\'plot\'][\'writeFigs\']', jcfg['Expt']['verb'], 1.5)
    return


def vol_matlab_dot_mat(volIn: float, pathOut: str):
    """Uses a MATLAB bridge to save a .mat file.

    Args:
        volIn (_type_): Volume to be saved, in python ordering
        pathOut (_type_): locaiton to be saved, string, should end in .mat
    """

    import matlab.engine
    import numpy as np

    vol = volIn.copy()
    vol = vol.reshape(vol.shape, order='F')
    print('Reshaped python volume for MATLAB')

    # Start MATLAB
    eng = matlab.engine.start_matlab()
    print('Started MATLAB engine to save .mat file')

    # Call SVMC
    svmcvol = np.array(eng.save_py_to_mat(vol, pathOut))
    print('Finished saving .mat file at '+pathOut)

    # Exit MATLAB
    eng.quit()

    return


def create_svg_movie(folder_path):
    import os
    import shutil

    # Get all subfolders in the main folder path
    subfolders = [f.path for f in os.scandir(folder_path) if f.is_dir()]

    # Sort the subfolders by name
    subfolders.sort()

    # Initialize a dictionary to store the .svg image filenames as keys and
    # their corresponding subfolder paths as values
    svg_files = {}

    # Iterate through each subfolder
    for subfolder in subfolders:
        # Remove the date/time stamp from the subfolder name
        new_subfolder_name = os.path.basename(subfolder)[16:]
        new_subfolder_path = os.path.join(os.path.dirname(subfolder),
                                          new_subfolder_name)

        # Rename the subfolder
        os.rename(subfolder, new_subfolder_path)

        # Get all the files in the renamed subfolder
        files = os.listdir(new_subfolder_path)

        # Filter the files to only keep .svg files
        svg_files_in_subfolder = [file for file in files if file.lower().endswith('.svg')]

        # Iterate through each .svg file and add it to the dictionary with its
        # filename as the key and subfolder path as the value
        for svg_file in svg_files_in_subfolder:
            svg_files[svg_file] = new_subfolder_path

    # Create the output folder where the movie will be saved
    output_folder = os.path.join(folder_path, 'svg_movie')
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through the .svg filenames and copy them to the output folder
    # while renaming them with a regular name
    for svg_filename in svg_files:
        svg_filepath = os.path.join(svg_files[svg_filename], svg_filename)
        # Extract the regular name without the date/time stamp
        new_filename = svg_filename.split('_')[-1]
        new_filepath = os.path.join(output_folder, new_filename)
        shutil.copy(svg_filepath, new_filepath)

    print("SVG movie created successfully!")


def fig_manual(fig, path, filename):
    # TODO: convert to svg
    import os
    import matplotlib.pyplot as plt
    plt.figure(fig)
    plt.savefig(os.path.join(path, filename + ".png"), format="png", dpi=800)
    return


def state_outputs(jcfg: dict, saveDesc='_results'):
    from src import tomca

    savepkl = 0
    savejson = 1
    jcfg_res_IM = 1

    # Option to save a full pkl file of state
    if "saveStatePkl" in jcfg['Expt']:
        if jcfg['Expt']['saveStatePkl']:
            savepkl = 1

    if "write" in jcfg['Expt']:
        if "jcfg_vol" in jcfg['Expt']['write']:
            if jcfg['Expt']['write']['jcfg_vol'] == 0:
                try:
                    del jcfg['vol']
                except:
                    pass
        if "jcfg_res_IM" in jcfg['Expt']['write']:
            if jcfg['Expt']['write']['jcfg_res_IM'] == 0:
                try:
                    del jcfg['res']['IM']
                except:
                    pass
        if "state_pkl" in jcfg['Expt']['write']:
            savepkl = jcfg['Expt']['write']['state_pkl']
        if "state_results_json" in jcfg['Expt']['write']:
            savejson = jcfg['Expt']['write']['state_results_json']
        if "media_table" in jcfg['Expt']['write']:
            if jcfg['Expt']['write']['media_table']:
                outTable = create_media_table(jcfg)
                tomca.writ.fig(jcfg, outTable, 'media_table', 'state')

    if savepkl:
        jcfg['Expt']['pklData'] = jcfg['Expt']['pathState']+'_simulated_jcfg.pkl'
        tomca.util.pickle_out(jcfg, jcfg['Expt']['pklData'])
        tomca.util.verb('Saved .pkl file at ' + jcfg['Expt']['pklData'],
                       jcfg['Expt']['verb'], 1)

    # Save a reduced json version.  removes all large arrays.
    if savejson:
        jcfg = jcfg_json(jcfg, desc=saveDesc)
    else:
        jcfg = reduce_jcfg(jcfg)
    return jcfg


def create_media_table(jcfg, columns='all'):
    # Create a list of dictionaries with the media properties
    import matplotlib.pyplot as plt
    import pandas as pd

    media_data = []
    for media in jcfg['Domain']['Media']:
        media_data.append(media)

    # Create a pandas DataFrame from the list of dictionaries
    df = pd.DataFrame(media_data)

    # Set the 'label' column as the index
    df.set_index('label', inplace=True)
    # Replace non-numeric with NaN
    df['mua'] = pd.to_numeric(df['mua'], errors='coerce')
    # Replace NaN with default value (e.g., 0)
    df['mua'].fillna(0, inplace=True)
    df.dropna(subset=['mua'], inplace=True)  # Remove rows with NaN in 'mua'

    # Replace non-numeric with NaN
    df['mus'] = pd.to_numeric(df['mus'], errors='coerce')
    # Replace NaN with default value (e.g., 0)
    df['mus'].fillna(0, inplace=True)
    df.dropna(subset=['mus'], inplace=True)  # Remove rows with NaN in 'mua'

    # Replace non-numeric with NaN
    df['g'] = pd.to_numeric(df['g'], errors='coerce')
    df['g'].fillna(0, inplace=True)  # Replace NaN with default value (e.g., 0)
    df.dropna(subset=['g'], inplace=True)  # Remove rows with NaN in 'mua'
    # Round 'mua' and 'mus' columns to 4 decimal points
    df['mua'] = df['mua'].round(4)
    df['mus'] = df['mus'].round(4)
    df['g'] = df['g'].round(4)
    # Reorder the columns
    columns_order = ['mua', 'mus', 'g', 'n', 'bf', 'sat', 'HbConcGpdL', 'dves',
                     'water', 'fat', 'mel', 'bone', 'mus0', 'dZ',
                     'layer_comp_labels', 'layer_comp_fracs', 'layer_comp_mua']
    df = df.reindex(columns=columns_order +
                    [col for col in df.columns if col not in columns_order])

    # Plot the table
    fig, ax = plt.subplots(figsize=(20, 8))  # set size frame
    ax.axis('tight')
    ax.axis('off')
    if columns == 'all':
        table = ax.table(cellText=df.values, colLabels=df.columns,
                         rowLabels=df.index, cellLoc='center', loc='center')
    else:
        table = ax.table(cellText=df[columns].values,
                         colLabels=df[columns].columns,
                         rowLabels=df[columns].index,
                         cellLoc='center',
                         loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.2, 1.2)

    # Add title over the table
    title = jcfg["Expt"]["exptName"]
    if "spectProfile" in jcfg["Optode"]["Source"]:
        title += f" - SpectProfile: {jcfg['Optode']['Source']['spectProfile']}"
    if "mu" in jcfg["Optode"]["Source"]:
        title += f" - central WL: {jcfg['Optode']['Source']['mu']}nm"
    if "sig" in jcfg["Optode"]["Source"]:
        title += f" - width: {jcfg['Optode']['Source']['sig']}nm"

    # Add title directly above the table
    plt.subplots_adjust(top=0.85)
    plt.suptitle(title, fontsize=12, fontweight='bold')

    # Adjust column width to fit content
    table.auto_set_column_width(col=list(range(len(df.columns))))

    return fig


def create_csv(filepath, filename, header):
    import csv
    import os
    with open(os.path.join(filepath, f'{filename}.csv'),
              'w', encoding='UTF-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, header, delimiter=';')
        writer.writeheader()


def append_csv(filepath, filename, csv_export, header):
    import csv
    import os

    with open(os.path.join(filepath, f'{filename}.csv'),
              'a', encoding='UTF-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, header, delimiter=';')
        for csv_row in csv_export:
            writer.writerow(csv_row)


def get_value(dictionary, key):
    if not isinstance(dictionary, dict):
        return None
    if key in dictionary:
        return dictionary[key]
    for subdictionary in dictionary.values():
        recursive = get_value(subdictionary, key)
        if recursive:
            return recursive
