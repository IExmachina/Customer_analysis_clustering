# -*- coding: utf-8 -*-
"""Customer_analysis-clustering.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DvAxE5ltEEtaYlNRDBAr-rPlC28pyAmn

# Customer Analysis - Data Science
Customer Personality Analysis is a detailed analysis of a company’s ideal customers. It helps a business to better understand its customers and makes it easier for them to modify products according to the specific needs, behaviors and concerns of different types of customers.

Customer personality analysis helps a business to modify its product based on its target customers from different types of customer segments. For example, instead of spending money to market a new product to every customer in the company’s database, a company can analyze which customer segment is most likely to buy the product and then market the product only on that particular segment.


Dataset -> [Kaggle](https://www.kaggle.com/imakash3011/customer-personality-analysis)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Commented out IPython magic to ensure Python compatibility.
# Activating the GPU
# %tensorflow_version 2.x
import tensorflow as tf
device_name = tf.test.gpu_device_name()
if device_name != '/device:GPU:0':
  raise SystemError('GPU device not found')
print('Found GPU at: {}'.format(device_name))

from google.colab import drive
drive.mount('/content/drive')

"""####CRISP DM - Methodology for Data Science projects.
* Business Understanding
* Data Understanding
* Data Preparation
* Modelling
* Evaluation
* Deployment

# Data Understanding
"""

df = pd.read_csv("/content/drive/MyDrive/datasets/marketing_campaign.csv", header=0, sep=';')
df

df.info()

"""As we saw above, we only have three columns of type object, one of which should be data type. I'll fix that and also the few null values ​​in the "income" column."""

# We will get dummies on this
df.Education.value_counts()

df.Marital_Status.value_counts()
# I will deal with these values ​​since alonme and single are the same thing and the last two classes don't make sense ("YOLO" and "Absurd").

df.describe()
# Looks like we have some outliers here, like in the "Income" column.

df.corr()



"""## Data Visualization"""

sns.boxplot(x=df.Income)
# As we suspect, we have a pretty big outlier.

"""I will now use a very complete library to analyze the data. A library called "dataprep"."""

!pip install dataprep

from dataprep.eda import plot, plot_correlation, create_report, plot_missing
# Great facilitator, this function. Let's take an in-depth look at the data interactively.
plot(df)

plot_correlation(df)

"""## Conclusion:
We saw missing values, outliers and some somewhat redundant columns.
Let's start processing the data.

We saw missing values, outliers and some somewhat redundant columns.
Let's start processing the data.
Our next steps will be:

* 1. Exclude outliers and treat null values.


* 2. Create and modify columns.


* 3. Leave the distribution closer to normal.

# Data preparation
"""

# Step 1
# Removing the outlier
df= df[df['Income']<600000]

# Replacing null values ​​with the mean.
df["Income"].fillna(df["Income"].mean(), axis=0, inplace=True)

# Step 2
# Creating an age column.
df['Age']=2014-df['Year_Birth']

# Creating an spending column.
df['Spending']= df['MntWines'] + df['MntFruits'] + df['MntMeatProducts'] + df['MntFishProducts'] + df['MntSweetProducts'] + df['MntGoldProds']

# Creating a children column
df['Children']= df['Kidhome'] + df['Teenhome']

#Seniority column creation
from datetime import date

last_date = date(2014,10, 4)
df['Seniority'] = pd.to_datetime(df['Dt_Customer'], dayfirst=True)
df['Seniority'] = round(pd.to_numeric(df['Seniority'].dt.date.apply(lambda x: (last_date - x)).dt.days, downcast='integer')/30)

# Organazing categorical variables
df = df.rename(columns={'NumWebPurchases': "Web",'NumCatalogPurchases':'Catalog','NumStorePurchases':'Store'})
df['Marital_Status'] = df['Marital_Status'].replace({'Divorced':'Alone','Single':'Alone','Married':'In couple','Together':'In couple','Absurd':'Alone','Widow':'Alone','YOLO':'Alone'})
df['Education'] = df['Education'].replace({'Basic':'Undergraduate','2n Cycle':'Undergraduate','Graduation':'Postgraduate','Master':'Postgraduate','PhD':'Postgraduate'})
df = df.rename(columns={'MntWines': "Wines",'MntFruits':'Fruits','MntMeatProducts':'Meat','MntFishProducts':'Fish','MntSweetProducts':'Sweets','MntGoldProds':'Gold'})

