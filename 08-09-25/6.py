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
y=cust['sales']
 
lm1=LinearRegression()
lm1.fit(X, y)
 
print('Intercept:')
print(lm1.intercept_)
print('Coefficients:')
print(lm1.coef_)
 
 
from sklearn.metrics import r2_score
 
lm2 = LinearRegression().fit(X[['TV', 'radio']], y)
lm2_pred = lm2.predict(X[['TV', 'radio']])
 
print('R² when choosig  TV and Radio  : ', r2_score(y, lm2_pred))
 
lm3 = LinearRegression().fit(X[['TV', 'radio', 'newspaper']], y)
lm3_pred = lm3.predict(X[['TV', 'radio', 'newspaper']])
 
print('R² when choosing all three : ', r2_score(y, lm3_pred))
 
 
lm4 = LinearRegression().fit(X[['TV']], y)
lm4_pred = lm4.predict(X[['TV']])
 
print('R² when choosing only TV: ', r2_score(y, lm4_pred))