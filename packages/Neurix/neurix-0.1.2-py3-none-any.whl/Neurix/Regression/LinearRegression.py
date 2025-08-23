import numpy as np
class LinearRegression:
    def __init__(self):
        self.coef=None
        self.intercept=None

    def fit(self,X_train,y_train):
        X_train=np.insert(X_train,0,1,axis=1)
        beta=np.linalg.inv(np.dot(X_train.T,X_train)).dot(X_train.T).dot(y_train)
        self.intercept=beta[0]
        self.coef=beta[1:]

    def predict(self,X_test):
        return np.dot(X_test,self.coef)+self.intercept
        
        