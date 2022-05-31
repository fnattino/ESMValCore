import textwrap

import yaml

from esmvalcore._dataset import (
    Dataset,
    datasets_from_recipe,
    datasets_to_recipe,
)


def test_datasets_from_recipe():

    recipe_txt = textwrap.dedent("""

    datasets:
      - {dataset: 'dataset1'}

    diagnostics:
      diagnostic1:
        additional_datasets:
          - {dataset: 'dataset2'}
        variables:
          ta:
          pr:
            additional_datasets:
              - {dataset: 'dataset3'}
      diagnostic2:
        variables:
          tos:
    """)

    recipe = yaml.safe_load(recipe_txt)

    datasets = [
        Dataset(
            diagnostic='diagnostic1',
            variable_group='ta',
            short_name='ta',
            dataset='dataset1',
            recipe_dataset_index=0,
        ),
        Dataset(
            diagnostic='diagnostic1',
            variable_group='ta',
            short_name='ta',
            dataset='dataset2',
            recipe_dataset_index=1,
        ),
        Dataset(
            diagnostic='diagnostic1',
            variable_group='pr',
            short_name='pr',
            dataset='dataset1',
            recipe_dataset_index=0,
        ),
        Dataset(
            diagnostic='diagnostic1',
            variable_group='pr',
            short_name='pr',
            dataset='dataset2',
            recipe_dataset_index=1,
        ),
        Dataset(
            diagnostic='diagnostic1',
            variable_group='pr',
            short_name='pr',
            dataset='dataset3',
            recipe_dataset_index=2,
        ),
        Dataset(
            diagnostic='diagnostic2',
            variable_group='tos',
            short_name='tos',
            dataset='dataset1',
            recipe_dataset_index=0,
        ),
    ]

    assert datasets_from_recipe(recipe) == datasets


def test_expand_datasets_from_recipe():

    recipe_txt = textwrap.dedent("""

    datasets:
      - {dataset: 'dataset1', ensemble: r(1:2)i1p1}

    diagnostics:
      diagnostic1:
        variables:
          ta:
    """)
    recipe = yaml.safe_load(recipe_txt)

    datasets = [
        Dataset(
            diagnostic='diagnostic1',
            variable_group='ta',
            short_name='ta',
            dataset='dataset1',
            ensemble='r1i1p1',
            recipe_dataset_index=0,
        ),
        Dataset(
            diagnostic='diagnostic1',
            variable_group='ta',
            short_name='ta',
            dataset='dataset1',
            ensemble='r2i1p1',
            recipe_dataset_index=1,
        ),
    ]

    assert datasets_from_recipe(recipe) == datasets


def test_datasets_to_recipe():
    datasets = [
        Dataset(
            diagnostic='diagnostic1',
            variable_group='group1',
            short_name='ta',
            dataset='dataset1',
        ),
        Dataset(
            diagnostic='diagnostic1',
            variable_group='group1',
            short_name='ta',
            dataset='dataset2',
        ),
    ]

    recipe_txt = textwrap.dedent("""

    diagnostics:
      diagnostic1:
        variables:
          group1:
            additional_datasets:
              - {dataset: 'dataset1', short_name: 'ta'}
              - {dataset: 'dataset2', short_name: 'ta'}

    """)
    recipe = yaml.safe_load(recipe_txt)

    assert datasets_to_recipe(datasets) == recipe