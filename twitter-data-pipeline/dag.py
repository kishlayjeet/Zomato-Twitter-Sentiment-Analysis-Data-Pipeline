from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from main import TwitterETL

# Create an instance of your class
etl = TwitterETL()

# Define the functions to be used in PythonOperator
def twitter_data_extraction():
    etl.twitter_data_extraction()

def twitter_data_transformation():
    etl.twitter_data_transformation()

# Set default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 8, 13),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG instance
dag = DAG(
    'twitter_dag',
    default_args=default_args,
    description='Twitter ETL',
    schedule_interval='@daily',
)

# Create the PythonOperator for running the ETL tasks
run_extraction = PythonOperator(
    task_id='twitter_data_extraction',
    python_callable=twitter_data_extraction,
    dag=dag,
)

run_transformation = PythonOperator(
    task_id='twitter_data_transformation',
    python_callable=twitter_data_transformation,
    dag=dag,
)

# Define task order
run_extraction >> run_transformation
