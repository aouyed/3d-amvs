import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from parameters import parameters

VMAX = 0.2


def big_histogram(ds, column_x, column_y, xedges, yedges, bins=100):
    """
    Generate a 2D histogram from the given dataset.

    Args:
        ds (xarray.Dataset): The dataset containing the data.
        column_x (str): The name of the column for the x-axis.
        column_y (str): The name of the column for the y-axis.
        xedges (list): The edges for the x-axis bins.
        yedges (list): The edges for the y-axis bins.
        bins (int, optional): The number of bins for the histogram. Defaults to 100.

    Returns:
        tuple: A tuple containing the transposed heatmap and the extent of the histogram.
    """
    xbins = np.linspace(xedges[0], xedges[1], bins + 1)
    ybins = np.linspace(yedges[0], yedges[1], bins + 1)
    heatmap = np.zeros((bins, bins), np.uint)

    df = ds[[column_x, column_y]].to_dataframe().reset_index().dropna()

    heatmap, _, _ = np.histogram2d(
        df[column_x].values, df[column_y].values, bins=[xbins, ybins]
    )
    heatmap = 100 * heatmap / np.sum(heatmap)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    return heatmap.T, extent


def hist_unit(ds, label1, label2, ax, xedges, yedges):
    """
    Plot a single histogram unit on the given axis.

    Args:
        ds (xarray.Dataset): The dataset containing the data.
        label1 (str): The label for the x-axis variable.
        label2 (str): The label for the y-axis variable.
        ax (matplotlib.axes.Axes): The axis to plot on.
        xedges (list): The edges for the x-axis bins.
        yedges (list): The edges for the y-axis bins.

    Returns:
        tuple: The axis and the image object.
    """
    hist, edges = big_histogram(ds, label1, label2, xedges, yedges)
    im = ax.imshow(
        hist,
        vmin=0,
        vmax=1.5e-1,
        extent=edges,
        aspect="auto",
        origin="lower",
        cmap="CMRmap_r",
    )
    return ax, im


def ax_compute(ax, var, edges, ds, df, letter, alg, is_amv):
    """
    Compute and plot a histogram on the given axis.

    Args:
        ax (matplotlib.axes.Axes): The axis to plot on.
        var (str): The variable name.
        edges (list): The edges for the bins.
        ds (xarray.Dataset): The dataset containing the data.
        df (pandas.DataFrame): The DataFrame containing correlation data.
        letter (str): The subplot label.
        alg (str): The algorithm name.
        is_amv (bool): Whether the data is from AMV.

    Returns:
        matplotlib.image.AxesImage: The image object.
    """
    ax, im = hist_unit(ds, var, var + "_era5", ax, edges, edges)
    if is_amv:
        ax.set_ylabel(r"$\mathrm{" + var + "}_{\mathrm{ERA 5}}$")
    ax.set_xlabel(r"$\mathrm{" + var + "}_{\mathrm{" + alg + "}}$")
    r = df["r"].loc[df["var"] == var].values.item()
    ax.text(0.7, 0.5, "r = " + str(round(r, 2)), transform=ax.transAxes)
    ax.text(0.1, 0.7, letter, transform=ax.transAxes)
    return im


def multiple_panel_hist(label, ds_rand, ds_tvl1, df_rand, df_tvl1):
    """
    Create a multiple-panel histogram plot.

    Args:
        label (str): The label for the plot.
        ds_rand (xarray.Dataset): The random dataset.
        ds_tvl1 (xarray.Dataset): The TVL1 dataset.
        df_rand (pandas.DataFrame): The random dataset correlations.
        df_tvl1 (pandas.DataFrame): The TVL1 dataset correlations.
    """
    fig, axes = plt.subplots(nrows=2, ncols=1)
    axlist = axes.flat
    im = ax_compute(axlist[0], "speed", [0, 30], ds_tvl1, df_tvl1, "(a)", "AMV", True)
    ax_compute(axlist[1], "speed", [0, 30], ds_rand, df_rand, "(b)", "rand", False)

    cbar_ax = fig.add_axes([0.12, -0.07, 0.77, 0.05])
    fig.colorbar(im, cax=cbar_ax, orientation="horizontal", label="percent")

    plt.tight_layout()
    plt.savefig(
        "../data/processed/plots/2d_hist_" + label + ".png",
        bbox_inches="tight",
        dpi=500,
    )
    plt.show()
    plt.close()


def compute_corr(ds):
    """
    Compute the correlation coefficients for the dataset.

    Args:
        ds (xarray.Dataset): The dataset containing the data.

    Returns:
        pandas.DataFrame: A DataFrame containing the correlation coefficients.
    """
    corrs = {"var": [], "r": []}

    r = xr.corr(ds["speed"], ds["speed_era5"]).item()
    corrs["var"].append("speed")
    corrs["r"].append(r)

    r = xr.corr(ds["u"], ds["u_era5"]).item()
    corrs["var"].append("u")
    corrs["r"].append(r)

    r = xr.corr(ds["v"], ds["v_era5"]).item()
    corrs["var"].append("v")
    corrs["r"].append(r)

    df = pd.DataFrame(data=corrs)

    return df


def compute(param):
    """
    Compute the dataset and correlation DataFrame for the given parameters.

    Args:
        param (parameters): The parameters object.

    Returns:
        tuple: A tuple containing the dataset and the correlation DataFrame.
    """
    print("computing corr")
    ds = xr.open_dataset("../data/processed/" + param.tag + ".nc")

    ds = ds.sel(satellite="j1")
    ds["speed"] = np.sqrt(ds.u**2 + ds.v**2)
    ds["speed_era5"] = np.sqrt(ds.u_era5**2 + ds.v_era5**2)

    df = compute_corr(ds)
    return ds, df


def main(param):
    """
    Main function to compute and plot histograms for the given parameters.

    Args:
        param (parameters): The parameters object.
    """
    param.set_alg("rand")
    ds_rand, df_rand = compute(param)

    param.set_alg("tvl1")
    ds_tvl1, df_tvl1 = compute(param)
    multiple_panel_hist(param.tag, ds_rand, ds_tvl1, df_rand, df_tvl1)


if __name__ == "__main__":
    param = parameters()
    param.set_plev_coarse(5)
    param.set_timedelta(6)
    param.set_Lambda(0.15)
    main(param)
