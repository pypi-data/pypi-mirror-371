from sklearn.base import BaseEstimator

class BaseApplicabilityDomain(BaseEstimator):
    """
    Base class for Applicability Domain estimation.
    
    Parameters
    ----------
    quantile : float, default=0.997
        Quantile to determine the threshold distance based on 3σ.
        Samples with distance larger than this threshold are considered.
    """

    def __init__(self):
        self.threshold_ = None

    def fit(self, X, y=None):
        """Fit the AD estimator on the training data."""
        raise NotImplementedError

    def predict(self, X):
        """Return binary in-domain (1) or out-of-domain (0) predictions."""
        raise NotImplementedError

    def score_samples(self, X):
        """Return continuous scores indicating how far a sample is from the domain."""
        raise NotImplementedError

    def fit_predict(self, X, y=None):
        self.fit(X, y)
        return self.predict(X)
    