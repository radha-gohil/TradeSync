import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def preprocess(data,time_steps=60):
    dataset=data[['Close']].values
    
    scaler=MinMaxScaler(feature_range=(0,1))
    scale=scaler.fit_transform(dataset)
    
    X,y=[],[]
    for i in range(time_steps,len(scale)):
        X.append(scale[i-time_steps:i,0])
        y.append(scale[i,0])
        
    X,y=np.array(X),np.array(y)
    
    X=np.reshape(X,(X.shape[0],X.shape[1],1))
    
    return X,y,scaler