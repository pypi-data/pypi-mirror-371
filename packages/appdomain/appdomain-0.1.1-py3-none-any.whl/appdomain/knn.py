import numpy as np
from .base import BaseApplicabilityDomain
from sklearn.neighbors import NearestNeighbors, LocalOutlierFactor
from sklearn.utils.validation import check_is_fitted

class kNNApplicabilityDomain(BaseApplicabilityDomain):
    """
    Applicability Domain estimation using k-Nearest Neighbors.

    Parameters
    ----------
    n_neighbors : int, default=5
        Number of neighbors to use for distance calculation.
    """

    def __init__(self, n_neighbors=10, quantile=0.997):
        super().__init__()
        self.n_neighbors = n_neighbors
        self.quantile = quantile

    def fit(self, X, y=None):
        """
        Fit the NearestNeighbors model on the training data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training input samples.

        y : Ignored
            Not used.
        """

        self.model_ = NearestNeighbors(n_neighbors=self.n_neighbors)
        self.model_.fit(X)

        distances, _ = self.model_.kneighbors()
        mean_distances = distances.mean(axis=1)

        self.threshold_ = np.quantile(mean_distances, self.quantile)
        return self

    def predict(self, X):
        """
        Predict whether samples are inside or outside the applicability domain.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Test input samples.

        Returns
        -------
        labels : ndarray of shape (n_samples,)
            1 if inside AD, 0 if outside AD.
        """

        check_is_fitted(self, "threshold_")

        distances, _ = self.model_.kneighbors(X)
        mean_distances = distances.mean(axis=1)
        return (mean_distances <= self.threshold_).astype(int)

    def score_samples(self, X):
        """
        Return mean neighbor distances as anomaly scores.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Test input samples.

        Returns
        -------
        scores : ndarray of shape (n_samples,)
            Mean distance to neighbors. Higher values indicate more out-of-distribution (OOD).
        """
        check_is_fitted(self, "threshold_")
        distances, _ = self.model_.kneighbors(X)
        return distances.mean(axis=1)

    @property
    def threshold(self):
        """
        Threshold distance used to determine AD.
        """
        check_is_fitted(self, "threshold_")
        return self.threshold_


class LOFApplicabilityDomain(BaseApplicabilityDomain):
    """
    Applicability Domain estimation using Local Outlier Factor.

    Parameters
    ----------
    n_neighbors : int, default=20
        Number of neighbors to use.

    Attributes
    ----------
    model_ : object
        Fitted LocalOutlierFactor model.
    """

    def __init__(self, n_neighbors=10, quantile=0.997):
        super().__init__()
        self.n_neighbors = n_neighbors
        self.quantile = quantile

    def fit(self, X, y=None):
        """
        Fit the LocalOutlierFactor model on the training data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training input samples.

        y : Ignored
            Not used.
        """
        self.model_ = LocalOutlierFactor(
            n_neighbors = self.n_neighbors,
            contamination = 1- self.quantile,
            novelty=True
        )
        self.model_.fit(X)
        return self

    def predict(self, X):
        """
        Predict whether samples are inside or outside the applicability domain.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Test input samples.

        Returns
        -------
        labels : ndarray of shape (n_samples,)
            1 if inside AD, 0 if outside AD.
        """
        check_is_fitted(self, "model_")
        return (self.model_.predict(X) == 1).astype(int)
    
    def score_samples(self, X):
        """
        Return mean lof scores.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Test input samples.

        """
        check_is_fitted(self, "model_")
        scores = self.model_.decision_function(X)
        return scores
    
    @property
    def threshold(self):
        """
        Threshold used to separate in-domain and out-of-domain samples.
        """
        check_is_fitted(self, "model_")
        return self.model_.offset_