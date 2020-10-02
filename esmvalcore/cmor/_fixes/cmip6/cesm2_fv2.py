"""Fixes for CESM2-FV2 model."""
from .cesm2 import Cl as BaseCl
from .cesm2 import Tas as BaseTas

from ..fix import Fix

import numpy as np
import iris
import cf_units


Cl = BaseCl


Cli = Cl


Clw = Cl


Tas = BaseTas


class msftmz(Fix):
    """Fix msftmz."""

    def fix_metadata(self, cubes):
        """
        Problems:
         basin has incorrect long name, var.
         Dimensions are also wrong.
        Parameters
        ----------
        cube: iris.cube.CubeList
        Returns
        -------
        iris.cube.CubeList
        """
        new_cubes = []
        for cube in cubes:

            # Fix regions coordinate
            cube.remove_coord(cube.coord("region"))
            values = np.array(['atlantic_arctic_ocean', 'indian_pacific_ocean',
                               'global_ocean',], dtype='<U21')
            basin_coord = iris.coords.AuxCoord(
                values,
                standard_name=u'region',
                units=cf_units.Unit('no_unit'),
                long_name=u'ocean basin',
                var_name='basin')

            # Replace broken coord with correct one.
            cube.add_aux_coord(basin_coord, data_dims=1)
            # Fix depth
            depth = cube.coord('lev')
            depth.var_name = 'depth'
            depth.standard_name = 'depth'
            depth.long_name = 'depth'
        return cubes

