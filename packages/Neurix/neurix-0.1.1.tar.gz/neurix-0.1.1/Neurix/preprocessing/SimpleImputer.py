import numpy as np
from collections import Counter
class SimpleImputer:
    def __init__(self,fill_value='mean'):
        self.fill_value=fill_value

    def fill(self,X):
        X=np.array(X,dtype=float)
        if self.fill_value=='mean':
            mean=np.nanmean(X)
            X[np.isnan(X)]=mean

        elif self.fill_value=='mode':
            non_nan=X[~np.isnan(X)]
            count=Counter(non_nan)
            mode=count.most_common(1)[0][0]
            X[np.isnan(X)]=mode
            

        elif self.fill_value=='median':
            median=np.nanmedian(X)
            X[np.isnan(X)]=median     

        elif isinstance(self.fill_value,(float,int)):
            X[np.isnan(X)]=self.fill_value

        else:
            raise ValueError(f"Invalid Fill value. Choose from 'mean', 'median', 'mode', or a number.")
        
        return X
        




        