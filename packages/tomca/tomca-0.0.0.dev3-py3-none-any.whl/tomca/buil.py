"""
Functions which \b build something for the simulation; volume, source, detector, ... .  
"""
import numpy as np
from Software import tmcx
import matplotlib.pyplot as plt

def vol_init(jcfg:dict):
    """Initialize a volume array based on the volume sizes described in the jcfg dict

    Args:
        jcfg (dict): configuration dictionary, used for sizes of x,y,z layers

    Returns:
        dict: jcfg with jcfg['vol'] key
    """    

    # find z depth of all layers described in volZ
    zVol = calc_vol_depth(jcfg)

    # Find number of voxels in each dimension
    xdimV = int(np.floor(jcfg['Vol']['volX']/jcfg['Domain']['LengthUnit']))
    ydimV = int(np.floor(jcfg['Vol']['volY']/jcfg['Domain']['LengthUnit']))
    zdimV = int(np.floor(zVol/jcfg['Domain']['LengthUnit']))
    jcfg['Domain']['Dim'] = [xdimV, ydimV, zdimV]

    jcfg['vol'] = np.ones([xdimV, ydimV, zdimV], dtype='uint8')
    if "useShapes" in jcfg['Vol']:
        if jcfg['Vol']['useShapes']==0:
            tmcx.util.verb("Initialized volume defined by voxels with dims " + str(jcfg['Domain']['Dim']), jcfg['Expt']['verb'], 1)
            if 'Shapes' in jcfg: 
                del jcfg['Shapes']
        else:
            jcfg['Domain']['Dim']=[xdimV, ydimV, zdimV]
            jcfg['Shapes'] = [{'Grid': {'Size': [xdimV, ydimV, zdimV]}, 'Tag': 0}]  # bounding box
            jcfg['Vol']['LastMediaIndex']=0
            tmcx.util.verb("Volume being computed as shapes with dims " + str(jcfg['Domain']['Dim']), jcfg['Expt']['verb'], 1)
    return (jcfg)


def calc_vol_depth(jcfg):
    if jcfg['Vol']['volZ'] == 'inMedia':
        dZ_values = []  # Initialize an empty list to store "dZ" values
        # Collect all the dZ layer thicknesses from the media
        for entry in jcfg["Domain"]["Media"]:
            if "dZ" in entry:
                dZ_values.append(entry["dZ"])  # Append "dZ" value to the list
    else:
        dZ_values = [jcfg['Vol']['volZ']]
    zVol = sum(dZ_values)
    return zVol


def vol_layers(jcfg):
    """
    Constructs a layered volume structure based on the configuration provided in jcfg. 

    The configuration includes information about the volume dimensions, the number of layers, 
    and the verbosity level for feedback. If only one layer is provided, a single bulk volume 
    is returned. The function modifies the configuration in place, adding the calculated volume 
    and providing verbose feedback if required.

    Args:
        jcfg (dict): Configuration dictionary containing the keys 'Vol', 'Domain', and 'Expt'. 
            'Vol' is a dict containing volume dimensions ('volX', 'volY', 'volZ') and optional zero padding ('zeroPadVol'). 
                It should also contain the number of layers in 'volZ' and the volume in 'vol'. 
            'Domain' is a dict containing the length unit ('LengthUnit') and domain dimensions ('Dim'). 
            'Expt' is a dict containing the verbosity level ('verb').

    Returns:
        dict: The configuration dictionary with the volume matrix updated.

    Note:
        The function modifies the configuration in place, adding the calculated volume and providing verbose feedback if required.
    """

    # find z depth of all layers described in volZ
    if jcfg['Vol']['volZ'] == 'inMedia':
        dZ_values = []  # Initialize an empty list to store "dZ" values
        # Collect all the dZ layer thicknesses from the media
        for entry in jcfg["Domain"]["Media"]:
            if "dZ" in entry:
                dZ_values.append(entry["dZ"])  # Append "dZ" value to the list
    else: 
        dZ_values=[jcfg['Vol']['volZ']]
            
    zVol = sum(dZ_values)

    # Find number of voxels in each dimension
    xdimV = int(np.floor(jcfg['Vol']['volX']/jcfg['Domain']['LengthUnit']))
    ydimV = int(np.floor(jcfg['Vol']['volY']/jcfg['Domain']['LengthUnit']))
    zdimV = int(np.floor(zVol/jcfg['Domain']['LengthUnit']))

    nLayers = len(dZ_values)
    layerIdxs = (np.arange(nLayers))

    if "useShapes" in jcfg['Vol']:
        if jcfg['Vol']['useShapes']==0:
            vol = jcfg['vol']
            tmpv = []
            # Assign indexes for each material, bottom up.
            if nLayers > 1:
                layerdNm1 = 0
                for ii in layerIdxs:
                    if ii == 0:
                        layerStartV = 0  # starting position of first layer
                        # end position of 1st layer
                        layerEndV = int(
                            np.floor(dZ_values[0]/jcfg['Domain']['LengthUnit']))
                    else:
                        # starting position of ii layer
                        layerStartV = int(
                            np.floor(sum(dZ_values[:ii])/jcfg['Domain']['LengthUnit']))
                        # end position of ii layer
                        layerEndV = int(
                            np.floor(sum(dZ_values[:ii+1])/jcfg['Domain']['LengthUnit']))
                    vol[0:xdimV, 0:ydimV, layerStartV:layerEndV] = ii + \
                        1  # Set volume index
            else:
                vol[vol == 0] = 0

            # Control boundaries
            #if 'zeroPadVol' in jcfg['Vol']:
            #    jcfg, vol = vol_bcs(jcfg, vol)

            # Put it back in the jcfg
            jcfg['vol'] = vol

            # Verbose feedback
            tmcx.util.verb('Z-axis cross section:',jcfg['Expt']['verb'], 3)
            tmcx.util.verb(str(vol[1, 1, :]),jcfg['Expt']['verb'], 3)
            if jcfg['Expt']['verb'] >= 3.5:
                fig = tmcx.grap.voxVol(np.sqrt(vol), [int(np.floor(jcfg['Domain']['Dim'][0]/2)), int(
                    np.floor(jcfg['Domain']['Dim'][1]/2)), int(np.floor(jcfg['Domain']['Dim'][2]/2))])
                fig.suptitle('Cutaways of layered structure')
        else:
        # "Shapes::XLayers/YLayers/ZLayers": "Layered structures, defined by an array of integer triples:
        #      [start,end,tag]. Ends are inclusive in MATLAB array indices. XLayers are perpendicular to x-axis, and so on",
        #       '{"Shapes":[{"ZLayers":[[1,10,1],[11,30,2],[31,60,3]]}]}'
        # "Shapes::XSlabs/YSlabs/ZSlabs": "Slab structures, consisted of a list of FP pairs [start,end]
        #      both ends are inclusive in MATLAB array indices, all XSlabs are perpendicular to x-axis, and so on",
            if nLayers > 1:
                jcfg['Shapes'].append({'ZLayers': []})
                for ii in layerIdxs:
                    if ii == 0:
                        layerStartV = 0  # starting position of first layer
                        # end position of 1st layer
                        layerEndV = int(np.floor(dZ_values[0]/jcfg['Domain']['LengthUnit']))
                    else:
                        # starting position of ii layer
                        layerStartV = int(np.floor(sum(dZ_values[:ii])/jcfg['Domain']['LengthUnit']))
                        # end position of ii layer
                        layerEndV = int(np.floor(sum(dZ_values[:ii+1])/jcfg['Domain']['LengthUnit']))
                    # Append the layer to the ZLayers list in the Shape dictionary
                    jcfg['Vol']['LastMediaIndex']+=1
                    jcfg['Shapes'][-1]['ZLayers'].append([layerStartV, layerEndV, jcfg['Vol']['LastMediaIndex']])       

            else:
                pass

    tmcx.util.verb("Added " + str(nLayers) + ' layers to volume', jcfg['Expt']['verb'], 1)

    return (jcfg)

