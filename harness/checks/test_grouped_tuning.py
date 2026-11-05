"""Small synthetic checks of explicit grouped tuning, not real-data validation."""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

pytest.importorskip('sklearn')
SCRIPT = (Path(__file__).resolve().parents[2] /
          'skills/model/shared/machine_learning_model/scripts/python/models/grouped_tuning.py')
SPEC = importlib.util.spec_from_file_location('grouped_tuning', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@pytest.fixture
def case():
    rng = np.random.default_rng(29)
    x = rng.normal(size=(32, 2))
    frame = pd.DataFrame({'x': x[:, 0], 'z': x[:, 1],
                          'y': 2 * x[:, 0] - x[:, 1] + rng.normal(0, .1, 32),
                          'station': np.repeat(np.arange(8), 4)})
    development, test = frame.iloc[:24].copy(), frame.iloc[24:].copy()
    development.loc[[0, 5, 12], 'x'] = np.nan
    test.loc[24, 'z'] = np.nan
    return development, test, np.repeat([1, 2, 3, 1, 2, 3], 4)


def run(case, learner='decision_tree', **overrides):
    dev, test, folds = case
    kwargs = dict(features=['x', 'z'], target='y', group_column='station', fold_id=folds,
                  learner=learner, search_space={'max_depth': [2, 3], 'min_samples_leaf': [1, 2]},
                  fixed_parameters={}, n_iter=3, seed=41, max_fits=10)
    if learner == 'linear_regression':
        kwargs.update(search_space={}, max_fits=1)
    if learner == 'random_forest':
        kwargs['fixed_parameters'] = {'n_estimators': 7, 'max_features': .8}
    kwargs.update(overrides)
    return MODULE.fit_grouped_regression(dev, test, **kwargs)


@pytest.mark.parametrize('learner', ['linear_regression', 'decision_tree', 'random_forest'])
def test_models_metrics_reproducible_without_input_mutation(case, learner):
    before = [case[0].copy(deep=True), case[1].copy(deep=True)]
    result = run(case, learner)
    repeat = run(case, learner)
    np.testing.assert_array_equal(result['predictions']['predicted'], repeat['predictions']['predicted'])
    assert result['selection'] == repeat['selection']
    p = result['predictions']
    sse = float(((p.observed - p.predicted) ** 2).sum())
    sst = float(((p.observed - p.observed.mean()) ** 2).sum())
    m = result['test_metrics']
    assert m['rmse'] == pytest.approx(np.sqrt(sse / len(p)))
    assert m['mae'] == pytest.approx(np.abs(p.observed - p.predicted).mean())
    assert m['r2'] == pytest.approx(1 - sse / sst)
    assert m['development_mean_reference']['prediction'] == pytest.approx(case[0].y.mean())
    pd.testing.assert_frame_equal(case[0], before[0])
    pd.testing.assert_frame_equal(case[1], before[1])
    assert result['estimator'].named_steps['impute'].statistics_[0] == pytest.approx(case[0].x.median())
    assert ('scale' in result['estimator'].named_steps) == (learner == 'linear_regression')
    if learner != 'linear_regression':
        assert result['selection']['fits_required'] == 10
        assert len(result['cv_results']) == 3


def test_group_and_fold_rejections(case):
    dev, test, folds = case
    overlap = test.copy(); overlap['station'] = dev.station.iloc[0]
    with pytest.raises(ValueError, match='group_overlap'):
        run((dev, overlap, folds))
    crossed = folds.copy(); crossed[0] = 2
    with pytest.raises(ValueError, match='crosses_folds'):
        run((dev, test, crossed))
    with pytest.raises(ValueError, match='contiguous'):
        run((dev, test, np.full(len(dev), 1)))
    with pytest.raises(ValueError, match='integer_fold'):
        run((dev, test, folds.astype(float)))
    with pytest.raises(ValueError, match='one_fold'):
        run((dev, test, folds[:-1]))


def test_fold_training_missingness_fails_before_fit(case):
    dev, test, folds = case
    dev.loc[folds != 1, 'z'] = np.nan
    with pytest.raises(ValueError, match='all_missing_training_feature'):
        run((dev, test, folds))


def test_each_fold_imputer_uses_only_training_rows(case, monkeypatch):
    original = MODULE.SimpleImputer.fit
    seen = []

    def record(self, x, *args, **kwargs):
        seen.append(np.array(x, copy=True))
        return original(self, x, *args, **kwargs)

    monkeypatch.setattr(MODULE.SimpleImputer, 'fit', record)
    run(case, search_space={'max_depth': [2]}, n_iter=1, max_fits=4)
    assert len(seen) == 4
    dev, _, folds = case
    for i, fold in enumerate([1, 2, 3]):
        np.testing.assert_array_equal(seen[i], dev.loc[folds != fold, ['x', 'z']].to_numpy())
    np.testing.assert_array_equal(seen[3], dev[['x', 'z']].to_numpy())


@pytest.mark.parametrize('learner', ['linear_regression', 'decision_tree', 'random_forest'])
def test_test_target_cannot_affect_selection(case, learner):
    dev, test, folds = case
    first = run(case, learner)
    altered = test.copy(); altered['y'] = 7.0
    second = run((dev, altered, folds), learner)
    assert first['selection'] == second['selection']
    # Wall-clock timing columns are observations, not deterministic selection inputs.
    stable = [c for c in first['cv_results'].columns if not c.endswith('_time')]
    pd.testing.assert_frame_equal(first['cv_results'][stable], second['cv_results'][stable])
    np.testing.assert_array_equal(first['predictions'].predicted, second['predictions'].predicted)
    assert second['test_metrics']['r2'] is None
    assert second['test_metrics']['r2_note'] == 'undefined_zero_test_target_variance'


@pytest.mark.parametrize('overrides,code', [
    ({'max_fits': 9}, 'fit_budget'), ({'n_iter': 17}, 'fit_budget'),
    ({'seed': True}, 'fit_budget'), ({'search_space': {}}, 'empty_search'),
    ({'search_space': {'max_depth': []}}, 'invalid_search'),
    ({'search_space': {'max_depth': list(range(1, 18))}}, 'invalid_search'),
    ({'search_space': {'max_depth': [2, 2]}}, 'invalid_search'),
    ({'search_space': {'max_depth': [None]}}, 'invalid_search'),
    ({'search_space': {'min_samples_leaf': [1, 2]}}, 'explicit_max_depth'),
    ({'search_space': {'max_depth': [0]}}, 'invalid_search'),
    ({'search_space': {'max_depth': [65]}}, 'invalid_search'),
    ({'fixed_parameters': {'max_depth': 3}}, 'overlapping'),
    ({'fixed_parameters': {'n_jobs': -1}}, 'unsupported_parameter'),
    ({'fixed_parameters': {'min_samples_leaf': False}, 'search_space': {'max_depth': [2]}}, 'invalid_fixed'),
    ({'learner': 'arbitrary_estimator'}, 'unsupported_learner'),
    ({'features': ['x', 'y']}, 'invalid_columns'),
])
def test_parameter_and_budget_rejections(case, overrides, code):
    with pytest.raises(ValueError, match=code):
        run(case, **overrides)


@pytest.mark.parametrize('column,value,code', [
    ('y', np.nan, 'nonfinite'), ('y', np.inf, 'nonfinite'),
    ('x', np.inf, 'nonfinite'), ('station', None, 'invalid_group'),
    ('station', '', 'invalid_group'), ('x', 'text', 'numeric_features'),
])
def test_invalid_data(case, column, value, code):
    dev, test, folds = case
    if isinstance(value, str):
        dev[column] = dev[column].astype(object)
    dev.loc[0, column] = value
    with pytest.raises(ValueError, match=code):
        run((dev, test, folds))


@pytest.mark.parametrize('parameters,code', [
    ({'max_depth': 3}, 'explicit_n_estimators'),
    ({'n_estimators': 513}, 'invalid_fixed'),
    ({'n_estimators': 7, 'max_features': 0}, 'invalid_fixed'),
    ({'n_estimators': 7, 'max_features': 1.1}, 'invalid_fixed'),
])
def test_forest_bounds(case, parameters, code):
    with pytest.raises(ValueError, match=code):
        run(case, 'random_forest', fixed_parameters=parameters,
            search_space={'min_samples_leaf': [1, 2], 'max_depth': [2, 3]}
            if 'max_depth' not in parameters else {'min_samples_leaf': [1, 2]})


def test_search_exhaustion_uses_actual_fit_budget(case):
    result = run(case, search_space={'max_depth': [2]}, n_iter=16, max_fits=4)
    assert result['selection']['n_candidates'] == 1
    assert result['selection']['fits_required'] == 4
