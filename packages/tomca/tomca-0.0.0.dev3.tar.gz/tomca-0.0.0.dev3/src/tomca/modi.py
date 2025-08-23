"""
functions which \b modify parameters  
"""
from Software import tmcx


def vol_bcs(cfg, vol):
    from Software import tmcx
    """ Applies boundary conditions to the volume, namely padding with 0 digit

    Args:
        cfg (_type_): _description_
        vol (_type_): _description_
    """

    if cfg['Vol']['zeroPadVol'][0]: 
        vol[0,:,:]=0
    if cfg['Vol']['zeroPadVol'][1]:  
        vol[:,0,:]=0
    if cfg['Vol']['zeroPadVol'][2]: 
        vol[:,:,0]=0
    if cfg['Vol']['zeroPadVol'][3]: 
        vol[-1,:,:]=0
    if cfg['Vol']['zeroPadVol'][4]: 
        vol[:,-1,:]=0
    if cfg['Vol']['zeroPadVol'][5]: 
        vol[:,:,-1]=0
    
    tmcx.util.verb('Modified volume boundary conditions', cfg['Expt']['verb'], 2)

    return(cfg, vol)

def mask_detected_photons(jcfg, resName='res', mask=None):
    """Masking function for detectors
    Checks if there exists a Mask
    The Mask should be a list that contains a sublists for each detector square.
    The sublists consist of:
        1. x position of center of the detector square
        2. y position of center of the detector square
        3. x size of detector square
        5. y size of detector square
    example for two detectors [[pos_x_1,pos_y_1,size_x_1,size_y_1], [pos_x_2,pos_y_2,size_x_2,size_y_2]]
    
    Added if/else clause; First the code checks whether a Mask exists, if not it will run as before. If it does exist it will use the mask for filtering the photons.
    the maked photons will be saved under jcfg[outName][...]; default for outName is res_replay
    """
    import numpy as np
    from Software.tmcx.util import verb
    from copy import deepcopy
        
    if resName not in jcfg:
        jcfg[resName]={}

    n_sim_det=len(jcfg[resName]['x'])
    
    # Start by saying we'll keep all photons from each constraint
    idxXMin, idxXMax, idxYMin, idxYMax, idxZMin, idxZMax, idxAcceptAngle = np.ones(n_sim_det), np.ones(n_sim_det), np.ones(n_sim_det), np.ones(n_sim_det), np.ones(n_sim_det), np.ones(n_sim_det), np.ones(n_sim_det)
    if mask is None:
        mask = []
    # If the Mask exists, find the indices of the photons that meet the constraint
    if mask != [] and mask != 'default':
        keep = []
        for detector in mask:
            loc_x, loc_y, size_x, size_y = detector
            idxXMin = (jcfg[resName]['x'][:, 0] > (loc_x - size_x/2)/jcfg['Domain']['LengthUnit'] -1)
            idxXMax = (jcfg[resName]['x'][:, 0] < (loc_x + size_x/2)/jcfg['Domain']['LengthUnit'] -1)
            idxYMin = (jcfg[resName]['x'][:, 1] > (loc_y - size_y/2)/jcfg['Domain']['LengthUnit'] -1)
            idxYMax = (jcfg[resName]['x'][:, 1] < (loc_y + size_y/2)/jcfg['Domain']['LengthUnit'] -1)
            
        #     keep.append(np.all(np.stack([idxXMin,idxXMax,idxYMin,idxYMax]), axis=0))
        # idxKeep = np.any(np.array(keep),axis=0)
    
    else:
        # If the constraint exists, find the indices of the photons that meet the constraint
        if 'xMin' in jcfg['Optode']['Detector']:
            idxXMin = jcfg[resName]['x'][:, 0] > jcfg['Optode']['Detector']['xMin']
        if 'xMax' in jcfg['Optode']['Detector']:
            idxXMax = jcfg[resName]['x'][:, 0] < jcfg['Optode']['Detector']['xMax']
        if 'yMin' in jcfg['Optode']['Detector']:
            idxYMin = jcfg[resName]['x'][:, 1] > jcfg['Optode']['Detector']['yMin']
        if 'yMax' in jcfg['Optode']['Detector']:
            idxYMax = jcfg[resName]['x'][:, 1] < jcfg['Optode']['Detector']['yMax']
        if 'zMin' in jcfg['Optode']['Detector']:
            idxZMin = jcfg[resName]['x'][:, 2] > jcfg['Optode']['Detector']['zMin']
        if 'zMax' in jcfg['Optode']['Detector']:
            idxZMax = jcfg[resName]['x'][:, 2] < jcfg['Optode']['Detector']['zMax']
            
    if "acceptAngle_deg" in jcfg['Optode']['Detector']:
        vz = np.array(jcfg[resName]['v'][:,2])
        # exclude unphysical numbers from rounding errors
        filtA = ((vz <= 1) & (vz >= -1))
        filtB = abs(vz) >= np.cos(jcfg['Optode']['Detector']['acceptAngle_deg']*np.pi/180)
        idxAcceptAngle = np.all(np.stack([filtA, filtB]), axis=0)

        # Find the indexes that meet all constraints
        idxKeep = np.all(np.stack([idxXMin, idxXMax, idxYMin, idxYMax, idxZMin, idxZMax, idxAcceptAngle]), axis=0)
    else:
        idxKeep = np.all(np.stack([idxXMin, idxXMax, idxYMin, idxYMax, idxZMin, idxZMax]), axis=0)
    
    # Create photon data that only includes the photons that meet all constraints
    if 'seeds' in jcfg[resName]:
        jcfg[resName]['seeds']  = jcfg[resName]['seeds'] [:, idxKeep]
    jcfg[resName]['detp'] = jcfg[resName]['detp'][:, idxKeep]
    nYf=sum(idxKeep)


    if 'd' in jcfg[resName]:
        jcfg[resName]['d'] = jcfg[resName]['d'][idxKeep,:]
    if 's' in jcfg[resName]:
        jcfg[resName]['s'] = jcfg[resName]['s'][idxKeep,:]
    if 'p' in jcfg[resName]:
        jcfg[resName]['p'] = jcfg[resName]['p'][idxKeep,:]
    if 'm' in jcfg[resName]:
        jcfg[resName]['m'] = jcfg[resName]['m'][idxKeep,:]
    if 'x' in jcfg[resName]:
        jcfg[resName]['x'] = jcfg[resName]['x'][idxKeep,:]
    if 'v' in jcfg[resName]:
        jcfg[resName]['v'] = jcfg[resName]['v'][idxKeep,:]
    if 'w' in jcfg[resName]:
        jcfg[resName]['w'] = jcfg[resName]['w'][idxKeep,:]
        
    if nYf!=n_sim_det:
        verb(f'Masked detected photons from {n_sim_det} to {nYf} seeds', jcfg['Expt']['verb'], 2)

    return jcfg