# The new dataframe
df=df[['Age','Education','Marital_Status','Income','Spending','Seniority','Children','Wines','Fruits','Meat','Fish','Sweets','Gold']]
df.head()

# Step 3
# locating the columns with the most skew values
log_columns = df.skew().sort_values(ascending=False)
log_columns = log_columns.loc[log_columns > 0.75]

log_columns

# The log transformations on the skewed columns
for col in log_columns.index:
    df[col] = np.log1p(df[col])

plot(df)

"""Now we have a new dataset, close enought to a normal distribution."""

# Finally, let's apply the one hot encoding and then normalize the data.
# The only two columns with categorical variables are Education and Marital status.
# As we have summarized education in two options, being graduated or ungraduated, and marital status as single or in a relationship, so as not to have irrelevant columns and 
# since if it is not an option it is the other, I will use the drop first function.
df = pd.get_dummies(df, drop_first=True)
df.head()

# Creating a copy that will not be scaled. We will use it after the clustering.
df2 = df.copy(deep=True)

from sklearn.preprocessing import MinMaxScaler

mms = MinMaxScaler()

for col in df.columns:
    df[col] = mms.fit_transform(df[[col]]).squeeze()

"""# Modelling 1 - Clustering
I'm going to use the K-means algorithm to try to find patterns in the data, since it's have no labels. First let's try to find the best value for k, and then actually apply the model.

When we have a sense of how many classes we find or want to have in the data, it helps a lot.
But we can also be guided by the inercia parameter to find the right number of clusters.

## K-means
"""

# Create and fit a range of models to find the best
from sklearn.cluster import KMeans

km_list = list()       

for clust in range(1,21):
    km = KMeans(n_clusters=clust, random_state=42)
    km = km.fit(df)
    
    km_list.append(pd.Series({'clusters': clust, 
                              'inertia': km.inertia_,
                              'model': km}))

# Plotting the results for each k
plot_data = (pd.concat(km_list, axis=1)
             .T
             [['clusters','inertia']]
             .set_index('clusters'))

ax = plot_data.plot(marker='o',ls='-')
ax.set_xticks(range(0,21,2))
ax.set_xlim(0,21)
ax.set(xlabel='Cluster', ylabel='Inertia');

# I test 6 clusters but 4 clusters was better for this data and we have a good result.
km = KMeans(n_clusters=4, random_state=42)
km = km.fit(df)

df['kmeans'] = km.predict(df)

df

"""### Evaluating K-Means
Let's see if the clusters that we create are impactful somehow.
"""

# For the comparisons I will use the unscaled dataset, to have a better understanding.

# Creating the same kmeans column in the unscaled dataset
df2["kmeans"] = df['kmeans']

df2

import plotly.express as px

fig = px.scatter(x='Spending', y='Income', data_frame=df2, color='kmeans')
fig.show()

df2.groupby("kmeans")["Income"].mean()

df2.groupby("kmeans")["Spending"].mean()

df2.groupby("kmeans")["Age"].mean()

df2.groupby("kmeans")[["Wines", "Fruits", "Meat", "Fish", "Sweets", "Gold"]].mean()

df2.groupby("kmeans")[["Education_Undergraduate",	"Marital_Status_In couple"]].sum().astype(int)

df2.groupby("kmeans")["Seniority"].mean()

"""## Agglomerative Clustering"""

from sklearn.cluster import AgglomerativeClustering
### BEGIN SOLUTION
ag = AgglomerativeClustering(n_clusters=4, linkage='ward', compute_full_tree=True)
ag = ag.fit(df)
df2['agglom'] = ag.fit_predict(df)

df2

import plotly.express as px

fig = px.scatter(x='Spending', y='Income', data_frame=df2, color='agglom')
fig.show()



df2.groupby("agglom")["Income"].mean()

df2.groupby("agglom")["Spending"].mean()

df2.groupby("agglom")["Age"].mean()

df2.groupby("agglom")[["Wines", "Fruits", "Meat", "Fish", "Sweets", "Gold"]].mean()

df2.groupby("agglom")[["Education_Undergraduate",	"Marital_Status_In couple"]].sum().astype(int)

