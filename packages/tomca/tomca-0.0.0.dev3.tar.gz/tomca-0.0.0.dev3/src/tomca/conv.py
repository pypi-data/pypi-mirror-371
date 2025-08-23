"""
functions which \b convert between two types of data  
"""

import numpy as np 
from Software import tmcx


def json_to_mcx(jcfg):    
    """This function takes in a dict type jcfg (as defined by mcx), then creates mcfg configured for pmcx. 
    Take care of your volume before this step.  it's an input.
    This should only be called right before the pmcx run function; changes to the simulation should be done
    in the jmcx space so that it's tracked and written out properly.
    
    Adapted input definitions from mcx_command_option_cheatsheet.xlsx in mcx folder


    Args:
        jcfg (dict): follow the typical MCX JSON file pattern.
        vol (3Darray): Volume to simulate through
        verb (int): Feedback level (do you want to know missing keys?)

    Returns:
        mcfg (dict): configuration parameters to send to pmcx.run function.
    """
    
    import numpy as np 
    from Software import tmcx
    import jdata
    
    if "Expt" not in jcfg:
        jcfg['Expt']={}
    if "verb" not in jcfg['Expt']:
        jcfg['Expt']['verb']=2 # Default verb level, if not specified
    
    # Make a function to extract keys from dict with layers: 
    def getKey(cfg_t, defaultVal, *keys):
        for key in keys:
            try:
                cfg_t = cfg_t[key]
            except KeyError:
                warn=('Did not find ' + key +' key in json file.') # Using default: '+ str(defaultVal))
                tmcx.util.verb(warn, jcfg['Expt']['verb'], 3)
                return # Can return default here.
        return cfg_t
        
    mcfg = {}
    

    ## Domain ##
    #if tmpKey:=getKey(jcfg,'','Domain','VolumeFile') is not None:  
    if 'vol' in jcfg:
        mcfg['vol'] = jcfg['vol']

    if 'MediaFormat' in jcfg['Domain']:
        if jcfg['Domain']['MediaFormat'] =='svmc':
            if "vol_svmc" in jcfg:
                mcfg['vol']=jcfg['vol_svmc']
                del jcfg['vol_svmc']
        else:
            mcfg['vol'] = jcfg['vol']
       
    if (tmpKey:=getKey(jcfg,[0,0,0],'Domain','Dim')) is not None:
        mcfg['dim'] = tmpKey   
              
    #### Media properties need some array gymnastics
    for ii in np.arange(len(jcfg['Domain']['Media'])): # For every media entry
        tmp_mua=jcfg['Domain']['Media'][ii]['mua'] # extract the values only
        tmp_mus=jcfg['Domain']['Media'][ii]['mus']
        tmp_g=jcfg['Domain']['Media'][ii]['g']
        tmp_n=jcfg['Domain']['Media'][ii]['n']
        tmp=np.array([tmp_mua,tmp_mus,tmp_g,tmp_n])
        
        if ii>0:    
            mcfg['prop']=np.vstack((mcfg['prop'],tmp)) # stack it on the array we're building
        else:
            mcfg['prop']=tmp
            
    if (tmpKey:=getKey(jcfg,1,'Domain','OriginType')) is not None:
        mcfg['issrcfrom0']=tmpKey
    if (tmpKey:=getKey(jcfg,0.01, 'Domain','LengthUnit')) is not None:
        mcfg['unitinmm']=tmpKey
    if (tmpKey:=getKey(jcfg,[0,0,1,1], 'Domain','MediaFormat')) is not None:
        mcfg['mediabyte']=tmpKey
        
    if (tmpKey:=getKey(jcfg,{}, 'Shapes')) is not None:
        import jdata as jd
        mcfg['shapes']=jd.show({'Shapes':tmpKey}, {'string':True})
        
    ## Forward  
    if (tmpKey:=getKey(jcfg,0,'Forward','T0')) is not None:
        mcfg['tstart']=tmpKey
    if (tmpKey:=getKey(jcfg,5e-9,'Forward','T1')) is not None:
        mcfg['tend']=tmpKey
    if (tmpKey:=getKey(jcfg,5e-9,'Forward','Dt')) is not None:
        mcfg['tstep']=tmpKey
    if (tmpKey:=getKey(jcfg,1.38,'Forward','N0')) is not None:
        mcfg['nout']=tmpKey              
    
    ## Optode
    if (tmpKey:=getKey(jcfg,'pencil','Optode','Source','Type')) is not None:
        mcfg['srctype']=tmpKey
    if tmpKey == 'angleinvcdf':
            del mcfg['srctype']
    if (tmpKey:=getKey(jcfg,[0,0,0,0],'Optode','Source','Pos')) is not None:
        mcfg['srcpos']=tmpKey
    if (tmpKey:=getKey(jcfg,[0,0,1,0],'Optode','Source','Dir')) is not None:
        mcfg['srcdir']=tmpKey
    if (tmpKey:=getKey(jcfg,[0,0,0,0],'Optode','Source','Param1')) is not None:
        mcfg['srcparam1']=tmpKey
    if (tmpKey:=getKey(jcfg,[0,0,0,0],'Optode','Source','Param2')) is not None:
        mcfg['srcparam2']=tmpKey
    if (tmpKey:=getKey(jcfg,'','Optode','Source','Pattern')) is not None:
        mcfg['srcpattern']=tmpKey
    if 'Optode' in jcfg:
        if 'Source' in jcfg['Optode']:
            if 'angleinvcdf' in jcfg['Optode']['Source']:
                if (tmpKey:=getKey(jcfg,None,'Optode','Source','angleinvcdf')) is not None:
                    mcfg['angleinvcdf']=np.asarray(np.squeeze(tmpKey))
        
    tmpKey=np.array(getKey(jcfg,[0,0,0],'Optode','Detector','Pos'))
    tmpKey1=getKey(jcfg,0,'Optode','Detector','R')
    if (tmpKey1) is not None:
        mcfg['detpos']=np.append(tmpKey,float(tmpKey1)).tolist()
    
    # Session
    ## MC Settings
    if (tmpKey:=getKey(jcfg,1e7,'Session','Photons')) is not None:
        mcfg['nphoton']=tmpKey
    if (tmpKey:=getKey(jcfg,1e7,'Session','Repeat')) is not None:
        mcfg['respin']=tmpKey
    if (tmpKey:=getKey(jcfg,1,'Session','DoMismatch')) is not None:
        mcfg['isreflect']=tmpKey
    if (tmpKey:=getKey(jcfg,'______000000','Session','BCFlags')) is not None:
        mcfg['bc']=tmpKey

    if (tmpKey:=getKey(jcfg,1,'Session','DoNormalize')) is not None:
        mcfg['isnormalize']=tmpKey
    if (tmpKey:=getKey(jcfg,0,'Session','RNGSeed')) is not None:
        mcfg['seed']=tmpKey
    if (tmpKey:=getKey(jcfg,1,'Session','DoSpecular')) is not None:
        mcfg['isspecular']=tmpKey
    if (tmpKey:=getKey(jcfg,1e8,'Session','maxdetphoton')) is not None:
        mcfg['maxdetphoton']=tmpKey
    
    ## GPU Settings
    if (tmpKey:= getKey(jcfg,1,'Session','DoAutoThread')) is not None:
        mcfg['autopilot']=tmpKey

    ## Output Settings
    if (tmpKey:=getKey(jcfg,'X','Session','OutputType')) is not None:
        mcfg['outputtype']=tmpKey
    if (tmpKey:=getKey(jcfg,'DP','Session','SaveDataMask')) is not None:
        mcfg['savedetflag']=tmpKey
    if (tmpKey:=getKey(jcfg,'0','Session','DoSaveExit')) is not None:
        mcfg['issaveexit']=tmpKey
    if (tmpKey:=getKey(jcfg,'P','Session','DebugFlag')) is not None:
        mcfg['debuglevel']=tmpKey
    if (tmpKey:=getKey(jcfg,'','Session','RootPath')) is not None:
        mcfg['root']=tmpKey
    if (tmpKey:=getKey(jcfg,'','Session','DoPartialPath')) is not None:
        mcfg['issavedet']=tmpKey
    if (tmpKey:=getKey(jcfg,0,'Session','DoSaveSeed')) is not None:
        mcfg['issaveseed']=tmpKey
    
    # Custom
    mcfg['verb']=jcfg['Expt']['verb']
    
    tmcx.util.verb('Converted jcfg to mcfg to simulate '+ str(mcfg['nphoton']) + ' photons', jcfg['Expt']['verb'], 2)
    
    jcfg['mcfg'] =mcfg
    
    return jcfg

