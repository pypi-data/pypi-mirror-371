import numpy as np
class OLSRidge:
    def __init__(self,alpha=0.1):
        self.coef=None
        self.intercept=None
        self.alpha=alpha

    def fit(self,X_train,y_train):
        X_train=np.insert(X_train,0,1,axis=1)
        I=np.identity(X_train.shape[1])
        I[0][0]=0
        beta=np.linalg.inv(np.dot(X_train.T,X_train)+self.alpha*I).dot(X_train.T).dot(y_train)
        self.intercept=beta[0]
        self.coef=beta[1:]

    def predict(self,X_test):
        return np.dot(X_test,self.coef)+self.intercept
        
        