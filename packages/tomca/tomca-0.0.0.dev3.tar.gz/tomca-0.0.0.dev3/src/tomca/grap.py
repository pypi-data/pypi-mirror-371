"""
functions which \b graph data in our jcfg formats, or general volume data
"""

import numpy as np
import matplotlib.pyplot as plt
from Software import tmcx


def plot_easy(jcfg, resDict, loc):
    """very quick plot of results

    Args:
        res (_type_): results from mcx
        type (_type_): plot type ()
        loc (1x3 int): vector describing plot plane eg [30,:,:]
    """

    jcfg[resDict].shape

    # Plot the results
    plt.imshow(np.log10(jcfg[resDict][30, :, :]))
    plt.colorbar()


def voxVol(jcfg_or_vol, planes, cmap_in=None, resKey='res'):
    """
    Takes a voxel volume and cuts it alone the three planes described
    by planes. Must call fig.show() where called.

    fig=tmcx.grap.voxVol(jcfg,[5,5,5])
    fig.suptitle('Cutaways')
    fig.show()

    Args:
        vol (voxel volume): any 3D cube of numbers
        planes (1x3, [x, y, z]): planes to keep constant in the cuts.
    """
    cmap = None

    if type(jcfg_or_vol) is dict:
        jcfg = jcfg_or_vol
        vol = np.squeeze(jcfg[resKey]['flux'])
        if "OutputType" in jcfg["Session"]:
            if jcfg["Session"]["OutputType"].lower() == "energy":
                suptitle = 'Energy Maps'
                if 'exptName' in jcfg['Expt']:
                    suptitle = jcfg['Expt']['stateName']+' Energy Maps'
                cBarLabel = 'Energy deposited; J/(mm^2)'
                cmap = 'Spectral_r'
            else:
                # default, same as
                # cfg["Session"]["OutputType"].lower()=="flux"
                # or
                # jcfg["Session"]["OutputType"].lower()=="fluence":
                suptitle = 'Fluence Maps'
                if 'exptName' in jcfg['Expt']:
                    suptitle = jcfg['Expt']['stateName']+' Fluence Maps'
                cBarLabel = r'fluence-rate; 1/(mm$^2\,$s) ; W/(mm$^2\,$) ; ' +\
                    r'J/(mm$^2\,$s)'
                cmap = 'plasma'
        if 'Str' in jcfg['Expt']:
            detailsStr = jcfg['Expt']['Str']
        else:
            detailsStr = ''

        if 'plot' in jcfg['Expt']:
            if "plotLog" in jcfg['Expt']['plot']:
                vol = np.log(vol)
                cBarLabel = 'ln '+cBarLabel

        if "plot" in jcfg['Expt']:
            if "cMax" in jcfg['Expt']['plot']:
                if jcfg['Expt']['plot']["cMax"] != "calc":
                    map_max = jcfg['Expt']['plot']["cMax"]
                else:
                    map_max = np.max(vol)
        else:
            map_max = np.max(vol)

        if "plot" in jcfg['Expt']:
            if "cMin" in jcfg['Expt']['plot']:
                if jcfg['Expt']['plot']["cMin"] != "calc":
                    map_min = jcfg['Expt']['plot']["cMin"]
                else:
                    map_min = np.min(vol)
        else:
            map_min = np.min(vol)

        normalizeFactor = jcfg['Domain']['LengthUnit']
    else:
        vol = jcfg_or_vol
        cBarLabel = ''
        suptitle = ''
        detailsStr = 'vol passed into grap.volVol'
        normalizeFactor = 1
        map_max = np.max(vol)
        map_min = np.min(vol)
    if map_min < -40:
        map_min = -40

    vol[vol < map_min] = map_min

    if cmap_in is not None:  # and cmap is None:
        import matplotlib.cm as cm
        cmap = cm.get_cmap(cmap_in)
        # if you want "zero" to be a different color
        # cmap.set_bad('midnightblue')
        # vol[vol<=-8] = np.nan
    elif cmap is not None:
        pass
    else:
        cmap = 'viridis'

    # Create the cutaways
    zplane = (np.squeeze(vol[:, :, planes[2]]).T)
    yplane = (np.squeeze(vol[:, planes[1], :]).T)
    xplane = (np.squeeze(vol[planes[0], :, :]).T)

    # Save them in the jcfg
    if type(jcfg_or_vol) is dict:
        plotKey_planes = 'plot_planes'
        jcfg[resKey][plotKey_planes] = {}
        jcfg[resKey][plotKey_planes]['slice'] = planes
        jcfg[resKey][plotKey_planes]['x'] = xplane
        jcfg[resKey][plotKey_planes]['y'] = yplane
        jcfg[resKey][plotKey_planes]['z'] = zplane

        # Plot the cutaways
        fig = tmcx.grap.voxPlanes(jcfg[resKey][plotKey_planes], detailsStr,
                                  cmap=cmap, vmin=map_min, vmax=map_max,
                                  cBarLabel=cBarLabel, suptitle=suptitle,
                                  normalizeFactor=normalizeFactor)

    else:
        plotKey_planes = resKey+'_planes'
        plotKey_planes = {}
        plotKey_planes['slice'] = planes
        plotKey_planes['x'] = xplane
        plotKey_planes['y'] = yplane
        plotKey_planes['z'] = zplane

        # Plot the cutaways
        fig = tmcx.grap.voxPlanes(plotKey_planes, detailsStr, cmap=cmap,
                                  vmin=map_min, vmax=map_max,
                                  cBarLabel=cBarLabel, suptitle=suptitle,
                                  normalizeFactor=normalizeFactor)

    return fig


