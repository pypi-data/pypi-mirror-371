"""
functions which \b calculate something for a simulation.  optical properties, etc. 
"""

import numpy as np
import pandas as pd
import pmcx
from Software import tmcx
import matplotlib.pyplot as plt
from pathlib import Path
import os
import platform

if 'RESOURCES_PATH' in os.environ:
    RESOURCES_PATH = Path(os.getenv("RESOURCES_PATH", default="Resources/Spectra"))
else:
    os_name = platform.system()
    if os_name == "Linux":
        RESOURCES_PATH="/home/ra-retinalimaging/dev/mcx/Resources/Spectra"
    else:
        RESOURCES_PATH= "C:\dev\mcx\Resources\Spectra"

def interpolate_spectra_blood_wavelengths(wls: float):
    """!
    Import and interpolate blood scattering properties through wavelengths of interest for a simulation.

    This function imports a file containing blood scattering properties and interpolates these properties
    at the wavelengths specified in the input. The interpolated properties are then returned as a DataFrame.
    
    Imports blood spectrum used by literature source: @cite Bosschaart_2013.

    @param wls: numpy array of wavelengths of interest for the simulation.
    @return DataFrame: DataFrame of interpolated optical properties. The first column matches the input wavelengths
                       and the remaining columns correspond to the interpolated scattering properties, each labelled
                       with their respective units.

    @note This function relies on a properly defined RESOURCES_PATH environment variable.
    """

    bld_spectra = pd.read_csv(Path(RESOURCES_PATH) / "Extinction_scattering_blood251-1995.txt", sep="\t", decimal=".",)

    lam = np.array(bld_spectra.iloc[:, 0])
    bld_spectra_interp = pd.DataFrame()
    bld_spectra_interp.insert(0, "Wavelength (nm)", wls)
    for ii in range(1, bld_spectra.shape[1]):
        colName = bld_spectra.columns[ii]
        out = np.interp(wls, lam, np.array(bld_spectra[colName]), left=-1, right=-1)
        bld_spectra_interp.insert(ii - 1, colName, out)
        # Insert at the ith position a column which is the interpolation of WLs through the dataset Lam with the iith column.
    return bld_spectra_interp


def interpolate_spectra_blood_oxysat(StO2: float, dves: float, bloodprops: pd.DataFrame, verb: float):
    """
    Interpolate blood scattering properties (mua, mus, g) at oxygenation saturation of interest.

    @param StO2: Blood saturation
    @param dves: Average blood vessel diameter (for microvasculature; must have bf>0 as well) See section \ref sec_pigmentpacking and source \cite Rajaram2010
    @param bloodprops: Dataframe with blood spectra
    @param verb: Verbosity level for feedback

    @return hb_StO2: The configuration dictionary with the incident spectrum updated.
    """

    # Error checking
    if StO2 < 0 or StO2 > 1:
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("XXXXX ERROR: Blood Saturation Outside 0 to 1 range XXXXX")
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    # u_a
    # Name the columns to be addressed
    mua_cols = [
        "mua_Hb (mmNaN1)",
        "mua_StO2=25%",
        "mua_StO2=50%",
        "mua_StO2=75%",
        "mua_HbO2 (mmNaN1)",
    ]
    # Give the borders in the data for new spectrum
    StO2_lims = np.arange(0, 1.25, 0.25)
    # Loop through the borders to see where the given sat lies
    for ii in enumerate(StO2_lims):
        if StO2_lims[ii[0]] <= StO2 and StO2 <= StO2_lims[ii[0] + 1]:
            mua_lessOxy = np.array(bloodprops[mua_cols[ii[0]]])
            mua_moreOxy = np.array(bloodprops[mua_cols[ii[0] + 1]])

            # Weight the input spectra with the input saturation weighting, transitioning between limits
            mua_StO2 = (1 - (StO2 - StO2_lims[ii[0]]) / 0.25) * mua_lessOxy + (
                StO2 - StO2_lims[ii[0]]
            ) / 0.25 * mua_moreOxy
            
            # if there are wavelengths above 1450 in the bloodprops "Wavelength (nm)" column, then interpolate the spo2 between only the columns mua_Hb (mmNaN1) and mua_HbO2 (mmNaN1) and mua_Hb (mmNaN1).
            if bloodprops["Wavelength (nm)"].iloc[-1] > 1450:
                mua_lessOxy = np.array(bloodprops[mua_cols[0]])
                mua_moreOxy = np.array(bloodprops[mua_cols[4]])
                mua_StO2_over1450 = (1 - StO2) * mua_lessOxy + StO2 * mua_moreOxy

            #replace only the the mua_StO2 values over 1450 with the mua_StO2_over1450 values over 1450
            if bloodprops["Wavelength (nm)"].iloc[-1] > 1450:
                mua_StO2 = np.where(bloodprops["Wavelength (nm)"] > 1450, mua_StO2_over1450, mua_StO2)
            
            # Remove RBC pigment packaging factor from current data set (eq. 3 of Bosschaart)
            mua_StO2_pure_Hb = -np.log(1-mua_StO2*0.007)/0.007  # 7um is a test-found value for the effective diameter of a RBC that makes the Bosschaart data match the pure Hb data. AA, VZ 14082025
            
            # Apply Vessel pigment packaging factor from current data set
            if dves == 0:
                vessel_pigment_packing_factor = 1 # CorrectionFactor pigment
            else:
                vessel_pigment_packing_factor = 1 - np.exp(-dves * mua_StO2_pure_Hb)
                vessel_pigment_packing_factor = vessel_pigment_packing_factor / (dves * mua_StO2_pure_Hb)

            mua_StO2_corrected = mua_StO2_pure_Hb * vessel_pigment_packing_factor

            # Plot as debug
            if verb > 6:
                fig = plt.figure()
                plt.plot(
                    bloodprops["Wavelength (nm)"],
                    np.array(bloodprops[mua_cols[ii[0]]]),
                    label=mua_cols[ii[0]],
                )
                plt.plot(
                    bloodprops["Wavelength (nm)"],
                    bloodprops[mua_cols[ii[0] + 1]],
                    label=mua_cols[ii[0] + 1],
                )
                plt.plot(
                    bloodprops["Wavelength (nm)"],
                    mua_StO2_corrected,
                    label="interpolated at " + str(StO2),
                )
                plt.title("Absorption Coefficient Interpolation")
                fig.legend()
                # fig.show()

            warn = (
                "StO2 "
                + str(StO2)
                + " is between "
                + str(StO2_lims[ii[0]])
                + " and "
                + str(StO2_lims[ii[0] + 1])
            )
            tmcx.util.verb(warn, verb, 4)
            break

    # u_s
    mus_cols = ["mus_Hb (mmNaN1)","mus_StO2=25%","mus_StO2=50%","mus_StO2=75%","mus_HbO2 (mmNaN1)",]
    StO2_lims = np.arange(0, 1.25, 0.25)
    # Loop through the borders to see where the given sat lies
    for ii in enumerate(StO2_lims):
        if StO2_lims[ii[0]] <= StO2 and StO2 <= StO2_lims[ii[0] + 1]:
            mus_StO2 = (1 - (StO2 - StO2_lims[ii[0]]) / 0.25) * np.array(
                bloodprops[mus_cols[ii[0]]]
            ) + (StO2 - StO2_lims[ii[0]]) / 0.25 * np.array(
                bloodprops[mus_cols[ii[0] + 1]]
            )
            
            # if there are wavelengths above 1450 in the bloodprops "Wavelength (nm)" column, then interpolate the spo2 between only the columns mua_Hb (mmNaN1) and mua_HbO2 (mmNaN1) and mua_Hb (mmNaN1).
            if bloodprops["Wavelength (nm)"].iloc[-1] > 1450:
                mus_lessOxy = np.array(bloodprops[mus_cols[0]])
                mus_moreOxy = np.array(bloodprops[mus_cols[4]])
                mus_StO2_over1450 = (1 - StO2) * mus_lessOxy + StO2 * mus_moreOxy

            #replace only the the mus_StO2 values over 1450 with the mus_StO2_over1450 values over 1450
            if bloodprops["Wavelength (nm)"].iloc[-1] > 1450:
                mus_StO2 = np.where(bloodprops["Wavelength (nm)"] > 1450, mus_StO2_over1450, mus_StO2)
                

            if verb > 6:
                fig = plt.figure()
                plt.plot(
                    bloodprops["Wavelength (nm)"],
                    bloodprops[mus_cols[ii[0]]],
                    label=mus_cols[ii[0]],
                )
                plt.plot(
                    bloodprops["Wavelength (nm)"],
                    bloodprops[mus_cols[ii[0] + 1]],
                    label=mus_cols[ii[0] + 1],
                )
                plt.plot(
                    bloodprops["Wavelength (nm)"],
                    mus_StO2,
                    label="interpolated at " + str(StO2),
                )
                plt.title("Scattering Coefficient Interpolation")
                fig.legend()
                # fig.show()

            warn = (
                "StO2 "
                + str(StO2)
                + " is between "
                + str(StO2_lims[ii[0]])
                + " and "
                + str(StO2_lims[ii[0] + 1])
            )
            tmcx.util.verb(warn, verb, 4)
            break

    # g
    g_cols = ["g Hb", "g StO2=25%", "g StO2=50%", "g StO2=75%", "g HbO2"]
    g_lims = np.arange(0, 1.25, 0.25)
    for ii in enumerate(g_lims):
        if g_lims[ii[0]] <= StO2 and StO2 <= g_lims[ii[0] + 1]:
            g_StO2 = (1 - (StO2 - g_lims[ii[0]]) / 0.25) * np.array(
                bloodprops[g_cols[ii[0]]]
            ) + (StO2 - g_lims[ii[0]]) / 0.25 * np.array(bloodprops[g_cols[ii[0] + 1]])

            if verb > 6:
                fig = plt.figure()
                plt.plot(
                    bloodprops["Wavelength (nm)"],
                    bloodprops[g_cols[ii[0]]],
                    label=g_cols[ii[0]],
                )
                plt.plot(
                    bloodprops["Wavelength (nm)"],
                    bloodprops[g_cols[ii[0] + 1]],
                    label=g_cols[ii[0] + 1],
                )
                plt.plot(
                    bloodprops["Wavelength (nm)"],
                    g_StO2,
                    label="interpolated at " + str(StO2),
                )
                plt.title("Anisotropy Coefficient Interpolation")
                fig.legend()
                # fig.show()

            warn = ("StO2 "+ str(StO2)+ " is between "+ str(g_lims[ii[0]])+ " and "+ str(g_lims[ii[0] + 1]))
            tmcx.util.verb(warn, verb, 4)
            break

    # Build output frame
    hb_StO2 = {
        "Wavelength (nm)": bloodprops["Wavelength (nm)"],
        f"mua StO2={StO2} (mmNaN1)": mua_StO2_corrected,
        f"mus StO2={StO2} (mmNaN1)": mus_StO2,
        f"g StO2={StO2}": g_StO2,
    }

    return pd.DataFrame(hb_StO2)