df2.groupby("agglom")["Seniority"].mean()

"""## DBSCAN"""

from sklearn.cluster import DBSCAN

dbscan = DBSCAN(eps=1.0, min_samples=8, n_jobs=-1)
dbscan.fit(df)

labels = dbscan.labels_
labels

df2['dbscan'] = labels
df2

fig = px.scatter(x='Spending', y='Income', data_frame=df2, color='dbscan')
fig.show()

df2.groupby("dbscan")["Income"].mean()

df2.groupby("dbscan")["Spending"].mean()

df2.groupby("dbscan")["Age"].mean()

df2.groupby("dbscan")[["Wines", "Fruits", "Meat", "Fish", "Sweets", "Gold"]].mean()

df2.groupby("dbscan")[["Education_Undergraduate",	"Marital_Status_In couple"]].sum().astype(int)

df2.groupby("dbscan")["Seniority"].mean()

"""## Conclusion:
I liked the results of the K-means and Agglomerative Clustering models.
They were very similar and you could clearly see the difference between the groups.

As for DBSCAN, as I expected, it was great for identifying outliers. But I didn't like the amount of clusters created, I found many relevant and it ends up not being interesting.

I'll stick with the K-means model, as I found it slightly better than Agglomerative Clustering.

## Findings with K-means:
We can see that we have 4 really distinct and interesting classes.
I will do hypothesis tests to confirm and satisfactorily if these classes really have differences but from the analysis above we already have a good idea.

The distinction of classes follows:

* **Class 0 -> Top Clients**
The oldest costumers, both in age and seniority. They are the customers who buy the most in general and have the best financial conditions. Also most of them are graduates.
They buy a lot of wine and meat and are all single with an average of 46 years old.

* **Class 1 -> Attention**
They are the youngest customers both in age and seniority.
It has the largest number of non-graduates and they are also in relationships.
They are the ones who spend and earn less.
The product that stands out for them is wine, which proportionally is the product that they buy the most.

* **Class 2 -> High Potential**
These are relatively new customers, with great potential to become top customers as well.
They are the second class that earns and buys the most, the big difference is that they have a higher rate of non-graduates and relationships.

* **Class 3 -> Ghosts**
These are customers who have been buying for a while and neither earn nor spend much.
They follow the same pattern, stagnant.
They need a motivation to attend and spend more.
While the way it is, they also doesn't tend to go away.
"""

# Droping the other models columns.
df2.drop(columns=['agglom', 'dbscan'], inplace=True)

# Creating a new column with the new names for the classes.
df2.loc[(df2['kmeans'] == 0), 'Customer_Profile'] = 'TOP'
df2.loc[(df2['kmeans'] == 1), 'Customer_Profile'] = 'ATTENTION'
df2.loc[(df2['kmeans'] == 2), 'Customer_Profile'] = 'HIGH POTENTIAL'
df2.loc[(df2['kmeans'] == 3), 'Customer_Profile'] = 'GHOSTS'
# Droping the 'kmeans' column since we have the new one.
df2.drop('kmeans', axis=1, inplace=True)

df2.head()

# Looking at the values for each class.
df2['Customer_Profile'].value_counts()

"""## Hypothesis tests.
Let's see if the classes really have statistical differences and if each one has an association with the independent variables.


"""

# First let's see if we have a strog skew in some column
log_columns = df2.skew().sort_values(ascending=False)
log_columns = log_columns.loc[log_columns > 0.75]

log_columns

# The log transformations
for col in log_columns.index:
    df2[col] = np.log1p(df2[col])

"""####Test 1:
**Is there a difference in Median values of income for each customer profile?**

We will use the **ANOVA** test, since there are more than two independent variables.

The requirements for the anova test are equality of variances and normal distribution.
Since we are dealing with means, according to the central limit theorem we have a normal distribution. As for the equality of variances, let's do a test too.

* **H_0: µ_1 = µ_2 ->** There IS NOT a difference in median values of income for each customer profile.
* **H_1: µ_1 ≠ µ_2 ->** There IS a difference in median values of income for each customer profile.
"""

