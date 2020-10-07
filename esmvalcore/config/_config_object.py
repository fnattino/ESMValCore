import os
from datetime import datetime
from pathlib import Path

import yaml

from ._config_validators import _validators
from ._validated_config import ValidatedConfig


class ESMValCoreConfig(ValidatedConfig):
    """The ESMValCore config object."""
    validate = _validators

    @staticmethod
    def load_from_file(filename):
        """Reload user configuration from the given file."""
        path = Path(filename).expanduser()
        if not path.exists():
            try_path = USER_CONFIG_DIR / filename
            if try_path.exists():
                path = try_path
            else:
                raise FileNotFoundError(f'No such file: `{filename}`')

        _load_user_config(path)

    def start_session(self, name):
        return Session(name, self.copy())


class Session(ValidatedConfig):
    """This class holds information about the current session. Different
    session directories can be accessed.

    Parameters
    ----------
    name : str
        Name of the session to initialize, for example, the name of the
        recipe (default='session').
    """
    validate = _validators

    def __init__(self, name: str = 'session', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_session_dir(name)

    def init_session_dir(self, name: str = 'session'):
        """Initialize session.

        The `name` is used to name the working directory, e.g.
        `recipe_example_20200916/`. If no name is given, such as in an
        interactive session, defaults to `session`.
        """
        now = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        session_name = f"{name}_{now}"
        self._session_dir = self['output_dir'] / session_name

    @property
    def session_dir(self):
        return self._session_dir

    @property
    def preproc_dir(self):
        return self.session_dir / 'preproc'

    @property
    def work_dir(self):
        return self.session_dir / 'work'

    @property
    def plot_dir(self):
        return self.session_dir / 'plots'

    @property
    def run_dir(self):
        return self.session_dir / 'run'

    @property
    def config_dir(self):
        return USER_CONFIG_DIR


def read_config_file(config_file):
    """Read config user file and store settings in a dictionary."""
    config_file = Path(config_file)
    if not config_file.exists():
        raise IOError(f'Config file `{config_file}` does not exist.')

    with open(config_file, 'r') as file:
        cfg = yaml.safe_load(file)

    return cfg


def _load_default_config(filename: str, drs_filename: str = None):
    """Load the default configuration."""
    mapping = read_config_file(filename)

    global config_default

    CFG_default.update(mapping)

    if drs_filename:
        drs_mapping = read_config_file(drs_filename)
        CFG_default.update(drs_mapping)


def _load_user_config(filename: str, raise_exception: bool = True):
    """Load user configuration from the given file (`filename`).

    The config cleared and updated in-place.

    Parameters
    ----------
    raise_exception : bool
        Raise an exception if `filename` can not be found (default).
        Otherwise, silently pass and use the default configuration. This
        setting is necessary for the case where `.esmvalcore/config-user.yml`
        has not been defined (i.e. first start).
    """
    try:
        mapping = read_config_file(filename)
    except IOError:
        if raise_exception:
            raise
        mapping = {}

    global CFG
    global CFG_orig

    CFG.clear()
    CFG.update(CFG_default)
    CFG.update(mapping)

    CFG_orig = ESMValCoreConfig(CFG.copy())


def get_user_config_location():
    """Check if environment variable `ESMVALTOOL_CONFIG` exists, otherwise use
    the default config location."""
    try:
        config_location = Path(os.environ['ESMVALTOOL_CONFIG'])
    except KeyError:
        config_location = USER_CONFIG_DIR / 'config-user.yml'

    return config_location


DEFAULT_CONFIG_DIR = Path(__file__).parent
DEFAULT_CONFIG = DEFAULT_CONFIG_DIR / 'config-default.yml'
DEFAULT_DRS = DEFAULT_CONFIG_DIR / 'drs-default.yml'

USER_CONFIG_DIR = Path.home() / '.esmvaltool'
USER_CONFIG = get_user_config_location()

# initialize placeholders
CFG_default = ESMValCoreConfig()
CFG = ESMValCoreConfig()
CFG_orig = ESMValCoreConfig()

# update config objects
_load_default_config(DEFAULT_CONFIG, DEFAULT_DRS)
_load_user_config(USER_CONFIG, raise_exception=False)