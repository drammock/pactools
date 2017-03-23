import numpy as np
import matplotlib as matplotlib
import matplotlib.pyplot as plt

from .utils import add_colorbar


def plot_comodulogram_histogram(comodulogram, low_fq_range, low_fq_width,
                                high_fq_range, high_fq_width, method,
                                vmin=None, vmax=None, save_name=None):
    """Plot one comodulogram with histograms."""
    vmin = min(0, comodulogram.min()) if vmin is None else vmin
    vmax = comodulogram.max() if vmax is None else vmax

    fig = plt.figure(figsize=(9, 9))
    gs = matplotlib.gridspec.GridSpec(9, 9)
    ax_vert = plt.subplot(gs[:-2, :2])
    ax_hori = plt.subplot(gs[-2:, 2:-1])
    ax_main = plt.subplot(gs[:-2, 2:-1])
    ax_cbar = plt.subplot(gs[:-2, -1])

    extent = [
        low_fq_range[0], low_fq_range[-1], high_fq_range[0], high_fq_range[-1]
    ]
    cax = ax_main.imshow(comodulogram.T, cmap=plt.cm.viridis, aspect='auto',
                         origin='lower', extent=extent, interpolation='none',
                         vmax=vmax, vmin=vmin)
    # remove x,y label from main plot
    ax_main.tick_params(labelbottom='off', labelleft='off')

    fig.colorbar(cax, cax=ax_cbar, ticks=np.linspace(vmin, vmax, 6))
    ax_hori.set_xlabel('Phase frequency (Hz) (w=%.1f)' % low_fq_width)
    ax_vert.set_ylabel('Amplitude frequency (Hz) (w=%.2f)' % high_fq_width)
    plt.suptitle('Phase Amplitude Coupling measured with Modulation Index'
                 ' (%s)' % method, fontsize=14)

    ax_vert.plot(np.mean(comodulogram.T, axis=1), high_fq_range)
    ax_vert.set_ylim(extent[2:])
    ax_hori.plot(low_fq_range, np.mean(comodulogram.T, axis=0))
    ax_hori.set_xlim(extent[:2])

    vmx = np.max([
        np.mean(comodulogram.T, axis=1).max(),
        np.mean(comodulogram.T, axis=0).max()
    ])
    vmx = vmax + vmax / 10
    ax_hori.set_ylim([0, vmx])  # same limits than in vert plot
    ax_vert.set_xlim([0, vmx])  # same limits than in hori plot
    ax_vert.spines['right'].set_visible(False)
    ax_vert.spines['top'].set_visible(False)
    ax_vert.yaxis.set_ticks_position('left')
    ax_vert.xaxis.set_ticks_position('bottom')
    ax_hori.spines['right'].set_visible(False)
    ax_hori.spines['top'].set_visible(False)
    ax_hori.yaxis.set_ticks_position('left')
    ax_hori.xaxis.set_ticks_position('bottom')

    if save_name is None:
        save_name = ('%s_wlo%.2f_whi%.1f' %
                     (method, low_fq_width, high_fq_width))
    fig.savefig(save_name + '.png')
    return fig


def plot_comodulogram(comodulograms, fs, low_fq_range, high_fq_range,
                      titles=None, fig=None, axs=None, cmap=None, vmin=None,
                      vmax=None, unit='', cbar=True, label=True,
                      contours=None):
    """
    Plot one or more comodulograms.

    Parameters
    ----------
    comodulograms : array, shape (len(low_fq_range), len(high_fq_range))
        Comodulogram for each couple of frequencies. If a list of comodulograms
        is given, or if the shape of the array is (n_channels,
        len(low_fq_range), len(high_fq_range)), it plots each comodulogram in
        each ax given in `axs`.

    fs : float,
        Sampling frequency

    low_fq_range : array or list
        List of filtering frequencies (phase signal)

    high_fq_range : array or list
        List of filtering frequencies (amplitude signal)

    titles : list of string or None
        List of titles for each comodulogram

    fig : matplotlib.figure.Figure or None
        Figure instance where the comodulograms are drawn.
        If None, a new figure is created.

    axs : list or array of matplotlib.axes._subplots.AxesSubplot
        Axes where the comodulograms are drawn. If None, a new figure is
        created. Typical use is: fig, axs = plt.subplots(3, 4)

    cmap : colormap or None
        Colormap used in the plot. If None, it uses 'viridis' colormap.

    vmin, vmax : float or None
        If not None, they define the min/max value of the plot, else they are
        set to (0, comodulograms.max()).

    unit : string (default: '')
        Unit of the comodulogram

    cbar : True or False
        Display colorbar or not

    label : True or False
        Display labels or not

    contours : None or float
        If not None, contours will be added around values above contours value
    """
    if isinstance(comodulograms, list):
        comodulograms = np.array(comodulograms)

    tight_layout = True
    if comodulograms.ndim == 2:
        comodulograms = comodulograms[None, :, :]
        tight_layout = False

    n_comods = comodulograms.shape[0]

    if fig is None or axs is None:
        fig, axs = plt.subplots(1, n_comods, figsize=(4 * n_comods, 3))
    axs = np.array(axs).ravel()

    if vmin is None and vmax is None:
        vmin = min(0, comodulograms.min())
        vmax = max(0, comodulograms.max())
        if vmin < 0 and vmax > 0:
            vmax = max(vmax, -vmin)
            vmin = -vmax
            if cmap is None:
                cmap = plt.get_cmap('RdBu_r')

    if cmap is None:
        cmap = plt.get_cmap('viridis')

    n_channels, n_low_fq, n_high_fq = comodulograms.shape
    extent = [
        low_fq_range[0], low_fq_range[-1], high_fq_range[0], high_fq_range[-1]
    ]

    # plot the image
    for i in range(n_channels):
        cax = axs[i].imshow(comodulograms[i].T, cmap=cmap, vmin=vmin,
                            vmax=vmax, aspect='auto', origin='lower',
                            extent=extent, interpolation='none')

        if titles is not None:
            axs[i].set_title(titles[i], fontsize=12)

        if contours is not None:
            axs[i].contour(comodulograms[i].T, levels=np.atleast_1d(contours),
                           colors='w', origin='lower', extent=extent)

    if label:
        axs[-1].set_xlabel('Driver frequency (Hz)')
        axs[0].set_ylabel('Signal frequency (Hz)')
    if tight_layout:
        fig.tight_layout()
    if cbar:
        # plot the colorbar once
        ax = axs[0] if len(axs) == 1 else None
        add_colorbar(fig, cax, vmin, vmax, unit=unit, ax=ax)

    return fig