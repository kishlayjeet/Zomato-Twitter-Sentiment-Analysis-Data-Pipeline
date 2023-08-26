import boto3
import psycopg2
import os
import logging


# Environment Variables
DB_PARAMS = {
    'dbname': os.environ['DB_NAME'],
    'user': os.environ['DB_USER'],
    'password': os.environ['DB_PASSWORD'],
    'host': os.environ['DB_HOST'],
    'port': os.environ['DB_PORT']
}
ACCESS_KEY = os.environ['Access_key']
ACCESS_SECRET = os.environ['Secret_access_key']

logging.basicConfig(level=logging.INFO)


def create_connection():
    try:
        connection = psycopg2.connect(**DB_PARAMS)
        logging.info("Connection established successfully.")
        return connection
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise

def delete_csv(bucket, file_name):
    s3 = boto3.client('s3')
    s3.delete_object(Bucket=bucket, Key=file_name)
    logging.info(f"Deleted {file_name} from S3.")

def load_data(bucket, file_name, conn):
    cur = conn.cursor()
    from_path = f"s3://{bucket}/{file_name}"
    query = f"COPY public.zomato_data FROM '{from_path}' CREDENTIALS 'aws_access_key_id={ACCESS_KEY};aws_secret_access_key={ACCESS_SECRET}' CSV DELIMITER ',' IGNOREHEADER 1;"
    cur.execute(query)
    conn.commit()

    logging.info(f"Data from {file_name} loaded successfully into Redshift.")
    delete_csv(bucket, file_name)

def lambda_handler(event, context):
    try:
        with create_connection() as conn:
            for record in event['Records']:
                bucket_name = record['s3']['bucket']['name']
                file_name = record['s3']['object']['key']
                
                # Ensure the file is a CSV
                if file_name.endswith('.csv'):
                    load_data(bucket_name, file_name, conn)
        return {
            'statusCode': 200,
            'body': 'Data loaded into Redshift successfully.'
        }
    except Exception as e:
        logging.error(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': str(e)
        }