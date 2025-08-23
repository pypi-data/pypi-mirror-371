import numpy as np
class MinMaxScaler:
    def __init__(self,min=0,max=1):
        self.min=min
        self.max=max
        self.range=max-min
        self.min_val=None
        self.max_val=None
        if self.range<0:
            raise Exception("Min value is greater than max value")
        
    def fit(self,x):
        self.max_val=np.max(x,axis=0)
        self.min_val=np.min(x,axis=0)
        self.scale_=np.where(self.max_val-self.min_val==0,1,self.max_val-self.min_val)
        return self
    
    def fit_transform(self,x):
        self.fit(x)
        return self.min+(x-self.min_val)*(self.range)/self.scale_
    
    def transform(self,x):
        return self.min+(x-self.min_val)*(self.range)/self.scale_


