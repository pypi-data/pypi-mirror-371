import numpy as np
class covariance:
    def __init__(self):
        self.x_mean=None
        self.y_mean=None
        self.feat_len=None
    
    def cov(self,x,y):
        if x.shape[0]!=y.shape[0]:
            raise Exception("Data dimensions not matching")
        self.x_mean=np.mean(x)
        self.y_mean=np.mean(y)
        self.feat_len=x.shape[0]
        return np.sum((x-self.x_mean)*(y-self.y_mean))/(self.feat_len-1)
    
    
