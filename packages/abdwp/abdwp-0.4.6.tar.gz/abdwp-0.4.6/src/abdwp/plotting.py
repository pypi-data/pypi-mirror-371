import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import importlib.resources
from typing import Optional, Tuple

# strike zone definitional constants
STRIKE_ZONE_WIDTH_INCHES = 20
STRIKE_ZONE_WIDTH_FEET = STRIKE_ZONE_WIDTH_INCHES / 12
STRIKE_ZONE_HALF_WIDTH = STRIKE_ZONE_WIDTH_FEET / 2


def use_abdwp_style():
    with importlib.resources.path("abdwp.style", "abdwp.mplstyle") as style_path:
        plt.style.use(str(style_path))


def draw_field(ax, show_mound=False, zorder=-1, set_aspect=True):

    # setup
    base_distance = 90
    mound_distance = 60.5
    outfield_radius = 400
    infield_radius = 200

    # coordinates of bases and mound
    home = np.array([0, 0])
    first = np.array([base_distance / np.sqrt(2), base_distance / np.sqrt(2)])
    second = np.array([0, base_distance * np.sqrt(2)])
    third = np.array([-base_distance / np.sqrt(2), base_distance / np.sqrt(2)])
    mound = np.array([0, mound_distance])

    # outfield arc
    theta = np.linspace(np.pi / 4, 3 * np.pi / 4, 200)
    outfield_x = outfield_radius * np.cos(theta)
    outfield_y = outfield_radius * np.sin(theta)
    outfield = np.vstack([outfield_x, outfield_y])

    # infield arc
    infield_x = infield_radius * np.cos(theta)
    infield_y = infield_radius * np.sin(theta)
    infield = np.vstack([infield_x, infield_y])

    # draw base paths
    ax.plot([home[0], first[0]], [home[1], first[1]], "k", zorder=zorder)
    ax.plot([first[0], second[0]], [first[1], second[1]], "k", zorder=zorder)
    ax.plot([second[0], third[0]], [second[1], third[1]], "k", zorder=zorder)
    ax.plot([third[0], home[0]], [third[1], home[1]], "k", zorder=zorder)

    # draw bases
    ax.scatter(*first, color="black", marker="D", s=20, zorder=zorder)
    ax.scatter(*second, color="black", marker="D", s=20, zorder=zorder)
    ax.scatter(*third, color="black", marker="D", s=20, zorder=zorder)

    # draw home plate
    ax.scatter(0, 0, color="black", marker="D", s=20, zorder=zorder)

    # draw mound
    if show_mound:
        ax.scatter(*mound, color="black", marker="_", zorder=zorder)

    # draw outfield arc
    ax.plot(outfield[0], outfield[1], c="k", zorder=zorder)

    # draw infield arc
    ax.plot(infield[0], infield[1], c="k", zorder=zorder)

    # foul lines
    ax.plot([home[0], outfield[0, 0]], [home[1], outfield[1, 0]], "k", zorder=zorder)
    ax.plot([home[0], outfield[0, -1]], [home[1], outfield[1, -1]], "k", zorder=zorder)

    # set equal aspect ratio for proper field proportions
    if set_aspect:
        ax.set_aspect("equal")


def draw_strikezone(
    ax,
    sz_bot: float = 1.5,
    sz_top: float = 3.5,
    sz_left: Optional[float] = None,
    sz_right: Optional[float] = None,
    fill_zorder: int = -999,
    border_zorder: int = 999,
    fill: bool = True,
    linewidth: float = 0.5,
    alpha: float = 0.2,
    set_aspect: bool = True,
    **kwargs,
) -> None:
    """
    Draw a strike zone rectangle on the given axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on
    sz_bot : float, default 1.5
        Bottom of strike zone in feet
    sz_top : float, default 3.5
        Top of strike zone in feet
    sz_left : float, optional
        Left edge of strike zone in feet (must be used with sz_right)
    sz_right : float, optional
        Right edge of strike zone in feet (must be used with sz_left)
    fill_zorder : int, default -1
        Drawing order for the fill rectangle
    border_zorder : int, optional
        Drawing order for the border rectangle. If None, defaults to fill_zorder + 1000
    fill : bool, default True
        Whether to fill the rectangle
    linewidth : float, default 0.5
        Width of the rectangle border
    alpha : float, default 0.2
        Transparency of the fill rectangle
    set_aspect : bool, default True
        Whether to set equal aspect ratio
    **kwargs
        Additional arguments passed to Rectangle

    Returns
    -------
    tuple of (patches.Rectangle, patches.Rectangle)
        The created rectangle patches (fill_rect, border_rect).
        Either can be None if not created.

    Raises
    ------
    ValueError
        If sz_top <= sz_bot or if only one of sz_left/sz_right is provided
    """

    if sz_top <= sz_bot:
        raise ValueError("sz_top must be greater than sz_bot")

    if (sz_left is not None) != (sz_right is not None):
        raise ValueError("If used, sz_left and sz_right must be supplied together.")

    height = sz_top - sz_bot
    if sz_left is not None and sz_right is not None:
        width = sz_right - sz_left
    else:
        width = STRIKE_ZONE_WIDTH_FEET
        sz_left = -STRIKE_ZONE_HALF_WIDTH

    if border_zorder is None:
        border_zorder = fill_zorder + 1000

    fill_rect = None
    border_rect = None

    if fill:
        fill_rect = patches.Rectangle(
            xy=(sz_left, sz_bot),
            width=width,
            height=height,
            facecolor="tab:gray",
            edgecolor="none",
            alpha=alpha,
            zorder=fill_zorder,
            **kwargs,
        )
        ax.add_patch(fill_rect)

    border_rect = patches.Rectangle(
        xy=(sz_left, sz_bot),
        width=width,
        height=height,
        facecolor="none",
        edgecolor="black",
        linewidth=linewidth,
        zorder=border_zorder,
        **kwargs,
    )
    ax.add_patch(border_rect)

    if set_aspect:
        ax.set_aspect("equal")


def format_strikezone_axes(
    ax,
    xlabel: str = "Horizontal Location (Feet)",
    ylabel: str = "Vertical Location (Feet)",
    xlim: Tuple[float, float] = (-2.75, 2.75),
    ylim: Tuple[float, float] = (-1, 6),
    set_aspect: bool = True,
    show_spines: bool = True,
    show_grid: bool = False,
    grid_alpha: float = 0.3,
) -> None:
    """
    Format axes for strike zone plotting.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to format
    xlabel : str, default "Horizontal Location (Feet)"
        X-axis label
    ylabel : str, default "Vertical Location (Feet)"
        Y-axis label
    xlim : tuple of float, default (-2.75, 2.75)
        X-axis limits
    ylim : tuple of float, default (-1, 6)
        Y-axis limits
    set_aspect : bool, default True
        Whether to set equal aspect ratio
    show_spines : bool, default True
        Whether to show axis spines
    show_grid : bool, default False
        Whether to show grid lines
    grid_alpha : float, default 0.3
        Transparency of grid lines
    """
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    if set_aspect:
        ax.set_aspect("equal")

    for spine in ax.spines.values():
        spine.set_visible(show_spines)

    if show_grid:
        ax.grid(True, alpha=grid_alpha)