def voxPlanes(plotKey_planes, detailsStr='planes passed into grap.voxPlanes',
              cmap='viridis', vmin=None, vmax=None,
              cBarLabel='No cbarlabel passed into grap.voxPlanes',
              suptitle='No suptitle into grap.voxPlanes', normalizeFactor=1):

    if vmin is None:
        vmin = np.min([np.min(plotKey_planes['x']),
                       np.min(plotKey_planes['y']),
                       np.min(plotKey_planes['z'])])
    if vmax is None:
        vmax = np.max([np.max(plotKey_planes['x']),
                       np.max(plotKey_planes['y']),
                       np.max(plotKey_planes['z'])])

    xplane = plotKey_planes['x']
    yplane = plotKey_planes['y']
    zplane = plotKey_planes['z']
    planes = plotKey_planes['slice']

    fig = plt.figure()
    gs = fig.add_gridspec(2, 2)
    (ax1, ax2), (ax3, ax4) = gs.subplots()

    im = ax1.imshow(zplane, cmap=cmap, interpolation='nearest', vmin=vmin,
                    vmax=vmax, extent=[0, zplane.shape[1] * normalizeFactor, 0,
                                       zplane.shape[0] * normalizeFactor])
    label_unit = ''
    if normalizeFactor != 1:
        label_unit = ' [mm]'
    ax1.set_ylabel('y axis'+label_unit)
    ax1.set_xticklabels([])
    ax1.set_title('z='+str(planes[2]))

    ax2.set_axis_off()
    ax2.text(0, 0, detailsStr, fontsize=6)

    im = ax3.imshow(yplane, cmap=cmap, interpolation='nearest', vmin=vmin,
                    vmax=vmax, extent=[0, yplane.shape[1] * normalizeFactor, 0,
                                       yplane.shape[0] * normalizeFactor])
    ax3.set_xlabel('x axis'+label_unit)
    ax3.set_ylabel('z axis'+label_unit)
    ax3.set_title('y='+str(planes[1]))

    im = ax4.imshow(xplane, cmap=cmap, interpolation='nearest', vmin=vmin,
                    vmax=vmax, extent=[0, xplane.shape[1] * normalizeFactor, 0,
                                       xplane.shape[0] * normalizeFactor])
    ax4.set_xlabel('y axis'+label_unit)
    ax4.set_yticklabels([])
    ax4.set_title('x='+str(planes[0]))

    fig.subplots_adjust(right=0.75)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    fig.colorbar(im, cax=cbar_ax, label=cBarLabel)
    fig.suptitle(suptitle)

    return fig


def addContours(fig_in, vol, planes, contours=None, cmap=None, color=None,
                linestyles='solid', normalizeFactor=1, linewidths=1):
    """Takes a figure and adds contours
    Args:
        fig
    """

    map_min = np.min(vol)
    map_max = np.max(vol)
    if contours is None or contours == []:
        contours = np.arange(start=map_min, stop=map_max, step=2)
    else:
        pass

    if color is not None:
        fig = plt.figure(fig_in, vol, planes)
        fig.axes[0].contour((np.fliplr(np.squeeze(vol[:, :, planes[2]]).T)), contours, colors=color, linestyles=linestyles, linewidths=linewidths, extent=[(np.squeeze(vol[:, :, planes[2]]).T).shape[1] * normalizeFactor, 0, (np.squeeze(vol[:, :, planes[2]]).T).shape[0] * normalizeFactor, 0])
        # fig.axes[0].clabel(tmp, tmp.levels, inline=True, fontsize=6)
        fig.axes[2].contour((np.fliplr(np.squeeze(vol[:, planes[1], :]).T)), contours, colors=color, linestyles=linestyles, linewidths=linewidths, extent=[(np.squeeze(vol[:, planes[1], :]).T).shape[1] * normalizeFactor, 0, (np.squeeze(vol[:, planes[1], :]).T).shape[0] * normalizeFactor, 0])
        # fig.axes[1].clabel(tmp, tmp.levels, inline=True, fontsize=6)
        fig.axes[3].contour((np.fliplr(np.squeeze(vol[planes[0], :, :]).T)), contours, colors=color, linestyles=linestyles, linewidths=linewidths, extent=[(np.squeeze(vol[planes[0], :, :]).T).shape[1] * normalizeFactor, 0, (np.squeeze(vol[planes[0], :, :]).T).shape[0] * normalizeFactor, 0])
        # fig.axes[2].clabel(tmp, tmp.levels, inline=True, fontsize=6)

    else:
        if cmap is None:
            cmap = 'Greys'
        fig = plt.figure(fig_in, vol, planes)
        fig.axes[0].contour((np.fliplr(np.squeeze(vol[:, :, planes[2]]).T)), contours, cmap=cmap, linestyles=linestyles, linewidths=linewidths, extent=[(np.squeeze(vol[:, :, planes[2]]).T).shape[1] * normalizeFactor, 0, (np.squeeze(vol[:, :, planes[2]]).T).shape[0] * normalizeFactor, 0])
        # fig.axes[0].clabel(tmp, tmp.levels, inline=True, fontsize=6)
        fig.axes[2].contour((np.fliplr(np.squeeze(vol[:, planes[1], :]).T)), contours, cmap=cmap, linestyles=linestyles, linewidths=linewidths, extent=[(np.squeeze(vol[:, planes[1], :]).T).shape[1] * normalizeFactor, 0, (np.squeeze(vol[:, planes[1], :]).T).shape[0] * normalizeFactor, 0])
        # fig.axes[1].clabel(tmp, tmp.levels, inline=True, fontsize=6)
        fig.axes[3].contour((np.fliplr(np.squeeze(vol[planes[0], :, :]).T)), contours, cmap=cmap, linestyles=linestyles, linewidths=linewidths, extent=[(np.squeeze(vol[planes[0], :, :]).T).shape[1] * normalizeFactor, 0, (np.squeeze(vol[planes[0], :, :]).T).shape[0] * normalizeFactor, 0])
        # fig.axes[2].clabel(tmp, tmp.levels, inline=True, fontsize=6)

    return fig


