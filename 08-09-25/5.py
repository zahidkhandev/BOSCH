import pandas as pd

import matplotlib.pyplot as plt

import seaborn as sns

from sklearn.linear_model import LinearRegression

from sklearn.model_selection import train_test_split
 
 
# Read the file

cust = pd.read_csv("advertising.csv")

# Let’s checkout the data -

print(cust.head())

print("No of Rows =" , cust.shape)

print("Column names  =" , cust.columns)

print("Info         = " , cust.info())
 
 
sns.pairplot(data=cust)

plt.show()
 
corr_matrix = cust.corr()

print(corr_matrix)
 
 
X =cust[['TV', 'radio', 'newspaper']]

Y=cust['sales']
 
X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size=0.2,random_state=10)
 
lm = LinearRegression()
 
lm.fit(X_train,Y_train)
 
print('Intercept:')

print(lm.intercept_)

print('Coefficients:')

print(lm.coef_)

 