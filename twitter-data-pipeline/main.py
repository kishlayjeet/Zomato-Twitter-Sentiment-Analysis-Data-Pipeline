import logging
import config
from scraper import TwitterScraper
from analyzer import SentimentAnalyzer
from script import GetDate, AwsControl, FileHandling, DataProcessor

# Setup logging
logging.basicConfig(level=logging.DEBUG)


class TwitterETL:

    def __init__(self):
        self.auth_token = config.auth_token
        self.aws_key = config.aws_key
        self.aws_secret = config.aws_secret
        self.raw_data_bucket_name = '<your_raw_data_bucket_name>' # eg:- "kishlay-zomato-raw-data-bucket"
        self.processed_data_bucket_name = '<your_processed_data_bucket_name>' # eg:- "kishlay-zomato-processed-data-bucket"
        self.aws = AwsControl(self.aws_key, self.aws_secret)

        try:
            self.query = self.construct_query()
            self.raw_file_name = self.construct_filename(self.query)
        except Exception as e:
            logging.error(f"An error occurred during setup: {e}")
            raise

    def construct_query(self):
        gd = GetDate()
        today, yesterday = gd.get_date()
        if today is None or yesterday is None:
            raise ValueError("Error when getting date data.")
        query = f'zomato lang:en until:{today} since:{yesterday} -filter:replies'
        logging.info(f"Query constructed: {query}")
        return query

    def construct_filename(self, query):
        fHandle = FileHandling()
        filename = fHandle.create_filename_by_query(query)
        logging.info(f"Filename constructed: {filename}")
        return filename

    def twitter_data_extraction(self):
        try:
            raw_df = self.scrape_data()
            self.upload_data(raw_df)
        except Exception as e:
            logging.error(f"An error occurred during the extraction: {e}")
            raise

    def scrape_data(self):
        scraper = TwitterScraper(self.query, self.auth_token)
        scraper.login_and_search()
        raw_df = scraper.scroll_and_scrap()
        logging.info("Data scraped successfully.")
        return raw_df

    def upload_data(self, raw_df):
        if raw_df is not None:
            self.aws.upload_to_s3(
                raw_df, self.raw_file_name, self.raw_data_bucket_name)
            logging.info("Data uploaded to S3 successfully.")

    def twitter_data_transformation(self):
        try:
            raw_df = self.download_data()
            processed_df = self.process_data(raw_df)
            self.upload_processed_data(processed_df)
        except Exception as e:
            logging.error(
                f"An error occurred during transformation process: {e}")
            raise

    def download_data(self):
        raw_df = self.aws.download_from_s3(
            self.raw_data_bucket_name, self.raw_file_name)
        logging.info("Data downloaded from S3 successfully.")
        return raw_df

    def process_data(self, raw_df):
        if raw_df is not None:
            process = DataProcessor(raw_df)
            process.remove_duplicates()
            # process.convert_utc_to_ist('created_at') 
            analyzer = SentimentAnalyzer(process.df)
            processed_df = analyzer.analyze()
            process.delete_column('text')
            process.delete_column('scores')
            logging.info("Data processed successfully.")
            return processed_df

    def upload_processed_data(self, processed_df):
        analyzed_file_name = f"analyzed_{self.raw_file_name}"
        self.aws.upload_to_s3(processed_df, analyzed_file_name,
                              self.processed_data_bucket_name)
        logging.info("Processed data uploaded to S3 successfully.")