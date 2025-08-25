import numpy as np
from .base import BaseApplicabilityDomain
from . import *
from sklearn.exceptions import NotFittedError

class ApplicabilityDomain(BaseApplicabilityDomain):
    """
    Consensus Applicability Domain combining multiple AD models.

    Parameters
    ----------
    models : list or tuple
        List of AD models implementing fit/predict.

    Attributes
    ----------
    models_ : list
        Fitted models.
    """

    def __init__(self, models:list | tuple | None = None, rule="majority"):
        self.models_ = models
        self.rule = rule

    def fit(self, X, y=None):
        """
        Fit the AD model on the training data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training input samples.

        y : Ignored
            Not used.
        """
        if self.models_ is None:
            self.models_ = (
                kNNApplicabilityDomain(),
                LOFApplicabilityDomain(),
                OCSVMApplicabilityDomain()
            )
        self.models_ = [m.fit(X) for m in self.models_]
        return self

    def predict(self, X):
        """
        Predict AD labels for samples in X according to the ensemble rule.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Input data.

        Returns
        -------
        labels : ndarray of shape (n_samples,)
            1 if inside AD, 0 if outside AD.

        Notes
        -----
        The prediction rule depends on the attribute `self.rule`:

        - "majority" : A sample is predicted as class 1 if the majority
        of base models predict 1 (i.e., mean >= 0.5).
        - "all" : A sample is predicted as class 1 only if *all* base models
        predict 1.
        - "any" : A sample is predicted as class 1 if *any* base model
        predicts 1.

        Raises
        ------
        ValueError
            If `self.rule` is not one of "majority", "all", "any".
        """
        if self.models_ is None:
            raise NotFittedError('Not fitted yet')
        
        preds = np.column_stack([m.predict(X) for m in self.models_])
        if self.rule == "majority":
            return (np.mean(preds, axis=1) >= 0.5).astype(int)
        elif self.rule == "all":
            return (np.all(preds == 1, axis=1)).astype(int)
        elif self.rule == "any":
            return (np.any(preds == 1, axis=1)).astype(int)
        else:
            raise ValueError(f"Unknown rule: {self.rule}")

