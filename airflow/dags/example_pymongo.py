"""Example tutorial for pymongo"""
import os
import logging
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
    client = MongoClient("mongodb://admin:adminpassword@localhost:27017")
    db = client["e_commerce_db"]

    json_data = generate_json_data()

    if isinstance(json_data, list):  # Check if JSON data is a list of documents
        db.test_data.insert_many(json_data)
        logging.info("Inserted documents %s", len(json_data))
    else:  # Otherwise, insert a single document
        logging.info("Inserted just one document")
        db.test_data.insert_one(json_data)

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
        task_id="load_json_into_mongo_db",
        python_callable=load_json_into_mongo_db
    )

    # pylint: disable=pointless-statement
    print_hello_world_task >> load_json_into_mongo_db_task

# Instantiate the DAG
dag = pymongo_tutorial_dag() # pylint: disable=invalid-name
