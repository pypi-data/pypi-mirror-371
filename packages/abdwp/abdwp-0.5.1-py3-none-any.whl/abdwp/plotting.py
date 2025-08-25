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
    all_zones: Optional[bool] = None,
    az: Optional[bool] = None,
    border_color: Optional[str] = None,
    bc: Optional[str] = None,
    border_linewidth: Optional[float] = None,
    blw: Optional[float] = None,
    border_alpha: Optional[float] = None,
    ba: Optional[float] = None,
    border_zorder: Optional[int] = None,
    bz: Optional[int] = None,
    fill: Optional[bool] = None,
    f: Optional[bool] = None,
    fill_color: Optional[str] = None,
    fc: Optional[str] = None,
    fill_alpha: Optional[float] = None,
    fa: Optional[float] = None,
    fill_zorder: Optional[int] = None,
    fz: Optional[int] = None,
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
    all_zones : bool, optional
        Whether to draw a 3x3 grid dividing the strike zone into 9 equal zones. If not provided, defaults to False
    az : bool, optional
        Short alias for all_zones. Takes precedence if both are provided
    border_color : str, optional
        Color for the border and grid lines. If not provided, defaults to "black"
    bc : str, optional
        Short alias for border_color. Takes precedence if both are provided
    border_linewidth : float, optional
        Width of the rectangle border. If not provided, defaults to 0.5
    blw : float, optional
        Short alias for border_linewidth. Takes precedence if both are provided
    border_alpha : float, optional
        Transparency of the border and grid lines. If not provided, defaults to 1.0
    ba : float, optional
        Short alias for border_alpha. Takes precedence if both are provided
    border_zorder : int, optional
        Drawing order for the border rectangle. If not provided, defaults to 999
    bz : int, optional
        Short alias for border_zorder. Takes precedence if both are provided
    fill : bool, optional
        Whether to fill the rectangle. If not provided, defaults to True
    f : bool, optional
        Short alias for fill. Takes precedence if both are provided
    fill_color : str, optional
        Color for the fill rectangle. If not provided, defaults to "tab:gray"
    fc : str, optional
        Short alias for fill_color. Takes precedence if both are provided
    fill_alpha : float, optional
        Transparency of the fill rectangle. If not provided, defaults to 0.2
    fa : float, optional
        Short alias for fill_alpha. Takes precedence if both are provided
    fill_zorder : int, optional
        Drawing order for the fill rectangle. If not provided, defaults to -999
    fz : int, optional
        Short alias for fill_zorder. Takes precedence if both are provided
    **kwargs
        Additional arguments passed to Rectangle

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If sz_top <= sz_bot or if only one of sz_left/sz_right is provided
    """

    if sz_top <= sz_bot:
        raise ValueError("sz_top must be greater than sz_bot")

    if (sz_left is not None) != (sz_right is not None):
        raise ValueError("If used, sz_left and sz_right must be supplied together.")

    # handle all_zones alias
    if az is not None:
        all_zones = az
    elif all_zones is None:
        all_zones = False

    # handle border_color alias
    if bc is not None:
        border_color = bc
    elif border_color is None:
        border_color = "black"

    # handle border_linewidth alias
    if blw is not None:
        lw = blw
    elif border_linewidth is not None:
        lw = border_linewidth
    else:
        lw = 0.5

    # handle border_alpha alias
    if ba is not None:
        border_alpha = ba
    elif border_alpha is None:
        border_alpha = 1.0

    # handle border_zorder alias
    if bz is not None:
        border_zorder = bz
    elif border_zorder is None:
        border_zorder = 999

    # handle fill alias
    if f is not None:
        fill = f
    elif fill is None:
        fill = True

    # handle fill_color alias
    if fc is not None:
        fill_color = fc
    elif fill_color is None:
        fill_color = "tab:gray"

    # handle fill_alpha alias
    if fa is not None:
        fill_alpha = fa
    elif fill_alpha is None:
        fill_alpha = 0.2

    # handle fill_zorder alias
    if fz is not None:
        fill_zorder = fz
    elif fill_zorder is None:
        fill_zorder = -999

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
            facecolor=fill_color,
            edgecolor="none",
            alpha=fill_alpha,
            zorder=fill_zorder,
            **kwargs,
        )
        ax.add_patch(fill_rect)

    border_rect = patches.Rectangle(
        xy=(sz_left, sz_bot),
        width=width,
        height=height,
        facecolor="none",
        edgecolor=border_color,
        linewidth=lw,
        alpha=border_alpha,
        zorder=border_zorder,
        **kwargs,
    )
    ax.add_patch(border_rect)

    if all_zones:
        v_line1_x = sz_left + width / 3
        v_line2_x = sz_left + 2 * width / 3
        h_line1_y = sz_bot + height / 3
        h_line2_y = sz_bot + 2 * height / 3

        # center lines
        center_x = sz_left + width / 2
        center_y = sz_bot + height / 2

        # vertical grid lines within strike zone
        ax.plot(
            [v_line1_x, v_line1_x],
            [sz_bot, sz_top],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )
        ax.plot(
            [v_line2_x, v_line2_x],
            [sz_bot, sz_top],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )

        # horizontal grid lines within strike zone
        ax.plot(
            [sz_left, sz_left + width],
            [h_line1_y, h_line1_y],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )
        ax.plot(
            [sz_left, sz_left + width],
            [h_line2_y, h_line2_y],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )

        # extended center lines beyond strike zone
        plot_top = 20
        plot_bottom = -20
        plot_left = -20
        plot_right = 20

        # vertical center line extending from top of strike zone to top of plot
        ax.plot(
            [center_x, center_x],
            [sz_top, plot_top],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )

        # vertical center line extending from bottom of strike zone to bottom of plot
        ax.plot(
            [center_x, center_x],
            [sz_bot, plot_bottom],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )

        # horizontal center line extending from left edge of strike zone to left of plot
        ax.plot(
            [sz_left, plot_left],
            [center_y, center_y],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )

        # horizontal center line extending from right edge of strike zone to right of plot
        ax.plot(
            [sz_left + width, plot_right],
            [center_y, center_y],
            color=border_color,
            linewidth=lw,
            alpha=border_alpha,
            zorder=border_zorder,
        )

        # ensure spines are on top of extended lines
        for spine in ax.spines.values():
            spine.set_zorder(border_zorder + 1)


def format_strikezone_axes(
    ax,
    xlabel: str = "Horizontal Location (Feet)",
    ylabel: str = "Vertical Location (Feet)",
    xlim: Tuple[float, float] = (-2.75, 2.75),
    ylim: Tuple[float, float] = (-1, 6),
    set_aspect: bool = True,
    show_spines: bool = True,
    show_grid: bool = True,
    grid_alpha: Optional[float] = None,
    grid_lw: Optional[float] = None,
    minor_grid: bool = False,
    minor_grid_alpha: Optional[float] = None,
    minor_grid_lw: Optional[float] = None,
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
    show_grid : bool, default True
        Whether to show grid lines
    grid_alpha : float, optional
        Transparency of grid lines. If None, uses matplotlib default
    grid_lw : float, optional
        Line width of grid lines. If None, uses matplotlib default
    minor_grid : bool, default False
        Whether to show minor grid lines
    minor_grid_alpha : float, optional
        Transparency of minor grid lines. If None, uses matplotlib default
    minor_grid_lw : float, optional
        Line width of minor grid lines. If None, uses matplotlib default
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
        if grid_alpha is not None or grid_lw is not None:
            grid_kwargs = {}
            if grid_alpha is not None:
                grid_kwargs["alpha"] = grid_alpha
            if grid_lw is not None:
                grid_kwargs["linewidth"] = grid_lw
            ax.grid(True, **grid_kwargs)
        else:
            ax.grid(True)
    else:
        ax.grid(False)

    if minor_grid:
        ax.xaxis.set_minor_locator(plt.MultipleLocator(1 / 12))
        ax.yaxis.set_minor_locator(plt.MultipleLocator(1 / 12))
        minor_grid_kwargs = {}
        if minor_grid_alpha is not None:
            minor_grid_kwargs["alpha"] = minor_grid_alpha
        if minor_grid_lw is not None:
            minor_grid_kwargs["linewidth"] = minor_grid_lw
        ax.grid(which="minor", **minor_grid_kwargs)
