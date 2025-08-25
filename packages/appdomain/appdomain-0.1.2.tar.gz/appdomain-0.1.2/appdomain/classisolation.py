import numpy as np
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from sklearn.base import check_is_fitted
from scipy.spatial.distance import cdist
from .base import BaseApplicabilityDomain
from typing import Literal

class OCSVMApplicabilityDomain(BaseApplicabilityDomain):
    """
    Applicability Domain estimation using One-Class SVM.

    Parameters
    ----------
    kernel : str, default="rbf"
        Kernel type.
    nu : float, default=0.01
        An upper bound on the fraction of training errors.
    gamma : str or float, default="auto"
        Kernel coefficient.

    Attributes
    ----------
    model_ : object
        Fitted OneClassSVM model.
    """

    def __init__(
            self, 
            quantile:float = 0.997, 
            gamma:float | Literal['scale', 'auto'] = 'auto',
            kernel:Literal['linear', 'poly', 'rbf', 'sigmoid'] = 'rbf'
        ):
        super().__init__()
        self.quantile = quantile
        self.nu = 1- quantile
        self.gamma = gamma
        self.kernel = kernel

    def fit(self, X, y=None):
        """
        Fit the OneClassSVM model on the training data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training input samples.

        y : Ignored
            Not used.
        """
        X = np.asarray(X)
        if self.gamma == 'auto' and self.kernel == 'rbf':
            gammas = 2 ** np.arange(-20, 11, dtype=float)
            dist_matrix = cdist(X, X, metric='seuclidean')[..., None]   # shape: (n_samples, n_samples, 1)
            gram_matrix = np.exp(-dist_matrix * gammas)     # shape: (n_samples, n_samples, num_gammas)
            self.optimal_gamma_ = gammas[np.argmax(gram_matrix.var(axis=(0, 1)))]
        else:
            self.optimal_gamma_ = self.gamma

        self.model_ = OneClassSVM(nu=self.nu, gamma=self.optimal_gamma_, kernel=self.kernel)
        self.model_.fit(X)

        scores = self.model_.decision_function(X)
        self.threshold_ = np.quantile(scores, 1 - self.quantile)
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
        check_is_fitted(self, 'model_')
        return (self.model_.predict(X) == 1).astype(int)
    
    def score_samples(self, X):
        """
        Return mean one class SVM scores.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Test input samples.
        """
        check_is_fitted(self, 'model_')
        scores = self.model_.decision_function(X)
        return scores

    @property
    def gamma_(self):
        """
        The gamma value actually used by the model.
        """
        check_is_fitted(self, 'model_')
        return self.optimal_gamma_
    
    @property
    def threshold(self):
        """
        Threshold distance used to determine AD.
        """
        check_is_fitted(self, 'threshold_')
        return self.threshold_


class iForestApplicabilityDomain(BaseApplicabilityDomain):
    """
    Isolation Forest 
    
    """
    def __init__(self, 
            quantile=0.997, 
            n_estimators=100, 
            contamination=0.03, 
            random_state=None
        ):
        super().__init__()
        self.quantile = quantile
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state

    def fit(self, X, y=None):
        """
        Fit the IsolationForest model on the training data for AD.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training input samples.

        y : Ignored
            Not used.
        """
        self.model_ = IsolationForest(
                        n_estimators=self.n_estimators,
                        contamination=self.contamination,
                        random_state=self.random_state
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
        return (self.model_.predict(X) == 1).astype(int)

    def score_samples(self, X):
        """
        Return mean iForest scores.

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
        Threshold distance used to determine AD.
        """
        check_is_fitted(self, "model_")
        return self.model_.offset_