def interpolate_spectrum_generic(jcfg: dict, absorber_name: str, wls: float):
    """!
    Generic interpolator from saved wavelengths to simulation wavelengths.
    
    @param jcfg: json formatted config dictionary
    @param wls: wavelengths used in the simulation
    @param absorber_name : str
        name of the absorber, currently available: water, fat, blood, bilirubin.

    @return MUA : numpy.array
        1D array of the absorbance in [mm-1]. Blood is a separate function!

    """


    # Water
    if absorber_name.lower() in ["water", "w"]:
        spectrum_range = (200, 200000)  # nm
        if wls[0] < spectrum_range[0] or wls[-1] > spectrum_range[1]:
            raise Exception("The interpolated spectral range ("+ str(wls[0])+ "nm, "+ str(wls[-1])+ "nm) is larger than the absorber ("+ absorber_name+ ") data spectral range ("+ str(spectrum_range[0])+ "nm, "+ str(spectrum_range[1])+ "nm)")
        datawater = np.loadtxt(
            Path(RESOURCES_PATH) / "water.txt",
            skiprows=5,
        )  # Spectra from 200 to 200000 nm
        lam_water = datawater[:, 0]
        ua_water = datawater[:, 1] / 10  # units are in /cm, devide by 10 to go to /mm
        MUA_water = np.interp(wls, lam_water, ua_water)
        return MUA_water

    # Fat
    elif absorber_name.lower() in ["fat", "f"]:
        spectrum_range = (429, 2449.5)  # nm
        # if LAM[0] < spectrum_range[0] or LAM[-1] > spectrum_range[1]:
        #     raise Exception("The interpolated spectral range (" + str(LAM[0]) + "nm, " + str(LAM[1]) + "nm) is larger than the absorber (" +absorber_name+ ") data spectral range (" + str(spectrum_range[0]) + "nm, " + str(spectrum_range[1]) + "nm)")

        datafat = np.loadtxt(
            Path(RESOURCES_PATH) / "fat_SWIR.txt",
            skiprows=6,
        )  # Spectra from 429 to 2449.5 nm
        lam_fat = datafat[:, 0]
        ua_fat = datafat[:, 1] / 10  # units are in /cm, devide by 10 to go to /mm
        MUA_fat = np.interp(wls, lam_fat, ua_fat)
        return MUA_fat

    # bilirubin
    elif absorber_name.lower() in ["bilirubin", "bili", "bil", "b"]:
        spectrum_range = (200, 200000)  # nm
        if wls[0] < spectrum_range[0] or wls[-1] > spectrum_range[1]:
            raise Exception("The interpolated spectral range ("+ str(wls[0])+ "nm, "+ str(wls[-1])+ "nm) is larger than the absorber ("+ absorber_name+ ") data spectral range ("+ str(spectrum_range[0])+ "nm, "+ str(spectrum_range[1])+ "nm)")
        databili = np.loadtxt(
            Path(RESOURCES_PATH) / "extinction_coefficients_betacarotene_bilirubin2.txt",
            skiprows=1,
        )
        lam = databili[:, 0]
        muaunb = (
            databili[:, 2] / 1000 / 1e6 * np.log(10)
        )  
        # values are in Per Molair per m-->divide by 1e9 to get values in per uM per mm
        # data in text file is extinction coefficient.  Multiplying by log(10) to convert.
        MUAUNB = np.interp(wls, lam, muaunb)
        return MUAUNB
    
    # collagen
    ## @cite Nazarian2024.
    elif absorber_name.lower() in ["collagen_mua", "coll_mua"]:
        
        lam, mua_collagen_lam = tmcx.impo.extracted_data(Path(RESOURCES_PATH) / "Collagen_muA_Nazarian2024_mm-1.json")

        # Boundary checking
        if lam[0] > wls[0]:
            tmcx.verb(f"!! The left side of the interpolated spectral range is lower than the collagen_mua data spectral range {wls[0]}, using musp = {round(mua_collagen_lam[0],3)}/mm for those points.", jcfg['Expt']['verb'], 0)
        if lam[-1] < wls[-1]:
            tmcx.verb(f"!! The right side of the interpolated spectral range is larger than the collagen_mua data spectral range {wls[-1]}, using musp ={round(mua_collagen_lam[-1],3)}/mm for those points.", jcfg['Expt']['verb'], 0)

        # Interpolation
        mua_collagen = np.interp(wls, lam, mua_collagen_lam, left=mua_collagen_lam[0], right=mua_collagen_lam[-1])
        
        # Convert from /cm to /mm
        mua_collagen = mua_collagen / 10
        
        return mua_collagen
    
    elif absorber_name.lower() in ["collagen_musp", "coll_musp"]:

        lam, musp_collagen_lam = tmcx.impo.extracted_data(Path(RESOURCES_PATH) / "Collagen_muSp_Nazarian2024_mm-1.json")
        
        # Boundary checking
        if lam[0] > wls[0]:
            tmcx.verb(f"!! The left side of the interpolated spectral range is lower than the collagen_musp data spectral range {wls[0]}, using musp = {round(musp_collagen_lam[0],3)}/mm for those points.", jcfg['Expt']['verb'], 0)
        if lam[-1] < wls[-1]:
            tmcx.verb(f"!! The right side of the interpolated spectral range is larger than the collagen_musp data spectral range {wls[-1]}, using musp = {round(musp_collagen_lam[-1],3)}/mm for those points.", jcfg['Expt']['verb'], 0)
        
        # Interpolation
        musp_collagen = np.interp(wls, lam, musp_collagen_lam, left=musp_collagen_lam[0], right=musp_collagen_lam[-1])
                                  
        # Convert from /cm to /mm
        musp_collagen = musp_collagen / 10
        
        return musp_collagen    
    
    elif absorber_name.lower() in ["bone_mua"]:
        
        lam, mua_bone_lam = tmcx.impo.extracted_data(Path(RESOURCES_PATH) / "Bone_mua_Dolenec2019_mm-1.json")
        
        # Boundary checking
        if lam[0] > wls[0]:
            tmcx.verb(f"!! The left side of the interpolated spectral range  is lower than the bone_mua data spectral range {wls[0]}, using musa = {round(mua_bone_lam[0],3)}/mm for those points.", jcfg['Expt']['verb'], 0)
        if lam[-1] < wls[-1]:
            tmcx.verb(f"!! The right side of the interpolated spectral range is larger than the bone_mua data spectral range {wls[-1]}, using musa = {round(mua_bone_lam[-1],3)}/mm for those points.", jcfg['Expt']['verb'], 0)
        
        # Interpolation
        mua_bone = np.interp(wls, lam, mua_bone_lam, left=mua_bone_lam[0], right=mua_bone_lam[-1])             
        
        return mua_bone
    
    elif absorber_name.lower() in ["bone_mus"]:
        
        lam, mus_bone_lam = tmcx.impo.extracted_data(Path(RESOURCES_PATH) / "Bone_mus_Dolenec2019_mm-1.json")
        
        # Boundary checking
        if np.floor(lam[0]) > np.round(wls[0]):
            tmcx.verb(f"!! The left side of the interpolated spectral range is lower than the bone_mus data spectral range {wls[0]}, using musp = {round(mus_bone_lam[0],3)}/mm for those points.", jcfg['Expt']['verb'], 0)
        if np.floor(lam[-1]) < np.round(wls[-1]):
            tmcx.verb(f"!! The right side of the interpolated spectral range is larger than the bone_mus data spectral range {wls[-1]}, using musp = {round(mus_bone_lam[-1],3)}/mm for those points.", jcfg['Expt']['verb'], 0)
        
        # Interpolation
        mus_bone = np.interp(wls, lam, mus_bone_lam, left=mus_bone_lam[0], right=mus_bone_lam[-1])             
        
        return mus_bone
    
    elif absorber_name.lower() in ["emel"]:
        # interpolate spectrum of epsilon (molar extinction coefficient) [mm^-1/(mol/L)] for eumelanin @cite Ansari2011. RPE = eumelanin
        lam, eps_eumel_lam = tmcx.impo.extracted_data(Path(RESOURCES_PATH) / "eumelanin_molar_ext_Ansari2011.json")
        eps_eumel_lam = [value / 10 for value in eps_eumel_lam] # convert to mm^-1 (current units is cm^-1/M)

        # Boundary checking
        if np.floor(lam[0]) > np.round(wls[0]):
            tmcx.verb(f"!! The left side of the interpolated spectral range is lower than the eumel_eps data spectral range {wls[0]}, using left bound value = {round(eps_eumel_lam[0],3)}/mm for those points.", jcfg['Expt']['verb'], 0)
        if np.floor(lam[-1]) < np.round(wls[-1]):
            tmcx.verb(f"!! The right side of the interpolated spectral range is larger than the eumel_eps data spectral range {wls[-1]}, using right bound value = {round(eps_eumel_lam[-1],3)}/mm for those points.", jcfg['Expt']['verb'], 0)
        
        # Interpolation
        eps_eumelanin = np.interp(wls, lam, eps_eumel_lam, left=eps_eumel_lam[0], right=eps_eumel_lam[-1])             
        
        return eps_eumelanin
    
    elif absorber_name.lower() in ["pmel"]:
        # interpolate spectrum of epsilon (molar extinction coefficient) [mm^-1/(mol/L)] for pheomelanin @cite Ansari2011. Choroid = pheomelanin

        lam, eps_pheomel_lam = tmcx.impo.extracted_data(Path(RESOURCES_PATH) / "pheomelanin_molar_ext_Ansari2011.json")
        eps_pheomel_lam = [value / 10 for value in eps_pheomel_lam] # convert to mm^-1 (current units is cm^-1/M)
        
        # Boundary checking
        if np.floor(lam[0]) > np.round(wls[0]):
            tmcx.verb(f"!! The left side of the interpolated spectral range is lower than the pheomel_eps data spectral range {wls[0]}, using left bound value = {round(eps_pheomel_lam[0],3)}/mm for those points.", jcfg['Expt']['verb'], 0)
        if np.floor(lam[-1]) < np.round(wls[-1]):
            tmcx.verb(f"!! The right side of the interpolated spectral range is larger than the pheomel_eps data spectral range {wls[-1]}, using right bound value = {round(eps_pheomel_lam[-1],3)}/mm for those points.", jcfg['Expt']['verb'], 0)
        
        # Interpolation
        eps_pheomelanin = np.interp(wls, lam, eps_pheomel_lam, left=eps_pheomel_lam[0], right=eps_pheomel_lam[-1])             
        
        return eps_pheomelanin

    else:
        raise Exception("absorber_name not in the list of available absorbers")


