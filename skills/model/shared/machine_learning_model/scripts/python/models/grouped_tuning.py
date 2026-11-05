"""Pure, bounded numeric regression with explicit development-only grouped folds.

Requires numpy, pandas and scikit-learn >=1.4. This direct helper performs no
I/O, task approval, spatial matching or between-family model selection. Callers
must freeze the model family before evaluating its held-out test data.
"""
from numbers import Integral, Real

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor


def _integer(value, lower, upper):
    return isinstance(value, Integral) and not isinstance(value, (bool, np.bool_)) and lower <= value <= upper


def _parameter(name, value):
    bounds = {'max_depth': (1, 64), 'min_samples_leaf': (1, 10000), 'n_estimators': (1, 512)}
    if name in bounds:
        return _integer(value, *bounds[name])
    return (name == 'max_features' and isinstance(value, Real)
            and not isinstance(value, (bool, np.bool_)) and np.isfinite(value) and 0 < value <= 1)


def _metrics(observed, predicted):
    residual = observed - predicted
    sse = float(np.dot(residual, residual))
    centered = observed - observed.mean()
    sst = float(np.dot(centered, centered))
    return {'rmse': float(np.sqrt(sse / len(observed))),
            'mae': float(np.abs(residual).mean()),
            'r2': None if sst == 0 else float(1 - sse / sst),
            'r2_note': 'undefined_zero_test_target_variance' if sst == 0 else None,
            'sse': sse, 'sst': sst, 'n': len(observed)}