def vol_svmc(jcfg, engine = 'octave', smoothing=1):
    """Uses a bridge to run the SVMC algorithm.  

    Args:
        vol (_type_): volume created in python

    Returns:
        _type_: SVMC smoothed volume
    """

    from Software import tmcx
    import numpy as np
    
    if "Vol" in jcfg:
        if "useShapes" in jcfg['Vol']:
            if jcfg['Vol']['useShapes']==1:
                if "MediaFormat" in jcfg['Domain']:
                    if jcfg['Domain']['MediaFormat']=="svmc":
                        del jcfg['Domain']['MediaFormat']
                        
    volHash=tmcx.util.hash_vol(jcfg)
    if "Vol" not in jcfg:
        jcfg['Vol']={}

    jcfg['Vol']['hash_sqpx'] = volHash
    
    if "MediaFormat" in jcfg['Domain']:
        if jcfg['Domain']['MediaFormat']!="svmc":
            del jcfg['Domain']['MediaFormat']
        else:
            
            # # extract relevant parameters from jcfg; this is replaced with a hash of the volume directly.
            # # This should create the jcfg_vol dict which describes every parameter used to generate the indexes volume
            # jcfg_vol=jcfg['Vol']
            # jcfg_vol['Domain']={}
            # jcfg_vol['Domain']['LengthUnit']=jcfg['Domain']['LengthUnit']
            # jcfg_vol['Domain']['Media']=[]
            # for medium in enumerate(jcfg['Domain']['Media']):
            #     if 'dZ' in medium[1]:
            #         jcfg_vol['Domain']['Media'].append({str(medium[0]) : { 'dZ' : medium[1]['dZ']}})
                    
            # Create a hash of the volume directly

            
            import os
            from path import Path
            # Check if save location has volume with this hash
            if os.name == "posix":
                # Linux
                try:
                    results_dir = Path(jcfg['Expt']['dirResults'][0])
                except:
                    pass
            else:
                # Windows
                try:
                    results_dir = Path(jcfg['Expt']['dirResults'][1])
                except: 
                    results_dir = Path(r'D:\MonteCarloData\Results_Tmp')
            
            
            # Check if there is a volume with the name "vol_"+results_dir+".pkl" in results_dir
            foldername = "volumes"
            filename = "vol_" + volHash + ".pkl"
            filepath = os.path.join(results_dir, foldername, filename)

            if os.path.isfile(filepath):
                # load the volume and update the jcfg with the volume being used
                tmcx.util.verb('Match found for smoothed volume, loading hash : '+ volHash, jcfg['Expt']['verb'], 1)
                jcfg['vol'] = tmcx.util.pickle_in(filepath)
                if 'Vol' in jcfg:
                    pass
                else: 
                    jcfg['Vol']={}
                jcfg['Vol']['hashFile'] = filepath
                
                jcfg['Vol']['svmc'] = int(1)
                jcfg['Vol']['hash_svmc'] = tmcx.util.hash_vol(jcfg)
                
            else:
                
                tmcx.util.verb('No match found for smoothed volume hash : '+ volHash, jcfg['Expt']['verb'], 1)

                # Preprocess volume for SVMC
                vol=jcfg['vol'].copy()
                # if engine is defined in model file, use that, otherwise use octave
                if "smoothingEngine" in jcfg['Domain']:
                    engine = jcfg['Domain']['smoothingEngine']

                # Start engine
                if engine == 'matlab':
                    import matlab.engine
                    eng = matlab.engine.start_matlab()
                    vol=vol.reshape(vol.shape,order='F')
                    tmcx.util.verb('Reshaped python volume for MATLAB', jcfg['Expt']['verb'], 3)
                elif engine == 'octave':
                    import oct2py
                    eng = oct2py.Oct2Py()
                    # log version of octave running
                    jcfg['Domain']['smoothingEngine_version'] = eng.OCTAVE_VERSION()
                else:
                    tmcx.util.verb('Invalid engine defined', jcfg['Expt']['verb'], 0)
                tmcx.util.verb('Started '+ engine +' engine for SVMC conversion', jcfg['Expt']['verb'], 3)

                # Call SVMC
                svmcvol = np.array(eng.mcxsvmc_wrapper(vol,'smoothing',smoothing))
                tmcx.util.verb('Finished importing smoothed volume into Python', jcfg['Expt']['verb'], 2)

                if engine == 'matlab':
                    # Exit MATLAB
                    jcfg['vol']=np.int8(svmcvol.reshape(svmcvol.shape,order='C')).copy()
                    tmcx.util.verb('Reshaped volume for Python', jcfg['Expt']['verb'], 3)
                    eng.quit()
                else:
                    jcfg['vol']=np.int8(svmcvol).copy()
                    eng.exit()
                    # Verify octave instance is closed
                    for ij in range(10): # Try closing up to 10 times
                        try:
                            eng.keys # Make call into Octave.  What it is doesnt really matter...
                        except oct2py.utils.Oct2PyError as e:
                            if "Session is closed" in str(e): # This is what we want.
                                tmcx.util.verb(f'Octave engine closed', jcfg['Expt']['verb'], 2)
                                break
                            else:
                                import time
                                tmcx.util.verb(f'Failed to close Octave engine after {ij} try.  Retrying...', jcfg['Expt']['verb'], 1)
                                eng.exit()
                                time.sleep(1)
                        else:
                            break
                    else:
                        raise RuntimeError("Failed to close octave engine after 10 tries")

                    tmcx.util.verb('Reimported volume to Python', jcfg['Expt']['verb'], 3)
                try:
                    jcfg['Domain']['MediaFormat']="svmc"
                except KeyError:
                    tmcx.util.verb('Did not find MediaFormat in JSON format.  Adding in jcfg.', jcfg['Expt']['verb'], 1)
                    jcfg['mediabyte'] = "svmc"
                tmcx.util.verb('Smoothed volume with svmc', jcfg['Expt']['verb'], 1)

                # Save volume to results directory and update the jcfg with the volume being used
                tmcx.util.pickle_out(jcfg['vol'], filepath)
                if "Vol" not in jcfg:
                    jcfg['Vol']={}
                jcfg['Vol']['hashFile'] = filepath
                tmcx.util.verb('Saving smoothed volume to volume library with hash : '+ volHash, jcfg['Expt']['verb'], 1)
            
                jcfg['Vol']['svmcDims']=str(jcfg['vol'].shape) 
                jcfg['Vol']['svmc'] = int(1)
                jcfg['Vol']['hash_svmc'] = tmcx.util.hash_vol(jcfg)
    else:
        tmcx.util.verb('svmc evaluation skipped, Toggle with jcfg[\'Domain\'][\'MediaFormat\']=\"svmc\"', jcfg['Expt']['verb'], 3)
        jcfg['Vol']['svmc'] = int(0)
    
    return jcfg