def voxPlanes_addContours(fig_in, plotKey_planes, contours=None, cmap=None,
                          color=None, linestyles='solid'):
    """Takes a figure generated with planes and adds contours

    Args:
        fig_in (matplotlib.figure.Figure): The figure to add contours to.
        plotKey_planes (dict): planes of the voxel volume evaluated at
        simulation time.  Must have keys 'x', 'y', 'z', and 'slice'.
        planes (list): The planes to keep constant in the cuts.
        contours (list, optional): The contour levels to plot.
            Defaults to [].
        cmap (str, optional): The colormap to use for the contours.
            Defaults to None.
        color (str, optional): The color of the contour lines.
            Defaults to None.
        linestyles (str, optional): The linestyle of the contour lines.
            Defaults to 'solid'.

    Returns:
        matplotlib.figure.Figure: The figure with added contours.
    """

    if contours is None or contours == []:
        vmin = np.min([np.min(plotKey_planes['x']),
                       np.min(plotKey_planes['y']),
                       np.min(plotKey_planes['z'])])
        vmax = np.max([np.max(plotKey_planes['x']),
                       np.max(plotKey_planes['y']),
                       np.max(plotKey_planes['z'])])
        contours = np.arange(start=vmin, stop=vmax, step=2)

    xplane = plotKey_planes['x']
    yplane = plotKey_planes['y']
    zplane = plotKey_planes['z']

    if color is not None:
        fig = plt.figure(fig_in)
        fig.axes[0].contour(zplane, contours, colors=color,
                            linestyles=linestyles)
        fig.axes[2].contour(yplane, contours, colors=color,
                            linestyles=linestyles)
        fig.axes[3].contour(xplane, contours, colors=color,
                            linestyles=linestyles)
    else:
        if cmap is None:
            cmap = 'Greys'
        fig = plt.figure(fig_in)
        fig.axes[0].contour(zplane, contours, cmap=cmap,
                            linestyles=linestyles)
        fig.axes[2].contour(yplane, contours, cmap=cmap,
                            linestyles=linestyles)
        fig.axes[3].contour(xplane, contours, cmap=cmap,
                            linestyles=linestyles)

    return fig


