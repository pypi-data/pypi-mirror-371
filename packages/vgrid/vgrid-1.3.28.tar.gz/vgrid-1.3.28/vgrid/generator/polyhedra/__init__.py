"""
Polyhedra module for vgrid.

This module provides various polyhedra implementations used in discrete global grid systems (DGGS).
"""

from .cube import cube
from .cube_s2 import cube_s2
from .hexagon import hexagon
from .octahedron import octahedron
from .tetrahedron import tetrahedron
from .fuller_icosahedron import fuller_icosahedron
from .rhombic_icosahedron import rhombic_icosahedron

__all__ = [
    'cube', 'cube_s2', 'hexagon', 'octahedron', 'tetrahedron',
    'fuller_icosahedron', 'rhombic_icosahedron'
]
