"""On-the-fly CMORizer for CESM2."""

import logging

from iris.cube import CubeList

from ..native_datasets import NativeDatasetFix

logger = logging.getLogger(__name__)


class AllVars(NativeDatasetFix):
    """Fixes for all variables."""

    # Dictionary to map invalid units in the data to valid entries
    INVALID_UNITS = {
        'fraction': '1',
    }

    def fix_metadata(self, cubes):
        """Fix metadata."""
        cube = self.get_cube(cubes)

        # Fix time, latitude, and longitude coordinates
        self.fix_regular_time(cube)
        self.fix_regular_lat(cube)
        self.fix_regular_lon(cube)

        # Fix scalar coordinates
        self.fix_scalar_coords(cube)

        # Fix metadata of variable
        self.fix_var_metadata(cube)

        return CubeList([cube])
