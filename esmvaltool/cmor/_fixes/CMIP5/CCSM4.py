"""Fixes for CCSM4 model."""
# pylint: disable=invalid-name, no-self-use, too-few-public-methods
import numpy as np

from ..fix import Fix


# noinspection PyPep8Naming
class rlut(Fix):
    """Fixes for rlut."""

    def fix_metadata(self, cubes):
        """
        Fix data.

        Fixes discrepancy between declared units and real units

        Parameters
        ----------
        cube: iris.cube.CubeList

        Returns
        -------
        iris.cube.Cube

        """
        cube = self.get_cube_from_list(cubes)
        lat = cube.coord('latitude')
        lat.points = np.round(lat.points, 3)
        lat.bounds = np.round(lat.bounds, 3)
        return cubes


class rlutcs(rlut):
    """Fixes for rlutcs."""


class rsut(rlut):
    """Fixes for rsut."""


class rsutcs(rlut):
    """Fixes for rsutcs."""


class rlus(rlut):
    """Fixes for rlus."""


class rsus(rlut):
    """Fixes for rsus."""


class rsuscs(rlut):
    """Fixes for rsuscs."""


class rlds(rlut):
    """Fixes for rlds."""


class rldscs(rlut):
    """Fixes for rldscs."""


class rsds(rlut):
    """Fixes for rsds."""


class rsdscs(rlut):
    """Fixes for rsdscs."""


class rsdt(rlut):
    """Fixes for rsdt."""


class so(Fix):
    """Fixes for so."""

    def fix_metadata(self, cubes):
        """
        Fix data.

        Fixes discrepancy between declared units and real units

        Parameters
        ----------
        cube: iris.cube.CubeList

        Returns
        -------
        iris.cube.Cube

        """
        self.get_cube_from_list(cubes).units = '1e3'
        return cubes
