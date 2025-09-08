import pandas as pd

data= pd.read_csv("3.csv")

# When we read in our data into a data frame 'df' with a column named 'x', there is an important difference between the two operations df[['x']] versus df['x'].

#     df[['x']] returns a Pandas data frame object that is an array we can use in sklearn
#     df['x'] returns a Pandas series that will give an error when using sklearn


X =data[['TV','radio','newspaper']]
X.head()
Y=data['sales']
Y.head()


# Now we have decided how we are going the names for our data, let us move to how we are going to model. We will assume that the response variable, , relates to the predictors, , through some unknown function generally expressed as:
# Y = f(x) + e. e -> is the random amount (not related to X). f(x) -> unknown function expressing an underlying rule to relate X and Y
# A statistical model is any algorithm that estimates f. We denote the estimated function as f^.

print(X.shape) # (n,p) (n => no of rows, p => no of predictors)
print(Y.shape) # (n,1) or (n,)