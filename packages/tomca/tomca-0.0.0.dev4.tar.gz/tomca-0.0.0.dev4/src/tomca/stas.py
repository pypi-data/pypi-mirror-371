"""
functions which do \b statistics on output simulation data
"""


def bin_voxels(dat, param, acceptAngle, verb):
    """ This takes in a json anbd jdat file and returns and bins the detected
        photons like a camera into a matrix for further processing/plotting
        Returns:
            IM:     image matrix
            param:  json file used for simulation
        """
    import numpy as np
    import scipy.stats as st
    from src import tomca

    Dim = param['Domain']['Dim']
    tomca.util.verb('Loaded analysis .json file with Dims: ' + str(Dim),
                   verb, 3)

    # Initialize image array
    IM = np.zeros((Dim[1]-1, Dim[0]-1))
    ppath = dat['MCXData']['PhotonData']['ppath']
    pos = dat['MCXData']['PhotonData']['p']
    vz = dat['MCXData']['PhotonData']['v'][:, 2]

    # exclude unphysical numbers from rounding errors
    filtA = (vz <= 1) & (vz >= -1)
    ppath = ppath[filtA]
    pos = pos[filtA]
    vz = vz[filtA]

    # Evaluate and filter detected photons for incoming acceptance angle
    incAngle = np.degrees(np.arccos(vz))
    filtB = (180 - incAngle) < acceptAngle
    ppath = ppath[filtB]
    pos = pos[filtB]
    vz = vz[filtB]

    x = pos[:, 0]
    y = pos[:, 1]

    bins1 = np.arange(0, Dim[1], 1)
    bins2 = np.arange(0, Dim[0], 1)

    # Calculate each index's contribution to photon weight
    factor = 0
    for kk in np.arange(0, np.shape(ppath)[1]):
        if kk == 99:  # inhere to change absorption of specific layer if needed
            factor = factor + dat['MCXData']['Info']['LengthUnit'] *\
                ppath[:, kk]*1000  # also tag0 info is saved, not in ppath
        else:
            factor = factor + dat['MCXData']['Info']['LengthUnit'] *\
                ppath[:, kk]*dat['MCXData']['Info']['Media'][kk+1]['mua']  \
                # also tag0 info is saved, not in ppath
    weights = 1*np.exp(-1*factor)

    results = st.binned_statistic_2d(y, x, weights, statistic='sum',
                                     bins=[bins1, bins2], range=None)
    IM = IM + results[0]

    tomca.util.verb('Binned with max: ' + str(np.max(IM)) + ' and min: '+str(
        np.min(IM)), 1, 1)

    return (IM, dat, param)


def virt_detector(dat, param, vDetPos, vDetRad, acceptAngle, verb):
    import numpy as np
    from src import tomca

    ppath = dat['MCXData']['PhotonData']['ppath']
    pos = dat['MCXData']['PhotonData']['p']
    vz = dat['MCXData']['PhotonData']['v'][:, 2]

    # Filter data by acceptance angle
    incAngle = np.degrees(np.arccos(vz))
    filtAng = (180 - incAngle) < acceptAngle
    ppath = ppath[filtAng]
    pos = pos[filtAng]
    vz = vz[filtAng]

    # Filter data by radius
    photRadSq = np.square(pos[:, 0]-vDetPos[0]) + np.square(pos[:, 1] -
                                                            vDetPos[1])
    filtDet = photRadSq <= vDetRad
    ppath = ppath[filtDet]
    pos = pos[filtDet]
    vz = vz[filtDet]

    # Calculate each index's contribution to photon weight
    factor = 0
    for kk in np.arange(0, np.shape(ppath)[1]):
        if kk == 99:  # inhere to change absorption of specific layer if needed
            factor += dat['MCXData']['Info']['LengthUnit']*ppath[:, kk] * 1000
        else:
            # also tag0 info is saved, not in ppath
            factor += dat['MCXData']['Info']['LengthUnit']*ppath[:, kk] *\
                dat['MCXData']['Info']['Media'][kk+1]['mua']
    weights = 1*np.exp(-1*factor)

    detWt = np.sum(weights)

    tomca.util.verb('Built virtual detector at: ' + str(vDetPos) + ', R = ' +
                   str(vDetRad) + ' and measured ' + str(weights.shape[0]) +
                   ' photons', verb, 3.5)

    return detWt