# First, let's test the equality of variance.
import scipy.stats
scipy.stats.levene(df2[df2['Customer_Profile'] == 'TOP']['Income'],
                   df2[df2['Customer_Profile'] == 'ATTENTION']['Income'],
                   df2[df2['Customer_Profile'] == 'HIGH POTENTIAL']['Income'],
                   df2[df2['Customer_Profile'] == 'GHOSTS']['Income'], center='mean')



# Since the p-value is greater than 0.05, we do not reject the null hyphotesis. So we assume that there are equality of variance.

# getting the variables for the ANOVA test
top = df2[df2['Customer_Profile'] == 'TOP']['Income']
attention =  df2[df2['Customer_Profile'] == 'ATTENTION']['Income']
potential = df2[df2['Customer_Profile'] == 'HIGH POTENTIAL']['Income']
ghosts = df2[df2['Customer_Profile'] == 'GHOSTS']['Income']

# Test
f_statistic, p_value = scipy.stats.f_oneway(top, attention, potential, ghosts)
print("F_Statistic: {0}, P-Value: {1}".format(f_statistic,p_value))

"""#####**Test 1 - Conclusion**:
Since the p-value is **less** than 0.05 we reject the null hyphotesis! 

We assume that there IS a difference in median values of income for each customer profile!

####Test 2:
Now, let's test for two variables at once.

**Is there a difference in median values of seniority and spending for each customer profile?**

We will use the **ANOVA** test, since there are more than two independent variables.


* **H_0: µ_1 = µ_2 ->** There IS NOT a difference in median values of seniority and spending for each customer profile.
* **H_1: µ_1 ≠ µ_2 ->** There IS a difference in median values of seniority and spending for each customer profile.
"""

# Test for the equality of variance in spending.
import scipy.stats
scipy.stats.bartlett(df2[df2['Customer_Profile'] == 'TOP']["Spending"],
                   df2[df2['Customer_Profile'] == 'ATTENTION']["Spending"],
                   df2[df2['Customer_Profile'] == 'HIGH POTENTIAL']["Spending"],
                   df2[df2['Customer_Profile'] == 'GHOSTS']["Spending"])



# Since the p-value is less than 0.05, we reject the null hyphotesis. So we assume that there are not equality of variance here.

# Test for the equality of variance in seniority.
import scipy.stats
scipy.stats.bartlett(df2[df2['Customer_Profile'] == 'TOP']["Seniority"],
                   df2[df2['Customer_Profile'] == 'ATTENTION']["Seniority"],
                   df2[df2['Customer_Profile'] == 'HIGH POTENTIAL']["Seniority"],
                   df2[df2['Customer_Profile'] == 'GHOSTS']["Seniority"])

# Since the p-value is greater than 0.05, we do not reject the null hyphotesis. So we assume that there are equality of variance here.

"""In practice, these assumptions need not all be rigorously satisfied. The results are empirically true whenever populations are approximately normal (that is, not very skewed) and have close variances. So despite the variances of "spending" not being equal, we will continue to test for ANOVA."""

# getting the variables for the ANOVA test
top = df2[df2['Customer_Profile'] == 'TOP'][["Spending", "Seniority"]]
attention =  df2[df2['Customer_Profile'] == 'ATTENTION'][["Spending", "Seniority"]]
potential = df2[df2['Customer_Profile'] == 'HIGH POTENTIAL'][["Spending", "Seniority"]]
ghosts = df2[df2['Customer_Profile'] == 'GHOSTS'][["Spending", "Seniority"]]

# Test
f_statistic, p_value = scipy.stats.f_oneway(top, attention, potential, ghosts)
print("F_Statistic: {0}, P-Value: {1}".format(f_statistic,p_value))

"""#####**Test 2 - Conclusion**:
Since the p-value is **less** than 0.05 for both, "Spending" and "Seniority", we reject the null hyphotesis! 

We assume that there IS a difference in median values of seniority and spending for each customer profile.

# Modelling 2 - Classification
We prove that the classes were well established and that there is a statistical difference between them.

Now let's create a classification model to try to classify new customers as one of the classes we get through the K-means model.
It will be interesting! Let's dive into it.
"""

# Models
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.svm import SVC
# Metrics
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report, confusion_matrix, plot_roc_curve

# Evaluation
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score, KFold
from sklearn.model_selection import train_test_split

"""
Let's use grid search to find the best parameters for the models.
But first, let's get our data."""