def mua_melanosome(wls, type="skin"):
    """!
    @brief Evaluate absorption coefficient of melanosome interior at specified wavelengths.
     
    Taken directly from section <em>1.2 Absorption coefficient of a single melanosome, mua.mel</em> in @cite Jacques1998

    @param wls: Array of wavelengths.
    @param type: Model description. Defaults to "skin".

    @return Array of absorption coefficients evaluated at each input wavelength.
    """

    uaMel = 6.6 * (10**10) * (wls ** (-3.33))

    # if type == "retina":
    #     uaMel = 1.70 * (10 ** 11) * (wls ** (-3.48)) # source shows as /cm
    # else:
    #     #skin 
    #     uaMel = 6.49 * (10 ** 11) * (wls ** (-3.48)) # source shows as /cm

    return uaMel

def try_evaluate_media_prop(jcfg, mediaPropName, media_idx):
    """
    This function looks for a key variable by name in the domain media and updates the media index.

    @param jcfg: Configuration dictionary.
    @param mediaPropName: Name of the media property.
    @param media_idx: Index of the media to update in media list.

    @return: The updated media index.
    """
    propOut = 0
    try:
        prop_jsonEntry = jcfg["Domain"]["Media"][media_idx][mediaPropName]
    except KeyError:
        propOut = 0
    else:
        
        varName = mediaPropName + "0"
        if varName in str(prop_jsonEntry):
            # Try to find a default property variable in the domain media.
            exec(varName + "= jcfg['Domain'][varName]")
            propOut = eval(prop_jsonEntry)
            # find a match with the string in Domain, if it's there it assigns that value to the layer. Like capillary Hb
        elif prop_jsonEntry in jcfg["Domain"]:
            propOut = jcfg["Domain"][prop_jsonEntry]
        else:
            # Just use the value in the entry
            propOut = prop_jsonEntry
    if mediaPropName in ["bf", "water", "iL_f", "fat"]:
        ## @cite Campbell2017
        layerLabel=jcfg["Domain"]["Media"][media_idx]['label']
        if propOut < 0:
            tmcx.util.verb(f"!! {mediaPropName} in {layerLabel} calculated to be negative.  Truncated to 0.",jcfg['Expt']['verb'],0)
            propOut=0
        if propOut > 1:
            tmcx.util.verb(f"!! {mediaPropName} in {layerLabel} calculated to be greater than 1.  Truncated to 1.",jcfg['Expt']['verb'],0)
            propOut= 1
    return propOut

