FROM apache/airflow:2.10.3

ADD airflow_requirements.txt .

RUN pip install apache-airflow==${AIRFLOW_VERSION} -r airflow_requirements.txt