def vol_us(jcfg, prop, planes):
    """Plot distribution of mua, mus, g, n as prop

    Args:
        jcfg (_type_): _description_
        planes (_type_): _description_
    """

    try:
        # if svmc, only take the first volume
        if jcfg['Domain']['MediaFormat'] == 'svmc':
            activeVol = jcfg['vol'][0, :, :, :]
        else:
            activeVol = jcfg['vol']
    except Exception:
        activeVol = jcfg['vol']

    MediaIndexes = np.unique(activeVol)

    tick_labels = []
    tick_locs = []

    zSliceActive = (np.squeeze(activeVol[:, :, planes[2]]).T)
    ySliceActive = (np.squeeze(activeVol[:, planes[1], :]).T)
    xSliceActive = (np.squeeze(activeVol[planes[0], :, :]).T)

    zSlice = np.ones(zSliceActive.shape)
    ySlice = np.ones(ySliceActive.shape)
    xSlice = np.ones(xSliceActive.shape)

    for mediaIndex in map(int, MediaIndexes):
        # this said =- 1, not sure if it should be = -1, or -=1
        propIdx = -1
        if prop == "mua":
            propIdx = 0
        elif prop == "mus":
            propIdx = 1
        elif prop == "g":
            propIdx = 2
        elif prop == "n":
            propIdx = 3
        else:
            # prop == "vol":
            zSlice[zSliceActive == mediaIndex] = mediaIndex
            ySlice[ySliceActive == mediaIndex] = mediaIndex
            xSlice[xSliceActive == mediaIndex] = mediaIndex
            tick_locs.append(mediaIndex)

        if propIdx >= 0:
            prop_val = jcfg['mcfg']['prop'][mediaIndex][propIdx]
            zSlice[zSliceActive == mediaIndex] = prop_val
            ySlice[ySliceActive == mediaIndex] = prop_val
            xSlice[xSliceActive == mediaIndex] = prop_val

            # set the tick locations where you want to label the color bar
            tick_locs.append(jcfg['mcfg']['prop'][mediaIndex][propIdx])

        # # set the tick labels for the tick locations
        # if 'label' in jcfg['Domain']['Media'][mediaIndex]:
        #     tick_labels.append(jcfg['Domain']['Media'][mediaIndex]['label'])
        # else:
        #     tick_labels.append("unlabeled")

    if prop == 'mua':
        cBarLabel = r'$\mu_a$, [$mm^{-1}$]'
        suptitle = r'$\mu_a$ distribution'
        cmap = 'Greys'
    elif prop == 'mus':
        cBarLabel = r'$\mu_s$, [$mm^{-1}$]'
        suptitle = r'$\mu_s$ distribution'
        cmap = 'Greens'
    elif prop == "g":
        cBarLabel = 'g [u]'
        suptitle = 'g distribution'
        cmap = 'Blues'
    elif prop == "n":
        cBarLabel = 'n [u]'
        suptitle = 'index of refreaction distribution'
        cmap = 'Purples'
    elif prop == 'vol' or prop == 'idx':
        cBarLabel = 'Index'
        suptitle = 'media index distribution'
        cmap = 'viridis'
    else:
        print("Invalid Media Parameter Given. Use mua mus g n vol")

    map_min = np.min(tick_locs)
    map_max = np.max(tick_locs)

    fig = plt.figure()
    fig.suptitle(suptitle)
    gs = fig.add_gridspec(2, 2)
    (ax1, ax2), (ax3, ax4) = gs.subplots()
    def remove_spines(ax):
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    remove_spines(ax1)
    remove_spines(ax2)
    remove_spines(ax3)
    remove_spines(ax4)
    
    im3 = ax1.imshow(zSlice, cmap=cmap, interpolation='nearest',
                     vmin=map_min, vmax=map_max)
    ax1.set_xticklabels([])
    ax1.set_ylabel('y axis')
    ax1.set_title('z='+str(round(planes[2]*jcfg['Domain']['LengthUnit'], 1)) +
                  ' mm')
    # Set axis tick labels in mm instead of voxels
    x_vox = jcfg['Domain']['Dim'][0]
    y_vox = jcfg['Domain']['Dim'][1]
    length_unit = jcfg['Domain']['LengthUnit']

    # Set x-axis ticks and labels in mm
    x_ticks = np.linspace(0, x_vox, num=5)
    x_ticklabels = [f"{round(tick * length_unit,1)}" for tick in x_ticks]
    ax1.set_xticks(x_ticks)
    ax1.set_xticklabels(x_ticklabels)

    # Set y-axis ticks and labels in mm
    y_ticks = np.linspace(0, y_vox, num=5)
    y_ticklabels = [f"{round(tick * length_unit,1)}" for tick in y_ticks]
    ax1.set_yticks(y_ticks)
    ax1.set_yticklabels(y_ticklabels)

    ax2.set_axis_off()
    ax2.text(0, 0, jcfg['Expt']['Str'], fontsize=6)

    im3 = ax3.imshow(ySlice, cmap=cmap, interpolation='nearest',
                     vmin=map_min, vmax=map_max)
    ax3.set_xlabel('x axis')
    ax3.set_ylabel('z axis')
    ax3.set_title('y='+str(round(planes[1]*jcfg['Domain']['LengthUnit'], 1)) +
                  ' mm')
    # Set axis tick labels in mm instead of voxels
    x_vox = jcfg['Domain']['Dim'][0]
    z_vox = jcfg['Domain']['Dim'][2]
    length_unit = jcfg['Domain']['LengthUnit']

    # Set x-axis ticks and labels in mm
    x_ticks = np.linspace(0, x_vox, num=5)
    x_ticklabels = [f"{round(tick * length_unit,1)}" for tick in x_ticks]
    ax3.set_xticks(x_ticks)
    ax3.set_xticklabels(x_ticklabels)

    # Set y-axis ticks and labels in mm
    y_ticks = np.linspace(0, z_vox, num=5)
    y_ticklabels = [f"{round(tick * length_unit,1)}" for tick in y_ticks]
    ax3.set_yticks(y_ticks)
    ax3.set_yticklabels(y_ticklabels)

    im3 = ax4.imshow(xSlice, cmap=cmap, interpolation='nearest',
                     vmin=map_min, vmax=map_max)
    ax4.set_yticklabels([])
    ax4.set_xlabel('y axis')
    ax4.set_title('x='+str(round(planes[0]*jcfg['Domain']['LengthUnit'], 1)) +
                  ' mm')
    # Set axis tick labels in mm instead of voxels
    y_vox = jcfg['Domain']['Dim'][1]
    z_vox = jcfg['Domain']['Dim'][2]
    length_unit = jcfg['Domain']['LengthUnit']

    # Set x-axis ticks and labels in mm
    x_ticks = np.linspace(0, y_vox, num=5)
    x_ticklabels = [f"{round(tick * length_unit,1)}" for tick in x_ticks]
    ax4.set_xticks(x_ticks)
    ax4.set_xticklabels(x_ticklabels)

    # Set y-axis ticks and labels in mm
    y_ticks = np.linspace(0, z_vox, num=5)
    y_ticklabels = [f"{round(tick * length_unit,1)}" for tick in y_ticks]
    ax4.set_yticks(y_ticks)
    ax4.set_yticklabels(y_ticklabels)

    fig.subplots_adjust(right=0.75)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    cbar = fig.colorbar(im3, cax=cbar_ax, ticklocation='left')
    cbar_ax.set_title(cBarLabel)
    # set the tick locations and labels for the color bar
    cbar.set_ticks(tick_locs, labels=tick_labels, minor=True)
    cbar.ax.tick_params(which='minor', labelsize=8, pad=8, labelleft=False,
                        labelright=True, left=False, right=True)

    # Adjust layout to prevent overlap between axis labels and titles
    # leave space for colorbar on the right
    fig.tight_layout(rect=[0, 0, 0.8, 1])

    fig.suptitle(suptitle)

    return (fig)

