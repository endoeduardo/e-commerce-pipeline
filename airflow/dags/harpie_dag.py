"""Example tutorial for pymongo"""
import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import pendulum
from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

DAG_START_DATE = pendulum.datetime(2024, 11, 17, tz="UTC")
DAG_SCHEDULE_INTERVAL = "0 0 * * 2-6"
SCRAPY_PROJECT_PATH = os.getenv("AIRFLOW_HOME") + "/dags/crawlers"
SCRAPY_SPIDER_NAME = "harpie_crawler"

def test_mongo_connection(uri: str) -> None:
    """Test mongo connection"""
    try:
        with MongoClient(uri, serverSelectionTimeoutMS=5000) as client:
            client.admin.command('ping')
            logging.info("Connection successful!")
    except ConnectionFailure as error:
        logging.error("Connection failed: %s", error)


def check_scraper_exists() -> None:
    """Checks if a given crawler is present in the project, otherwise it will raise an error"""
    spider_path = os.path.join(SCRAPY_PROJECT_PATH, 'spiders', f'{SCRAPY_SPIDER_NAME}.py')
    if not os.path.exists(spider_path):
        raise FileNotFoundError(f"Spider {SCRAPY_SPIDER_NAME} does not exist in the project.")
    

@dag(
    schedule_interval=DAG_SCHEDULE_INTERVAL,
    start_date=DAG_START_DATE,
    catchup=False
)
def harpie_dag():
    """Main DAG"""

    test_mongo_connection_task = PythonOperator(
        task_id="test_mongo_connection",
        python_callable=test_mongo_connection,
        op_kwargs={"uri": "mongodb://admin:adminpassword@mongo-test"}
    )

    list_available_scrapers_task = BashOperator(
        task_id="list_available_scrapers",
        bash_command=f"cd {SCRAPY_PROJECT_PATH} && scrapy list"
    )

    validate_scraper = PythonOperator(
        task_id='validate_scraper',
        python_callable=check_scraper_exists
    )

    # pylint: disable=pointless-statement
    test_mongo_connection_task >> list_available_scrapers_task >> validate_scraper

dag = harpie_dag() # pylint: disable=invalid-name
