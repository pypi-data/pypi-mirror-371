from meegsim._check import check_colors, check_scale_factors
from meegsim.sources import _get_point_sources_in_hemi, _get_patch_sources_in_hemis
from meegsim.utils import _hemi_to_index


DEFAULT_COLORS = dict(point="green", patch="Oranges", noise="black", candidate="yellow")
DEFAULT_SCALE_FACTORS = dict(point=0.75, noise=0.3, candidate=0.05)
DEFAULT_PLOT_KWARGS = dict(
    background="w",
    cortex="low_contrast",
    colorbar=False,
    clim=dict(kind="value", lims=[0, 0.5, 1]),
    transparent=True,
)


def plot_source_configuration(
    sc,
    subject,
    hemi="lh",
    colors=None,
    scale_factors=None,
    show_noise_sources=True,
    show_candidate_locations=False,
    **plot_kwargs,
):
    """
    This function can be used to plot the positions of all sources in the
    configuration. Parameters and their values are described in the docstring
    of :meth:`SourceConfiguration.plot`.
    """
    # Overwrite the default values with user input
    check_colors(colors)
    source_colors = DEFAULT_COLORS.copy()
    if colors is not None:
        source_colors.update(colors)

    check_scale_factors(scale_factors)
    source_scale_factors = DEFAULT_SCALE_FACTORS.copy()
    if scale_factors is not None:
        source_scale_factors.update(scale_factors)

    hemis = ["lh", "rh"] if hemi in ["both", "split"] else [hemi]

    # NOTE: we start with plotting all patch sources as an stc object
    # to ensure that the Brain object is initialized correctly
    patch_data_stc = _get_patch_sources_in_hemis(sc._sources.values(), sc.src, hemis)

    kwargs = DEFAULT_PLOT_KWARGS.copy()
    kwargs.update(plot_kwargs)
    brain = patch_data_stc.plot(
        subject=subject, hemi=hemi, colormap=source_colors["patch"], **kwargs
    )

    # Point/noise sources and candidate locations are added via
    # add_foci that needs to be run for each hemisphere separately
    for hemi in hemis:
        # All candidate locations (resource-heavy, disabled by default)
        if show_candidate_locations:
            src_idx = _hemi_to_index(hemi)
            candidate_locations = sc.src[src_idx]["vertno"]
            brain.add_foci(
                candidate_locations,
                coords_as_verts=True,
                hemi=hemi,
                color=source_colors["candidate"],
                scale_factor=source_scale_factors["candidate"],
            )

        # Noise sources
        if show_noise_sources:
            brain.add_foci(
                _get_point_sources_in_hemi(sc._noise_sources.values(), hemi),
                coords_as_verts=True,
                hemi=hemi,
                color=source_colors["noise"],
                scale_factor=source_scale_factors["noise"],
            )

        # Point sources (always shown)
        brain.add_foci(
            _get_point_sources_in_hemi(sc._sources.values(), hemi),
            coords_as_verts=True,
            hemi=hemi,
            color=source_colors["point"],
            scale_factor=source_scale_factors["point"],
        )

    return brain
