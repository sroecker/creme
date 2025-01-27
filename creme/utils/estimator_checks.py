import copy
import functools
import itertools
import math
import random

from sklearn import datasets


__all__ = ['check_estimator']


def make_random_features(model, n_observations, n_features):
    for _ in range(n_observations):
        yield {i: random.random() for i in range(n_features)}


def make_random_targets(model, n_observations):

    from .. import base

    random_func = None

    if isinstance(model, base.Regressor):
        random_func = random.random

    elif isinstance(model, base.MultiClassClassifier):
        random_func = functools.partial(random.choice, ['a', 'b', 'c', 'd'])

    elif isinstance(model, base.BinaryClassifier):
        random_func = functools.partial(random.choice, [True, False])

    elif isinstance(model, base.Transformer):
        if model.is_supervised:
            random_func = random.random
        else:
            random_func = lambda: None

    elif isinstance(model, base.Clusterer):
        random_func = functools.partial(random.choice, [0, 1, 2, 3])

    for _ in range(n_observations):
        yield random_func()


def make_random_X_y(model, n_observations, n_features):
    return zip(
        make_random_features(model, n_observations, n_features),
        make_random_targets(model, n_observations)
    )


def check_fit_one(model):

    klass = model.__class__

    for x, y in make_random_X_y(model, n_observations=20, n_features=4):

        xx, yy = copy.deepcopy(x), copy.deepcopy(y)

        model = model.fit_one(x, y)

        # Check the model returns itself
        assert isinstance(model, klass)

        # Check fit_one is pure (i.e. x and y haven't changed)
        assert x == xx
        assert y == yy


def check_predict_proba_one(model):

    for x, y in make_random_X_y(model, n_observations=20, n_features=4):

        xx, yy = copy.deepcopy(x), copy.deepcopy(y)

        model = model.fit_one(x, y)
        y_pred = model.predict_proba_one(x)

        # Check the probabilities are coherent
        assert isinstance(y_pred, dict)
        assert math.isclose(sum(y_pred.values()), 1.0)
        for proba in y_pred.values():
            assert 0.0 <= proba <= 1.0

        # Check predict_proba_one is pure (i.e. x and y haven't changed)
        assert x == xx
        assert y == yy


def check_a_better_than_b(model_a, model_b, X_y_func, metric):
    """Trains two models and checks that model_a does better than model_b."""

    from .. import model_selection

    metric_a = model_selection.online_score(
        X_y=X_y_func(),
        model=model_a,
        metric=copy.deepcopy(metric)
    )
    metric_b = model_selection.online_score(
        X_y=X_y_func(),
        model=model_b,
        metric=copy.deepcopy(metric)
    )

    if metric.bigger_is_better:
        assert metric_a.get() > metric_b.get()
    else:
        assert metric_a.get() < metric_b.get()


def check_better_than_dummy_binary(classifier):

    from .. import dummy
    from .. import metrics
    from .. import stream

    for dummy_model, X_y_func, metric in itertools.product(
        (dummy.NoChangeClassifier(), dummy.PriorClassifier()),
        (functools.partial(
            stream.iter_sklearn_dataset,
            datasets.load_breast_cancer(),
            shuffle=True,
            random_state=42,
        ),),
        (metrics.Accuracy(),)
    ):
        check_a_better_than_b(
            model_a=copy.deepcopy(classifier),
            model_b=copy.deepcopy(dummy_model),
            X_y_func=X_y_func,
            metric=copy.deepcopy(metric)
        )


def check_better_than_dummy_multi(classifier):

    from .. import dummy
    from .. import metrics
    from .. import stream

    for dummy_model, X_y_func, metric in itertools.product(
        (dummy.NoChangeClassifier(), dummy.PriorClassifier()),
        (functools.partial(
            stream.iter_sklearn_dataset,
            datasets.load_iris(),
            shuffle=True,
            random_state=42,
        ),),
        (metrics.Accuracy(),)
    ):
        check_a_better_than_b(
            model_a=copy.deepcopy(classifier),
            model_b=copy.deepcopy(dummy_model),
            X_y_func=X_y_func,
            metric=copy.deepcopy(metric)
        )


def check_better_than_dummy_regression(regressor):

    from .. import dummy
    from .. import metrics
    from .. import stats
    from .. import stream

    for dummy_model, X_y_func, metric in itertools.product(
        (dummy.StatisticRegressor(stats.Mean()),),
        (functools.partial(
            stream.iter_sklearn_dataset,
            datasets.load_boston(),
            shuffle=True,
            random_state=42,
        ),),
        (metrics.MSE(),)
    ):
        check_a_better_than_b(
            model_a=copy.deepcopy(regressor),
            model_b=copy.deepcopy(dummy_model),
            X_y_func=X_y_func,
            metric=copy.deepcopy(metric)
        )


def check_predict_proba_one_binary(classifier):

    for x, y in make_random_X_y(classifier, n_observations=20, n_features=4):
        y_pred = classifier.predict_proba_one(x)
        classifier = classifier.fit_one(x, y)
        assert len(y_pred) == 2
        assert True in y_pred
        assert False in y_pred


def yield_all_checks(model):

    from .. import base

    yield check_fit_one

    if isinstance(model, base.Classifier):
        yield check_predict_proba_one

    # MultiClassClassifiers are also BinaryClassifiers so binary will apply to both
    if isinstance(model, base.BinaryClassifier):
        yield check_better_than_dummy_binary

        # Some tests work for BinaryClassifiers but not for MultiClassClassifiers
        if not isinstance(model, base.MultiClassClassifier):
            yield check_predict_proba_one_binary

    if isinstance(model, base.MultiClassClassifier):
        yield check_better_than_dummy_multi

    if isinstance(model, base.Regressor):
        yield check_better_than_dummy_regression


def check_estimator(model):

    for check in yield_all_checks(model):
        check(copy.deepcopy(model))