def vol_cyl(jcfg, vol):
    """
    Construct a cylindrical volume structure based on the configuration provided in jcfg and a volume matrix vol. 

    The configuration includes information about the volume dimensions, the number of layers, 
    and the verbosity level for feedback.

    Args:
        jcfg (dict): Configuration dictionary containing the keys 'Vol', 'Domain', and 'Expt'. 
            'Vol' is a dict containing volume dimensions ('volX', 'volY', 'volZ') and optional zero padding ('zeroPadVol'). 
                It should also contain the number of layers in 'volZ' and the volume in 'vol'. 
            'Domain' is a dict containing the length unit ('LengthUnit') and domain dimensions ('Dim'). 
            'Expt' is a dict containing the verbosity level ('verb').
        
        vol (numpy.array): Volume matrix

    Returns:
        tuple: The configuration dictionary with the volume matrix updated.

    Note:
        The function modifies the configuration in place, adding the calculated volume and providing verbose feedback if required.
    """

    # Position cylinder in X coodinates
    # Can be a numerical position, in vx, or "c" for center
    if jcfg['Vol']['Shapes']['Cylinder']['x_loc'] == "c":
        jcfg['Vol']['Shapes']['Cylinder']['x_pos'] =  jcfg['Domain']['Dim'][0]/2-1# (np.floor(jcfg['Vol']['volSize'][0]+1)/jcfg['Domain']['LengthUnit']/2)
    elif jcfg['Vol']['Shapes']['Cylinder']['x_loc'] == "-1":
        jcfg['Vol']['Shapes']['Cylinder']['x_pos'] = int(
            np.floor(jcfg['Vol']['volSize'][0]/jcfg['Domain']['LengthUnit']))-1
    else:
        jcfg['Vol']['Shapes']['Cylinder']['x_pos'] = jcfg['Vol']['Shapes']['Cylinder']['x_loc'] / \
            jcfg['Domain']['LengthUnit']-1

    azimuth_rad = np.pi/180*jcfg['Vol']['Shapes']['Cylinder']['dazimuth']
    azimuth0_rad = jcfg['Vol']['Shapes']['Cylinder']['azimuth0']

    # position in mm of axis
    if jcfg['Vol']['Shapes']['Cylinder']['top_depth'] == 'c':
        jcfg['Vol']['Shapes']['Cylinder']['z_pos'] = jcfg['Vol']['volSize'][2]/2
    elif jcfg['Vol']['Shapes']['Cylinder']['top_depth'] == '-1':
        jcfg['Vol']['Shapes']['Cylinder']['z_pos'] = jcfg['Vol']['volSize'][2]
    else:
        jcfg['Vol']['Shapes']['Cylinder']['z_pos'] = jcfg['Vol']['Shapes']['Cylinder']['r'] + \
            jcfg['Vol']['Shapes']['Cylinder']['top_depth']

    coordArr = np.mgrid[0:jcfg['Domain']['Dim'][0], 0:jcfg['Domain']
                        ['Dim'][1], 0:jcfg['Domain']['Dim'][2]]  # Create coordinate arrays
    dist = np.square(coordArr[0]-jcfg['Vol']['Shapes']['Cylinder']['x_pos']) + np.square(coordArr[2]-(jcfg['Vol']
                                                                                                      ['Shapes']['Cylinder']['z_pos']/jcfg['Domain']['LengthUnit']))  # Evaluate distance from center of blood vessel
    ang = np.arctan2(coordArr[0]-jcfg['Vol']['Shapes']['Cylinder']['x_pos'], coordArr[2]-(
        jcfg['Vol']['Shapes']['Cylinder']['z_pos']/jcfg['Domain']['LengthUnit']))

    # rad_azimuth
    # Debug tool to visualize distance in volume of every point to vessel
    if jcfg['Expt']['verb'] >= 3.5:
        fig = tmcx.grap.voxVol(ang, [jcfg['Vol']['Shapes']['Cylinder']['x_pos'], int(np.floor(jcfg['Vol']['volSize'][1]/jcfg['Domain']
                               ['LengthUnit']/2))-1, int(np.floor(jcfg['Vol']['Shapes']['Cylinder']['z_pos']/jcfg['Domain']['LengthUnit']))-1])
        fig.suptitle('Cutaways angles of cylinder')

    # Debug tool to visualize distance in volume of every point to vessel
    if jcfg['Expt']['verb'] >= 3.5:
        fig2 = tmcx.grap.voxVol(np.sqrt(dist), [jcfg['Vol']['Shapes']['Cylinder']['x_pos'], int(np.floor(jcfg['Vol']['volSize'][1] /
                                jcfg['Domain']['LengthUnit']/2))-1, int(np.floor(jcfg['Vol']['Shapes']['Cylinder']['z_pos']/jcfg['Domain']['LengthUnit']))-1])
        fig2.suptitle('Cutaways of distance from blood vessel')

    # Assign indexes based on distance from the vessel array
    nextidx = np.max(vol)+1
    less_than_radius = np.logical_and(dist >= (np.square(jcfg['Vol']['Shapes']['Cylinder']['r0']/jcfg['Domain']['LengthUnit'])), dist <= (
        np.square(jcfg['Vol']['Shapes']['Cylinder']['r']/jcfg['Domain']['LengthUnit'])))
    outside_dPhi = np.logical_and(
        ang >= (-np.pi + azimuth_rad + azimuth0_rad), ang <= (np.pi - azimuth_rad + azimuth0_rad))
    vol[np.logical_and(less_than_radius, outside_dPhi)] = nextidx

    # Verbose feedback
    tmcx.util.verb("Built cylinder at x= "+ str(jcfg['Vol']['Shapes']['Cylinder']['x_pos']) + " dia = " + str(jcfg['Vol']['Shapes']['Cylinder']['r']) + "mm, depth= " + str(
        jcfg['Vol']['Shapes']['Cylinder']['z_pos']) + "mm" + ' cutting out an angle of: '+str(round(azimuth_rad, 2))+' rad', jcfg['Expt']['verb'], 1)
    if jcfg['Expt']['verb'] >= 2.5:
        fig3 = tmcx.grap.voxVol(vol, [jcfg['Vol']['Shapes']['Cylinder']['x_pos']-1, int(np.floor(jcfg['Vol']['volSize'][1]/jcfg['Domain']
                                ['LengthUnit']/2))-1, int(np.floor(jcfg['Vol']['Shapes']['Cylinder']['z_pos']/jcfg['Domain']['LengthUnit']))-1])
        fig3.suptitle('Cutaways of distance from blood vessel')

    return (jcfg, vol)

