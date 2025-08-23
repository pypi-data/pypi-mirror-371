import numpy as np
class MaxAbsScaler:
    def __init__(self):
        self.Absmax=None
    
    def fit(self,x):
        self.Absmax=np.max(abs(x),axis=0)
        self.scale_=np.where(self.Absmax==0,1,self.Absmax)
        return self
    
    def fit_transform(self,x):
        self.fit(x)
        return x/self.scale_
    
    def transform(self,x):
        return x/self.scale_
    
