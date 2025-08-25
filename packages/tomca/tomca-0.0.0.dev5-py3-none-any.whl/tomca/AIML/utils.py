import numpy as np
from scipy.interpolate import RBFInterpolator, CloughTocher2DInterpolator, LinearNDInterpolator
import matplotlib.pyplot as plt


def interpolate_plot(x, y, z, x_text="", y_text="", z_text="", title_text=""):
    """
    Simple function to plot 3d points as a 2d interpolated plot where the thirds axis is indicated by the color.
    """
    x0, x1 = x.min(), x.max()
    y0, y1 = y.min(), y.max()
    z0, z1 = z.min(), z.max()

    xy = np.concatenate([x[:, None], y[:, None]], axis=1)

    n = 100
    x_edges = np.linspace(x0, x1, n + 1)
    y_edges = np.linspace(y0, y1, n + 1)
    x_centers = x_edges[:-1] + np.diff(x_edges[:2])[0] / 2.
    y_centers = y_edges[:-1] + np.diff(y_edges[:2])[0] / 2.
    x_i, y_i = np.meshgrid(x_centers, y_centers)
    x_i = x_i.reshape(-1, 1)
    y_i = y_i.reshape(-1, 1)
    xy_i = np.concatenate([x_i, y_i], axis=1)

    #rbf = CloughTocher2DInterpolator(xy, z) # this does cubic interpolation, which makes it difficult to interpret because the whole map changes scaling. 
    rbf = LinearNDInterpolator(xy, z)
    z_i = rbf(xy_i)

    # Plot
    fig, ax = plt.subplots()
    X_edges, Y_edges = np.meshgrid(x_edges, y_edges)
    lims = dict(cmap='YlOrRd', vmin=z0, vmax=z1)
    mapping = ax.pcolormesh(
        X_edges, Y_edges, z_i.reshape(100, 100),
        shading='flat', **lims
    )
    # ax.scatter(xy[:, 0], xy[:, 1], 100, z, edgecolor='w', lw=0.1, **lims)
    ax.set(
        title=title_text
    )
    ax.set_xlabel(x_text)
    ax.set_ylabel(y_text)
    cbar = fig.colorbar(mapping)
    cbar.set_label(z_text)