def vol_vessel(jcfg):
    """
    Modify a volume array with concentric cylindrical indexes based on the configuration provided in jcfg. 

    The configuration includes information about the volume dimensions, the number of layers, 
    and the verbosity level for feedback. 

    Args:
        jcfg (dict): Configuration dictionary containing the keys 'Vol', 'Domain', and 'Expt'. 
            'Vol' is a dict containing volume dimensions ('v_topDepth', 'v_twall', 'v_tcfz', 'v_rblood') and optional zero padding ('zeroPadVol'). 
            'Domain' is a dict containing the length unit ('LengthUnit') and domain dimensions ('Dim'). 
            'Expt' is a dict containing the verbosity level ('verb').

    Returns:
        dict: The configuration dictionary with the volume matrix updated.

    Note:
        The function modifies the configuration in place, adding the calculated volume and providing verbose feedback if required.

    """
    
    if 'vessel' in jcfg['Vol']:
        if "useShapes" in jcfg['Vol']:
            if jcfg['Vol']['useShapes']==0:
                vol=jcfg['vol']

                # Write thickness of the full cylinder
                jcfg['Vol']['vessel']['rVess'] = jcfg['Vol']['vessel']['rBlood'] + \
                    jcfg['Vol']['vessel']['tCFZ']+jcfg['Vol']['vessel']['tWall']
                jcfg['Vol']['vessel']['rCFZ'] = jcfg['Vol']['vessel']['rVess'] - \
                    jcfg['Vol']['vessel']['tWall']
                jcfg['Vol']['vessel']['v_xPos'] = jcfg['Domain']['Dim'][0]/2 -1
                
                # position in mm of blood vessel center
                if jcfg['Vol']['vessel']['topDepth'] == 'c':
                    v_zPos = jcfg['Vol']['volSize'][2]/2-1
                elif jcfg['Vol']['vessel']['topDepth'] == '-1':
                    v_zPos = jcfg['Vol']['volSize'][2]-1
                else:
                    v_zPos = jcfg['Vol']['vessel']['rVess'] + \
                        jcfg['Vol']['vessel']['topDepth']

                jcfg['Vol']['vessel']['zPos']=v_zPos

                coordArr = np.mgrid[0:jcfg['Domain']['Dim'][0], 0:jcfg['Domain']
                                    ['Dim'][1], 0:jcfg['Domain']['Dim'][2]]  # Create coordinate arrays

                dist = np.square(coordArr[0]-jcfg['Vol']['vessel']['v_xPos']) + np.square(coordArr[2]-(
                    v_zPos/jcfg['Domain']['LengthUnit']))  # Evaluate distance from center of blood vessel

                # Debug tool to visualize distance in volume of every point to vessel
                if jcfg['Expt']['verb'] >= 3.5:
                    fig = tmcx.grap.voxVol(np.sqrt(dist), [round(jcfg['Vol']['vessel']['v_xPos']), int(np.floor(
                        jcfg['Domain']['Dim'][1]/2))-1, int(np.floor(v_zPos/jcfg['Domain']['LengthUnit']))-1])
                    fig.suptitle('Cutaways of distance from blood vessel')

                # Assign indexes based on distance from the vessel array
                nextidx = np.max(vol)+1
                vol[dist <= (np.square(jcfg['Vol']['vessel']['rVess'] /
                            jcfg['Domain']['LengthUnit']))] = nextidx
                vol[dist <= (np.square(jcfg['Vol']['vessel']['rCFZ'] /
                            jcfg['Domain']['LengthUnit']))] = nextidx+1
                vol[dist <= (np.square(jcfg['Vol']['vessel']['rBlood'] /
                            jcfg['Domain']['LengthUnit']))] = nextidx+2

                ## Control boundaries
                #jcfg, vol = vol_bcs(jcfg, vol)

                # Verbose feedback
                tmcx.util.verb("Built blood vessel radius = " + str(
                    jcfg['Vol']['vessel']['rVess']) + "mm, depth center= " + str(v_zPos) + "mm", jcfg['Expt']['verb'], 1)
                if jcfg['Expt']['verb'] >= 3.5:
                    fig2 = tmcx.grap.voxVol(vol, [round(jcfg['Vol']['vessel']['v_xPos']), int(np.floor(
                        jcfg['Domain']['Dim'][1]/2))-1, int(np.floor(v_zPos/jcfg['Domain']['LengthUnit']))-1])
                    fig2.suptitle('Cutaways of distance from blood vessel')
                jcfg['vol']=vol  
    
            else:
                # Write thickness of the full cylinder
                jcfg['Vol']['vessel']['rVess'] = jcfg['Vol']['vessel']['rBlood'] + jcfg['Vol']['vessel']['tCFZ'] + jcfg['Vol']['vessel']['tWall']
                jcfg['Vol']['vessel']['rCFZ'] = jcfg['Vol']['vessel']['rVess'] - jcfg['Vol']['vessel']['tWall']
                jcfg['Vol']['vessel']['v_xPos'] = int(np.floor(jcfg['Domain']['Dim'][0]/2))

                # position in mm of blood vessel center
                if jcfg['Vol']['vessel']['topDepth'] == 'c':
                    v_zPos = jcfg['Vol']['volSize'][2]/2
                elif jcfg['Vol']['vessel']['topDepth'] == '-1':
                    v_zPos = jcfg['Vol']['volSize'][2]
                else:
                    v_zPos = jcfg['Vol']['vessel']['rVess'] + jcfg['Vol']['vessel']['topDepth']

                # Define the cylinders
                    #  "Shapes::Cylinder": "A finite cylinder, defined by the two ends, C0 and C1, along the axis and a radius R",
                    #   {"Cylinder": {"Tag":2, "C0": [0.0,0.0,0.0], "C1": [15.0,8.0,10.0], "R": 4.0}},
                     
                cylinders = [
                    {"Cylinder": {"Tag": jcfg['Vol']['LastMediaIndex']+1, "C0": [jcfg['Vol']['vessel']['v_xPos'], 0.0, v_zPos/jcfg['Domain']['LengthUnit']], "C1": [jcfg['Vol']['vessel']['v_xPos'], jcfg['Domain']['Dim'][1], v_zPos/jcfg['Domain']['LengthUnit']], "R": jcfg['Vol']['vessel']['rVess']/jcfg['Domain']['LengthUnit']}},
                    {"Cylinder": {"Tag": jcfg['Vol']['LastMediaIndex']+2, "C0": [jcfg['Vol']['vessel']['v_xPos'], 0.0, v_zPos/jcfg['Domain']['LengthUnit']], "C1": [jcfg['Vol']['vessel']['v_xPos'], jcfg['Domain']['Dim'][1], v_zPos/jcfg['Domain']['LengthUnit']], "R": jcfg['Vol']['vessel']['rCFZ']/jcfg['Domain']['LengthUnit']}},
                    {"Cylinder": {"Tag": jcfg['Vol']['LastMediaIndex']+3, "C0": [jcfg['Vol']['vessel']['v_xPos'], 0.0, v_zPos/jcfg['Domain']['LengthUnit']], "C1": [jcfg['Vol']['vessel']['v_xPos'], jcfg['Domain']['Dim'][1], v_zPos/jcfg['Domain']['LengthUnit']], "R": jcfg['Vol']['vessel']['rBlood']/jcfg['Domain']['LengthUnit']}}
                ]
                jcfg['Vol']['LastMediaIndex']+=3     
                # Add the cylinders to the Shapes list
                jcfg['Shapes'].extend(cylinders)

                # Verbose feedback
                tmcx.util.verb("Built blood vessel radius = " + str(
                    jcfg['Vol']['vessel']['rVess']) + "mm, depth center= " + str(v_zPos) + "mm", jcfg['Expt']['verb'], 1)
    else:
        pass

    return (jcfg)