def fit_grouped_regression(development, test, *, features, target, group_column,
                           fold_id, learner, search_space, fixed_parameters,
                           n_iter, seed, max_fits):
    """Fit one declared family and evaluate the frozen fit on test exactly once.

    ``fold_id`` is a positional, one-dimensional sequence of development-row
    labels 1..k (2 <= k <= 5), with every group confined to one validation fold.
    Features are numeric with optional NaN; targets must be finite. Parameters
    use unprefixed sklearn names from the existing bounded Python model set.
    Search lists contain 1..16 distinct values and at most 65536 combinations.
    ``max_fits`` is an integer in 1..81 and counts candidate/fold fits plus the final development refit;
    linear regression accepts empty parameter dictionaries and fits once.

    Returns an in-memory estimator, selection metadata, CV result DataFrame,
    test metrics (including development-mean reference), and a prediction
    DataFrame retaining the test index. Inputs are neither edited nor sampled.
    This is an engineering operation, not scientific study approval.
    """
    allowed = {'linear_regression': set(),
               'decision_tree': {'max_depth', 'min_samples_leaf'},
               'random_forest': {'max_depth', 'min_samples_leaf', 'n_estimators', 'max_features'}}
    if learner not in allowed:
        raise ValueError('unsupported_learner')
    if not _integer(seed, 0, 2**32 - 1) or not _integer(n_iter, 1, 16) or not _integer(max_fits, 1, 81):
        raise ValueError('invalid_seed_or_fit_budget')
    if (not isinstance(features, (list, tuple)) or not features
            or any(not isinstance(c, str) or not c.strip() for c in features)
            or len(set(features)) != len(features)
            or not isinstance(target, str) or not isinstance(group_column, str)
            or target == group_column or target in features or group_column in features):
        raise ValueError('invalid_columns')
    if not isinstance(search_space, dict) or not isinstance(fixed_parameters, dict):
        raise ValueError('parameter_dictionaries_required')
    if (set(search_space) | set(fixed_parameters)) - allowed[learner]:
        raise ValueError('unsupported_parameter')
    if set(search_space) & set(fixed_parameters):
        raise ValueError('overlapping_search_and_fixed_parameters')
    if any(not _parameter(k, v) for k, v in fixed_parameters.items()):
        raise ValueError('invalid_fixed_parameter')
    combinations = 1
    for name, values in search_space.items():
        if (not isinstance(values, (list, tuple)) or not 1 <= len(values) <= 16
                or any(not _parameter(name, v) for v in values)
                or len(set(values)) != len(values)):
            raise ValueError('invalid_search_values')
        combinations *= len(values)
    if combinations > 65536:
        raise ValueError('search_space_too_large')
    if learner != 'linear_regression' and not search_space:
        raise ValueError('empty_search_space')
    declared = set(search_space) | set(fixed_parameters)
    if learner != 'linear_regression' and 'max_depth' not in declared:
        raise ValueError('explicit_max_depth_required')
    if learner == 'random_forest' and 'n_estimators' not in declared:
        raise ValueError('explicit_n_estimators_required')

    arrays = []
    groups = []
    for frame in (development, test):
        if not isinstance(frame, pd.DataFrame) or frame.empty or not frame.columns.is_unique:
            raise ValueError('nonempty_unique_column_dataframe_required')
        if not set([*features, target, group_column]).issubset(frame.columns):
            raise ValueError('missing_column')
        columns = [*features, target]
        if any(not pd.api.types.is_numeric_dtype(frame[c]) or pd.api.types.is_complex_dtype(frame[c])
               or pd.api.types.is_bool_dtype(frame[c]) for c in columns):
            raise ValueError('numeric_features_and_target_required')
        matrix = frame[features].to_numpy(dtype=float, na_value=np.nan)
        outcome = frame[target].to_numpy(dtype=float, na_value=np.nan)
        if np.isinf(matrix).any() or not np.isfinite(outcome).all():
            raise ValueError('nonfinite_features_or_target')
        ids = frame[group_column].tolist()
        if any(not isinstance(g, (str, Real)) or isinstance(g, (bool, np.bool_))
               or (isinstance(g, str) and not g.strip())
               or (isinstance(g, Real) and not np.isfinite(g)) for g in ids):
            raise ValueError('invalid_group_id')
        arrays.append((matrix, outcome))
        groups.append(ids)
    if set(groups[0]) & set(groups[1]):
        raise ValueError('development_test_group_overlap')
    labels = np.asarray(fold_id, dtype=object)
    if labels.ndim != 1 or len(labels) != len(development):
        raise ValueError('one_fold_per_development_row_required')
    if any(not _integer(v, 1, 5) for v in labels):
        raise ValueError('integer_fold_labels_required')
    unique = sorted(set(labels.tolist()))
    if not 2 <= len(unique) <= 5 or unique != list(range(1, len(unique) + 1)):
        raise ValueError('contiguous_two_to_five_folds_required')
    assigned = {}
    for group, fold in zip(groups[0], labels):
        if group in assigned and assigned[group] != fold:
            raise ValueError('group_crosses_folds')
        assigned[group] = fold
    x, y = arrays[0]
    folds = [(np.flatnonzero(labels != f), np.flatnonzero(labels == f)) for f in unique]
    if any(np.isnan(x[train]).all(axis=0).any() for train, _ in folds):
        raise ValueError('all_missing_training_feature_in_fold')
    actual_iter = 0 if learner == 'linear_regression' else min(n_iter, combinations)
    fits = 1 if learner == 'linear_regression' else actual_iter * len(folds) + 1
    if fits > max_fits:
        raise ValueError('fit_budget_exceeded')

    if learner == 'linear_regression':
        model = LinearRegression()
    elif learner == 'decision_tree':
        model = DecisionTreeRegressor(random_state=int(seed), **fixed_parameters)
    else:
        model = RandomForestRegressor(random_state=int(seed), n_jobs=1, **fixed_parameters)
    steps = [('impute', SimpleImputer(strategy='median'))]
    if learner == 'linear_regression':
        steps.append(('scale', StandardScaler()))
    pipeline = Pipeline([*steps, ('model', model)])
    if learner == 'linear_regression':
        estimator = pipeline.fit(x, y)
        cv_results = pd.DataFrame()
        best_cv_rmse = None
    else:
        search = RandomizedSearchCV(
            pipeline, {f'model__{k}': list(v) for k, v in search_space.items()},
            n_iter=actual_iter, scoring='neg_root_mean_squared_error', cv=folds,
            random_state=int(seed), n_jobs=1, refit=True, error_score='raise', return_train_score=False)
        search.fit(x, y)
        estimator = search.best_estimator_
        cv_results = pd.DataFrame(search.cv_results_)
        best_cv_rmse = float(-search.best_score_)
    selected_parameters = estimator.named_steps['model'].get_params(deep=False)
    # Selection is complete before any test predictions or target-based metrics.
    predicted = estimator.predict(arrays[1][0])
    if not np.isfinite(predicted).all():
        raise ValueError('nonfinite_test_prediction')
    mean_reference = float(y.mean())
    test_metrics = _metrics(arrays[1][1], predicted)
    test_metrics['development_mean_reference'] = {
        'prediction': mean_reference,
        **_metrics(arrays[1][1], np.full(len(test), mean_reference))}
    return {'estimator': estimator,
            'selection': {'learner': learner, 'parameters': selected_parameters,
                          'search_space': {k: list(v) for k, v in search_space.items()},
                          'fixed_parameters': dict(fixed_parameters),
                          'scoring': None if learner == 'linear_regression' else 'neg_root_mean_squared_error',
                          'seed': int(seed), 'fold_id': labels.tolist(), 'fold_count': len(folds),
                          'n_iter_requested': int(n_iter), 'n_candidates': actual_iter,
                          'fits_required': fits, 'max_fits': int(max_fits),
                          'best_cv_rmse': best_cv_rmse, 'refit_on': 'development',
                          'test_used_for_selection': False},
            'cv_results': cv_results, 'test_metrics': test_metrics,
            'predictions': pd.DataFrame({'observed': arrays[1][1], 'predicted': predicted,
                                         'development_mean_reference': mean_reference}, index=test.index)}