def mcfg_dept_to_dict_MCX_style(res, savedetflag):
    """Converts the res results of pmcx into a dict with useful naming

        1 D output detector ID (1)
        2 S output partial scat. even counts (#media)
        4 P output partial path-lengths (#media)
        8 M output momentum transfer (#media)
        16 X output exit position (3)
        32 V output exit direction (3)
        64 W output initial weight (1)

    Args:
        res (dict): Results directly from tmcx.run or pmcx.run
        savedetflag (str): the flag(s) for pmcx on which photondata to save

    Returns:
        res_new (dict): res dictionary parsed with d (1), s (N), p (N), m (N), x (3), v (3), w (1) entries.
                    and an traj key if traj data in input res
    """    
    import numpy as np
    
    
    nCols = res['detp'].shape[0]
    
    fixedCols = 0
    if 'd' in savedetflag: fixedCols+= 1
    if 'x' in savedetflag: fixedCols+= 3
    if 'v' in savedetflag: fixedCols+= 3
    if 'w' in savedetflag: fixedCols+= 1
    
    nMediaDepCols=0
    if 's' in savedetflag: nMediaDepCols+= 1
    if 'p' in savedetflag: nMediaDepCols+= 1
    if 'm' in savedetflag: nMediaDepCols+= 1
    
    nMediaIndexes = np.int8((nCols-(fixedCols))/nMediaDepCols)

    strout = ''
    endIdx = 0
    detp = {}
    if 'd' in savedetflag:
        detp['detid']=res['detp'][0,:]
        endIdx+=1
        strout+=' d'
    if 's' in savedetflag:
        detp['nscat']=res['detp'][endIdx:endIdx+nMediaIndexes,:].T
        endIdx+=nMediaIndexes
        strout+=' s'
    if 'p' in savedetflag:
        detp['ppath']=res['detp'][endIdx:endIdx+nMediaIndexes,:].T # ppath
        endIdx+=nMediaIndexes
        strout+=' p'
    if 'm' in savedetflag:
        detp['mom']=res['detp'][endIdx:endIdx+nMediaIndexes,:]
        endIdx+=nMediaIndexes
        strout+=' m'
    if 'x' in savedetflag:
        detp['p']=res['detp'][endIdx:endIdx+3,:].T
        endIdx+=3
        strout+=' x'
    if 'v' in savedetflag:
        detp['v']=res['detp'][endIdx:endIdx+3,:].T
        endIdx+=3
        strout+=' v'
    if 'w' in savedetflag:
        detp['w0']=res['detp'][endIdx:endIdx+1,:]
        endIdx+=1
        strout+=' w'
    
    if 'traj' in res.keys():
        ## different key labels between mcx methods
        ## in mcx executable keys are ['photonid', 'p', 'w0']
        ## in pmcx.mcxlab() keys are dict_keys(['pos', 'id', 'data'])
        from struct import unpack
        ##### extract the scatter (traj) data from res output of tmcx.run or pmcx.run
        
        ### output is c struct that needs to be converted to integers in the photon id case (other cases are floats which numpy automatically assumes I guess)
        structAr = np.asarray(res['traj'][0], order = 'C')
        lenstr = str(len(structAr))
        traj_id =  np.array( unpack( lenstr + 'I', structAr))
        
        ### output is c struct that needs to be converted to floats which seems to be the standard behaviour of numpy
        traj_pos = res['traj'][1:4].T
        traj_weight = res['traj'][4]
        traj_reserved = res['traj'][5]
        
        traj = {'id': traj_id, 'pos': traj_pos, 'w': traj_weight, 'reserved': traj_reserved}
        
        traj_order(traj)
        res_new = {'detp': detp, 'traj': traj}
        return res_new
        
    
    
    res_new = {'detp': detp}
    return res_new