def source(jcfg):
    """
    Evaluates sources from the configuration provided in jcfg.

    The configuration includes information about the source type, location, size, and direction.
    The function modifies the configuration in place, adding the calculated source parameters
    and providing verbose feedback if required.

    Args:
        jcfg (dict): Configuration dictionary containing the keys 'Source', 'Domain', and 'Expt'.
            'Source' is a dict containing source parameters like type, location, size, and direction.
            'Domain' is a dict containing the length unit ('LengthUnit') and domain dimensions ('Dim').
            'Expt' is a dict containing the verbosity level ('verb').

    Returns:
        dict: The configuration dictionary with the source parameters updated.

    Note:
        The function modifies the configuration in place, adding the calculated source parameters and
        providing verbose feedback if required.
    """
    if 'Dim' not in jcfg['Domain']:
        dims=jcfg['vol'].shape
        jcfg['Domain']['Dim'] = [dims[0], dims[1], dims[2]]
        
    if jcfg['Optode']['Source']['Type'] == "custom":
        # Leave source parameters alone, as decribed in script
        if jcfg['Expt']['verb'] >= 1:
            print("Define srctyle, srcpos, srcparam1, srcparam2, and srcdir manually")
        # jcfg['Optode']['Source']['Pos'] = "MANUAL"
        # jcfg['Optode']['Source']['Param1'] = "MANUAL"
        # jcfg['Optode']['Source']['Param2'] = "MANUAL"
        # jcfg['Optode']['Source']['Dir'] = "MANUAL"

    if jcfg['Optode']['Source']['Type'] == "line":
        for tii in np.arange(3):  # Cycle over the three axes
            if jcfg['Optode']['Source']['Loc'][tii] == 'c':  # Check if centered
                # Calculate centered size of line
                jcfg['Optode']['Source']['Param1'][tii] = int(np.floor(jcfg['Optode']['Source']['Size'][tii] / \
                    jcfg['Domain']['LengthUnit']))
                # Calculate centered position of line
                jcfg['Optode']['Source']['Pos'][tii] = jcfg['Domain']['Dim'][tii]/2 - \
                    jcfg['Optode']['Source']['Param1'][tii] / \
                    2  # Assign center adjusted for length of source
            # Check if assigned to dimension extreme
            if jcfg['Optode']['Source']['Loc'][tii] == '-1':
                # Calculate centered size of line
                jcfg['Optode']['Source']['Param1'][tii] = jcfg['Optode']['Source']['Size'][tii] / \
                    jcfg['Domain']['LengthUnit']
                # Calculate centered position of line
                jcfg['Optode']['Source']['Pos'][tii] = jcfg['Domain']['Dim'][tii] - 1 - \
                    jcfg['Optode']['Source']['Param1'][tii]  # Assign center adjusted for length of source
        tmcx.util.verb("Built line source at "+ str(jcfg['Optode']['Source']['Pos']) + "vox, length: "+ str(jcfg['Optode']['Source']['Param1']) , jcfg['Expt']['verb'], 1)
    
    if jcfg['Optode']['Source']['Type'] == "fullSurface":
        # 3D quadrilateral uniform planar source, with three corners specified by srcpos, srcpos+srcparam1(1:3) and srcpos+srcparam2(1:3)
        jcfg['Optode']['Source']['Type'] = 'planar'
        # [((-x_vol/cfg.unitinmm)/2) ((-y_vol/cfg.unitinmm)/2) 1];
        jcfg['Optode']['Source']['Pos'] = [0, 0, 0]
        jcfg['Optode']['Source']['Param1'] = [jcfg['Domain']['Dim'][0],
                                              0, 0, 0]  # 1 by 3 vector, for planar this is the X length
        jcfg['Optode']['Source']['Param2'] = [0, jcfg['Domain']['Dim']
                                              [1], 0, 0]  # 1 by 3 vector, for planar this is the Y length
        # 1 by 4 vector, specifying the incident vector;
        jcfg['Optode']['Source']['Dir'] = [0, 0, 1, 0]
        tmcx.util.verb('Built source of Type: ' + jcfg['Optode']['Source']['Type'] + ' at Pos: ' + str(
            jcfg['Optode']['Source']['Pos']), jcfg['Expt']['verb'], 1)
        
    if jcfg['Optode']['Source']['Type'] == "bar_source":
        # 3D quadrilateral uniform planar source, with three corners specified by srcpos, srcpos+srcparam1(1:3) and srcpos+srcparam2(1:3)
        jcfg['Optode']['Source']['Type'] = 'planar'
        # [((-x_vol/cfg.unitinmm)/2) ((-y_vol/cfg.unitinmm)/2) 1];
        # right side of the volume
        volXDim=jcfg['Domain']['Dim'][0]
        SourceDetPitch_vox=jcfg['Optode']['Source']['Pitch']/ jcfg['Domain']['LengthUnit']
        halfSourceWidth=jcfg['Optode']['Source']['Size']/ jcfg['Domain']['LengthUnit']/2
        jcfg['Optode']['Source']['Pos'] = [volXDim/2-SourceDetPitch_vox-halfSourceWidth-1, 0, jcfg['Domain']['Dim'][2]-1]
        jcfg['Optode']['Source']['Param1'] = [-jcfg['Optode']['Source']['Size']/ jcfg['Domain']['LengthUnit'],
                                              0, 0, 0]  # 1 by 3 vector, for planar this is the X length
        jcfg['Optode']['Source']['Param2'] = [0, jcfg['Domain']['Dim']
                                              [1], 0, 0]  # 1 by 3 vector, for planar this is the Y length
        
        tmcx.util.verb('Built source of Type: ' + jcfg['Optode']['Source']['Type'] + ' at Pos: ' + str(
            jcfg['Optode']['Source']['Pos']), jcfg['Expt']['verb'], 1)
    
    if jcfg['Optode']['Source']['Type'] == "gaussian":
        	# "Type": "gaussian",
            # "Loc": ["c","c", 0],
            # "Dir": [0,0,1],
            # "Size": beam radius in mm
        # Cycle over the three axes
        jcfg['Optode']['Source']['Pos']=[0,0,0]
        for tii in np.arange(3):  
            # Check if centered
            if jcfg['Optode']['Source']['Loc'][tii] == 'c':  
                # Assign to center position of beam
                jcfg['Optode']['Source']['Pos'][tii] = jcfg['Domain']['Dim'][tii]/2 - 1
            #Assign to start of volume
            elif jcfg['Optode']['Source']['Loc'][tii] == '0': 
                jcfg['Optode']['Source']['Pos'][tii] = 0
            # Assign to end of volume
            elif jcfg['Optode']['Source']['Loc'][tii] == '-1': 
                jcfg['Optode']['Source']['Pos'][tii] = jcfg['Domain']['Dim'][tii]
            else:
                 jcfg['Optode']['Source']['Pos'][tii]=jcfg['Optode']['Source']['Loc'][tii]
        # Parameters above are in voxels aready from the Dim key, below we convert size from mm to vox.
        jcfg['Optode']['Source']['Param1']=[jcfg['Optode']['Source']['Size']/jcfg['Domain']['LengthUnit'],0,0,0]
        jcfg['Optode']['Source']['Param2']=[0,0,0,0]
    
    if jcfg['Optode']['Source']['Type'] == "hyperboloid":
        	# "Type": "gaussian",
            # "Loc": ["c","c", 0],
            # "Dir": [0,0,1],
            # "Param1": [5,0,0,0]
        # Cycle over the three axes
        jcfg['Optode']['Source']['Pos']=[0,0,0]
        for tii in np.arange(3):  
            # Check if centered
            if jcfg['Optode']['Source']['Loc'][tii] == 'c':  
                # Assign to center position of beam
                jcfg['Optode']['Source']['Pos'][tii] = jcfg['Domain']['Dim'][tii]/2 -1
            #Assign to start of volume
            elif jcfg['Optode']['Source']['Loc'][tii] == '0': 
                jcfg['Optode']['Source']['Pos'][tii] = 0
            # Assign to end of volume
            elif jcfg['Optode']['Source']['Loc'][tii] == '-1': 
                jcfg['Optode']['Source']['Pos'][tii] = jcfg['Domain']['Dim'][tii]
            else:
                 jcfg['Optode']['Source']['Pos'][tii]=jcfg['Optode']['Source']['Loc'][tii]

        # Notice that size here is really the beam, which is the radius.  Size for other types is the diameter. 
        w0 = jcfg['Optode']['Source']['Size']/jcfg['Domain']['LengthUnit']

        if jcfg['Optode']['Source']['FocusDist'] == 'c':
            fdist = jcfg['Domain']['Dim'][2]/2
        else:
            fdist = jcfg['Optode']['Source']['FocusDist']/jcfg['Domain']['LengthUnit'] 

        zR = jcfg['Optode']['Source']['zR']/jcfg['Domain']['LengthUnit'] 

        jcfg['Optode']['Source']['Param1'] = [w0, fdist, zR, 0]

        jcfg['Optode']['Source']['Param2']=[0,0,0,0]

    if jcfg['Optode']['Source']['Type'] == "pattern":
        # a 3D quadrilateral uniform planar source, with three corners specified 
        #                         by srcpos, srcpos+srcparam1(1:3) and srcpos+srcparam2(1:3)

        # 'pattern' [*] - a 3D quadrilateral pattern illumination, same as above, except
        #                         srcparam1(4) and srcparam2(4) specify the pattern array x/y dimensions,
        #                         and srcpattern is a floating-point pattern array, with values between [0-1]. 
        #                         if cfg.srcnum>1, srcpattern must be a floating-point array with 
        #                         a dimension of [srcnum srcparam1(4) srcparam2(4)]"""
        # First find the size of the input image
        
       if np.any(np.logical_or(jcfg['Optode']['Source']['Pattern']<0 , jcfg['Optode']['Source']['Pattern']>1)): # give an error when the pattern values are below 0 or above 1
            raise ValueError("Pattern values cannot be below 0 or above 1")
       else:

            sourceDims=jcfg['Optode']['Source']['Pattern'].shape
            volDims = jcfg['Domain']['Dim']

            # Set the position of the origin
            jcfg['Optode']['Source']['Pos']=[0,0,0]
            for tii in np.arange(3):  
                # Check if centered
                if jcfg['Optode']['Source']['Loc'][tii] == 'c':  
                    # Assign to center position of beam
                    jcfg['Optode']['Source']['Pos'][tii] = volDims[tii]/2
                    if tii <=1:
                        jcfg['Optode']['Source']['Pos'][tii]-=sourceDims[tii]/2 # center the image
                #Assign to start of volume
                elif jcfg['Optode']['Source']['Loc'][tii] == '0': 
                    jcfg['Optode']['Source']['Pos'][tii] = 0
                # Assign to end of volume
                elif jcfg['Optode']['Source']['Loc'][tii] == '-1': 
                    jcfg['Optode']['Source']['Pos'][tii] = jcfg['Domain']['Dim'][tii]
                else:
                    jcfg['Optode']['Source']['Pos'][tii]=jcfg['Optode']['Source']['Loc'][tii]
            
            # Set the position of the X corner
            jcfg['Optode']['Source']['Param1']=[sourceDims[0],0,0,sourceDims[0]]
            # Set the position of the Y corner
            jcfg['Optode']['Source']['Param2']=[0,sourceDims[1],0,sourceDims[1]]

    if jcfg['Optode']['Source']['Type'] == "disk":
        	# "Type": "disk",
            # "Loc": ["c","c", 0],
            # "Dir": [0,0,1],
            # "Param1": [5,0,0,0]
        # Cycle over the three axes
        jcfg['Optode']['Source']['Pos']=[0,0,0]
        for tii in np.arange(3):  
            # Check if centered
            if jcfg['Optode']['Source']['Loc'][tii] == 'c':  
                # Assign to center position of beam
                jcfg['Optode']['Source']['Pos'][tii] = jcfg['Domain']['Dim'][tii]/2 -1
            #Assign to start of volume
            elif jcfg['Optode']['Source']['Loc'][tii] == '0': 
                jcfg['Optode']['Source']['Pos'][tii] = 0
            # Assign to end of volume
            elif jcfg['Optode']['Source']['Loc'][tii] == '-1': 
                jcfg['Optode']['Source']['Pos'][tii] = jcfg['Domain']['Dim'][tii]
            else:
                 jcfg['Optode']['Source']['Pos'][tii]=jcfg['Optode']['Source']['Loc'][tii]
        jcfg['Optode']['Source']['Param1']=2*[jcfg['Optode']['Source']['Size']/jcfg['Domain']['LengthUnit'],0,0,0]
        jcfg['Optode']['Source']['Param2']=[0,0,0,0]
           
    if "NA" in jcfg['Optode']['Source']:
        xyz=jcfg['Optode']['Source']["Dir"][0:3]
        theta = 2*np.arcsin(jcfg['Optode']['Source']["NA"]/jcfg['Domain']['Media'][0]['n'])  # Calculate angle in radians
        depth = jcfg['Optode']['Source']["Size"] / np.tan(theta) / jcfg['Domain']['LengthUnit'] # Calculate long side
        xyz.append(-depth)
        jcfg['Optode']['Source']["Dir"]=xyz
        tmcx.util.verb("Set source NA to "+str(jcfg['Optode']['Source']["NA"])+" for dir vector "+str(xyz), jcfg['Expt']['verb'], 1)
    
    if jcfg['Optode']['Source']['Type'] == "angleinvcdf":
        # This case is designed for using the angle inverse CDF as an input.  this can be either a direct list, or a file; if it's a file it should have a specific format; see import function. 
        # This prioritizes importing and reinterpolating the angles over reading them directly from the jcfg. 
        # Cycle over the three axes
        jcfg['Optode']['Source']['Pos']=[0,0,0]
        for tii in np.arange(3):  
            # Check if centered
            if jcfg['Optode']['Source']['Loc'][tii] == 'c':  
                # Assign to center position of beam
                jcfg['Optode']['Source']['Pos'][tii] = jcfg['Domain']['Dim'][tii]/2 -1
            #Assign to start of volume
            elif jcfg['Optode']['Source']['Loc'][tii] == '0': 
                jcfg['Optode']['Source']['Pos'][tii] = 0
            # Assign to end of volume
            elif jcfg['Optode']['Source']['Loc'][tii] == '-1': 
                jcfg['Optode']['Source']['Pos'][tii] = jcfg['Domain']['Dim'][tii]
            else:
                 jcfg['Optode']['Source']['Pos'][tii]=jcfg['Optode']['Source']['Loc'][tii]
        jcfg['Optode']['Source']['Dir'][3]=0 # This is 0 for interpolation, 1 for discrete emissions. 
        jcfg['Optode']['Source']['Param1']=[0,0,0,0]
        jcfg['Optode']['Source']['Param2']=[0,0,0,0]
        if "angleinvcdf" in jcfg['Optode']['Source']:
            # 0 is along the Dir, 0.5 is perpendicular to Dir, 1 is backwards.  0.25 is at 45 degrees with respect to Dir.
            if jcfg['Optode']['Source']['angleinvcdf']=='calc':
                # import the emission probability distribution of the source, as a .json
                thetas, probs = tmcx.impo.extracted_data(jcfg['Optode']['Source']['angleinvcdf_file'])
                import os
                file_name = os.path.basename(jcfg['Optode']['Source']['angleinvcdf_file'])
                if (('Polar' in file_name) or ('polar' in file_name)):
                    thetas, probs = tmcx.calc.coord_transform_carthesian_to_polar(thetas,probs)
                    probs = np.array(probs)[np.array(thetas)>=0]
                    thetas = np.array(thetas)[np.array(thetas)>=0]
                theta_equal_probs=tmcx.calc.equally_probable_theta_intervals(thetas, probs, num_data_points=3000)
                jcfg['Optode']['Source']['angleinvcdf']=theta_equal_probs
                tmcx.util.verb("Calculated angles of emission with equal probability", jcfg['Expt']['verb'], 2)
            else: 
                tmcx.util.verb("Relying on angleinvcdf being defined in jcfg directly", jcfg['Expt']['verb'], 1)
        else:
            pass
        
    
    if np.sqrt(np.sum(np.array(jcfg['Optode']['Source']['Dir'][:3])**2)) !=1:
        jcfg['Optode']['Source']['Dir'][:3]=jcfg['Optode']['Source']['Dir'][:3]/np.sqrt(np.sum(np.array(jcfg['Optode']['Source']['Dir'][:3])**2))
        tmcx.util.verb(f"Source direction not normalized. Normalized to {jcfg['Optode']['Source']['Dir']}", jcfg['Expt']['verb'], 1)
    # cfg['Optode']['Type']= 'gaussian'
    # cfg['Custom']['df'] = -0.0147;               #mm focus distance
    # cfg['Custom']['w0'] = 0.010;                 #mm -->10um
    # cfg['Optode']['Pos']=[cfg['Domain']['Dim'][0]/2,cfg['Domain']['Dim'][1]/2,0]
    # cfg['Optode']['Param1']=[cfg['Custom']['w0']/cfg['Domain']['LengthUnit'], 0, 0 ]
    # cfg['Optode']['Dir']= [0, 0, cfg['Custom']['df']/cfg['Domain']['LengthUnit']]
    # cfg['Optode']['size']=
    # cfg['Optode']['Pos']=[cfg['Domain']['Dim'][0]/2,cfg['Domain']['Dim'][1]/2,0]
    # cfg['Optode']['Param1']=[cfg['Custom']['w0']/cfg['Domain']['LengthUnit'], 0, 0 ]
    # cfg['Optode']['Dir']= [0, 0, cfg['Custom']['df']/cfg['Domain']['LengthUnit']]

    return jcfg

