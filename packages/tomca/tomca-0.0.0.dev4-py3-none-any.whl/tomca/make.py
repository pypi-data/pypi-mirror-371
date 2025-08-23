"""
functions which \b make something on the save disk, such as directories, files, etc.  
"""

from src import tomca
import numpy as np
from pathlib import Path
from datetime import datetime
import os
import sys
import shutil

def sim_easy():
    """Create a quick and easy simulation for testing, 60 vox3

    Returns:
        cfg: configuration 
    """
    import numpy as np
    
    # Simulation parameters taken from pmcx example code.
    cfg = {}
    cfg['nphoton'] = 3e6
    cfg['vol'] = np.ones([60, 60, 60], dtype='uint8')
    cfg['tstart'] = 0
    cfg['tend'] = 5e-9
    cfg['tstep'] = 5e-9
    cfg['srcpos'] = [30, 30, 0]
    cfg['srcdir'] = [0, 0, 1]
    cfg['prop'] = [[0, 0, 1, 1], [0.005, 1, 0.01, 1.37]]
    

    return cfg

def sim_retina():
    """ Builds cfg variable for default retina simulation
    
    Returns:
    cfg: configuration 
    """
    import jdata
    from pathlib import Path
     
    jsonFile=Path("C:\dev\tomca\src\tomca\resources\template_JSON\retina_default.json")
    cfg=jdata.load(jsonFile)
    cfg['Expt']['parentJSON']=str(jsonFile)
    
    return cfg

def dir_expt(jcfg:dict):
    
    # Current date and time for tagging entire experiment run
    now = datetime.now() 
    jcfg['Expt']['time']=now.strftime("%Y%m%d_%H%M%S")
    
    # Build save path
    dirExpt=str(jcfg['Expt']['time'])+'_'+jcfg['Expt']['exptName']
    # Determine the appropriate directory path based on the operating system

    if os.name == "posix":
        # Linux
        selected_dir = Path(jcfg['Expt']['dirResults'][0])
    else:
        # Windows
        selected_dir = Path(jcfg['Expt']['dirResults'][1])
    jcfg['Expt']['pathExpt'] = str(selected_dir / dirExpt)
    os.makedirs(jcfg['Expt']['pathExpt'], exist_ok=True)
    tomca.util.verb('Prepared experiment save path @ ' + jcfg['Expt']['pathExpt'], jcfg['Expt']['verb'], 0)
    
    return jcfg


def dir_state(jcfg:dict, post_build=0, append_str=""):
    """ This function builds the folder to the experiment path, and saves it in the jcfg variable.
    This is a folder where the data is saved for this model state.

    Returns:
    jcfg

    Altered:
    cfg['Custom']['time']
    cfg['Custom']['pathExpt']

    """

    if post_build == 1:
        pass
    else:
        # Current date and time for tagging entire experiment run
        now = datetime.now()
        jcfg['Expt']['time'] = now.strftime("%Y%m%d_%H%M%S")

    # Check if experiment save path is built
    if "pathExpt" not in jcfg['Expt']:
        dirExpt = str(jcfg['Expt']['time']) + '_' + jcfg['Expt']['exptName']
        jcfg['Expt']['pathExpt'] = str(Path(jcfg['Expt']['dirResults'],dirExpt))
        os.makedirs(jcfg['Expt']['pathExpt'], exist_ok=True)

    # Make state save path
    jcfg['Expt']['pathState'] = str(Path(jcfg['Expt']['pathExpt'], str(jcfg['Expt']['time'])+'_'+jcfg['Expt']['stateName']+append_str))
    os.makedirs(jcfg['Expt']['pathState'], exist_ok=True)

    # jcfg['Expt']['script_path'] = Path(sys.argv[0])
    # shutil.copy2(jcfg['Expt']['script_path'], jcfg['Expt']['pathState'])

    jcfg['Expt']['script_path'] = str(Path(sys.argv[0]))

    tomca.util.verb('Prepared state save path @ ' + jcfg['Expt']['pathState'], jcfg['Expt']['verb'], 1)

    return jcfg


