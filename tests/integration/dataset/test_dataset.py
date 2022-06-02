from pathlib import Path

import iris.coords
import iris.cube
import pytest

from esmvalcore.dataset import Dataset
from esmvalcore.experimental import CFG


@pytest.fixture
def example_data(tmp_path):

    cwd = Path(__file__).parent
    tas_src = cwd / 'tas.nc'
    areacella_src = cwd / 'areacella.nc'

    rootpath = tmp_path / 'climate_data'
    tas_tgt = (rootpath / 'cmip5' / 'output1' / 'CCCma' / 'CanESM2' /
               'historical' / 'mon' / 'atmos' / 'Amon' / 'r1i1p1' /
               'v20120718' /
               'tas_Amon_CanESM2_historical_r1i1p1_185001-200512.nc')
    areacella_tgt = (rootpath / 'cmip5' / 'output1' / 'CCCma' / 'CanESM2' /
                     'historical' / 'fx' / 'atmos' / 'fx' / 'r0i0p0' /
                     'v20120410' / 'areacella_fx_CanESM2_historical_r0i0p0.nc')

    tas_tgt.parent.mkdir(parents=True, exist_ok=True)
    tas_tgt.symlink_to(tas_src)

    areacella_tgt.parent.mkdir(parents=True, exist_ok=True)
    areacella_tgt.symlink_to(areacella_src)

    CFG['rootpath']['CMIP5'] = str(rootpath)
    CFG['drs']['CMIP5'] = 'ESGF'
    CFG['output_dir'] = tmp_path / 'output_dir'


def test_load(example_data):

    session = CFG.start_session('test_session')
    tas = Dataset(short_name='tas',
                  mip='Amon',
                  project='CMIP5',
                  dataset='CanESM2',
                  ensemble='r1i1p1',
                  exp='historical',
                  timerange='1850/185002')
    tas.add_ancillary(short_name='areacella', mip='fx', ensemble='r0i0p0')

    tas.augment_facets(session)

    tas.find_files(session)

    cube = tas.load(session)

    assert isinstance(cube, iris.cube.Cube)
    assert cube.cell_measures()