def mcfg_detp_to_dict(res, savedetflag):
    """Converts the res results of pmcx into a dict with useful naming
    
        1 D output detector ID (1)
        2 S output partial scat. even counts (#media)
        4 P output partial path-lengths (#media)
        8 M output momentum transfer (#media)
        16 X output exit position (3)
        32 V output exit direction (3)
        64 W output initial weight (1)

    Args:
        res (dict): Results directly from tmcx.run or pmcx.run
        savedetflag (str): the flag(s) for pmcx on which photondata to save

    Returns:
        res_new (dict): res dictionary parsed with d (1), s (N), p (N), m (N), x (3), v (3), w (1) entries.
                    and an traj key if traj data in input res
    """    
    import numpy as np
    
    
    nCols = res['detp'].shape[0]
    
    fixedCols = 0
    if 'd' in savedetflag: fixedCols+= 1
    if 'x' in savedetflag: fixedCols+= 3
    if 'v' in savedetflag: fixedCols+= 3
    if 'w' in savedetflag: fixedCols+= 1
    
    nMediaDepCols=0
    if 's' in savedetflag: nMediaDepCols+= 1
    if 'p' in savedetflag: nMediaDepCols+= 1
    if 'm' in savedetflag: nMediaDepCols+= 1
    
    nMediaIndexes = np.int8((nCols-(fixedCols))/nMediaDepCols)

    strout = ''
    endIdx = 0
    detp = {}
    if 'd' in savedetflag:
        detp['d']=res['detp'][0,:]
        endIdx+=1
        strout+=' d'
    if 's' in savedetflag:
        detp['s']=res['detp'][endIdx:endIdx+nMediaIndexes,:].T
        endIdx+=nMediaIndexes
        strout+=' s'
    if 'p' in savedetflag:
        detp['p']=res['detp'][endIdx:endIdx+nMediaIndexes,:].T # ppath
        endIdx+=nMediaIndexes
        strout+=' p'
    if 'm' in savedetflag:
        detp['m']=res['detp'][endIdx:endIdx+nMediaIndexes,:]
        endIdx+=nMediaIndexes
        strout+=' m'
    if 'x' in savedetflag:
        detp['x']=res['detp'][endIdx:endIdx+3,:].T
        endIdx+=3
        strout+=' x'
    if 'v' in savedetflag:
        detp['v']=res['detp'][endIdx:endIdx+3,:].T
        endIdx+=3
        strout+=' v'
    if 'w' in savedetflag:
        detp['w']=res['detp'][endIdx:endIdx+1,:]
        endIdx+=1
        strout+=' w'
    
    if 'traj' in res.keys():
        from struct import unpack
        ##### extract the scatter (traj) data from res output of tmcx.run or pmcx.run
        
        ### output is c struct that needs to be converted to integers in the photon id case (other cases are floats which numpy automatically assumes I guess)
        structAr = np.asarray(res['traj'][0], order = 'C')
        lenstr = str(len(structAr))
        traj_id =  np.array( unpack( lenstr + 'I', structAr))
        
        ### output is c struct that needs to be converted to floats which seems to be the standard behaviour of numpy
        traj_pos = res['traj'][1:4].T
        traj_weight = res['traj'][4]
        traj_reserved = res['traj'][5]
        
        traj = {'id': traj_id, 'pos': traj_pos, 'w': traj_weight, 'reserved': traj_reserved}
        
        traj_order(traj)
        res_new = {'detp': detp, 'traj': traj}
        return res_new
        
    
    
    res_new = {'detp': detp}
    return res_new

