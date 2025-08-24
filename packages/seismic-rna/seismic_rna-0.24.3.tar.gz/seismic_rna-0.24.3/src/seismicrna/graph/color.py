from abc import ABC, abstractmethod
from functools import cache, cached_property
from inspect import getmembers
from sys import modules
from typing import Any, Hashable

from .base import BaseGraph
from ..core.seq import BASEA, BASEC, BASEG, BASET, BASEN
from ..core.table import REL_CODES

DEFAULT_CODE = "x"
DEFAULT_NAME = "Default"


class ColorMap(ABC):
    """ Color map for a graph. """

    def __init__(self, name: str, **kwargs):
        self.name = name
        self._colors = self._set_colors(**kwargs)

    @abstractmethod
    def _set_colors(self, **kwargs):
        return dict(**kwargs)

    @abstractmethod
    def get_default_color(self) -> str:
        """ Default color. """

    def get(self, item: Hashable, default: Any | None = None):
        return self._colors.get(item, (default if default is not None
                                       else self.get_default_color()))


class SeqColorMap(ColorMap):
    """ Color map for bases A, C, G, and T. """

    def __init__(self, name: str, a: str, c: str, g: str, t: str, n: str):
        super().__init__(name, a=a, c=c, g=g, t=t, n=n)

    def _set_colors(self, *, a: str, c: str, g: str, t: str, n: str):
        return {BASEA: a, BASEC: c, BASEG: g, BASET: t, BASEN: n}

    def get_default_color(self):
        return self._colors[BASEN]


class RelColorMap(ColorMap):
    """ Color map for relationships. """

    def __init__(self,
                 name: str,
                 v: str,
                 n: str,
                 e: str,
                 m: str,
                 d: str,
                 i: str,
                 s: str,
                 a: str,
                 c: str,
                 g: str,
                 t: str,
                 x: str):
        super().__init__(name,
                         v=v,
                         n=n,
                         e=e,
                         m=m,
                         d=d,
                         i=i,
                         s=s,
                         a=a,
                         c=c,
                         g=g,
                         t=t,
                         x=x)

    def _set_colors(self, **kwargs):
        colors = {DEFAULT_NAME: kwargs.pop(DEFAULT_CODE)}
        for key, field in REL_CODES.items():
            colors[field] = kwargs.pop(key)
        if kwargs:
            raise TypeError(f"Unexpected keyword arguments: {kwargs}")
        return colors

    def get_default_color(self):
        return self._colors[DEFAULT_NAME]


basic = SeqColorMap("basic",
                    a="#FF0000",
                    c="#0000FF",
                    g="#FFC000",
                    t="#008000",
                    n="#7f7f7f")
water = SeqColorMap("water",
                    a="#A15252",
                    c="#3D427D",
                    g="#E3CC7B",
                    t="#76B887",
                    n="#7f7f7f")
earth = SeqColorMap("earth",
                    a="#D17777",
                    c="#464EA6",
                    g="#E3CC7B",
                    t="#336140",
                    n="#7f7f7f")
steel = SeqColorMap("steel",
                    a="#663328",
                    c="#716B80",
                    g="#91B8AC",
                    t="#D9D5B4",
                    n="#7f7f7f")
tetra = SeqColorMap("tetra",
                    a="#F09869",
                    c="#8875C7",
                    g="#F7ED8F",
                    t="#99C3EB",
                    n="#f0f0f0")
# The BWong palette is from Wong, B. Points of view: Color blindness.
# Nat Methods 8, 441 (2011). https://doi.org/10.1038/nmeth.1618
bwong = SeqColorMap("bwong",
                    a="#d55e00",
                    c="#0072b2",
                    g="#e69f00",
                    t="#56b4e9",
                    n="#999999")
# The Bright palette is adapted (with minor adjustments)
# from the R Color Palette Finder:
# https://r-graph-gallery.com/color-palette-finder
bright = SeqColorMap("bright",
                     a="#D44D5C",
                     c="#046E8F",
                     g="#FFAA24",
                     t="#96D6D2",
                     n="#999999")

crayons = RelColorMap("crayons",
                      v="#424242",
                      n="#A9A9A9",
                      e="#942193",
                      m="#929000",
                      d="#FF2600",
                      i="#00FA92",
                      s="#FF40FF",
                      a="#73FCD6",
                      c="#FFD479",
                      g="#7A81FF",
                      t="#FF8AD8",
                      x="#AAAAAA")
hexta = RelColorMap("hexta",
                    v="#FBED94",
                    n="#C05F15",
                    e="#597DE4",
                    m="#0F155F",
                    d="#FBED94",
                    i="#0F155F",
                    s="#743B4A",
                    a="#C05F15",
                    c="#597DE4",
                    g="#743B4A",
                    t="#9BD1D0",
                    x="#AAAAAA")
# The Safe palette was adapted from the R Color Palette Finder:
# https://r-graph-gallery.com/color-palette-finder
safe = RelColorMap("safe",
                   v="#555555",
                   n="#6699CC",
                   e="#88CCEE",
                   m="#661100",
                   d="#AA4499",
                   i="#44AA99",
                   s="#999933",
                   a="#CC6677",
                   c="#332288",
                   g="#DDCC77",
                   t="#117733",
                   x="#AAAAAA")

DEFAULTS: dict[type[ColorMap], ColorMap] = {
    RelColorMap: safe,
    SeqColorMap: bright,
}


@cache
def get_colormaps(cmap_class: type[ColorMap]):
    """ Return a dict of all color maps of a given class. """
    colormaps: dict[str, cmap_class] = dict()
    for _, cmap in getmembers(modules[__name__],
                              lambda item: isinstance(item, cmap_class)):
        if cmap.name in colormaps:
            raise ValueError(
                f"Duplicate {cmap_class.__name__}: {repr(cmap.name)}"
            )
        colormaps[cmap.name] = cmap
    if (default := DEFAULTS[cmap_class]) not in colormaps:
        raise ValueError(
            f"Default {cmap_class.__name__} {repr(default)} does not exist")
    return colormaps


def get_cmap(cmap_class: type[ColorMap], name: str | None = None):
    """ Get a color map of a given class by its name. """
    if name is None:
        # Use the default color map for the class.
        return DEFAULTS[cmap_class]
    cmaps = get_colormaps(cmap_class)
    if not cmaps:
        raise ValueError(f"No color maps of class {repr(cmap_class.__name__)}")
    return cmaps[name]


class ColorMapGraph(BaseGraph, ABC):
    """ Graph with an explicit color map. """

    @classmethod
    @abstractmethod
    def get_cmap_type(cls) -> type[ColorMap]:
        """ Type of the color map. """

    def __init__(self, *, cmap: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self._cmap_name = cmap

    @cached_property
    def cmap(self) -> ColorMap:
        """ Color map of the graph. """
        return get_cmap(self.get_cmap_type(), self._cmap_name)
