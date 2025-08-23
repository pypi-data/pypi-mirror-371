"""
functions which \b impoert data; includes functions to import jdat, json with logging in tmcx.
"""

import json
import os
import platform
import pandas as pd
import numpy as np
import jdata

from pathlib import Path

from Software import tmcx


#TODO: Remove unused function
def jdat_json(jdatFilePath: str, verb: float):
    """Takes in an experiment path directory, reads in JSON then all jdat files in the directory, single jdat right now, should be extended to multiple.

    Args:
        jdatFilePath (str): Path to folder with jdat data file
        verb (float): verboseness level
    """        

    # Import JSON file accompanying JDAT in same directory
    jsonPath=jdatFilePath.replace('_detp.jdat', '.json')
    json_file = open(jsonPath)
    param = json.load(json_file, strict=False)
    json_file.close()
    tmcx.util.verb('Loaded analysis .json file with exptName: ' + str(param['Expt']['exptName']), verb, 2) 
    
    # Loop over all .dat files in the experiment directory, summing repeats together.
    file=[]
    dat=[]
    
    tmcx.util.verb('Loading .jdat file...', verb, 2)  
    dat = jdata.load(jdatFilePath) # Notice this isnt yet implemented for mulitple jdat files
    tmcx.util.verb('Loaded .jdat file: '+ jdatFilePath, verb, 1)
    
    return dat, param

def jcfg_json(json_FilePath: str, verb: float):
    """Takes in an json directory path, reads in JSON, returns the dictionary.

    Args:
        json_FilePath (str): Path to folder with jdat data file
        verb (float): verboseness level
    """        
    
    tmcx.util.verb('Loading .json file...', verb, 2)  
    dat = jdata.load(json_FilePath) # Notice this isnt yet implemented for mulitple jdat files
    tmcx.util.verb('Loaded .jdat file: '+ json_FilePath, verb, 1)
    
    return dat

def load_results_jsons(main_folder_path: str, verb: float = 1):
    """Function to load multiple simulation state results that are stored in a main folder

    Args:
        main_folder_path (str): 
        verb (float): verboseness level
    """

    results_data = []
    # Loop over all items in the specified folder
    for item in os.listdir(main_folder_path):
        item_path = os.path.join(main_folder_path, item)
        
        # Check if the item is a directory
        if os.path.isdir(item_path):
            # Loop over files in the subfolder
            for file in os.listdir(item_path):
                # Check if the file ends with 'jcfg_results.json'
                if file.endswith('jcfg_results.json'):
                    file_path = os.path.join(item_path, file)
                    tmcx.util.verb(f"Found file: {file_path}",verb, 2)

                    results_json = tmcx.impo.jdat_json(file_path, verb=verb)
                    results_data.append(results_json)

    return results_data

def expt_results_paths(expt_folder: str, verb: float = 1, endsWith='jcfg_results.json'):
    """ Function to return a list of all the paths to the results json files in the experiment folder"""
    
    results_paths = []
    for state_folder in os.listdir(expt_folder):
        state_path = os.path.join(expt_folder, state_folder)
        if os.path.isdir(state_path):
            for file in os.listdir(state_path):
                if file.endswith(endsWith):
                    file_path = os.path.join(state_path, file)
                    tmcx.util.verb(f"Found file: {file_path}",verb, 2)
                    results_paths.append(file_path)
    return results_paths

def expt_results(expt_folder: str, verb: float = 1):
    """ Function to load all the results json files in the experiment folder"""
    
    results_data = []
    results_paths = expt_results_paths(expt_folder, verb)
    for result_path in results_paths:
        results_data.append(jdat_json(result_path, verb=verb))
    
    return results_data

def svmc_vol(jcfg: dict):
    """Imports a SVMC volume file as defined in jcfg volume path.

    Args:
        jcfg (dict): JSON dictionary with jcfg.VolumeFIle

    Returns:
        vol_svmc (numpy array): _description_
    """
    
    vol_svmc=np.fromfile(jcfg['VolumeFile'], dtype='uint8') #np.uint8)
    tmcx.util.verb('Loaded svmc volume: '+jcfg['VolumeFile']+'(fn not finished)', jcfg["verb"], 1)
    
    return vol_svmc


def blood_spectra():
    """
    Import optical properties from file embedded in tmcx

    @return: DataFrame with all optical properties of blood at various oxygen saturation levels.
    """
    bld_spectra = pd.read_csv(r'mcx\Resources\Spectra\absorption_coefficients_whole_blood_saturation2.txt', sep="\t")
    
    return bld_spectra


def jcfg_json(json_path: str | Path):
    """Import a JSON file into a python dict type

    Args:
        json_path (str): path to JSON file

    Returns:
        jcfg (dict): dict with contents of JSON file, including an entry to trace lineage of dict jcfg['Expt']['parentJSON']
    """
    json_path=Path(json_path)
    jcfg=jdata.load(str(json_path))
    if 'Expt' not in jcfg:
        jcfg['Expt'] = {}
    jcfg['Expt']['parentJSON'] = str(json_path)
    
    return jcfg


