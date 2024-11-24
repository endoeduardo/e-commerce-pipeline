"""Example tutorial for pymongo"""
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import pendulum
from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

TARGET_SCRAPER = "harpie_crawler"
DAG_START_DATE = pendulum.datetime(2024, 11, 17, tz="UTC")
DAG_SCHEDULE_INTERVAL = "0 0 * * 2-6"

def test_mongo_connection(uri: str) -> None:
    """Test mongo connection"""
    try:
        with MongoClient(uri, serverSelectionTimeoutMS=5000) as client:
            client.admin.command('ping')
            logging.info("Connection successful!")
    except ConnectionFailure as error:
        logging.error("Connection failed: %s", error)


def check_scraper_exists(**kwargs) -> None:
    """Checks if a given crawler is present in the project, otherwise it will raise an error"""
    ti = kwargs["ti"]
    spiders_list = ti.xcom_pull(task_ids='list_spiders')
    logging.info("Available spiders (%s)", spiders_list)
    
    if TARGET_SCRAPER not in spiders_list.splitlines():
        logging.error("Scraper '%s' not found in the project!", TARGET_SCRAPER)
        raise ValueError
    logging.info("Scraper '%s' is present.", TARGET_SCRAPER)


@dag(
    schedule_interval=DAG_SCHEDULE_INTERVAL,
    start_date=DAG_START_DATE,
    catchup=False
)
def pymongo_tutorial_dag():
    """Main DAG"""

    test_mongo_connection_task = PythonOperator(
        task_id="test_mongo_connection",
        python_callable=test_mongo_connection,
        op_kwargs={"uri": "mongodb://admin:adminpassword@mongo-test"}
    )

    list_available_scrapers_task = BashOperator(
        task_id="list_available_scrapers",
        bash_command="cd dags/crawlers && scrapy list"
    )

    validate_scraper = PythonOperator(
        task_id='validate_scraper',
        python_callable=check_scraper_exists,
        provide_context=True,
    )

    # pylint: disable=pointless-statement
    test_mongo_connection_task >> list_available_scrapers_task >> validate_scraper

dag = pymongo_tutorial_dag() # pylint: disable=invalid-name