# ## Kernel Plotting
# # Create meshgrid
# xmax=jcfg['Domain']['Dim'][0]-1
# ymax=jcfg['Domain']['Dim'][1]-1
# xx, yy = np.mgrid[0:xmax:10, 0:ymax:10]
# positions = np.vstack([xx.ravel(), yy.ravel()])
# nPlot=500000
# values = np.vstack([jcfg['res']['x'][0,0:nPlot],
#                     jcfg['res']['x'][1,0:nPlot]])
# kernel = st.gaussian_kde(values)
# f = np.reshape(kernel(positions).T, xx.shape)

# fig = plt.figure(figsize=(8,8))
# ax = fig.gca()
# ax.set_xlim(0, xmax)
# ax.set_ylim(0, ymax)
# cfset = ax.contourf(xx, yy, f, cmap='coolwarm')
# ax.imshow(np.rot90(f), cmap='coolwarm', extent=[ 0, xmax, 0 , ymax])
# # cset = ax.contour(xx, yy, f, colors='k')
# # ax.clabel(cset, inline=1, fontsize=10)
# ax.set_xlabel('X')
# ax.set_ylabel('Y')
# plt.title('2D Gaussian Kernel density estimation')


def wave2rgb(wave):
    '''
    Code that returns the RGB digits of from a wavelength of
    light input (in nm)
    '''
    # This is a port of javascript code from
    # http://stackoverflow.com/a/14917481
    gamma = 0.8
    intensity_max = 1

    if wave < 380:
        red, green, blue = 0, 0, 0
    elif wave < 440:
        red = -(wave - 440) / (440 - 380)
        green, blue = 0, 1
    elif wave < 490:
        red = 0
        green = (wave - 440) / (490 - 440)
        blue = 1
    elif wave < 510:
        red, green = 0, 1
        blue = -(wave - 510) / (510 - 490)
    elif wave < 580:
        red = (wave - 510) / (580 - 510)
        green, blue = 1, 0
    elif wave < 645:
        red = 1
        green = -(wave - 645) / (645 - 580)
        blue = 0
    elif wave <= 780:
        red, green, blue = 1, 0, 0
    else:
        red, green, blue = 0, 0, 0

    # let the intensity fall of near the vision limits
    if wave < 380:
        factor = 0
    elif wave < 420:
        factor = 0.3 + 0.7 * (wave - 380) / (420 - 380)
    elif wave < 700:
        factor = 1
    elif wave <= 780:
        factor = 0.3 + 0.7 * (780 - wave) / (780 - 700)
    else:
        factor = 0

    def f(c):
        if c == 0:
            return 0
        else:
            return intensity_max * pow(c * factor, gamma)

    return f(red), f(green), f(blue)


def state_xsection_CCD(jcfg, resName='res', desc=''):
    writeFig = 1
    if "write" in jcfg['Expt']:
        if "fig_CCD_image" in jcfg['Expt']['write']:
            writeFig = jcfg['Expt']['write']['fig_CCD_image']

    # Plot CCD image
    map_min = -1
    fig = plt.figure()
    fig.suptitle('CCD image at virtual detector')
    cBarLabel = 'ln media-weighted intensity at detector'
    im = plt.imshow(np.log(jcfg[resName]['IM']), vmin=map_min, vmax=4.5)
    plt.xlabel('X-axis voxel')
    plt.ylabel('Y-axis voxel')
    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    fig.colorbar(im, cax=cbar_ax, label=cBarLabel)

    if writeFig:
        if 'fig' not in jcfg:
            jcfg['fig'] = {}
        jcfg['fig']['CCD_image'] = fig
        tmcx.writ.fig(jcfg, fig, 'CCD_image_'+resName+desc)
    else:
        tmcx.util.verb('Skipping writing of CCD image.'
                       'Toggle with jcfg[\'Expt\'][\'write\']'
                       '[\'fig_CCD_image\']', jcfg['Expt']['verb'], 2)