def savedetflags_to_dict_MCX_style(jcfg, isReplay='res'):
    # TODO: "add replay functionality as an input option  with isReplay"
    """Converts the res results of pmcx into a dict with useful naming
    
        1 D output detector ID (1)
        2 S output partial scat. even counts (#media)
        4 P output partial path-lengths (#media)
        8 M output momentum transfer (#media)
        16 X output exit position (3)
        32 V output exit direction (3)
        64 W output initial weight (1)

    Args:
        res (dict): Results directly from tmcx.run

    Returns:
        res (dict): res dictionary parsed with d (1), s (N), p (N), m (N), x (3), v (3), w (1) entries.  
    """    
    import numpy as np
    from Software import tmcx
    
    nCols=jcfg['res']['detp'].shape[0]
    
    fixedCols=0
    if 'd' in jcfg['Session']['SaveDataMask']: fixedCols+= 1
    if 'x' in jcfg['Session']['SaveDataMask']: fixedCols+= 3
    if 'v' in jcfg['Session']['SaveDataMask']: fixedCols+= 3
    if 'w' in jcfg['Session']['SaveDataMask']: fixedCols+= 1
    
    nMediaDepCols=0
    if 's' in jcfg['Session']['SaveDataMask']: nMediaDepCols+= 1
    if 'p' in jcfg['Session']['SaveDataMask']: nMediaDepCols+= 1
    if 'm' in jcfg['Session']['SaveDataMask']: nMediaDepCols+= 1
    
    nMediaIndexes=np.int8((nCols-(fixedCols))/nMediaDepCols)

    strout=''
    endIdx=0
    if 'd' in jcfg['Session']['SaveDataMask']:
        jcfg['res']['detid']=jcfg['res']['detp'][0,:]
        endIdx+=1
        strout+=' d'
    if 's' in jcfg['Session']['SaveDataMask']:
        jcfg['res']['nscat']=jcfg['res']['detp'][endIdx:endIdx+nMediaIndexes,:].T
        endIdx+=nMediaIndexes
        strout+=' s'
    if 'p' in jcfg['Session']['SaveDataMask']:
        jcfg['res']['ppath']=jcfg['res']['detp'][endIdx:endIdx+nMediaIndexes,:].T # ppath
        endIdx+=nMediaIndexes
        strout+=' p'
    if 'm' in jcfg['Session']['SaveDataMask']:
        jcfg['res']['mom']=jcfg['res']['detp'][endIdx:endIdx+nMediaIndexes,:]
        endIdx+=nMediaIndexes
        strout+=' m'
    if 'x' in jcfg['Session']['SaveDataMask']:
        jcfg['res']['p']=jcfg['res']['detp'][endIdx:endIdx+3,:].T
        endIdx+=3
        strout+=' x'
    if 'v' in jcfg['Session']['SaveDataMask']:
        jcfg['res']['v']=jcfg['res']['detp'][endIdx:endIdx+3,:].T
        endIdx+=3
        strout+=' v'
    if 'w' in jcfg['Session']['SaveDataMask']:
        jcfg['res']['w0']=jcfg['res']['detp'][endIdx:endIdx+1,:]
        endIdx+=1
        strout+=' w'
    
    if 'traj' in jcfg['res'].keys():
        ## different key labels between mcx methods
        ## in mcx executable keys are ['photonid', 'p', 'w0']
        ## in pmcx.mcxlab() keys are dict_keys(['pos', 'id', 'data'])
        from struct import unpack
        ##### extract the scatter (traj) data from res_replay
        
        ### output is c struct that needs to be converted to integers in the photon id case (other cases are floats which numpy automatically assumes I guess)
        structAr = np.asarray(jcfg['res']['traj'][0], order = 'C')
        lenstr = str(len(structAr))
        traj_id =  np.array( unpack( lenstr + 'I', structAr))
        
        ### output is c struct that needs to be converted to floats which seems to be the standard behaviour of numpy
        traj_pos = jcfg['res']['traj'][1:4].T
        traj_weight = jcfg['res']['traj'][4]
        traj_reserved = jcfg['res']['traj'][5]
        
        traj = {'id': traj_id, 'pos': traj_pos, 'w': traj_weight, 'reserved': traj_reserved}
        
        # Update traj to add two keys for sorted Traj;     'traj_posSort', 'traj_idStart'
        traj=traj_order(traj)
        
        jcfg['res']['traj'] = traj
        #return detp, traj
        
        traj_order(traj)
    
    tmcx.util.verb(f'Found {nMediaIndexes} media indexes in results. Parsed into'+strout, jcfg['Expt']['verb'], 2)

    return jcfg

