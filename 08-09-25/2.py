import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Read the file

customers = pd.read_csv("2.csv")

# Let’s checkout the data -

print(customers.head())
print(customers.describe())

# sns.jointplot(x='Time on Website',y='Yearly Amount Spent', data=customers)
# sns.jointplot(x='Time on App',y='Yearly Amount Spent', data=customers)
# sns.jointplot(x='Time on App',y='Length of Membership', data=customers,kind='hex')
# sns.pairplot(data=customers)

# sns.lmplot(x='Length of Membership',y='Yearly Amount Spent',data=customers)
X =customers[['Avg. Session Length','Time on App','Time on Website','Length of Membership']]
X.head()
Y=customers['Yearly Amount Spent']
Y.head()


from sklearn.model_selection import train_test_split

X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size=0.3,random_state=101)
from sklearn.linear_model import LinearRegression

lm = LinearRegression() # Creating an Instance of LinearRegression model
lm.fit(X_train,Y_train) # Train/fit on the trainingdata, this will give-

# The coefficients/slopes of model -

print(lm.coef_)
prediction = lm.predict(X_test)

plt.scatter(Y_test,prediction)



from sklearn import metrics
print('MAE= ', metrics.mean_absolute_error(Y_test,prediction) )
print('MSE= ', metrics.mean_squared_error(Y_test,prediction))
print('RMSE: ', np.sqrt(metrics.mean_squared_error(Y_test, prediction)))
plt.hist(prediction-Y_test,bins=50)


co=pd.DataFrame(lm.coef_,X.columns)
co.columns = ['Coefficient']
print(co)
plt.show()