def detectors(jcfg):
    """
    Evaluates detectors from the configuration provided in jcfg. 

    The configuration includes information about the detector type, location, size, and direction. 
    The function modifies the configuration in place, adding the calculated detector parameters 
    and providing verbose feedback if required.

    Args:
        jcfg (dict): Configuration dictionary containing the keys 'Detector', 'Domain', and 'Expt'. 
        'Detector' is a dict containing detector parameters like type, location, size, and direction. 
        'Domain' is a dict containing the length unit ('LengthUnit') and domain dimensions ('Dim'). 
        'Expt' is a dict containing the verbosity level ('verb').

    Returns:
        dict: The configuration dictionary with the detector parameters updated.

    Note: 
        The function modifies the configuration in place, adding the calculated detector parameters 
        and providing verbose feedback if required.
    """
    if jcfg['Optode']['Detector']['Type'] == "custom":
        # Leave source parameters alone, as decribed in script
        tmcx.util.verb('Built detector of Type: ' + jcfg['Optode']['Detector']
                       ['Type'] + '. Define Pos and R in script!', jcfg['Expt']['verb'], 1)

#         jcfg['Optode']['Detector']['Type']=""
#         jcfg['Optode']['Detector']['Pos']=[0,0,0]
#         jcfg['Optode']['Detector']['R']=[0,0,0]
    
        if 'Loc' in jcfg['Optode']['Detector']:
            jcfg['Optode']['Detector']['Pos']=[0,0,0]
            for tii in np.arange(3):  
                # Check if centered
                if jcfg['Optode']['Detector']['Loc'][tii] == 'c':  
                    # Assign to center position of beam
                    jcfg['Optode']['Detector']['Pos'][tii] = jcfg['Domain']['Dim'][tii]/2 - 1
                #Assign to start of volume
                elif jcfg['Optode']['Detector']['Loc'][tii] == '0': 
                    jcfg['Optode']['Detector']['Pos'][tii] = 0
                # Assign to end of volume
                elif jcfg['Optode']['Detector']['Loc'][tii] == '-1': 
                    jcfg['Optode']['Detector']['Pos'][tii] = jcfg['Domain']['Dim'][tii]-1
                else:
                    jcfg['Optode']['Detector']['Pos'][tii]=jcfg['Optode']['Detector']['Loc'][tii]
             

    if jcfg['Optode']['Detector']['Type'] == "bc_planes":
        jcfg['Session']['BCFlags'] = jcfg['Session']['BCFlags'][0:6] + \
            jcfg['Optode']['Detector']['bc_planes']
        tmcx.util.verb('Built detector of Type: ' + jcfg['Optode']['Detector']['Type'] +
                       ' on planes: ' + jcfg['Optode']['Detector']['bc_planes'], jcfg['Expt']['verb'], 1)

    if jcfg['Optode']['Detector']['Type'] == "Sphere":
        jcfg['Optode']['Detector']['Pos'] = [
            jcfg['Domain']['Dim'][0]/2, jcfg['Domain']['Dim'][1]/2, 0]
        # This is the longest length of the largest face of the volume
        jcfg['Optode']['Detector']['R'] = (
            np.max([jcfg['Domain']['Dim'][0], jcfg['Domain']['Dim'][1]]))/2*np.sqrt(2)
        jcfg['Vol']['zeroPadVol'] = [0, 0, 1, 0, 0, 0]
        # an N by 4 array, each row specifying a detector: [x,y,z,radius]
        tmcx.util.verb('Built detector of Type: ' + jcfg['Optode']['Detector']['Type'] + ' at Pos: ' + str(
            jcfg['Optode']['Source']['Pos']), jcfg['Expt']['verb'], 1)

    return jcfg

