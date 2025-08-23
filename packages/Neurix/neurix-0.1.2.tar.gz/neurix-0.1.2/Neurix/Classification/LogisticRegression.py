import numpy as np
class LogisticRegression:
    def __init__(self,epochs=1000,learning_rate=0.1,patience=20,min_del=1e-4):
        self.w=None
        self.b=None
        self.no_of_class=None
        self.epochs=epochs
        self.learning_rate=learning_rate
        self.patience=patience
        self.min_del=min_del

    def softmax(self,z):
        num=np.exp(z-np.max(z,axis=1,keepdims=True))
        return num/np.sum(num,axis=1,keepdims=True)
    
    def one_hot(self,y):
        one_hot=np.zeros((y.shape[0],self.no_of_class))
        for i in range(y.shape[0]):
            one_hot[i,y[i]]=1
        return one_hot
    
    def compute_loss(self,y_true,y_pred):
        m=y_true.shape[0]
        return -np.sum(y_true*np.log(y_pred+1e-4))/m
    

    def fit(self,X,y):
        # m-row n-column
        # y is m-row 1-column
        m,n=X.shape
        # number of classes
        self.no_of_class=np.max(y)+1
        # weight n*k(no. of class)
        self.w=np.zeros((n,self.no_of_class))
        # b 1*k
        self.b=np.zeros((1,self.no_of_class))
        epoch_no=0
        best_loss=float('inf')
        for epoch in range(self.epochs):
            # z m*k
            z=np.dot(X,self.w)+self.b
            # y_hat m*k
            y_hat=self.softmax(z)
            # m*c
            y_true=self.one_hot(y)

            loss=self.compute_loss(y_true,y_hat)
            if best_loss-loss>=self.min_del:
                best_loss=loss
                epoch_no=0
                
            else:
                epoch_no+=1
                
            if epoch_no>=self.patience:
                print(f"No improvement since {self.patience} epochs.Performing early stoping at {epoch}...")
                break


            # applying gradient descent
            self.w-=self.learning_rate*np.dot(X.T,(y_hat-y_true))/m
            self.b-=np.sum(self.learning_rate*(y_hat-y_true),keepdims=True)/m
        
    def predict(self,X):
        z=np.dot(X,self.w)+self.b
        prob=self.softmax(z)
        return np.argmax(prob,axis=1)
    
    def predict_prob(self,X):
        z=np.dot(X,self.w)+self.b
        return self.softmax(z)

    
        