def savedetflags_to_dict(jcfg, resName='res'):
    # TODO: "add replay functionality as an input option  with isReplay"
    """Converts the res results of pmcx into a dict with useful naming
    
        1 D output detector ID (1)
        2 S output partial scat. even counts (#media)
        4 P output partial path-lengths (#media)
        8 M output momentum transfer (#media)
        16 X output exit position (3)
        32 V output exit direction (3)
        64 W output initial weight (1)

    Args:
        res (dict): Results directly from tmcx.run

    Returns:
        res (dict): res dictionary parsed with d (1), s (N), p (N), m (N), x (3), v (3), w (1) entries.  
    """    
    import numpy as np
    from Software import tmcx
    
    nCols=jcfg[resName]['detp'].shape[0]
    
    fixedCols=0
    if 'd' in jcfg['Session']['SaveDataMask']: fixedCols+= 1
    if 'x' in jcfg['Session']['SaveDataMask']: fixedCols+= 3
    if 'v' in jcfg['Session']['SaveDataMask']: fixedCols+= 3
    if 'w' in jcfg['Session']['SaveDataMask']: fixedCols+= 1
    
    nMediaDepCols=0
    if 's' in jcfg['Session']['SaveDataMask']: nMediaDepCols+= 1
    if 'p' in jcfg['Session']['SaveDataMask']: nMediaDepCols+= 1
    if 'm' in jcfg['Session']['SaveDataMask']: nMediaDepCols+= 1
    
    nMediaIndexes=np.int8((nCols-(fixedCols))/nMediaDepCols)

    strout=''
    endIdx=0
    if 'd' in jcfg['Session']['SaveDataMask']:
        jcfg[resName]['d']=jcfg[resName]['detp'][0,:]
        endIdx+=1
        strout+=' d'
    if 's' in jcfg['Session']['SaveDataMask']:
        jcfg[resName]['s']=jcfg[resName]['detp'][endIdx:endIdx+nMediaIndexes,:].T
        endIdx+=nMediaIndexes
        strout+=' s'
    if 'p' in jcfg['Session']['SaveDataMask']:
        jcfg[resName]['p']=jcfg[resName]['detp'][endIdx:endIdx+nMediaIndexes,:].T # ppath
        endIdx+=nMediaIndexes
        strout+=' p'
    if 'm' in jcfg['Session']['SaveDataMask']:
        jcfg[resName]['m']=jcfg[resName]['detp'][endIdx:endIdx+nMediaIndexes,:]
        endIdx+=nMediaIndexes
        strout+=' m'
    if 'x' in jcfg['Session']['SaveDataMask']:
        jcfg[resName]['x']=jcfg[resName]['detp'][endIdx:endIdx+3,:].T
        endIdx+=3
        strout+=' x'
    if 'v' in jcfg['Session']['SaveDataMask']:
        jcfg[resName]['v']=jcfg[resName]['detp'][endIdx:endIdx+3,:].T
        endIdx+=3
        strout+=' v'
    if 'w' in jcfg['Session']['SaveDataMask']:
        jcfg[resName]['w']=jcfg[resName]['detp'][endIdx:endIdx+1,:]
        endIdx+=1
        strout+=' w'
    
    if 'traj' in jcfg[resName].keys():
        from struct import unpack


        ##### extract the scatter (traj) data from res_replay
        
        ### output is c struct that needs to be converted to integers in the photon id case (other cases are floats which numpy automatically assumes I guess)
        structAr = np.asarray(jcfg[resName]['traj'][0], order = 'C')
        lenstr = str(len(structAr))
        traj_id =  np.array( unpack( lenstr + 'I', structAr))
        
        ### output is c struct that needs to be converted to floats which seems to be the standard behaviour of numpy
        traj_pos = jcfg[resName]['traj'][1:4].T
        traj_weight = jcfg[resName]['traj'][4]
        traj_reserved = jcfg[resName]['traj'][5]
        
        traj = {'id': traj_id, 'pos': traj_pos, 'w': traj_weight, 'reserved': traj_reserved}
        
        # Update traj to add two keys for sorted Traj;     'traj_posSort', 'traj_idStart'
        traj=traj_order(traj)
        
        jcfg[resName]['traj'] = traj
        #return detp, traj
        
        traj_order(traj)
    
    tmcx.util.verb(f'Found {nMediaIndexes} media indexes in results. Parsed into'+strout, jcfg['Expt']['verb'], 2)

    return jcfg