def state_str(jcfg):
    """Create a string to describe the current state being run, for figures, descriptions, etc.

    Args:
        jcfg (dict): Full description of simulatiuon, at or after simulation

    Returns:
        jcfg: Same dict as input with added jcfg['Expt']['Str'] string.  Use in plot. 
    """
    
    def strBuilder(expStr, label, parentKey, key):
        # Formats string, testing if it exists first.
        if key in parentKey:
            expStr+="\n" + label+": "+ str(parentKey[key])    
        return expStr
    
    expStr=f"Expt name: {jcfg['Expt']['exptName']}"
    expStr+=f"\nState name: {jcfg['Expt']['stateName']}"
    expStr+=f"\nTime:{jcfg['Expt']['time']}"
    expStr+=f"\nParent JSON: {jcfg['Expt']['parentJSON']}"
    expStr=strBuilder(expStr, "Vol Dims", jcfg['Domain'] , 'Dim')
    expStr=strBuilder(expStr, "Vox Size", jcfg['Domain'] , 'LengthUnit')
    expStr=strBuilder(expStr, "Vol Fmt", jcfg['Domain'] , 'MediaFormat')
    if 'vessel' in jcfg['Vol']: expStr=strBuilder(expStr, "Vess Depth", jcfg['Vol']['vessel'] , 'topDepth')
    if 'vessel' in jcfg['Vol']: expStr=strBuilder(expStr, "Vess Rad", jcfg['Vol']['vessel'] , 'rVess')
    expStr=strBuilder(expStr, "Sim nPhot", jcfg['Session'] , 'Photons')
    #expStr=strBuilder(expStr, "props", jcfg['mcfg'] , 'prop') ## messy
    expStr+=f"\nSrc Type: {jcfg['Optode']['Source']['Type']}, Pos: {jcfg['Optode']['Source']['Pos']}, Dir: {jcfg['Optode']['Source']['Dir']}\n  P1:{jcfg['Optode']['Source']['Param1']}, P2:{jcfg['Optode']['Source']['Param2']}"
    expStr=strBuilder(expStr, "Spect Prof", jcfg['Optode']['Source'] , 'spectProfile')
    if 'Detector' in jcfg['Optode']:
        if 'Type' in jcfg['Optode']['Detector']:
            if jcfg['Optode']['Detector']['Type'] == 'bc_planes':
                expStr+=f"\nDet: {jcfg['Optode']['Detector']['Type']}, {jcfg['Optode']['Detector']['bc_planes']}"
            else:
                expStr+=f"\nDet: {jcfg['Optode']['Detector']['Type']}, {jcfg['Optode']['Detector']['Pos']}, {jcfg['Optode']['Detector']['R']}"
    jcfg['Expt']['Str']=expStr
        
    return jcfg


def sim_easyHyperboloid():
    """Create a simple simulation for testing backscattering with a hyperboloid source.
    
    Simple simulation with hyperboloid source on/in a homogeneous medium. Simulation
    saves the number of scatterings, partial paths, exitposition and exitdirection of
    all photons that exit through the z=0 surface (all backscattered photons).

    Returns:
    -------

    mcfg: pmcx dict
        python dictionary in pmcx style containing all the simulation parameters
        for a pmcx.run(mcfg), or a tomca.run(mcfg).
        
         
    """   
    Nx, Ny, Nz = 15, 15, 15 ## Simulation volume, number of voxels in each direction
    voxelsize = 0.1 ## mm
    inv_voxelsize = 1/voxelsize
    
    mua = 1e-5 ### 1/mm
    mus = 1.0  ### 1/mm
    g = 0.5
    n = 1.0
    
    zR = 160 * 1e-3 ## mm
    w0 = 6 * 1e-3  ## mm   
    
    ### the simulation config dictionary
    mcfg = {}
    mcfg['nphoton'] = 1e6
    mcfg['vol'] = np.ones([Nx, Ny, Nz], dtype='uint8') ### array with media type numbers of simulation volume
    mcfg['unitinmm'] = voxelsize
    mcfg['prop'] = [[0, 0, 1, 1], [mua, mus, g, n]]
    mcfg['tstart'] = 0
    mcfg['tend'] = 5e-9
    mcfg['tstep'] = 5e-9
    mcfg['seed'] = -1 ### -1; photon seeds depend on system clock
    
    ### beam source, focused Gaussian beam (surfaces of consant intensity are hyperboloids)
    mcfg['srctype'] = 'hyperboloid'
    mcfg['srcpos'] = [Nx/2, Ny/2, 0]
    mcfg['srcdir'] = [0, 0, 1, 0] ### along the x direction and 4th zero to prevent mcx from refocussing
    
    distFocusVox = Nz/2
    zRVox = inv_voxelsize * zR # in voxel units (voxelsize is in mm)
    w0Vox = inv_voxelsize * w0 # in voxel units (voxelsize is in mm)
    mcfg['srcparam1'] = [w0Vox, distFocusVox, zRVox, 0.0]
    
    
    ### pmcx detection parameters
    mcfg['bc'] = '______001000'        ### '_' means use standard Fresnel refraction or as defined at 'relfect'; 001000 for z=0 plane as detector
    mcfg['issavedet'] = 1              ### issavedet must be set to 1 or True in order to save detected photons
    mcfg['issrcfrom0'] = 1             ### set this flag to ensure src/det coordinates align with voxel space
    mcfg['savedetflag'] = 'spxv'       ### what photon data to save, full is 'dspmxvw'
    mcfg['maxdetphoton'] = 10000000    ### determines memory assignment for detected photon data
    
    return mcfg