def combine_sims(jcfgs):

    ## Things to combine: 
    
    # flux or energy
    
    # IM
    
    # Detectors
    
    # Should we check whether the rest of the simulation matches? only changes in the source should be in the delta_cfg?
    jcfg0=jcfgs[0]
    jcfg1=jcfgs[1]
    differences, err = tmcx.util.compare_mcfg(jcfg0['mcfg'], jcfg1['mcfg'], verb=jcfg1['Expt']['verb'])
   
    if not err: 
        jcfg01={}
        jcfg01['0']=jcfg0
        jcfg01['1']=jcfg1
        jcfg01['res']={}
        jcfg01['res']['IM']=jcfg0['res']['IM']+jcfg1['res']['IM']
        if "flux" in jcfg0['res']:
            jcfg01['res']['flux']=jcfg0['res']['flux']+jcfg1['res']['flux']
        if 'doReplay' in jcfg0['Expt']:
            jcfg01['res_replay']['IM']=jcfg0['res_replay']['IM']+jcfg1['res_replay']['IM']
            if "flux" in jcfg0['res_replay']:
                jcfg01['res_replay']['flux']=jcfg0['res_replay']['flux']+jcfg1['res_replay']['flux']
            if "CalculateEnergy" in jcfg0['Session']: 
                jcfg01['res_replay']['EnergyPerMedia']=jcfg0['res_replay']['EnergyPerMedia']+jcfg1['res_replay']['EnergyPerMedia']
                jcfg01['res_replay']['MediaLabels']=jcfg0['res_replay']['MediaLabels']
                jcfg01['res_replay']['DetectorMeas']=jcfg0['res_replay']['DetectorMeas']+jcfg1['res_replay']['DetectorMeas']
        jcfg01['Vol']=jcfg0['Vol']
        jcfg01['Session']=jcfg0['Session']
        jcfg01['Forward']=jcfg0['Forward']
        jcfg01['Domain']=jcfg0['Domain']
        
def combine_n_sims(jcfgs):
    from copy import deepcopy
    
    if not jcfgs:
        raise ValueError("No configurations provided")
    
    combined_jcfg = deepcopy(jcfgs[0])
    for jcfg in jcfgs[1:]:

        combined_jcfg['res']['IM'] += jcfg['res']['IM']
        if "flux" in combined_jcfg['res']:
            combined_jcfg['res']['flux'] += jcfg['res']['flux']
        if 'doReplay' in combined_jcfg['Expt']:
            combined_jcfg['res_replay']['IM'] += jcfg['res_replay']['IM']
            if "flux" in combined_jcfg['res_replay']:
                combined_jcfg['res_replay']['flux'] += jcfg['res_replay']['flux']
            if jcfg['Session']['OutputType'] == 'energy':
                if "CalculateEnergy" in combined_jcfg['Session']:
                    for key, value in jcfg['res_replay']['EnergyPerMedia'].items():
                        if key in combined_jcfg['res_replay']['EnergyPerMedia']:
                            combined_jcfg['res_replay']['EnergyPerMedia'][key] += value
                        else:
                            combined_jcfg['res_replay']['EnergyPerMedia'][key] = value
                    combined_jcfg['res_replay']['DetectorMeas'] += jcfg['res_replay']['DetectorMeas']

    return combined_jcfg
        
        
        
        