def json_shapes(json_path: str | Path):
    """Import a JSON file into a python dict type

    Args:
        json_path (str): path to JSON file

    Returns:
        shapes (dict): dict with contents of JSON file, 
        set mcfg.shapes = this output in main file.
    """

    json_path=Path(json_path)
    shapes=jdata.load(json_path)
    # jcfg['Expt']['parentJSON']=json_path
    return shapes


def incident_spectrum(jcfg: dict):
    # Make sure the resources_path is changed correctly for different operating systems: windows vs linux
    if 'RESOURCES_PATH' in os.environ:
        RESOURCES_PATH = Path(os.getenv("RESOURCES_PATH", default="Resources/Spectra"))
    else:
        os_name = platform.system()
        if os_name == "Linux":
            RESOURCES_PATH="/home/ra-retinalimaging/dev/mcx/Resources/Spectra"
        else:
            RESOURCES_PATH= "C:\dev\mcx\Resources\Spectra"

    source_file = jcfg['Optode']['Source']['sourceSpectra'][jcfg['Optode']['Source']['spectProfile']]
    source_file = source_file.replace("\\", "/")
    file_path = Path(RESOURCES_PATH) / source_file
    
    """Tijmen: Added if/else clause
    The spectra for the 5 LEDs used in determine are all in a folder called determine, within the main folder containing all the spectra. 
    These 5 files have a different structure and thus need to be processed slightly different.
    The if part filters out all the cases where the file path contains determine and then processes them appropriately.
    The else part processes all other spectrum files as before.
    """
    if 'determine' in source_file:
        wls=np.arange(jcfg['Optode']['Source']['lam0'],jcfg['Optode']['Source']['lamN'],jcfg['Optode']['Source']['dlam'])
        tmcx.util.verb(f"Imported incident spectrum from: {file_path}", jcfg['Expt']['verb'], 1)
        tmcx.util.verb(f"Interpolating spectrum from {jcfg['Optode']['Source']['lam0']} to {jcfg['Optode']['Source']['lamN']} stepping {jcfg['Optode']['Source']['dlam']}", jcfg['Expt']['verb'], 3)
        
        inc_spectra = pd.read_excel(file_path,header=None,names=['Wavelength', 'intensity'],skiprows=6)

        lam = np.array(inc_spectra.iloc[:, 0])
        filt_spectra_interp = pd.DataFrame()
        filt_spectra_interp.insert(0, "Wavelength (nm)", wls)
        colName = inc_spectra.iloc[:,0]
        out = (np.interp(wls, lam, np.array(inc_spectra.iloc[:,1]), left=0, right=0))
        filt_spectra_interp.insert(1,os.path.basename(file_path), out)
        jcfg["Optode"]["Source"]["Spectrum"]=filt_spectra_interp
        
    else:                               
        wls=np.arange(jcfg['Optode']['Source']['lam0'],jcfg['Optode']['Source']['lamN'],jcfg['Optode']['Source']['dlam'])
        tmcx.util.verb(f"Imported incident spectrum from: {file_path}", jcfg['Expt']['verb'], 1)
        tmcx.util.verb(f"Interpolating spectrum from {jcfg['Optode']['Source']['lam0']} to {jcfg['Optode']['Source']['lamN']} stepping {jcfg['Optode']['Source']['dlam']}", jcfg['Expt']['verb'], 3)
        
        inc_spectra = pd.read_csv(file_path, sep="\,", decimal='.', header=2, engine='python')

        lam = np.array(inc_spectra.iloc[:, 0])
        filt_spectra_interp = pd.DataFrame()
        filt_spectra_interp.insert(0, "Wavelength (nm)", wls)
        colName = inc_spectra.iloc[:,0]
        out = (np.interp(wls, lam, np.array(inc_spectra.iloc[:,1]), left=0, right=0))
        filt_spectra_interp.insert(1,os.path.basename(file_path), out)
        jcfg["Optode"]["Source"]["Spectrum"]=filt_spectra_interp
    
    return jcfg
    

def  tiff_image(path_to_tiff: str):
    """import a tiff image

    Args:
        path_to_tiff (str): Path to image to import

    Returns:
        array: matrix of pixel data read from tiff
    """
    import tifffile as tiff

    try:
        with tiff.TiffFile(path_to_tiff) as tif:
            tiff_data = tif.asarray()
            return tiff_data
    except Exception as e:
        print(f"Error reading TIFF image: {e}")
        return None
    
def extracted_data(json_file):
    """ Takes data from https://plotdigitizer.com/app eported as a json format, parses it, sorts on X, and returns two lists with x and y

    Written 20241003 by MV and VZ aided with copilot
    
    Args:
        json_file (path): path to json file

    Returns:
        list, list : x_values, y_values
    """     
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    # Extract x and y values
    x_values = [float(item['x']) for item in data]
    y_values = [float(item['y']) for item in data]
    
    # Combine x and y values into a list of tuples and sort by x values
    combined = sorted(zip(x_values, y_values))
    
    # Separate the sorted x and y values
    sorted_x_values, sorted_y_values = zip(*combined)
    
    return list(sorted_x_values), list(sorted_y_values)