# The predicting features
X = df2[['Age', 'Income', 'Spending', 'Seniority', 'Children', 'Wines', 'Fruits',
       'Meat', 'Fish', 'Sweets', 'Gold', 'Education_Undergraduate',
       'Marital_Status_In couple']].values

# Our target
y = df['kmeans'].values

X.shape, y.shape

"""### Grid Search"""

# Gradient Boosting Classifier

tree_list = [100, 150, 200, 300]
parameters = {'n_estimators': tree_list,
              'learning_rate': [0.1, 0.01, 0.001],
              'subsample': [1.0, 0.5, 0.1],
              'max_features': [1, 2, 3, 4]}

gbc_grid = GridSearchCV(GradientBoostingClassifier(random_state=42), 
                      param_grid=parameters, 
                      scoring='accuracy',
                      n_jobs=-1, cv=10)

gbc_grid = gbc_grid.fit(X,  df['kmeans'])

print(f'Best parameters: {gbc_grid.best_params_}')
print(f'Best result: {gbc_grid.best_score_}')

# Random Forest
parameters = {'criterion': ['gini', 'entropy'],
              'n_estimators': [100, 150],
              'min_samples_split': [2, 5, 10],
              'min_samples_leaf': [1, 5, 10]}

rf_grid = GridSearchCV(estimator=RandomForestClassifier(random_state=42), param_grid=parameters, scoring='accuracy',
                      n_jobs=-1, cv=10)
rf_grid.fit(X, df['kmeans'])

print(rf_grid.best_params_)
print(rf_grid.best_score_)

# SVC
# The SVC needs data scaled and the target numerical.
from sklearn.pipeline import Pipeline

pipe = Pipeline([("Scaler", MinMaxScaler())])
X_scaler = pipe.fit_transform(X)

parameters = {'tol': [0.001, 0.0001],
              'C': [1.0, 1.5, 2.0],
              'kernel': ['rbf', 'linear', 'sigmoid']}

svc_grid = GridSearchCV(estimator=SVC(), param_grid=parameters, scoring='accuracy',
                      n_jobs=-1, cv=10)
svc_grid.fit(X_scaler, df['kmeans'].values)

print(svc_grid.best_params_)
print(svc_grid.best_score_)

"""# Evaluation
To get the classification report and the confusion matrix, I will use train test split.
"""

X_train, X_test, y_train, y_test = train_test_split(X, df['kmeans'], test_size=0.25, random_state=42)
X_train.shape, y_train.shape, X_test.shape, y_test.shape

# getting predictions for each model
gbc = GradientBoostingClassifier(learning_rate=0.1, max_features=2, n_estimators=300, subsample=0.5, random_state=42)
gbc.fit(X_train, y_train)

rf = RandomForestClassifier(criterion='gini', min_samples_leaf=1, min_samples_split=2, n_estimators=150, n_jobs=-1)
rf.fit(X_train, y_train)

X_scaler_train = pipe.fit_transform(X_train)
X_scaler_test = pipe.fit_transform(X_test)
svc = SVC(C=2.0, kernel='rbf', tol=0.001)
svc.fit(X_scaler_train, y_train)
y_hat_gbc = gbc.predict(X_test)
y_hat_rf = rf.predict(X_test)
y_hat_svc = svc.predict(X_scaler_test)

# plotting the confusion matrix
predictions = [y_hat_gbc, y_hat_rf, y_hat_svc]
model_names = ["GBC", "Random Forest", "SVC"]
names = 0
for y in predictions:
  print(model_names[names])
  sns.set_context('talk')
  cm = confusion_matrix(y_test, y)
  ax = sns.heatmap(cm, annot=True, fmt='d')
  plt.show()
  print("=========================================")
  names += 1

# plotting the classification report for each model
models = [gbc, rf, svc]
model_names = ["GBC", "Random Forest", "SVC"]
names = 0

for i in models:
  y_hat = i.predict(X_test)
  print(f'Model:{model_names[names]} \n {classification_report(y_test, y_hat)}')
  print("======================================================")
  print("======================================================")
  names += 1

roc_auc_score

"""# Deployment
GBC is the best model.
"""

# Saving the model.
import pickle
pickle.dump(gbc_grid, open('gbc_classifier.pkl', 'wb'))