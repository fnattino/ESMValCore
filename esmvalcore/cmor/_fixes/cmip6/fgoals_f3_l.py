"""Fixes for CMIP6 FGOALS-f3-L model."""
import cftime
import dask.array as da
import numpy as np

from ..common import OceanFixGrid
from ..fix import Fix

Tos = OceanFixGrid


class AllVars(Fix):
    """Fixes for all vars."""
    def fix_metadata(self, cubes):
        """Fix parent time units.

        FGOALS-f3-L Amon data may have a bad time bounds spanning 20 days.

        Parameters
        ----------
        cubes : iris.cube.CubeList
            Input cubes.

        Returns
        -------
        iris.cube.CubeList
        """
        for cube in cubes:
            if cube.attributes['table_id'] == 'Amon':
                time = cube.coord('time')
                if np.any(time.bounds[:-1, 1] != time.bounds[1:, 0]):
                    times = time.units.num2date(time.points)
                    starts = [
                        cftime.DatetimeNoLeap(c.year, c.month, 1)
                        for c in times
                    ]
                    ends = [
                        cftime.DatetimeNoLeap(c.year, c.month +
                                              1, 1) if c.month < 12 else
                        cftime.DatetimeNoLeap(c.year + 1, 1, 1) for c in times
                    ]
                    time.bounds = time.units.date2num(
                        np.stack([starts, ends], -1))
        return cubes


class Sftlf(Fix):
    """Fixes for sftlf."""
    def fix_data(self, cube):
        """Fix data.

        Unit is %, values are <= 1.

        Parameters
        ----------
        cube: iris.cube.Cube
            Cube to fix

        Returns
        -------
        iris.cube.Cube
            Fixed cube. It can be a difference instance.
        """
        if cube.units == "%" and da.max(cube.core_data()).compute() <= 1.:
            cube.data = cube.core_data() * 100.
        return cube

class Omon(Fix):
    """Fixes for ocean variables."""

    def fix_metadata(self, cubes):
        """Fix ocean depth coordinate.

        Parameters
        ----------
        cubes: iris CubeList
            List of cubes to fix

        Returns
        -------
        iris.cube.CubeList

        """
        for cube in cubes:
            if not cube.coord('latitude').bounds:
                cube.coord('latitude').guess_bounds()
            if not cube.coord('longitude').bounds:
                cube.coord('longitude').guess_bounds()

            if cube.coords('latitude'):
                cube.coord('latitude').var_name = 'lat'
            if cube.coords('longitude'):
                cube.coord('longitude').var_name = 'lon'

            if cube.coords(axis='Z'):
                z_coord = cube.coord(axis='Z')
                if str(z_coords.units) == 'cm' and np.max(z_points)>10000.:
                    z_coord.units = cf_units.Unit('m')
                fix_ocean_depth_coord(cube)
        return cubes


