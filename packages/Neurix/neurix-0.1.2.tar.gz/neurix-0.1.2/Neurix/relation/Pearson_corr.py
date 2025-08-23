import numpy as np
class Pearson_corr:
    def __init__(self):
        self.x_mean=None
        self.y_mean=None
        self.x_std=None
        self.y_std=None
        self.feat_len=None
    
    def corr(self,x,y):
        if x.shape[0]!=y.shape[0]:
            raise Exception("Data dimensions not matching")
        self.x_mean=np.mean(x)
        self.y_mean=np.mean(y)
        self.x_std=np.std(x,ddof=1)
        self.y_std=np.std(y,ddof=1)
        self.feat_len=x.shape[0]
        return np.sum((x-self.x_mean)*(y-self.y_mean))/((self.x_std)*(self.y_std)*(self.feat_len-1))
    