import numpy as np
class score:
    def __init__(self,y_test,y_pred):
        
        self.y_test=y_test
        self.y_pred=y_pred
        if self.y_test.shape[0]!=self.y_pred.shape[0]:
            raise ValueError("Given values do not have same dimensions")

    def r2_score(self):
        res=0
        tot=0
        y_mean=self.y_test.mean()

        for i in range(self.y_test.shape[0]):
            res+=(self.y_test[i]-self.y_pred[i])**2
            tot+=(self.y_test[i]-y_mean)**2
        if tot==0:
            raise ValueError("r2 not defined")
        return 1-(res/tot)
    
    def adjusted_r2_score(self,n_features_in):
   
        r=self.r2_score()
        p=n_features_in
        n=self.y_test.shape[0]
        return 1-((1-r)*(n-1)/(n-p-1))
    
    def mse(self):
        n=self.y_test.shape[0]
        mse=0
       
        for i in range(n):
            mse+=(self.y_test[i]-self.y_pred[i])**2
        return mse/n    

    def rmse(self):
        return np.sqrt(self.mse())

    def mae(self):
        n=self.y_test.shape[0]
        mae=0
       
        for i in range(n):
            mae+=abs(self.y_test[i]-self.y_pred[i])
        return mae/n  