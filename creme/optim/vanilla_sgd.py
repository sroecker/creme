from . import base


__all__ = ['VanillaSGD']


class VanillaSGD(base.Optimizer):
    """Plain stochastic gradient descent.

    Example:

        ::

            >>> from creme import compose
            >>> from creme import linear_model
            >>> from creme import metrics
            >>> from creme import model_selection
            >>> from creme import optim
            >>> from creme import preprocessing
            >>> from creme import stream
            >>> from sklearn import datasets

            >>> X_y = stream.iter_sklearn_dataset(
            ...     dataset=datasets.load_breast_cancer(),
            ...     shuffle=True,
            ...     random_state=42
            ... )
            >>> optimiser = optim.VanillaSGD()
            >>> model = compose.Pipeline([
            ...     ('scale', preprocessing.StandardScaler()),
            ...     ('learn', linear_model.LogisticRegression(optimiser))
            ... ])
            >>> metric = metrics.F1()

            >>> model_selection.online_score(X_y, model, metric)
            F1: 0.966102

    References:
        1. `A Stochastic Approximation Method <https://pdfs.semanticscholar.org/34dd/d8865569c2c32dec9bf7ffc817ff42faaa01.pdf>`_

    """

    def __init__(self, lr=0.1):
        super().__init__(lr)

    def _update_after_pred(self, w, g):

        for i, gi in g.items():
            w[i] -= self.learning_rate * gi

        return w
