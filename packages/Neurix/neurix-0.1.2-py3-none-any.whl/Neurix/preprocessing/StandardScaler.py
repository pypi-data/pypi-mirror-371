import numpy as np
class StandardScaler:
    def __init__(self):
        self.mean=None
        self.std=None
    
    def fit(self,X_train):
        self.mean=X_train.mean(axis=0)
        self.std=X_train.std(axis=0)
        self.std[self.std==0]=1
        return self
    
    def fit_transform(self,X_train):
        self.fit(X_train)
        return (X_train-self.mean)/self.std
    
    def transform(self,X_test):
        return (X_test-self.mean)/self.std



