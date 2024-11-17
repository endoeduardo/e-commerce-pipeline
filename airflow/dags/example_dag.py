"""Example tutorial dag"""
from datetime import datetime
from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import pendulum

def print_current_datetime() -> None:
    """Prints current datetime"""
    current_datetime = datetime.now().strftime(format="%Y-%m-%d %H:%M:%S")
    print(current_datetime)

@dag(
    schedule_interval="0 0 * * 2-6",  # Correct parameter name
    start_date=pendulum.datetime(2024, 6, 1, tz="UTC"),
    catchup=True
)
def tutorial_dag():
    """Main DAG"""
    print_hello_world_task = BashOperator(
        task_id="print_hello_world",
        bash_command="echo 'Hello World'"
    )

    print_current_datetime_task = PythonOperator(
        task_id="print_current_datetime",
        python_callable=print_current_datetime
    )

    # pylint: disable=pointless-statement
    print_hello_world_task >> print_current_datetime_task

# Instantiate the DAG
dag = tutorial_dag() # pylint: disable=invalid-name