def state_xsection_CCDx(jcfg, resName='res', desc=''):
    writeFig = 1
    if "write" in jcfg['Expt']:
        if "fig_CCD_XSection" in jcfg['Expt']['write']:
            writeFig = jcfg['Expt']['write']['fig_CCD_XSection']

    # Plot cross sections of CCD image
    fig_crossSections = plt.figure()
    fig_crossSections.suptitle('Cross section of CCD image at virtual'
                               'detector, averaged along Y axis')
    if 'plot' in jcfg['Expt']:
        if "plotLog" in jcfg['Expt']['plot']:
            plt.plot(np.log(np.mean(jcfg[resName]['IM'], axis=0)))
            plt.xlabel('X-axis voxel')
            plt.ylabel('ln media-weighted intensity at detector')
        else:
            plt.plot(np.mean(jcfg[resName]['IM'], axis=0))
            plt.xlabel('X-axis voxel')
            plt.ylabel('Media-weighted intensity at detector')

    if writeFig:
        if 'fig' not in jcfg:
            jcfg['fig'] = {}
        jcfg['fig']['CCD_XSection'] = fig_crossSections
        tmcx.writ.fig(jcfg, fig_crossSections, 'CCD_XSection_'+resName+desc)
    else:
        tmcx.util.verb('Skipping writing of CCD cross section.'
                       'Toggle with jcfg[\'Expt\'][\'write\']'
                       '[\'fig_CCD_XSection\']', jcfg['Expt']['verb'], 2)


def get_vessel_zPos(jcfg):
    zPos = 0
    if "Vol" in jcfg:
        if "vessel" in jcfg['Vol']:
            if 'zPos' in jcfg['Vol']['vessel']:
                zPos = int(np.floor(jcfg['Vol']['vessel']['zPos']/jcfg[
                    'Domain']['LengthUnit']))-1
            else:
                zPos = ((jcfg['Vol']['vessel']['rBlood'] + jcfg['Vol'][
                    'vessel']['tCFZ'] + jcfg['Vol']['vessel']['tWall'])/jcfg[
                        'Domain']['LengthUnit'])-1
    return zPos


def get_plotCuts(jcfg):
    '''! Extract or build planes to cut the volume on.
    Controlled by jcfg['Expt']['plot']['plotCuts']=[x,y,x].
    '''
    if "plotCuts" in jcfg['Expt']['plot']:
        plotCuts = [0, 0, 0]
        for tii in np.arange(3):
            # Check if centered
            if jcfg['Expt']['plot']['plotCuts'][tii] == 'c':
                # Assign to center position of beam
                plotCuts[tii] = jcfg['Domain']['Dim'][tii]/2 - 1
            # Assign to start of volume
            elif jcfg['Expt']['plot']['plotCuts'][tii] == '0':
                plotCuts[tii] = 0
            # Assign to end of volume
            elif jcfg['Expt']['plot']['plotCuts'][tii] == '-1':
                plotCuts[tii] = jcfg['Domain']['Dim'][tii]-1
            else:
                plotCuts[tii] = jcfg['Expt']['plot']['plotCuts'][tii]
    else:
        zPos = get_vessel_zPos(jcfg)
        plotCuts = [int(np.floor(jcfg['Domain']['Dim'][0]/2))-1,
                    int(np.floor(jcfg['Domain']['Dim'][1]/2))-1, int(zPos)]
    plotCuts = [int(np.floor(plotCuts[0])), int(np.floor(plotCuts[1])),
                int(np.floor(plotCuts[2]))]

    jcfg['Expt']['plot']['plotCuts_vox'] = plotCuts

    return plotCuts


def state_xsection_flux(jcfg, plotCuts=None, desc=''):
    # Plot the flux map
    writeFig = 1
    if "write" in jcfg['Expt']:
        if "fig_simulation_XSections" in jcfg['Expt']['write']:
            writeFig = jcfg['Expt']['write']['fig_simulation_XSections']

    if not plotCuts:
        plotCuts = get_plotCuts(jcfg)

    # See if flux is available
    if 'flux' in jcfg['res']:
        # Plot cross section of flux chosen
        fig2 = voxVol(jcfg, plotCuts, resKey='res')
        fig2.suptitle('simulation_XSections')
        jcfg['fig']['simulation_XSections'] = fig2
        if writeFig:
            tmcx.writ.fig(jcfg, fig2, 'simulation_XSections'+desc)
        else:
            tmcx.util.verb('Skipping writing of simulation_XSections.'
                           'Toggle with jcfg[\'Expt\'][\'write\']'
                           '[\'fig_simulation_XSections\']',
                           jcfg['Expt']['verb'], 2)


