import boto3
import logging
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
from botocore.exceptions import NoCredentialsError


# Setup logging
logging.basicConfig(level=logging.INFO)


class GetDate:
    def get_date(self):
        """Returns today's and yesterday's date."""
        try:
            today = datetime.today()
            yesterday = today - timedelta(days=1)
            today_str = today.strftime("%Y-%m-%d")
            yesterday_str = yesterday.strftime("%Y-%m-%d")
            return today_str, yesterday_str
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None, None


class FileHandling:
    def create_filename_by_query(self, query):
        """
        Generates a filename based on query.
        Expected format: "keyword date_until:YYYY-MM-DD date_since:YYYY-MM-DD ..."
        """
        try:
            split_list = query.split(" ")
            if len(split_list) < 4:
                logging.error("Input string does not contain enough elements.")
                return "default.csv"

            searched_keyword = split_list[0]
            date_since = split_list[3].split(":")[1]

            filename = f"{searched_keyword}_{date_since}"
            valid_filename = "".join(
                i for i in filename if i not in "\/:*?<>|")

            return f"{valid_filename}.csv"
        except IndexError:
            logging.error(
                "Error: Index out of range. Check your input string format. Expected format: 'keyword date_until:YYYY-MM-DD date_since:YYYY-MM-DD ...'")


class DataProcessor:
    def __init__(self, df):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("df should be a pandas DataFrame")
        self.df = df

    def remove_duplicates(self):
        """Removes duplicate entries."""
        self.df.drop_duplicates(
            subset=['user', 'username', 'text', 'created_at'], inplace=True)
        return self
    
    def delete_column(self, column_name):
        """Deletes a specified column."""
        if column_name in self.df.columns:
            self.df.drop(columns=column_name, inplace=True)
        else:
            raise ValueError(f"The column {column_name} does not exist in the DataFrame.")
        return self

    def convert_utc_to_ist(self, column_name):
        """Converts a specified column from UTC to IST."""
        if column_name in self.df.columns:
            self.df[column_name] = pd.to_datetime(
                self.df[column_name], errors='coerce')
            self.df[column_name] = self.df[column_name].dt.tz_convert(
                'Asia/Kolkata')
        else:
            raise ValueError(
                f"The column {column_name} does not exist in the dataframe.")
        return self


class AwsControl:
    def __init__(self, aws_key, aws_secret, region_name='ap-south-1'):
        self.aws_key = aws_key
        self.aws_secret = aws_secret
        self.region_name = region_name

    def upload_to_s3(self, df, file_name, bucket_name):
        """Uploads a file to AWS S3."""
        if file_name is None or df is None:
            logging.error("No file or data to upload.")
            return

        try:
            s3 = boto3.client('s3',
                              region_name=self.region_name,
                              aws_access_key_id=self.aws_key,
                              aws_secret_access_key=self.aws_secret)

            csv_buffer = df.to_csv(index=False).encode()
            s3.put_object(Bucket=bucket_name,
                          Key=file_name,
                          Body=csv_buffer)
            logging.info(
                f"Successfully uploaded {file_name} to {bucket_name}")
        except FileNotFoundError:
            logging.error(f"The file {file_name} was not found")
        except NoCredentialsError:
            logging.error("Credentials not available.")
        except Exception as e:
            logging.error(f"An unknown error occurred: {e}")

    def download_from_s3(self, bucket_name, file_name):
        """Downloads a file from AWS S3."""
        try:
            s3 = boto3.client('s3',
                              region_name=self.region_name,
                              aws_access_key_id=self.aws_key,
                              aws_secret_access_key=self.aws_secret)

            csv_obj = s3.get_object(Bucket=bucket_name, Key=file_name)
            body = csv_obj['Body'].read().decode('utf-8')
            df = pd.read_csv(StringIO(body))
            logging.info(
                f"Successfully downloaded {file_name} from {bucket_name}.")
            return df
        except Exception as e:
            logging.error(f"An unknown error occurred.")
            raise e