def bin_voxels_tmcx(jcfg, acceptAngle=45, inName='res'):
    """ This takes in a json and jdat file and returns and bins the detected
        photons like a camera into a matrix for further processing/plotting
        The variable outname is used to determine which photon data to use,
        the default is the photon data masked in 'res_replay'
        Returns:
            IM:     image matrix
            param:  json file used for simulation

        """
    import numpy as np
    import scipy.stats as st
    from src import tomca

    verb = jcfg['Expt']['verb']

    dims = jcfg['Domain']['Dim']
    tomca.util.verb('Binning photons detected', verb, 3)

    IM = np.zeros((dims[1]-1, dims[0]-1))
    ppath = jcfg[inName]['p']
    pos = jcfg[inName]['x']
    vz = np.array(jcfg[inName]['v'][:, 2])
    voxelsize = jcfg['Domain']['LengthUnit']

    # exclude unphysical numbers from rounding errors
    filtA = ((vz <= 1) & (vz >= -1))
    ppath = ppath[filtA]
    pos = pos[filtA]
    vz = vz[filtA]

    # Evaluate and filter detected photons for incoming acceptance angle
    if "acceptAngle_deg" in jcfg['Optode']['Detector']:
        acceptAngle = jcfg['Optode']['Detector']['acceptAngle_deg']
        tomca.util.verb('Using acceptance angle of ' + str(acceptAngle) +
                       ' degrees', verb, 2)
    filtB = abs(vz) >= np.cos(acceptAngle*np.pi/180)
    ppath = ppath[filtB]
    pos = pos[filtB]
    vz = vz[filtB]

    x = pos[:, 0]
    y = pos[:, 1]

    bins1 = np.arange(0, dims[1], 1)
    bins2 = np.arange(0, dims[0], 1)

    # Calculate each index's contribution to photon weight
    factor = 0
    nIndexes = np.shape(ppath)[1]
    for kk in np.arange(0, nIndexes):
        factor += voxelsize*ppath[:, kk]*jcfg['Domain']['Media'][kk+1]['mua']

    if 'w' in jcfg[inName]:
        phtWt = np.squeeze(jcfg[inName]['w'])[filtA]
        phtWt = phtWt[filtB]
        weights = phtWt*np.exp(-1*factor)
    else:
        weights = 1*np.exp(-1*factor)

    results = st.binned_statistic_2d(y, x, weights, statistic='sum',
                                     bins=[bins1, bins2], range=None)
    IM = IM + results[0]

    tomca.util.verb('Binned ' + str(np.squeeze(x.shape)) + ' photons with max: '
                   + str(np.max(IM)) + ' and min: '+str(np.min(IM)), verb, 1)
    try:
        # Bin detected photons into angle
        hist_values = tomca.stas.bin_detp_angles(jcfg, weights, inName=inName)
        return (IM, hist_values)
    except:
        return (IM, np.ones_like(weights))


def bin_detp_angles(jcfg, weights, inName='res'):
    """ This function calculates the angles of the detected photons in the z
    direction and adds them to the jcfg dictionary."""

    import numpy as np
    from src import tomca

    rise_component = -jcfg[inName]['v'][:, 2]
    run_component = (jcfg[inName]['v'][:, 0]**2 +
                     jcfg[inName]['v'][:, 1]**2)**0.5

    angles = 90/(np.pi/2)*np.arctan(rise_component/run_component)

    bins = np.arange(0, 90.5, 0.5)
    hist_values, bin_edges = np.histogram(
        angles, bins=bins, density=False, weights=weights)

    tomca.util.verb(
        'Calculated angles of detected photons in the z direction for: '
        + inName, jcfg['Expt']['verb'], 2)

    return hist_values
