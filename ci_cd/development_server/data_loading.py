#Imports
import requests
import json
import time
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

# Ignore all warnings
warnings.filterwarnings('ignore')

#SKLearn
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor

repositories = []
parameters={ 'q': 'stars:>=50', 'per_page': 100,  'page': 1   }
while len(repositories) < 1000:
  response = requests.get('https://api.github.com/search/repositories', params=parameters)
  if response.status_code == 200:
    batch = response.json()['items']
    repositories.extend(batch)
    print("Batch size: " ,len(batch), " Total number of repositories: ", len(repositories))
    if 'next' in response.links:
      parameters['page'] += 1
    else:
      break
#print(repositories[:10])

fieldnames = repositories[0].keys()
print(fieldnames)
with open("original_project_data.csv", 'w', newline='', encoding='utf-8') as csv_file:
  writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
  writer.writeheader()
  for repo in repositories:
    writer.writerow(repo)
