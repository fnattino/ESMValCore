"""Test diagnostic script runs."""
import contextlib
import shutil
import sys
from textwrap import dedent

import pytest
import yaml

from esmvalcore._main import run


def write_config_user_file(dirname):
    config_file = dirname / 'config-user.yml'
    cfg = {
        'output_dir': str(dirname / 'output_dir'),
        'auxiliary_data_dir': str(dirname / 'extra_data'),
        'CMIP5': {
            'data': [{
                'input_dir':
                ('{institute}/{dataset}/{exp}/{frequency}/{modeling_realm}'
                 '/{mip}/{ensemble}/{latestversion}/{short_name}'),
                'input_file':
                '{short_name}_{mip}_{dataset}_{exp}_{ensemble}*.nc',
                'rootpath':
                '~/data/CMIP5',
            }],
            'output_file':
            '{project}_{dataset}_{mip}_{exp}_{ensemble}_{short_name}',
        },
        'log_level': 'debug',
        # 'max_parallel_tasks': 1,
    }
    config_file.write_text(yaml.safe_dump(cfg, encoding=None))
    return str(config_file)


@contextlib.contextmanager
def arguments(*args):
    backup = sys.argv
    sys.argv = list(args)
    yield
    sys.argv = backup


def check(result_file):
    """Check the results."""
    result = yaml.safe_load(result_file.read_text())

    print(result)

    required_keys = {
        'input_files',
        'log_level',
        'plot_dir',
        'run_dir',
        'work_dir',
    }
    missing = required_keys - set(result)
    assert not missing


def interpreter_not_installed(interpreter):
    """Check if an interpreter is installed for script."""
    return shutil.which(interpreter) is None


def diagnostic_run(tmp_path, script_file, script):

    recipe_file = tmp_path / 'recipe_test.yml'
    script_file = tmp_path / script_file
    result_file = tmp_path / 'result.yml'

    # Write script to file
    script_file.write_text(str(script))

    # Create recipe
    recipe = dedent("""
        documentation:
          description: Recipe with no data.
          authors: [andela_bouwe]

        diagnostics:
          diagnostic_name:
            scripts:
              script_name:
                script: {}
                setting_name: {}
        """.format(script_file, result_file))
    recipe_file.write_text(str(recipe))

    config_user_file = write_config_user_file(tmp_path)
    with arguments(
            'esmvaltool',
            'run',
            '--config_file',
            config_user_file,
            str(recipe_file),
    ):
        run()

    check(result_file)


@pytest.mark.installation
@pytest.mark.xfail(interpreter_not_installed('ncl'),
                   run=False,
                   reason="Interpreter not available")
def test_diagnostic_run_ncl(tmp_path):
    script_file = 'diagnostic.ncl'
    script = dedent("""
        begin
            print("INFO    Loading settings from " + getenv("settings"))
            loadscript("$settings")
        end
        print("INFO Writing " + diag_script_info@setting_name)
        n = str_get_nl()
        result = "run_dir: " + config_user_info@run_dir + n +\
                 "work_dir: " + config_user_info@work_dir + n +\
                 "plot_dir: " + config_user_info@plot_dir + n +\
                 "log_level: " + config_user_info@log_level + n +\
                 "input_files: []" + n

        system("echo '" + result + "' > " + diag_script_info@setting_name)
        """)
    diagnostic_run(tmp_path, script_file, script)


@pytest.mark.installation
@pytest.mark.xfail(interpreter_not_installed('Rscript'),
                   run=False,
                   reason="Interpreter not available")
def test_diagnostic_run_r(tmp_path):
    script_file = 'diagnostic.R'
    script = dedent("""
        library(yaml)

        args <- commandArgs(trailingOnly = TRUE)
        print(paste0("INFO    Loading settings from ", args[1]))
        settings <- yaml::read_yaml(args[1])

        print(paste0("INFO    Writing settings to ", settings$setting_name))
        yaml::write_yaml(settings, settings$setting_name)
    """)
    diagnostic_run(tmp_path, script_file, script)


@pytest.mark.skip(reason="TODO: make independent of YAML library")
@pytest.mark.installation
@pytest.mark.xfail(interpreter_not_installed('julia'),
                   run=False,
                   reason="Interpreter not available")
def test_diagnostic_run_jl(tmp_path):
    script_file = 'diagnostic.jl'
    script = dedent("""
        import YAML
        @info "Starting diagnostic script with" ARGS
        config_file = ARGS[1]
        cfg = YAML.load_file(config_file)
        out_file = cfg["setting_name"]
        @info "Copying file to" out_file
        Base.Filesystem.cp(config_file, out_file)
        @info "Done"
    """)
    diagnostic_run(tmp_path, script_file, script)


@pytest.mark.skip(reason="TODO: make independent from ESMValTool installation")
@pytest.mark.installation
@pytest.mark.xfail(interpreter_not_installed('python'),
                   run=False,
                   reason="Interpreter not available")
def test_diagnostic_run_py(tmp_path):
    script_file = 'diagnostic.py'
    script = dedent("""
    import yaml
    from esmvaltool.diag_scripts.shared import run_diagnostic

    def main(cfg):
        with open(cfg['setting_name'], 'w') as file:
            yaml.safe_dump(cfg, file)

    if __name__ == '__main__':
        with run_diagnostic() as config:
            main(config)
    """)
    diagnostic_run(tmp_path, script_file, script)