def mu_abs_scatt(jcfg):
    """!
    @brief Calculate the absorption and scattering coefficients for a given media configuration.

    This function calculates the absorption and scattering coefficients for each media type in the given configuration. 
    It uses the absorption and scattering properties of various media types such as blood, melanin, bilirubin, fat, water, and intralipid.
    
    Normalizes blood data according to the source of the data, @cite Bosschaart_2013 <em>The data we have is measured for 45% volume RBC, at 15.5g/dL.</em>.  More details in section \ref sec_bloodSpectra 
    
    @param jcfg Configuration dictionary. The following keys are used:
        - 'Optode' (dict): Contains the source spectrum and base wavelengths.
            - 'Source' (dict): Contains the source spectrum.
                - 'Spectrum' (pandas.DataFrame): DataFrame containing the source spectrum.
        - 'Domain' (dict): Contains the media configuration.
            - 'Media' (list): List of media configurations. Each media configuration is a dict containing the media properties.
            - 'Scattering' (dict): Contains the scattering properties.
        - 'Expt' (dict): Contains the experiment configuration.

    @return The configuration dictionary with the absorption and scattering coefficients updated.

    @note The function modifies the configuration in place, adding the calculated absorption and scattering coefficients.

    @throws Exception If the sum of all absorbers fraction is greater than 1.
    
    @todo break this function up into absorption and scattering functions.
    
    """
    # First import the source spectrum and base wls
    source = jcfg["Optode"]["Source"]["Spectrum"]
    wls = np.array(source.iloc[:, 0])
    source_norm = source.iloc[:, 1] / sum(source.iloc[:, 1])

    # Initialize plot absorption spectra used
    plt_muASpectra = plt.figure()
    plt.plot(wls, source_norm, label="Source")
    plt.ylabel("$\\mu_a$ ($mm^{-1}$)")
    plt.xlabel("Wavelength (nm)")
    plt.yscale("log")
    plt.ylim([1e-6, 1e4])
    
    # Initialize plot scattering spectra used
    plt_muSSpectra = plt.figure()
    plt.plot(wls, source_norm, label="Source")
    plt.ylabel("$\\mu_S$ ($mm^{-1}$)")
    plt.xlabel("Wavelength (nm)")
    plt.yscale("log")
    plt.ylim([1e-6, 1e4])

    plt_bfrac = 1
    plt_bili_f = 1
    plt_fat_f = 1
    plt_mel_f = 1
    plt_emel = 1
    plt_pmel = 1
    plt_h20_f = 1
    plt_iL_f = 1
    plt_collagen_f = 1
    plt_bone_f=1

    # For each media type
    for iiMedia in enumerate(jcfg["Domain"]["Media"]):
        layerLabel=jcfg["Domain"]["Media"][iiMedia[0]]['label']
        layer_comp=[]
        layer_comp_labels=[]
        layer_comp_mua=[]
        
        # write_mua determines whether mua in the media index is overwritten, this update requires that we put "calc" in fields that we want to be calculated, otherwise it uses the input values
        write_mua = 0
        if jcfg["Domain"]["Media"][iiMedia[0]]['mua'] == "calc":
            write_mua = 1

        ## Absorption

        ## Blood 
        media_idx=iiMedia[0]
        bFrac = try_evaluate_media_prop(jcfg, "bf", media_idx)
        bConc = try_evaluate_media_prop(jcfg, "HbConcGpdL", media_idx)
        sat = try_evaluate_media_prop(jcfg, "sat", media_idx)
        dves = try_evaluate_media_prop(jcfg, "dves", media_idx)
        
        jcfg["Domain"]["Media"][iiMedia[0]]['bf_eff'] = bFrac
        jcfg["Domain"]["Media"][iiMedia[0]]['sat_eff'] = sat
        jcfg["Domain"]["Media"][iiMedia[0]]['dves_eff'] = dves
        

        if bFrac > 0 and sat >= 0:
            bloodprops = interpolate_spectra_blood_wavelengths(wls)
            
            if plt_bfrac == 1:
                plt.figure(plt_muASpectra)
                plt.plot(wls, bloodprops.iloc[:, 1], 'b',label="Hb")
                plt.plot(wls, bloodprops.iloc[:, 0], 'r', label="HbO2")
                plt_bfrac = 0
                
            ## Interpolate blood spectrum at saturation
            hbStO2 = interpolate_spectra_blood_oxysat(sat, dves, bloodprops, jcfg["Expt"]["verb"])
            
            ## Reduce absorption spectrum by blood fraction (bf) \cite Jacques1998
            ua_Hb = hbStO2.iloc[:, 1] * bFrac
            
            ## account for changes in hemoglobin concentration
            # @cite Bosschaart_2013 The data we have is measured for 45% volume RBC, at 15.5g/dL. 
            ua_Hb = ua_Hb * bConc / 15.5
                        
            layer_comp.append(bFrac)
            layer_comp_labels.append("bf")
            layer_comp_mua.append(round(sum(ua_Hb * source_norm),4))
            
            write_mua = 1
        else:
            ua_Hb = 0
            bFrac = 0

        ## Eumelanin "emel"
        melConc = try_evaluate_media_prop(jcfg, "emel", media_idx)
        if melConc > 0: #not a fraction but conc
            ua_emel = np.log(10) * melConc * interpolate_spectrum_generic(jcfg, "emel", wls)  # log(10) is conversion factor because molar ext. coeff is measure base(10) whereas mu_a is base(e) (Lambert-Beer)
            if plt_emel == 1: # only plot it for the first layer that the mel is in; once plotted, changed to 0 so it's not plotted again
                plt.figure(plt_muASpectra)
                plt.plot(wls, ua_emel, label="Eumelanin")
                plt_emel = 0

            layer_comp.append(melConc) # 
            layer_comp_labels.append("emel")
            layer_comp_mua.append(round(sum(ua_emel * source_norm),4)) # tracks mu_a contribution to mu_a of each layer .
            
            write_mua = 1
        else:
            ua_emel = 0

        ## Eumelanin "pmel"
        melConc = try_evaluate_media_prop(jcfg, "pmel", media_idx)
        if melConc > 0: #concentration in [mmol*L^-1]
            ua_pmel = np.log(10) * melConc * interpolate_spectrum_generic(jcfg, "pmel", wls)
            if plt_pmel == 1: # only plot it for the first layer that the mel is in; once plotted, changed to 0 so it's not plotted again
                plt.figure(plt_muASpectra)
                plt.plot(wls, ua_pmel, label="Pheomelanin")
                plt_pmel = 0

            layer_comp.append(melConc) # 
            layer_comp_labels.append("mel")
            layer_comp_mua.append(round(sum(ua_pmel * source_norm),4)) # tracks mu_a contribution to mu_a of each layer .
            
            write_mua = 1 # this ensures that melanin is taken into account when mu_a = 'calc' in model .json
        else:
            ua_pmel = 0

        ##  melanosomes "mel" - given in fraction
        mel_f = try_evaluate_media_prop(jcfg, "mel", media_idx)
        if mel_f > 0:
            uaMelSpect = mua_melanosome(wls)
            if plt_mel_f == 1:
                plt.figure(plt_muASpectra)
                plt.plot(wls, uaMelSpect, label="Melanin")
                plt_mel_f = 0
            # Multiply spectrum by mel conc.
            ua_mel = mel_f * uaMelSpect
            
            layer_comp.append(mel_f)
            layer_comp_labels.append("mel")
            layer_comp_mua.append(round(sum(ua_mel * source_norm),4))
            
            write_mua = 1
        else:
            ua_mel = 0
            mel_f = 0

        # Bili
        # Bili_f should be in units uM. 
        
        bili_f = try_evaluate_media_prop(jcfg, "bili",media_idx)
        if bili_f > 0:
            uaBiliSpect = interpolate_spectrum_generic(jcfg, "bili", wls)
            if plt_bili_f == 1:
                plt.figure(plt_muASpectra)
                plt.plot(wls, uaBiliSpect, label="Bili")
                plt_bili_f = 0
            # Multiply spectrum by conc.
            ua_Bili = bili_f / 1e-6 *  uaBiliSpect

            layer_comp.append(bili_f)
            layer_comp_labels.append("bili")
            layer_comp_mua.append(round(sum(ua_Bili * source_norm),4))
            
            write_mua = 1
        else:
            ua_Bili = 0
            bili_f = 0

        # Fat
        notFat_f=bFrac
        fat_f = try_evaluate_media_prop(jcfg, "fat",media_idx)
        # Evaluate how much space is left outside of blood fraction
        if notFat_f + fat_f > 1:
            tmcx.util.verb(f"!! fat_f + notfat_f > 1 in {layerLabel}.  fat_f adjusted from {fat_f} to {1-notFat_f}.",jcfg['Expt']['verb'],0)
            jcfg["Domain"]["Media"][iiMedia[0]]['fat']=1-notFat_f
            fat_f=jcfg["Domain"]["Media"][iiMedia[0]]['fat']
            
        if fat_f > 0:
            uaFatSpect = interpolate_spectrum_generic(jcfg, "fat", wls)
            if plt_fat_f == 1:
                plt.figure(plt_muASpectra)
                plt.plot(wls, uaFatSpect, label="Fat")
                plt_fat_f = 0
            # Multiply spectrum by fat conc.
            ua_fat = fat_f * uaFatSpect
            
            layer_comp.append(fat_f)
            layer_comp_labels.append("fat")
            layer_comp_mua.append(round(sum(ua_fat * source_norm),4))
            
            write_mua = 1
        else:
            ua_fat = 0
            fat_f = 0
            
        # Collagen
        notCollagen_f=notFat_f + fat_f
        collagen_f = try_evaluate_media_prop(jcfg, "collagen",media_idx)
        # Evaluate how much space is left outside of blood fraction
        if notCollagen_f + collagen_f > 1:
            tmcx.util.verb(f"!! collagen_f + notCollagen_f > 1 in {layerLabel}.  collagen_f adjusted from {collagen_f} to {1-notCollagen_f}.",jcfg['Expt']['verb'],0)
            jcfg["Domain"]["Media"][iiMedia[0]]['collagen']=1-notCollagen_f
            collagen_f=jcfg["Domain"]["Media"][iiMedia[0]]['collagen']
            
        if collagen_f > 0:
            ua_collagen_spect = interpolate_spectrum_generic(jcfg, "collagen_mua", wls)
            if plt_collagen_f == 1:
                plt.figure(plt_muASpectra)
                plt.plot(wls, ua_collagen_spect, label="Collagen")
                plt_collagen_f = 0
            # Multiply spectrum by fat conc.
            ua_collagen = collagen_f * ua_collagen_spect
            
            layer_comp.append(collagen_f)
            layer_comp_labels.append("collagen")
            layer_comp_mua.append(round(sum(ua_collagen * source_norm),4))
            
            write_mua = 1
        else:
            ua_fat = 0
            ua_collagen = 0
            
                    
        # Bone 
        notBone_f=notCollagen_f + collagen_f
        bone_f = try_evaluate_media_prop(jcfg, "bone",media_idx)
        if bone_f > 0:
            uaBoneSpect = interpolate_spectrum_generic(jcfg, "bone_mua", wls)
            if plt_bone_f == 1:
                plt.figure(plt_muASpectra)
                plt.plot(wls, uaBoneSpect, label="Bone")
                plt_bone_f = 0
            # Multiply spectrum by fat conc.
            ua_bone = bone_f * uaBoneSpect
            
            layer_comp.append(bone_f)
            layer_comp_labels.append("bone")
            layer_comp_mua.append(round(sum(ua_bone * source_norm),4))
            
            write_mua = 1
        else:
            ua_bone = 0
            bone_f = 0

        # Water
        uaWaterSpect = interpolate_spectrum_generic(jcfg, "water", wls)
        
        notWater_f=notBone_f + bone_f
        water_f = try_evaluate_media_prop(jcfg, "water",media_idx)
        # Check if there is volume left for water
        if notWater_f + water_f > 1:
            tmcx.util.verb(f"!! water_f + notWater_f > 1 in {layerLabel}.  water_f adjusted from {water_f} to {1-notWater_f}.",jcfg['Expt']['verb'],0)
            jcfg["Domain"]["Media"][iiMedia[0]]['water']=1-notWater_f
            water_f=jcfg["Domain"]["Media"][iiMedia[0]]['water']
        
        iL_f = try_evaluate_media_prop(jcfg, "iL_f",media_idx)
        if water_f > 0 or iL_f > 0:
            ua_water = water_f * uaWaterSpect
            
            layer_comp.append(water_f)
            layer_comp_labels.append("water")
            layer_comp_mua.append(round(sum(ua_water * source_norm),4))
            
            write_mua = 1
            if plt_h20_f == 1:
                plt.figure(plt_muASpectra)
                plt.plot(wls, uaWaterSpect, label="Water")
                plt_h20_f = 0
        else:
            ua_water = 0
            water_f = 0

        # IL
        notiL_f=(notWater_f+water_f)
        # Check if there is volume left for IL
        if notiL_f + iL_f > 1:
            tmcx.util.verb(f"!! iL_f + notiL_f > 1 in {layerLabel}.  iL_f adjusted from {iL_f} to {1-notiL_f}.",jcfg['Expt']['verb'],0)
            jcfg["Domain"]["Media"][iiMedia[0]]['iL_f']=1-notiL_f
            iL_f=jcfg["Domain"]["Media"][iiMedia[0]]['iL_f']
        
        if iL_f > 0:
            # iL_f is defined as the fraction of IL 20%.
            # Typically IL is sold at a conc of 0.2 and cut further with water.  Eg. 50% IL20% and 50% water
            # would have iL_f = 0.5.
            uaOil = mua_soybeanOil(wls)
            ua_iL = 0.2 * iL_f * uaOil + (1 - (0.2 * iL_f)) * uaWaterSpect
            
            layer_comp.append(iL_f)
            layer_comp_labels.append("iL_f")
            layer_comp_mua.append(round(sum(ua_iL * source_norm),4))
            
            if plt_iL_f == 1:
                plt.figure(plt_muASpectra)
                plt.plot(wls, uaOil, label="Soy oil")
                plt.plot(wls, 0.2 * uaOil + (1 - (0.2)) * uaWaterSpect, label="IL 100%")
                plt_iL_f = 0
            write_mua = 1
        else:
            ua_iL = 0
            iL_f = 0


        # Multiply ua by source and return
        if write_mua:
            ua_tot = ua_Hb + ua_mel + ua_emel + ua_pmel + ua_fat + ua_Bili + ua_water + ua_iL + ua_collagen + ua_bone
            
            tmcx.util.verb(
                'Calculated absorption components for '+ jcfg["Domain"]["Media"][iiMedia[0]]["label"]
                , jcfg['Expt']['verb'], 2)
                        
            tmcx.util.verb(f'Absorption components: ' + str(layer_comp_labels), jcfg['Expt']['verb'], 3)
            tmcx.util.verb(f'Component fractions: ' + str(np.round(layer_comp,3)), jcfg['Expt']['verb'], 3.5)
            tmcx.util.verb(f'Absorption component mua\'s: ' + str(np.round(layer_comp_mua,3)), jcfg['Expt']['verb'], 3.5)
            
            jcfg["Domain"]["Media"][iiMedia[0]]["layer_comp_labels"]=layer_comp_labels
            jcfg["Domain"]["Media"][iiMedia[0]]["layer_comp_fracs"]=layer_comp
            jcfg["Domain"]["Media"][iiMedia[0]]["layer_comp_mua"]=layer_comp_mua

            jcfg["Domain"]["Media"][iiMedia[0]]["mua"] = sum(ua_tot * source_norm)

            # Plot this layer on the absorption spectra plot
            if jcfg["Domain"]["Media"][iiMedia[0]]["mua"] > 0:
                plt.figure(plt_muASpectra)
                plt.plot(wls,ua_tot,"--",label=["eval_" + jcfg["Domain"]["Media"][iiMedia[0]]["label"]],)
        
        if water_f + bili_f + fat_f  + bFrac + iL_f > 1:
            print(
                f"Error: sum all absorbers fraction is > 1\nbf = {bFrac}, water = {water_f}, fat = {fat_f}, bili = {bili_f}, IL = {iL_f}, collagen = {collagen_f}, bone = {bone_f}"
            )

        ## Scattering
        usp_collagen_spect = None
        if "collagen" in jcfg["Domain"]["Media"][iiMedia[0]]:
            if jcfg["Domain"]["Media"][iiMedia[0]]["collagen"] > 0:
                if jcfg["Domain"]["Media"][iiMedia[0]]["musp"] == "calc":
                    usp_collagen_spect = interpolate_spectrum_generic(jcfg, "collagen_musp", wls)
                    # Cut the scattering fraction by the collagen fraction
                    usp_collagen_spect = usp_collagen_spect * collagen_f
            else: 
                jcfg["Domain"]["Media"][iiMedia[0]]["collagen"] = 0
        
        us_bone_spect = None
        if bone_f > 0:
            us_bone_spect = interpolate_spectrum_generic(jcfg, "bone_mus", wls)
            # Cut the scattering fraction by the collagen fraction
            us_bone_spect = us_bone_spect * bone_f
        else: 
            jcfg["Domain"]["Media"][iiMedia[0]]["bone"] = 0
                
        
        
        # Calculate the scattering function's spectral shape
        a1 = jcfg["Domain"]["Scattering"]["a1"]
        a2 = jcfg["Domain"]["Scattering"]["a2"]
        a3 = jcfg["Domain"]["Scattering"]["a3"]
        lam0 = jcfg["Domain"]["Scattering"]["lam0"]
        
        if 'a1' in jcfg["Domain"]["Media"][iiMedia[0]]:
            a1 = jcfg["Domain"]["Media"][iiMedia[0]]['a1']
        if 'a2' in jcfg["Domain"]["Media"][iiMedia[0]]:
            a2 = jcfg["Domain"]["Media"][iiMedia[0]]['a2']
        if 'a3' in jcfg["Domain"]["Media"][iiMedia[0]]:
            a3 = jcfg["Domain"]["Media"][iiMedia[0]]['a3']
        if 'lam0' in jcfg["Domain"]["Media"][iiMedia[0]]:
            lam0 = jcfg["Domain"]["Media"][iiMedia[0]]['lam0']

        uSProfile = (a1* ((wls / lam0) ** a2)+ a3)
        
        # Retrieve all relevant scattering factors from model
        mus0 = jcfg["Domain"]["Media"][iiMedia[0]].get("mus0", None)
        mus_factor = jcfg["Domain"].get("mus_factor", 1)
        musp = jcfg["Domain"]["Media"][iiMedia[0]].get("musp", None)
        g_factor = jcfg["Domain"]["Media"][iiMedia[0]].get("g", None)
        
        if usp_collagen_spect is not None:
            musp=usp_collagen_spect
            uSProfile=1
            tmcx.util.verb(f"Using collagen spectral musp rather than jcfg musp directly.",jcfg['Expt']['verb'],3)	
            
        if us_bone_spect is not None:
            mus0=us_bone_spect
            uSProfile=1
            tmcx.util.verb(f"Using bone spectral mus rather than jcfg mus directly.",jcfg['Expt']['verb'],3)

        # muS0: the fundamental scattering length
        if mus0 is not None:
            mus0 *= mus_factor
            mus0_spect = mus0 * uSProfile
            plt.figure(plt_muSSpectra)
            plt.plot(wls, mus0_spect, label=layerLabel)
            mus=sum(mus0_spect*source_norm)
            tmcx.util.verb(f"Using mus_factor {mus_factor} with mus0 amplitude for mus {mus}",jcfg['Expt']['verb'],3)

        # muSprime: componded scattering coefficient with the g factor
        elif musp is not None and g_factor is not None:
            musp *= mus_factor
            musp_spect = musp * uSProfile
            mus_spect = musp_spect / (1 - g_factor)
            plt.figure(plt_muSSpectra)
            plt.plot(wls, mus_spect, label=layerLabel)
            mus = sum(mus_spect*source_norm)
            if len(mus_spect) >1:
                muspDisp='from spectral file'
            else: 
                muspDisp=musp
            tmcx.util.verb(f"Using mus_factor {mus_factor} with musp amplitude {muspDisp} and g {g_factor} for mus {mus}",jcfg['Expt']['verb'],3)
        # Uses input mus directly from the model jcfg
        else:
            mus = jcfg["Domain"]["Media"][iiMedia[0]]["mus"]
            tmcx.util.verb(f"Using mus directly from jcfg model, {mus}",jcfg['Expt']['verb'],3)

        # Assign mus
        jcfg["Domain"]["Media"][iiMedia[0]]["mus"] = mus

        # Change pure blood properties
        if jcfg["Domain"]["Media"][iiMedia[0]]["label"] == "Blood":
            jcfg["Domain"]["Media"][iiMedia[0]]["g"] = sum(hbStO2.iloc[:, 3] * source_norm)
            jcfg["Domain"]["Media"][iiMedia[0]]["mus"] = sum(hbStO2.iloc[:, 2] * source_norm)

        # Change 20% IL scattering properties
        if iL_f > 0:
            lam_tmp = [300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
            nWaterSpect_tmp = [1.349,1.343,1.339,1.34,1.339,1.337,1.334,1.332,1.3298,1.3279,1.326,1.3248,1.3235,1.3224,1.3214]  # from https://refractiveindex.info/?shelf=main&book=H2O&page=Hale for lam <400 and from Kienle for Lam > 400
            nWaterSpect = np.interp(wls, lam_tmp, nWaterSpect_tmp)

            nILSpect = (
                nWaterSpect + 0.14 * 0.2 * iL_f
            )  # The difference bw water and oil is a constant 0.14.  This gets cut by the water fraction of IL and conc evaluated.
            jcfg["Domain"]["Media"][iiMedia[0]]["n"] = sum(nILSpect * source_norm)

            g_IL = g_intralipid(wls)
            jcfg["Domain"]["Media"][iiMedia[0]]["g"] = sum(g_IL * source_norm)

            usp_IL20pct = musp_intralipid(wls) * iL_f
            mus_spect_IL = usp_IL20pct / (1 - g_IL)
            plt.figure(plt_muSSpectra)
            plt.plot(wls, mus_spect_IL, label=layerLabel)
            mus = sum(mus_spect_IL*source_norm)
            jcfg["Domain"]["Media"][iiMedia[0]]["mus"] = mus
            

    if jcfg['Expt']['verb']>=1.5:
        plt.figure(plt_muASpectra)
        plt_muASpectra.legend(loc="upper left", bbox_to_anchor=(0.9, 0.9))
        plt.grid(visible=True)
        plt.minorticks_on()
        plt.grid(visible=True, which='minor', axis='both', linestyle=':', linewidth=0.5)
        plt.minorticks_on()
        plt.tick_params(axis='both', which='minor', length=4, width=1)
        plt.tick_params(axis='both', which='major', length=7, width=1.5)
        plt.gca().xaxis.set_minor_locator(plt.MultipleLocator(10))
        plt.gca().yaxis.set_minor_locator(plt.LogLocator(base=10.0, subs=np.arange(1.0, 10.0) * 0.1, numticks=100))
        
        if 'write' in jcfg['Expt']:
            if 'fig_spectra_mua' in jcfg['Expt']['write']:
                if jcfg['Expt']['write']['fig_spectra_mua']:
                    tmcx.writ.fig(jcfg, plt_muASpectra, "spectra_mua")
        else:
            tmcx.writ.fig(jcfg, plt_muASpectra, "spectra_mua")
        
        plt.figure(plt_muSSpectra)
        plt_muSSpectra.legend(loc="upper left", bbox_to_anchor=(0.9, 0.9))
        plt.grid(visible=True)
        if 'write' in jcfg['Expt']:
            if 'fig_spectra_mus' in jcfg['Expt']['write']:
                if jcfg['Expt']['write']['fig_spectra_mus']:
                    tmcx.writ.fig(jcfg, plt_muSSpectra, "spectra_muS")
        else:
            tmcx.writ.fig(jcfg, plt_muSSpectra, "spectra_muS")
            
    plt.close('all')
    
    return jcfg

def musp_intralipid(wls: float):
    """!
    Function to evaluate mu_S *prime* of intralipid 20%.

    From table 5 in @cite Michels_2008.

    @param wls: Wavelengths to evaluate usp at.

    @return: usp vector.
    """

    y_0 = 8.261e1
    a = -1.288e-1
    b = 6.093e-5

    return y_0 + a * wls + b * wls**2


def mua_soybeanOil(wls: float):
    """!
    Function to evaluate usp of intralipid 20%.

    From table 6 in @cite Michels_2008.

    Typical processing:
    mua_soybeanOil = calc.mua_soybeanOil(wls)
    mua_IL0 = 0.2*mua_soybeanOil + 0.8*MUAWATER
    ...dilute further with water...

    @param wls: Wavelengths to evaluate at.

    @return: mua value for undiluted intralipid.
    """
    a = 1.171e5
    b = -3.659e1
    x_0 = -3.210e2

    return a / (1 + np.e ** (-(wls - x_0) / b))


#TODO: Remove unused function
def g_intralipid(wls: float):
    """!
    Function to evaluate g of intralipid 20%.

    From table 3 in \cite Michels_2008.

    @param wls: Wavelengths to evaluate at.

    @return: mua value for undiluted intralipid.
    """

    gSpect = 1.09 - 6.812e-4 * wls  # Kienle

    return gSpect


def il_f_from_muS(muS: float, wl: float):
    """!
    @brief Function to evaluate the IL fraction of intralipid 20% for a specific muS at a specific WL.

    From table 4 in \cite Michels_2008  
    muS=(3.873e8*wl^-2.397e0)*il_f
    il_f=muS/(3.873e8*wl^-2.397e0)

    @param muS: Desired muS. Can be a list of muS to evaluate
    @param wl: Wavelengths to evaluate at

    @return: mua value for undiluted intralipid. List returned if multiple muS
    """

    il_f = []
    for muS in muS:
        fmt_ilf = float("{:.5g}".format(muS / (3.873e8 * pow(wl, -2.397e0))))
        il_f.append(fmt_ilf)

    return il_f


def img_detectors(jcfg: dict):
    if "imgDetectors" in jcfg['Optode']:
        if "type" in jcfg["Optode"]["imgDetectors"]:
            if jcfg["Optode"]["imgDetectors"]["type"]=='donut':
                jcfg=tmcx.anly.img_detectors_donut(jcfg)
            else:
                # Evaluate detection points on image generated
                jcfg['Optode']['imgDetectors']['Pos']=[]
                for pitch in jcfg['Optode']['imgDetectors']['Pitches']:
                    jcfg['Optode']['imgDetectors']['Pos'].append([jcfg['Optode']['Source']['Pos'][0]+pitch/jcfg['Domain']['LengthUnit'],jcfg['Optode']['Source']['Pos'][1]])

                # Evaluate average photons detected at each image detector, save to jcfg
                jcfg['res']['imgDetectors']={}
                jcfg=tmcx.anly.image_detectors(jcfg, jcfg['Optode']['imgDetectors']['Pos'], jcfg['Optode']['imgDetectors']['R']/jcfg['Domain']['LengthUnit'])
            
        tmcx.util.verb('Evaluated detectors in post processing', jcfg['Expt']['verb'], 1)
        
    return jcfg

#TODO: Remove unused function   
def conffun(z: float, zf: float, zR: float) -> float:
    """!
    Confocal function for SMF detection from calculating overlap SMF mode and coherently or incoherently
    backpropageted SMF mode (reflected beam). zR and zf are the Rayleigh range and focus postion of the
    SMF mode at the reflection surface!!!.

    Args:
        z (float): The depth at which the function is evaluated.
        zf (float): The focus position of the SMF mode at the reflection surface.
        zR (float): The Rayleigh range of the SMF mode at the reflection surface.

    Returns:
        float: The value of the confocal function at the given depth.
    """
    return 1 / (1 + ((z - zf) / zR) ** 2)


def SinglyScatModel(A: float, z: float, zf: float, zR: float, mut: float) -> float:
  """!
  Returns for a homogeneous medium the backscattered intensity of singly scattered photons with confocal function applied.
  z distance from sample surface, zf, a parameter of the Gaussian beam at the backscatter plane,
  the focus position w.r.t. sample surface. zR, a parameter of the Gaussian beam at the backscatter plane,
  the Rayleigh range. mut the attenuation coefficient of the medium

  Args:
      A (float): The initial intensity of the photons.
      z (float): The distance from the sample surface.
      zf (float): The focus position of the Gaussian beam at the backscatter plane.
      zR (float): The Rayleigh range of the Gaussian beam at the backscatter plane.
      mut (float): The attenuation coefficient of the medium.

  Returns:
      float: The backscattered intensity of singly scattered photons with the confocal function applied.
  """
  conf = conffun(z, zf, zR)
  Aline = A * conf * np.exp(-2 * mut * z)
  return Aline


def I_Gausbeam(w0: float, zR: float, x0: float, y0: float, z0: float, x1: float = 0, y1: float = 0, z1: float = 0) -> float:
    """!
    Calculate intensity of Gaussian beam

    Intensity distribution of Gaussian beam as function of axial (`z`) and lateral (`x`,`y`) coordinates w.r.t. the
    the coordinate system `x1`, `y1`, `z1`, where the beam propagates along z and [`x1`, `y1`, `z1`] is the position
    of the focus. `w0` is field mode radius and `zR` = pi/wvl *w0**2 the Rayleigh range. The field mode radius
    `w0` is the lateral distance from the focus where the field amplitude has been reduced by 1/e and the
    intensity by 1/e^2.

    Args:
        w0 (float): The field mode radius.
        zR (float): The Rayleigh range.
        x0 (float): The initial x-coordinate.
        y0 (float): The initial y-coordinate.
        z0 (float): The initial z-coordinate.
        x1 (float, optional): The final x-coordinate. Defaults to 0.
        y1 (float, optional): The final y-coordinate. Defaults to 0.
        z1 (float, optional): The final z-coordinate. Defaults to 0.

    Returns:
        float: The intensity of the Gaussian beam.
    """
    x = x1 - x0
    y = y1 - y0
    z = z1 - z0

    wz2 = w0**2 * (1 + (z / zR) ** 2)
    return w0**2 / wz2 * np.exp(-2 * (x**2 + y**2) / wz2)

def shapes_props(jcfg: dict):
    for n in range(len(jcfg["Shapes"])):
        for shape in jcfg["Shapes"][n]:
            for prop in jcfg["Shapes"][n][shape]:
                if prop == "Size" and jcfg["Shapes"][n][shape][prop] == "fullVol":
                    jcfg["Shapes"][n][shape][prop] = jcfg["Domain"]["Dim"]
                if prop == "O" and jcfg["Shapes"][n][shape][prop] == "c":
                    jcfg["Shapes"][n][shape][prop] = jcfg["Domain"]["Dim"] / 2

    return jcfg
    
def equally_probable_theta_intervals(xx, yy, num_data_points=31):
    """This function calculates locations of x which have equal probability in the function defined by xx and yy with num_data_points

    Written 20241003 by MV and VZ aided with copilot
    
    Args:
        xx (list of floats): X values where probabilit fn is measured
        yy (list of floats): Probabilities at xx positions
        num_data_points (_type_): number of output points.  With a relatively smooth function we've found 30 to be OK.  Consider testing further. 

    Returns:
        list of floats : locations of theta which have equal probabilitiy between values defined by CDF
    """    
    from scipy.interpolate import CubicSpline
    from scipy.integrate import quad
    
    # Convert degrees to radians
    x_rad = [xi * np.pi / 180 for xi in xx]

    # Fit a cubic spline to the data
    spline = CubicSpline(x_rad, yy)

    # Define the integration limits
    x_min, x_max = min(x_rad), max(x_rad)

    # Define new x values with a higher sampling rate for CDF
    new_x = np.linspace(x_min, x_max, 1000)

    # Calculate the CDF
    cdf = np.cumsum(spline(np.cos(new_x)))
    cdf /= cdf[-1]  # Normalize CDF

    # Generate equally spaced probabilities
    equal_probs = np.linspace(0, 1, num_data_points)

    # Calculate the inverse CDF (interpolation)
    theta_values = np.interp((equal_probs), cdf, (new_x))
    
    # replace negative values w 0
    theta_values = [x for x in theta_values if x >= 0]
    
    # Normalize theta_values to be between 0 and 0.5
    theta_values = [np.arccos(x)/ (np.pi) for x in theta_values]
    
    # Adjust theta_values to have equal distances between 0 and 0.5
    # theta_values = np.linspace(0, 0.5, num_data_points)
    
    # theta_values need to be monotonically increasing
    theta_values = theta_values[::-1]
    
    theta_values = [x for x in theta_values if not np.isnan(x)]
    
    return theta_values

def energy_volume(jcfg):
    # To be filled in, this should calculate the energy in the volume of the domain from the flux and the absorption of each media type. 
    
    if jcfg['Session']['OutputType']=='flux':
        
        jcfg['res']['flux'] 
        
    else: 
        tmcx.util.verb('Energy calculation requires jcfg[\'Session\'][\'OutputType\']==\'flux\'', jcfg['Expt']['verb'], 0)

def energy_per_media(jcfg, saveKey='res_replay'):

    # Assuming jcfg is your data structure
    vol = jcfg['vol']
    flux = jcfg[saveKey]['flux']

    # Get the unique media types
    media_types = np.unique(vol)

    # Initialize a dictionary to store the average flux for each media type
    average_flux = {}
    labels=[]
    
    # Calculate the average flux for each media type
    for media in media_types:
        
        # Calculate the average flux for the current media type
        avg_flux = np.sum(flux[vol == media])
        
        # Store the result in the dictionary
        average_flux[str(media)] = avg_flux
        
        labels.append(jcfg['Domain']['Media'][media]['label'])
        
    jcfg[saveKey]['EnergyPerMedia'] = average_flux
    jcfg[saveKey]['MediaLabels'] = labels
    jcfg[saveKey]['DetectorMeas']=round(np.sum(jcfg['res']['IM']),0)
    
    
    
    tmcx.util.verb('Energy per media calculated for '+ saveKey, jcfg['Expt']['verb'], 1)
    
    return jcfg


def coord_transform_carthesian_to_polar(xx, yy):
    """calculate angles and probabilities from carthesian coordinates for determine LED angular distributions
    angle is 0 when x=0 and y=1 (-pi/2 with respect to unity circle)
    outputs a list of emission probabilites per angle, sorted by angle.
    Args:
        xx (_type_): x-coordinates
        yy (_type_): y-coordinates
    """
    combined = sorted(zip(xx, yy))
    rr=[]
    ttheta=[]
    for x,y in combined:
        rr.append((x**2+y**2)**0.5)
        ttheta.append((np.rad2deg(np.arctan2(y,x))-90)*-1)
    combined2 = sorted(zip(ttheta,rr))
    sorted_theta_values, sorted_r_values = zip(*combined2)
    return sorted_theta_values, sorted_r_values