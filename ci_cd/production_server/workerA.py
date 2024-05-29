from celery import Celery
from celery import Celery
import pickle
from numpy import loadtxt
import numpy as np
from tensorflow.keras.models import model_from_json
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score

#model_json_file = './model.json'
model_weights_file = './best_model.pkl'
data_file = './original_project_data.csv'

def load_data():
    data = pd.read_csv(data_file)
    data = data.drop(columns=[col for col in data.columns if 'url' in col])
    data = data.drop(columns=[col for col in data.columns if data[col].dtype == 'object'])
    data = data.replace({True: 1, False: 0})
    data = data.drop(columns=['id', 'private', 'fork', 'disabled', 'allow_forking', 'watchers', 'forks', 'score', "watchers_count", "open_issues_count"]) 
    label = 'stargazers_count'
    features = data.columns.to_list()
    features.remove('stargazers_count')
    print("Label:", label)
    print("Features:", features)
    X = data[features]
    y = data[label]
    return X, y

def load_model():
    loaded_model = pickle.load(open(model_weights_file , 'rb'))
    return loaded_model

# Celery configuration

CELERY_BROKER_URL = 'pyamqp://rabbitmq:rabbitmq@rabbit:5672/'
CELERY_RESULT_BACKEND = 'rpc://'
# Initialize Celery
celery = Celery('workerA',broker=CELERY_BROKER_URL,backend=CELERY_RESULT_BACKEND)


@celery.task()
def add_nums(a, b):
    return a + b
    
@celery.task
def get_predictions():
    results ={}
    X, y = load_data()
    loaded_model = load_model()
    prediction =loaded_model.predict(X)
    r2 = r2_score(y, prediction)
    X['pred_stars']=prediction
    X['stars']=y

    top5=X.sort_values(by=['pred_stars']).head(5)
    results['size'] = top5['size'].tolist() 
    results['has_issues'] = top5['has_issues'].tolist() 
    results['has_downloads'] = top5['has_downloads'].tolist() 
    results['has_wiki'] = top5['has_wiki'].tolist() 
    results['pred_stars'] = top5['pred_stars'].tolist() 
    results['stars'] = top5['stars'].tolist()    
    return results

@celery.task
def get_accuracy():
    results ={}
    X, y = load_data()
    loaded_model = load_model()
    prediction =loaded_model.predict(X)
    r2 = r2_score(y, prediction)

    return r2


