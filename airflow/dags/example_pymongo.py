"""Example tutorial for pymongo"""
import os
import json
from datetime import datetime
from random import randint
from pymongo import MongoClient
from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import pendulum

def generate_json_data() -> dict:
    """Generates a JSON document data"""
    current_datetime = datetime.now().strftime(format="%Y-%m-%d %H:%M:%S")
    random_value = randint(0, 100)

    json_data = {"current_datetime": current_datetime, "random_value": random_value}
    return json_data

def load_json_into_mongo_db() -> None:
    """Load fake data into mongodb"""
    client = MongoClient(os.environ["MONGO_URI"])
    db = client[os.environ["MONGO_DATABASE"]]
    collection = db["test_data"]

    json_data = generate_json_data()

    data = json.load(json_data)

    if isinstance(data, list):  # Check if JSON data is a list of documents
        collection.insert_many(data)
    else:  # Otherwise, insert a single document
        collection.insert_one(data)

@dag(
    schedule_interval="0 0 * * 2-6",
    start_date=pendulum.datetime(2024, 11, 17, tz="UTC"),
    catchup=False
)
def pymongo_tutorial_dag():
    """Main DAG"""
    print_hello_world_task = BashOperator(
        task_id="print_hello_world",
        bash_command="echo 'Hello World'"
    )

    load_json_into_mongo_db_task = PythonOperator(
        task_id="print_current_datetime",
        python_callable=generate_json_data
    )

    # pylint: disable=pointless-statement
    print_hello_world_task >> load_json_into_mongo_db_task

# Instantiate the DAG
dag = pymongo_tutorial_dag() # pylint: disable=invalid-name