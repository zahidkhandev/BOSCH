#supervised learning
# regression and classfication
# regression is  predict numerical value
 
 
import numpy  as np                 # pip install numpy
import matplotlib.pyplot as mtp
import pandas as pd
 
data=pd.read_csv('1.csv')
 
# data frame is similar to RDBMS Table , stored in memory with rows and columns
 
 
print(data.head())    # prints top 5 records
 
print(data.shape)     # prints no of rows and columns
 
 
x=data[['GPA']]   # X is independant  variable
y=data[['SAT']]   # y is dependant variable
 
from sklearn.model_selection import train_test_split
 
x_train, x_test , y_train , y_test=train_test_split(x,y,test_size=0.2, random_state=0)
 
from sklearn.linear_model import LinearRegression
 
model=LinearRegression()
 
model.fit(x_train,y_train)
 
#Prediction of Test and Training set result
 
y_pred=model.predict(x_test)
x_pred =model.predict(x_train)
 
#visualizing the Training set results:
mtp.scatter(x_train, y_train, color="blue")   
mtp.plot(x_train, x_pred, color="red")    
mtp.title("SAT vs GPA (Training Dataset)")  
mtp.xlabel("SAT SCORE")  
mtp.ylabel("GPA")  
mtp.show()  
 
#visualizing the Test set results  
mtp.scatter(x_test, y_test, color="blue")   
mtp.plot(x_test, y_pred, color="red")   
mtp.title("SAT vs GPA (Test Dataset)")  
mtp.xlabel("SAT")  
mtp.ylabel("GPA")  
mtp.show()  

 
 
print(model.score(x_test,y_test))
 