"""Fixes for CanESM5 model."""
import dask.array as da

from ..fix import Fix
from ..common import ClFixHybridPressureCoord


class Cl(ClFixHybridPressureCoord):
    """Fixes for cl."""

    def fix_metadata(self, cubes):
        """
        Fix metadata.

        Remove duplicate coordinate.

        Parameters
        ----------
        cubes: iris.cube.CubeList
            Input cubes.

        Returns
        -------
        iris.cube.CubeList
        """
        for cube in cubes:
            cube.remove_coord("air_pressure")

        return cubes


Cli = Cl


Clw = Cl


class Co2(Fix):
    """Fixes for co2."""

    def fix_data(self, cube):
        """Convert units from ppmv to 1.

        Parameters
        ----------
        cube : iris.cube.Cube
            Input cube.

        Returns
        -------
        iris.cube.Cube

        """
        metadata = cube.metadata
        cube *= 1.e-6
        cube.metadata = metadata
        return cube


class Gpp(Fix):
    """Fixes for gpp, ocean values set to 0 instead of masked."""

    def fix_data(self, cube):
        """Fix masked values.

        Parameters
        ----------
        cube: iris.cube.Cube
            Input cube.

        Returns
        -------
        iris.cube.Cube

        """
        cube.data = da.ma.masked_equal(cube.core_data(), 0.0)
        return cube