def incident_spectrum(jcfg: dict):
    """
    Construct an incident spectrum based on the configuration provided in jcfg. 

    The configuration includes information about the spectrum profile, wavelength range, and other parameters. 
    The function modifies the configuration in place, adding the calculated spectrum and providing verbose feedback if required.

    Args:
        jcfg (dict): Configuration dictionary containing the keys 'Optode', 'Expt'. 
            'Optode' is a dict containing the source parameters like type, location, size, and direction. 
            'Expt' is a dict containing the verbosity level ('verb').

    Returns:
        dict: The configuration dictionary with the incident spectrum updated.

    Note:
        The function modifies the configuration in place, adding the calculated spectrum and providing verbose feedback if required.
    """
  
    import os
    import pandas as pd

    if jcfg['Optode']["Source"]['spectProfile'] == "gaussian":
        # "Optode": {
		# "Source": {
        # "spectProfile": "gaussian",
        # "lam0" : 400,
		# "lamN" : 750,
		# "dlam" : 1,
		# "mu" : 532,
		# "sig" : 6

        def gaussian(x, mu, sig):
            return 1/(np.sqrt(2*np.pi)*sig)*np.exp(-np.power((x - mu)/sig, 2)/2)
    
        mu=jcfg['Optode']['Source']['mu']
        sig=jcfg['Optode']['Source']['sig']
        
        tmcx.util.verb(f"Building incident spectrum with gaussian profile mu={mu} sig={sig}", jcfg['Expt']['verb'], 1)
        tmcx.util.verb(f"Interpolating spectrum from {jcfg['Optode']['Source']['lam0']} to {jcfg['Optode']['Source']['lamN']} stepping {jcfg['Optode']['Source']['dlam']}", jcfg['Expt']['verb'], 2)
        
        filt_spectra_interp = pd.DataFrame()
        wls=np.arange(jcfg['Optode']['Source']['lam0'],jcfg['Optode']['Source']['lamN'],jcfg['Optode']['Source']['dlam'])
        filt_spectra_interp.insert(0, "Wavelength (nm)", wls)
        
        filt_spectra_interp.insert(1,f"gaussian mu={mu} sig={sig}", gaussian(wls, mu, sig))
        jcfg["Optode"]["Source"]["Spectrum"]=filt_spectra_interp
        
    elif jcfg['Optode']["Source"]['spectProfile'] == "bandpass":
        # "Optode": {
		# "Source": {
        # "lam0" : 400,
		# "lamN" : 750,
		# "dlam" : 1,
        # "spectProfile": "bandpass",
		# "mu" : 532,
		# "sig" : 6
  
        mu=jcfg['Optode']['Source']['mu'] # center of bandpass
        sig=jcfg['Optode']['Source']['sig'] # width in nm
        
        tmcx.util.verb(f"Building incident spectrum with bandpass profile at WL={mu}nm width={sig}nm", jcfg['Expt']['verb'], 1)
        tmcx.util.verb(f"Interpolating spectrum from {jcfg['Optode']['Source']['lam0']} to {jcfg['Optode']['Source']['lamN']} stepping {jcfg['Optode']['Source']['dlam']}", jcfg['Expt']['verb'], 2)
        
        filt_spectra_interp = pd.DataFrame()
        wls=np.arange(jcfg['Optode']['Source']['lam0'],jcfg['Optode']['Source']['lamN'],jcfg['Optode']['Source']['dlam'])
        filt_spectra_interp.insert(0, "Wavelength (nm)", wls)
        
        bPFilt=np.multiply(np.multiply(wls > mu-sig/2,1) + np.multiply(wls < mu+sig/2,1)==2,1)
        bPFilt=bPFilt/sum(bPFilt)
        
        filt_spectra_interp.insert(1,f"gaussian mean={mu} width={sig}", bPFilt)
        jcfg["Optode"]["Source"]["Spectrum"]=filt_spectra_interp
            
    else:
        # "Optode": {
		# "Source": {
        # "spectProfile": "file path or variable number in sourceSpectra",     
     	# "sourceFilter" : "0",
		# "sourceSpectra" : 
		# {
		# 	"0": "C:\\dev\\mcx\\Resources\\Spectra\\sources\\ET520-20m.csv",
		# 	"1": "C:\\dev\\mcx\\Resources\\Spectra\\sources\\ET550-20m.csv"
		# }
  
        jcfg = tmcx.impo.incident_spectrum(jcfg)
        
    if jcfg["Expt"]["verb"] >= 3:
        fig_exSource=plt.figure()
        plt.plot(jcfg["Optode"]["Source"]["Spectrum"].iloc[:,0],jcfg["Optode"]["Source"]["Spectrum"].iloc[:,1])
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Source Spectrum (arb. u)")
        # fig_exSource.show()
    return jcfg