def traj_order(traj:dict):
    """Sort the photon scatter events in traj on photon ID, within a photon ID the scatter positions are ordered in time.

    Args:
        traj (dict): _description_

    Returns:
        updated dict:
            'traj_posSort', 'traj_idStart' keys get new arrays
        
        traj_posSort: array_like
            events (source, scatter and termination positions, [x,y,z]) of each photon
            sorted in photon id ordere and within a photond id positions are ordered in time.
            So source, scatter1, scattere2, ...., termination.
        
        traj_idStart: array_like, int
            array of length number of photons plus 1. Value at index i returns the index of 
            traj_posSort that has the source postion of photon with photon id i.
            So traj_posSort[traj_idStart[photonid]] = source pos of photonid,
            traj_posSort[traj_idStart[photonid] + 1] = scatter1 of photonid.
            Last element of traj_idStart gives the final index of traj_posSort. So
            traj_posSort[traj_idStart[-1]] = traj_posSort[-1] = termination pos of last photon id.
    """

    #### Sort scatter data for easier access
    ### array to get the trajid sorted in photid order, the stable option to keep the order of identical values (photon id)
    indxsort = np.argsort(traj['id'], kind='stable')
    ### sort the other traj data in photon id order while keeping order between of equal photon id
    traj_posSort = traj['pos'][indxsort]
    
    ### construct array to find specific photon id in traj_posSort 
    ### get counts for each photonid (always also outputs array with the unique values of the array sorted)
    unqid, countid = np.unique(traj['id'], return_counts = True)
    ### get cummulative sum of counts so we know the number of events associated with each photon id
    cumcountid = np.cumsum(countid) ### So traj_posSort[cumcountid[photid - 1]] = first event of photid (launch position)
    
    ### include entry for photid = 0
    traj_idStart = np.zeros(len(cumcountid) + 1, dtype=int)
    traj_idStart[1:] = cumcountid ### So traj_posSort[cumcountid[photid]] = first event of photid (launch position)

    traj['traj_posSort'] = traj_posSort
    traj['traj_idStart'] = traj_idStart

    return traj

