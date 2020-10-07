"""Tests for _data_finder.py."""
import os
import shutil
import tempfile

import pytest
import yaml

from esmvalcore._data_finder import get_output_file

# Load test configuration
with open(os.path.join(os.path.dirname(__file__), 'data_finder.yml')) as file:
    CONFIG = yaml.safe_load(file)


def print_path(path):
    """Print path."""
    txt = path
    if os.path.isdir(path):
        txt += '/'
    if os.path.islink(path):
        txt += ' -> ' + os.readlink(path)
    print(txt)


def tree(path):
    """Print path, similar to the the `tree` command."""
    print_path(path)
    for dirpath, dirnames, filenames in os.walk(path):
        for dirname in dirnames:
            print_path(os.path.join(dirpath, dirname))
        for filename in filenames:
            print_path(os.path.join(dirpath, filename))


def create_file(filename):
    """Create an empty file."""
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(filename, 'a'):
        pass


def create_tree(path, filenames=None, symlinks=None):
    """Create directory structure and files."""
    for filename in filenames or []:
        create_file(os.path.join(path, filename))

    for symlink in symlinks or []:
        link_name = os.path.join(path, symlink['link_name'])
        os.symlink(symlink['target'], link_name)


@pytest.mark.parametrize('cfg', CONFIG['get_output_file'])
def test_get_output_file(cfg):
    """Test getting output name for preprocessed files."""
    from pathlib import Path
    drs = cfg['drs']
    output_file = get_output_file(cfg['variable'], drs['output_file'])

    expected = Path(cfg['output_file'])

    assert output_file == expected


@pytest.fixture
def root():
    """Root function for tests."""
    dirname = tempfile.mkdtemp()
    yield os.path.join(dirname, 'output1')
    print("Directory structure was:")
    tree(dirname)
    shutil.rmtree(dirname)


@pytest.mark.parametrize('cfg', CONFIG['get_input_filelist'])
def test_get_input_filelist(root, cfg):
    """Test retrieving input filelist."""
    create_tree(root, cfg.get('available_files'),
                cfg.get('available_symlinks'))

    from esmvalcore._projects import ProjectData

    drs = cfg['drs']
    project_data = ProjectData(name='test', **drs)
    project_data.set_rootpath(root)
    variable = cfg['variable']

    # Find files
    (input_filelist, dirnames,
     filenames) = project_data.get_input_filelist(variable)

    # Test result
    ref_files = [os.path.join(root, file) for file in cfg['expected_files']]
    if cfg['expected_dirs'] is None:
        ref_dirs = []
    else:
        ref_dirs = [os.path.join(root, dir) for dir in cfg['expected_dirs']]
    ref_patterns = cfg['expected_patterns']

    assert sorted(input_filelist) == sorted(ref_files)
    assert sorted(dirnames) == sorted(ref_dirs)
    assert sorted(filenames) == sorted(ref_patterns)