def vol_modify_region(jcfg):
    """
    Modify one or more specific regions within a volume with either absolute reassignment or incrementation.

    Args:
        jcfg (dict): Configuration dictionary containing the volume in jcfg['vol']
        regions (list): List of dictionaries, each containing:
            'region': dict with region parameters:
                'x': x start position (voxels)
                'y': y start position (voxels) 
                'z': z start position (voxels)
                'dx': x extent (voxels)
                'dy': y extent (voxels)
                'dz': z extent (voxels)
            'operation': str, either 'absolute' for reassignment or 'increment' for adding offset
            'value': int/float, value to assign (absolute) or add (increment)

    Returns:
        dict: The configuration dictionary with the modified volume

    Note:
        The function modifies the volume in place and provides verbose feedback if required.
        Region boundaries are automatically clipped to volume dimensions.
    """
    if "modify_region" in jcfg['Vol']:
        regions = jcfg['Vol']['modify_region']
    else:
        regions = []
        

    if 'vol' not in jcfg:
        raise ValueError("No volume found in jcfg. Run vol_init first.")
    
    vol = jcfg['vol']
    vol_dims = vol.shape
    
    if not isinstance(regions, list):
        raise ValueError("Regions must be a list of dictionaries")
    
    total_regions_processed = 0
    
    # Process each region
    for i, region_config in enumerate(regions):
        if not isinstance(region_config, dict):
            tmcx.util.verb(f"Warning: Region config {i} is not a dict - skipping", jcfg['Expt']['verb'], 1)
            continue
            
        if 'operation' not in region_config or 'value' not in region_config:
            tmcx.util.verb(f"Warning: Region config {i} missing required keys (region, operation, value) - skipping", jcfg['Expt']['verb'], 1)
            continue
            
        region = region_config
        operation = region_config['operation']
        value = region_config['value']
        
        if not isinstance(region, dict):
            tmcx.util.verb(f"Warning: Region {i} is not a dict - skipping", jcfg['Expt']['verb'], 1)
            continue
        
        # Extract region parameters with validation
        # Handle special string values and negative positions
        if region.get('x', 0) == "-1":
            x_start = vol_dims[0] - 1  # Last valid index in x dimension
        elif isinstance(region.get('x', 0), (int, float)) and region.get('x', 0) < 0:
            # Negative value: distance from the end in mm, converted to voxels
            x_start = vol_dims[0] - 1 + round(region.get('x', 0)/jcfg['Domain']['LengthUnit'])
        else:
            x_start = round(max(0, region.get('x', 0))/jcfg['Domain']['LengthUnit']-1) # convert to voxels
            
        if region.get('y', 0) == "-1":
            y_start = vol_dims[1] - 1  # Last valid index in y dimension
        elif isinstance(region.get('y', 0), (int, float)) and region.get('y', 0) < 0:
            # Negative value: distance from the end in mm, converted to voxels
            y_start = vol_dims[1] - 1 + round(region.get('y', 0)/jcfg['Domain']['LengthUnit'])
        else:
            y_start = round(max(0, region.get('y', 0))/jcfg['Domain']['LengthUnit']-1)
            
        if region.get('z', 0) == "-1":
            z_start = vol_dims[2] - 1  # Last valid index in z dimension
        elif isinstance(region.get('z', 0), (int, float)) and region.get('z', 0) < 0:
            # Negative value: distance from the end in mm, converted to voxels
            z_start = vol_dims[2] - 1 + round(region.get('z', 0)/jcfg['Domain']['LengthUnit'])
        else:
            z_start = round(max(0, region.get('z', 0))/jcfg['Domain']['LengthUnit']-1)

        dx = round(region.get('dx', vol_dims[0])/jcfg['Domain']['LengthUnit'])
        dy = round(region.get('dy', vol_dims[1])/jcfg['Domain']['LengthUnit'])
        dz = round(region.get('dz', vol_dims[2])/jcfg['Domain']['LengthUnit'])
        
        # Calculate actual start and end positions, handling negative deltas
        if dx >= 0:
            x_start_actual = x_start
            x_end_actual = x_start + dx
        else:
            x_start_actual = x_start + dx
            x_end_actual = x_start
            
        if dy >= 0:
            y_start_actual = y_start
            y_end_actual = y_start + dy
        else:
            y_start_actual = y_start + dy
            y_end_actual = y_start
            
        if dz >= 0:
            z_start_actual = z_start
            z_end_actual = z_start + dz
        else:
            z_start_actual = z_start + dz
            z_end_actual = z_start
        
        # Clip to volume boundaries
        x_start_actual = max(0, x_start_actual)
        y_start_actual = max(0, y_start_actual)
        z_start_actual = max(0, z_start_actual)
        x_end_actual = min(vol_dims[0], x_end_actual)
        y_end_actual = min(vol_dims[1], y_end_actual)
        z_end_actual = min(vol_dims[2], z_end_actual)
        
        # Validate region
        if x_start_actual >= x_end_actual or y_start_actual >= y_end_actual or z_start_actual >= z_end_actual:
            tmcx.util.verb(f"Warning: Invalid region {i} specified - skipping", jcfg['Expt']['verb'], 1)
            continue
        
        # Extract the region of interest before modification
        region_slice = vol[x_start_actual:x_end_actual, y_start_actual:y_end_actual, z_start_actual:z_end_actual]
        original_unique_values = np.unique(region_slice)
        
        # Perform the specified operation
        if operation == 'absolute':
            vol[x_start_actual:x_end_actual, y_start_actual:y_end_actual, z_start_actual:z_end_actual] = value
            tmcx.util.verb(f"Region {i+1}: Absolute assignment: Set region [{x_start_actual}:{x_end_actual}, {y_start_actual}:{y_end_actual}, {z_start_actual}:{z_end_actual}] to value {value}", 
                           jcfg['Expt']['verb'], 1)
            
        elif operation == 'increment':
            vol[x_start_actual:x_end_actual, y_start_actual:y_end_actual, z_start_actual:z_end_actual] += value
            tmcx.util.verb(f"Region {i+1}: Increment operation: Added {value} to region [{x_start_actual}:{x_end_actual}, {y_start_actual}:{y_end_actual}, {z_start_actual}:{z_end_actual}]", 
                           jcfg['Expt']['verb'], 1)
            tmcx.util.verb(f"Region {i+1}: Original values {original_unique_values} became {np.unique(vol[x_start_actual:x_end_actual, y_start_actual:y_end_actual, z_start_actual:z_end_actual])}", 
                           jcfg['Expt']['verb'], 2)

        else:
            tmcx.util.verb(f"Warning: Invalid operation '{operation}' for region {i} - skipping", jcfg['Expt']['verb'], 1)
            continue
        
        # Verbose feedback about the modification
        if jcfg['Expt']['verb'] >= 2:
            modified_values = np.unique(vol[x_start_actual:x_end_actual, y_start_actual:y_end_actual, z_start_actual:z_end_actual])
            tmcx.util.verb(f"Region {i+1}: Size: {abs(dx)}x{abs(dy)}x{abs(dz)} voxels", jcfg['Expt']['verb'], 2)
            tmcx.util.verb(f"Region {i+1}: Final values in region: {modified_values}", jcfg['Expt']['verb'], 2)
        
        total_regions_processed += 1
    
    # Update the volume in jcfg
    jcfg['vol'] = vol
    
    tmcx.util.verb(f"Successfully processed {total_regions_processed} out of {len(regions)} regions", jcfg['Expt']['verb'], 1)
    
    plt.close('all')
    
    return jcfg