def get_nonDuplicates(arr):
    r"""Get mask for arr that removes all elements that occur muliple times

        Created assuming arr as an arry of positions (x,y,z). 
        So works for arrays [[x1,y1,z1],[x2,y2,z2], etc.] not tested for 
        anything more general.

        Parameters
        ----------
        arr : array_like
            array with shape = [i,j]
                   
        Returns
        -------
        NoDupMask: array_like
            Mask (indeces) that when used on arr creates an array containing only
            those values of arr that are without duplicates in arr.
        
    """
    Un, Indx, Count = np.unique(arr, return_index=True, return_counts=True, axis = 0)
    # OneOccur = Count == 1
    NoDupMask = Indx[Count == 1]
    
    return NoDupMask

def join_by_exitpos(arr1, arr2, dupCheck=True):
    r"""short description

        Find the indeces for arr1 and arr2 that will sort them into arrays with matching values
        (so np.all(arr1[indx1] == arr2[indx2] = True).

        Parameters
        ----------
        arr1 : array_like
            description
        arr2 : array_like
            description       
                 
        Returns
        -------
        .....: array_like
            
        
    """
    if dupCheck:
        ## Create arrays with only those values of the original array that occour only once
        NoDupMask1 = get_nonDuplicates(arr1)
        NoDupMask2 = get_nonDuplicates(arr2)
        arr1 = arr1[NoDupMask1]
        arr2 = arr2[NoDupMask2]
    
    ### needed to reconstruct individual arrays after concatenation
    nPhot1 = arr1.shape[0]
    ### concatenate the arrays so we can sort their identical positions next to eachother
    auxCon = np.concatenate((arr1, arr2))
    ### get indeces that will sort auxCon
    ### do the lex sort (first element to sort on at the end and last at the beginning)
    idx2sortAuxCon = np.lexsort(auxCon.T) ### rows are interpreted as sorting keys so transpose for columns

    ### sort the auxCon
    auxCon = auxCon[idx2sortAuxCon]

    ### check if adjecent elements in the sorted array are equal.
    flag = np.concatenate(([False], np.all(auxCon[1:] == auxCon[:-1], axis = 1))) ## False at the beginning for first element with last

    ### copy for if needed for debugging
    #flag1 = np.copy(flag)
    ### if either on the left or right is True that index has a match, if duplicates Trues with elements that have the same original array are possible
    flag[:-1] = flag[1:] + flag[:-1]

    ### get indeces of the unsorted auxCon array that gave true in our flag
    idxIn = idx2sortAuxCon[flag]

    ### get the corresponding indeces in the arrays we concatenated
    idx1 = idxIn[(idxIn < nPhot1 )] 
    idx2 = idxIn[(idxIn >= nPhot1 )] - nPhot1

    ### idx1 and 2 will be only the matching indeces and sorted in the same way
    ### to construct the matching arrays
    if dupCheck:
        return NoDupMask1[idx1], NoDupMask2[idx2]
    else:
        return idx1, idx2

if __name__ == '__main__':
    print("You hit play on the wrong script.  Please try again.")