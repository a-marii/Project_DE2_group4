from ray import tune
import ray
import requests
import json
import time
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from ray import train 
# Ignore all warnings
warnings.filterwarnings('ignore')
import pickle

#SKLearn
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from ray.tune.schedulers import ASHAScheduler
import joblib 
#ray.shutdown()
ray.init(address="auto")


data = pd.read_csv("original_project_data.csv")
data = data.drop(columns=[col for col in data.columns if 'url' in col])
data = data.drop(columns=[col for col in data.columns if data[col].dtype == 'object'])
data = data.replace({True: 1, False: 0})
data = data.drop(columns=['id', 'private', 'fork', 'disabled', 'allow_forking', 'watchers', 'forks', 'score', "watchers_count", "open_issues_count"]) 
#ray.init(address="auto")


label = 'stargazers_count'
features = data.columns.to_list()
features.remove('stargazers_count')
print("Label:", label)
print("Features:", features)
X = data[features]
y = data[label]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
def train_rf(config):
    model = RandomForestRegressor(max_depth= config["max_depth"], n_estimators= config["n_estimators"])
    model.fit(X_train, y_train)
    prediction = model.predict(X_test)
    mse = mean_squared_error(y_test, prediction)
    r2 = r2_score(y_test, prediction)
    train.report(dict(mean_accuracy=r2 ))

def train_dt(config):
    model = DecisionTreeRegressor(max_depth= config["max_depth"], min_samples_split= config["min_samples_split"])
    model.fit(X_train, y_train)
    prediction = model.predict(X_test)
    mse = mean_squared_error(y_test, prediction)
    r2 = r2_score(y_test, prediction)
    train.report(dict(mean_accuracy=r2 ))

def train_lr(config):
    model = LinearRegression(n_jobs= config["n_jobs"])
    model.fit(X_train, y_train)
    prediction = model.predict(X_test)
    mse = mean_squared_error(y_test, prediction)
    r2 = r2_score(y_test, prediction)
    train.report(dict(mean_accuracy=r2 ))

def train_svr(config):
    model = SVR(C= config['C'], gamma = config['gamma'])
    model.fit(X_train, y_train)
    prediction = model.predict(X_test)
    mse = mean_squared_error(y_test, prediction)
    r2 = r2_score(y_test, prediction)
    train.report(dict(mean_accuracy=r2 ))

def train_knn(config):
    model = KNeighborsRegressor(n_neighbors = config["n_neighbors"])
    model.fit(X_train, y_train)
    prediction = model.predict(X_test)
    mse = mean_squared_error(y_test, prediction)
    r2 = r2_score(y_test, prediction)
    train.report(dict(mean_accuracy=r2 ))

search_spaces = {
    "RandomForestRegressor": {
        "max_depth": tune.grid_search([5, 20, None]),
        "n_estimators": tune.grid_search([150, 300])
    },
    "DecisionTreeRegressor": {
        "max_depth": tune.grid_search([1, 2, 3, 4]),
        "min_samples_split": tune.grid_search([2, 4, 6, 8, 10])
    },
    "LinearRegression": {
        "n_jobs": tune.grid_search([1, 2, 3, 4])
    },
    "SVR": {
        'C': tune.grid_search([0.1, 1, 10, 100]),
        'gamma': tune.grid_search(['scale', 'auto', 0.1, 1, 10])
    },
    "KNeighborsRegressor": {
        "n_neighbors": tune.grid_search(list(range(2, 10)))
    }
}

models = [
    (train_rf, search_spaces["RandomForestRegressor"], "RandomForestRegressor"),
    (train_dt, search_spaces["DecisionTreeRegressor"], "DecisionTreeRegressor"),
    (train_lr, search_spaces["LinearRegression"], "LinearRegression"),
    (train_svr, search_spaces["SVR"], "SVR"),
    (train_knn, search_spaces["KNeighborsRegressor"], "KNeighborsRegressor")
]

best_params=[]
for train_func, search_space, model_name in models:
    print(f"Running hyperparameter tuning for {model_name}")

    analysis = tune.run(
        train_func,
        config=search_space,
        resources_per_trial={"cpu": 1},
        scheduler=ASHAScheduler(metric="mean_accuracy", mode="max"),
        verbose=1
    )
    best_params.append(analysis.get_best_config(metric='mean_accuracy', mode='max'))

best_acc=0

models_func=[RandomForestRegressor(),DecisionTreeRegressor(),LinearRegression(),SVR(), KNeighborsRegressor()]
for idx, (train_func, search_space, model_name) in  enumerate(models):
    model = models_func[idx]
    model.set_params(**best_params[idx])
    model.fit(X_train, y_train)
    prediction = model.predict(X_test)
    mse = mean_squared_error(y_test, prediction)
    r2 = r2_score(y_test, prediction)
    if r2>best_acc:
        best_acc=r2
        with open('best_model.pkl','wb') as f:
            pickle.dump(model,f)

    print(f"Model {model_name}, parameters {best_params[idx]}, R2 {r2}")
    with open(f'{model_name}.pkl','wb') as f:
        pickle.dump(model,f)

ray.shutdown()