def state_xsection_flux_replay(jcfg, plotCuts=None, desc=''):
    # Plot the replay flux
    writeFig = 1
    if "write" in jcfg['Expt']:
        if "fig_simulation_XSections_replay" in jcfg['Expt']['write']:
            writeFig = jcfg['Expt']['write']['fig_simulation_XSections_replay']
    if not plotCuts:
        plotCuts = get_plotCuts(jcfg)

    # Replay plot
    if jcfg['Expt']['doReplay']:
        for replay_key in jcfg['Optode']['Detector']['configs_labels']:
            fig3 = voxVol(jcfg, plotCuts, resKey=replay_key)
            fig3.suptitle('Replay Simulation')
            jcfg['fig']['simulation_XSections_'+replay_key] = fig3
            if writeFig:
                tmcx.writ.fig(jcfg, fig3, 'simulation_XSections_' +
                              replay_key + '_' + desc)
            else:
                tmcx.util.verb('Skipping writing of'
                               'simulation_XSections_replay' + desc +
                               '. Toggle with jcfg[\'Expt\'][\'write\']'
                               '[\'fig_simulation_XSections_replay\']',
                               jcfg['Expt']['verb'], 2)


def state_xsection_property_plots(jcfg, plotCuts=None):

    if not plotCuts:
        plotCuts = get_plotCuts(jcfg)

    # Property Plots
    propList = ['mua', 'mus', 'g', 'n', 'idx']
    for prop in propList:
        titleStr = 'XSections_' + prop
        writeFig = 1
        if "write" in jcfg['Expt']:
            if "fig_"+titleStr in jcfg['Expt']['write']:
                writeFig = jcfg['Expt']['write']["fig_"+titleStr]
        if writeFig:
            figmua = vol_us(jcfg, prop, plotCuts)
            jcfg['fig'][titleStr] = figmua
            tmcx.writ.fig(jcfg, figmua, titleStr)
        else:
            tmcx.util.verb('Skipping writing of '+titleStr+'. Toggle with '
                           'jcfg[\'Expt\'][\'write\'][\'fig_'+titleStr+'\']',
                           jcfg['Expt']['verb'], 2)


def state_xsections(jcfg):
    """Generate cross section plots and CCD of a state jcfg
    Args:
        jcfg (dict): jcfg from the simulator, includes ref subdict
    """
    if jcfg['Expt']['verb'] >= 1.5:
        if 'calcFigs' in jcfg['Expt']['plot']:
            tmcx.util.verb('Skipping cross-sectional plots calculation. '
                           'Toggle with jcfg[\'Expt\'][\'plot\']'
                           '[\'calcFigs\']', jcfg['Expt']['verb'], 1)
        else:
            jcfg['Expt']['plot']['calcFigs'] = 1
    else:
        jcfg['Expt']['plot']['calcFigs'] = 0

    if jcfg['Expt']['plot']['calcFigs']:

        state_xsection_CCD(jcfg)
        state_xsection_CCDx(jcfg)
        state_xsection_flux(jcfg)
        state_xsection_flux_replay(jcfg)
        state_xsection_property_plots(jcfg)

    return jcfg


def expt_CCD(results_list):
    ''' Plot the "CCD" image over all states simualted from results_list[ii]
    ['res']['IM'] in a single figure.  Saves to expt folder.
    '''
    # Calculate the number of rows and columns for a square arrangement
    num_images = len(results_list)
    rows = int(np.ceil(np.sqrt(num_images)))
    cols = int(np.ceil(num_images / rows))
    # Adjust figsize as needed
    fig2, axs = plt.subplots(rows, cols, figsize=(10, 10))

    for ii in range(num_images):
        image = results_list[ii]['res']['IM']
        image += 1e-10
        if num_images != 1:
            # Use ravel() to flatten the array of axes and index into it
            ax = axs.ravel()[ii]
        else:
            ax = axs
        ax.imshow(image, aspect=1)  # Set aspect to 1 for a 1:1 aspect ratio

        x_center = results_list[ii]['Vol']['volX'] / 2 /\
            results_list[ii]['Domain']['LengthUnit']
        if 'vessel' in results_list[ii]['Vol']:
            nVox_vessel = (results_list[ii]['Vol']['vessel']['rBlood']) /\
                results_list[ii]['Domain']['LengthUnit']
            # Example: dashed red line
            ax.axvline(x_center-nVox_vessel, color='red', linestyle='--')
            ax.axvline(x_center+nVox_vessel, color='red', linestyle='--')
        ax.set_title(f'Image {ii}')
        ax.axis('off')

    # Adjust subplot params so that the subplot(s) fits in to the figure area
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                        wspace=None, hspace=None)
    results_list[0]['Expt']['plot']['writeFigs'] = 1
    tmcx.writ.fig(results_list[0], fig2, 'summary_images', location='Expt')


