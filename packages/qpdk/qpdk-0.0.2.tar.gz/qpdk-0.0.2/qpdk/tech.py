"""Technology definitions."""

from collections.abc import Callable
from functools import partial, wraps
from typing import Any

import gdsfactory as gf
from doroutes.bundles import add_bundle_astar
from gdsfactory.cross_section import (
    CrossSection,
)
from gdsfactory.technology import (
    LayerLevel,
    LayerMap,
    LayerStack,
    LayerViews,
)
from gdsfactory.typings import (
    ConnectivitySpec,
    Layer,
    LayerSpec,
)

from qpdk.config import PATH

nm = 1e-3


class LayerMapQPDK(LayerMap):
    """Layer map for Cornerstone technology."""

    M1_DRAW: Layer = (10, 0)  # CPW center + pads
    M1_ETCH: Layer = (11, 0)  # Subtractive etch / negative mask regions
    M1_CUTOUT: Layer = (12, 0)  # Keepouts/slotting/DRC voids

    # Airbridges
    AB_DRAW: Layer = (20, 0)  # Bridge metal
    AB_VIA: Layer = (21, 0)  # Landing pads / contacts
    AB_ETCH: Layer = (22, 0)  # Sacrificial/undercut windows (if used)

    # Junction (markers / optional area)
    JJ_MARK: Layer = (40, 0)  # EBL / SEM localization marker (non-fab geometry)
    JJ_AREA: Layer = (41, 0)  # Optional bridge/overlap definition

    # Packaging / backside / misc
    TSV: Layer = (60, 0)  # Throughs / vias / backside features
    DICE: Layer = (70, 0)  # Dicing lanes

    # Alignment / admin
    ALN_TOP: Layer = (80, 0)  # Frontside alignment
    ALN_BOT: Layer = (81, 0)  # Backside alignment
    TEXT: Layer = (90, 0)  # Mask text / version labels

    # Simulation-only helpers (never sent to fab)
    SIM_ONLY: Layer = (99, 0)

    # labels for gdsfactory
    LABEL_SETTINGS: Layer = (100, 0)  # type: ignore
    LABEL_INSTANCE: Layer = (101, 0)  # type: ignore


L = LAYER = LayerMapQPDK


def get_layer_stack(thickness_m1: float = 150e-9) -> LayerStack:
    """Returns LayerStack.

    Args:
        thickness_m1: thickness of base metal film in um.
    """
    return LayerStack(
        layers={
            # Base metal film (e.g., Al 150 nm on sapphire)
            "m1": LayerLevel(
                layer=L.M1_DRAW,
                thickness=thickness_m1,
                zmin=0.0,  # top of substrate
                material="Al",
                sidewall_angle=90.0,
                mesh_order=1,
            ),
            # Optional: alignment metal (Cr/Au) if you physically pattern it
            "aln_top": LayerLevel(
                layer=L.ALN_TOP,
                thickness=50e-9,  # nominal
                zmin=0.0,
                material="CrAu",
                sidewall_angle=90.0,
                mesh_order=2,
            ),
            # Airbridge metal sitting above M1 (example: +300 nm)
            "ab_metal": LayerLevel(
                layer=L.AB_DRAW,
                thickness=300e-9,
                zmin=150e-9,  # stacked above M1 for EM exports
                material="Al",
                sidewall_angle=90.0,
                mesh_order=3,
            ),
            # (Optional) JJ_AREA can be exported as a thin film if you use it in EM
            "jj_area": LayerLevel(
                layer=L.JJ_AREA,
                thickness=50e-9,
                zmin=150e-9,
                material="AlOx/Al",  # placeholder; use what your solver expects
                sidewall_angle=90.0,
                mesh_order=4,
            ),
            # SIM_ONLY is non-fab; keep thin so it won’t perturb EM
            "sim_only": LayerLevel(
                layer=L.SIM_ONLY,
                thickness=1e-9,
                zmin=0.0,
                material="vacuum",
                sidewall_angle=90.0,
                mesh_order=9,
            ),
            # You can add TSV/backside as real films if you simulate them
            # "tsv": LayerLevel(layer=L.TSV, thickness=... , zmin=... , material="Cu"),
        }
    )


