import numpy as np
class MeanScaler:
    def __init__(self):
        self.mean=None
    
    def fit(self,X_train):
        self.mean=X_train.mean(axis=0)   
        return self
    
    def fit_transform(self,X_train):
        self.fit(X_train)
        return X_train-self.mean
    
    def transform(self,X_test):
        return X_test-self.mean