def expt_middleProfiles(results_list):
    '''
    Plot the middle profile of the results_list[ii]['res']['IM'] image for
    each ii. Saves to expt folder.
    '''
    fig = plt.figure()
    for ii in range(len(results_list)):
        image = results_list[ii]['res']['IM']
        middle_profile = image[:, image.shape[1] // 2]
        plt.plot(middle_profile)
        plt.xlabel('Pixel')
        plt.ylabel('Intensity')
        plt.title(f'Middle Profile of Image {ii}')
    results_list[0]['Expt']['plot']['writeFigs'] = 1
    tmcx.writ.fig(results_list[0], fig, 'summary_middle_profiles',
                  location='Expt')


def detector_angles_histogram(jcfg, inName):
    """
    Create a histogram of the angles of the
    detector in the jcfg[inName]['det_angles'] array.
    """
    if "write" in jcfg['Expt']:
        if "fig_det_angles" in jcfg['Expt']['write']:
            hist_values = jcfg[inName]['det_angles']
            fig, ax = plt.subplots()
            bins = np.arange(0, 90.5, 0.5)
            ax.bar(
                bins[:-1],
                hist_values,
                width=np.diff(bins),
                align='edge',
                color='black',
                alpha=0.7,
            )
            ax.set_xlabel(r'angle [$\degree$]')
            ax.set_ylabel(r'occurence [-]')
            try:
                fig.suptitle(f"Total power on"
                             f"detector: { np.sum(jcfg[inName]['IM'])}")
            except Exception as ex:
                fig.suptitle('wrong; ', ex)
            tmcx.writ.fig(jcfg, fig, f'angleshist_{inName}')

    return jcfg


def create_curoled_image(sim, contour=False, cmap0='default', scaling=0.06):
    if contour:
        fig = sim['fig']['simulation_XSections_contour']
    else:
        fig = sim['fig']['simulation_XSections']
    ax1 = fig.axes[0]
    ax2 = fig.axes[2]
    cbar = fig.axes[4]
    ticks = cbar.get_yticks()
    # cbar.set_yticklabels([f'{int(i/abs(i) if i!=0 else 1)}e{int(abs(i))}' for
    #                       i in ticks])
    ylabel = cbar.get_ylabel()

    if (len(ylabel) == 61) or (len(ylabel) == 29):
        ylabel = ylabel[3:]
        cbar.set_ylabel(ylabel)

    if cmap0 == 'default':
        cmap = ax1.get_images()[0].get_cmap()
    else:
        cmap = cmap0
    if sim['Optode']['Source']["spectProfile"] == "660":
        if sim['Session']['OutputType'] == 'energy':
            cmap = 'hot_r'
        else:
            cmap = 'hot'
    else:
        if sim['Session']['OutputType'] == 'energy':
            cmap = 'gray_r'
        else:
            cmap = 'gray'
    new_fig, axs = plt.subplots(1, 3, gridspec_kw={'width_ratios': [6, 1, 1]},
                                figsize=(12, 4))
    cbar_data = axs[0].imshow(fig.axes[0].get_images()[0].get_array() +
                              np.log(scaling)/np.log(10),
                              cmap=cmap,
                              vmin=ax1.get_images()[0].get_clim()[0] +
                              np.log(scaling)/np.log(10),
                              vmax=ax1.get_images()[0].get_clim()[1] +
                              np.log(scaling)/np.log(10),
                              extent=ax1.get_images()[0].get_extent())
    axs[1].imshow(fig.axes[2].get_images()[0].get_array()+np.log(scaling) /
                  np.log(10), cmap=cmap,
                  vmin=ax1.get_images()[0].get_clim()[0]+np.log(scaling) /
                  np.log(10),
                  vmax=ax1.get_images()[0].get_clim()[1]+np.log(scaling) /
                  np.log(10),
                  extent=ax2.get_images()[0].get_extent())

    cbar = new_fig.colorbar(cbar_data, ax=axs[2], shrink=1, location='left')

    size = sim['Vol']['volX']
    size_z_pixels = sim['vol'].shape[2]
    size_z_mm = size_z_pixels * sim["Domain"]['LengthUnit']
    ax1 = axs[0]
    ax1.set_yticks([0, size/2, size])
    ax1.set_yticklabels([-size/2, 0, size/2])
    ax1.set_xticks([0, size/2, size])
    ax1.set_xticklabels([-size/2, 0, size/2])
    ax1.set_xlabel('x-axis [mm]')
    ax1.set_ylabel('y-axis [mm]')
    ax1.set_title('z=0')

    ax2 = axs[1]
    ax2.set_xticks([0, size/2, size])
    ax2.set_xticklabels([-size/2, 0, size/2])
    ax2.set_yticks(np.linspace(size_z_mm, size_z_mm % 5, 6))
    ax2.set_yticklabels(np.linspace(0, size_z_mm//5*5, 6, dtype=int))
    ax2.set_xlabel('x-axis [mm]')
    ax2.set_ylabel('z-axis [mm]')
    ax2.set_title('y=0')

    ticks = cbar.get_ticks()
    cbar.set_ticklabels([f"1e{i}" for i in ticks])
    ylabel = cbar.set_label(ylabel)

    axs[2].text(0, 0, sim["Expt"]["Str"], fontsize=6)
    axs[2].set_axis_off()

    new_fig.tight_layout()

    if contour:
        tmcx.writ.fig(sim, new_fig, 'Result_img_contour')
    else:
        tmcx.writ.fig(sim, new_fig, 'Result_img')
        sim['fig']['simulation_XSections_adjusted'] = new_fig