LAYER_STACK = get_layer_stack()
LAYER_VIEWS = gf.technology.LayerViews(PATH.lyp_yaml)


class Tech:
    """Technology parameters."""

    pass


TECH = Tech()

############################
# Cross-sections functions
############################

cross_sections: dict[str, Callable[..., CrossSection]] = {}
_cross_section_default_names: dict[str, str] = {}


def xsection(func: Callable[..., CrossSection]) -> Callable[..., CrossSection]:
    """Returns decorated to register a cross section function.

    Ensures that the cross-section name matches the name of the function that generated it when created using default parameters

    .. code-block:: python

        @xsection
        def strip(width=TECH.width_strip, radius=TECH.radius_strip):
            return gf.cross_section.cross_section(width=width, radius=radius)
    """
    default_xs = func()
    _cross_section_default_names[default_xs.name] = func.__name__

    @wraps(func)
    def newfunc(**kwargs: Any) -> CrossSection:
        xs = func(**kwargs)
        if xs.name in _cross_section_default_names:
            xs._name = _cross_section_default_names[xs.name]
        return xs

    cross_sections[func.__name__] = newfunc
    return newfunc


@xsection
def strip(
    width: float = 3,
    layer: LayerSpec = "M1_DRAW",
) -> CrossSection:
    """Return Strip cross_section."""
    radius = width
    return gf.cross_section.cross_section(
        width=width,
        layer=layer,
        radius=radius,
    )


@xsection
def metal_routing(
    width: float = 3,
    layer: LayerSpec = "M1_DRAW",
) -> CrossSection:
    """Return metal cross_section."""
    radius = width
    return gf.cross_section.cross_section(
        width=width,
        layer=layer,
        radius=radius,
    )


############################
# Routing functions
############################

route_single = partial(gf.routing.route_single, cross_section="strip")
route_bundle = partial(gf.routing.route_bundle, cross_section="strip")


route_bundle_rib = partial(
    route_bundle,
    cross_section="rib",
)
route_bundle_metal = partial(
    route_bundle,
    straight="straight_metal",
    bend="bend_metal",
    taper=None,
    cross_section="metal_routing",
    port_type="electrical",
)
route_bundle_metal_corner = partial(
    route_bundle,
    straight="straight_metal",
    bend="wire_corner",
    taper=None,
    cross_section="metal_routing",
    port_type="electrical",
)

route_astar = partial(
    add_bundle_astar,
    layers=["WG"],
    bend="bend_euler",
    straight="straight",
    grid_unit=500,
    spacing=3,
)

route_astar_metal = partial(
    add_bundle_astar,
    layers=["PAD"],
    bend="wire_corner",
    straight="straight_metal",
    grid_unit=500,
    spacing=15,
)


routing_strategies = dict(
    route_bundle=route_bundle,
    route_bundle_metal_corner=route_bundle_metal_corner,
    route_astar=route_astar,
    route_astar_metal=route_astar_metal,
)

if __name__ == "__main__":
    from typing import cast

    from gdsfactory.technology.klayout_tech import KLayoutTechnology

    LAYER_VIEWS = LayerViews(PATH.lyp_yaml)
    # LAYER_VIEWS.to_lyp(PATH.lyp)

    connectivity = cast(list[ConnectivitySpec], [("HEATER", "HEATER", "PAD")])

    t = KLayoutTechnology(
        name="qpdk",
        layer_map=LAYER,
        layer_views=LAYER_VIEWS,
        layer_stack=LAYER_STACK,
        connectivity=connectivity,
    )
    t.write_tech(tech_dir=PATH.klayout)
    # print(DEFAULT_CROSS_SECTION_NAMES)
    # print(strip() is strip())
    # print(strip().name, strip().name)
    # c = gf.c.bend_euler(cross_section="metal_routing")
    # c.pprint_ports()
