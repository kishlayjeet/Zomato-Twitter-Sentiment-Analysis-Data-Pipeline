# 🍔 Zomato's Twitter Sentiment Analysis Data Pipeline

This project provides valuable customer sentiment insights for Zomato, a popular food delivery company, by tracking and analyzing tweets related to their brand and services. The data pipeline scrubs Twitter for relevant data, processes and analyzes it, and then stores the results for visualization. This helps Zomato keep a close eye on their customer satisfaction levels and continuously refine their services.

## 💡 Overview

Due to recent restrictions imposed on the Twitter API, we've adopted a scraping strategy using Selenium. The pipeline is scheduled to scrape tweets daily, specifically targeting those mentioning Zomato. These tweets are then processed, analyzed, and stored in AWS Redshift, followed by a sentiment analysis to evaluate customer sentiments. The final output is a dashboard reflecting customer sentiment trends over the preceding seven weeks.

🔮 Sneak Peek at Our Architectural Blueprint!

![Architecture](https://imgur.com/A5jBo0p.png)

## 🛠️ Pipeline Architecture

1. **Tweet Scraping:** The journey begins with Selenium, a powerful browser automation tool, which is set to scrape tweets about Zomato.

2. **Raw Data Storage:** Once we've collected our tweets, we use `boto3`, a Python library for AWS, to upload this raw data to an AWS S3 bucket. S3 is a scalable storage solution provided by Amazon Web Services.

3. **Data Transformation:** Next, we pull the raw data back down from S3 using `boto3`. We use Python's powerful data manipulation library, Pandas, to clean the data and remove duplicates.

4. **Sentiment Analysis:** After the data has been cleaned, we use the `vader_lexicon` feature of NLTK (Natural Language Toolkit) to perform sentiment analysis. This allows us to classify the tweets into positive, negative, or neutral categories based on their content.

5. **Storing Processed Data:** Once the sentiment analysis is complete, we upload the processed data back to S3 using `boto3`. From there, AWS Lambda transfers the data to the Redshift warehouse using `psycopg2`, ensuring it's ready for further analysis or visualization.

6. **Data Visualization:** Finally, we use Power BI, a business analytics tool, to create a dashboard from the processed data. This dashboard provides an overview of customer sentiment trends regarding Zomato's services over a specified period.

## 🛠️ Tools and Environment Setup

### Key tools and technologies utilized:

- **Data Scraping:** `Selenium`
- **Raw Data Storage:** `AWS S3`
- **Data Transformation & Cleaning:** `Pandas`
- **Sentiment Analysis:** `NLTK's Vader Lexicon`
- **Serverless Data Processing:** `AWS Lambda`
- **Processed Data Warehousing:** `AWS Redshift`
- **Data Visualization:** `Power BI`

### Hardware Used

I utilized a local machine with the following specifications:

```bash
  Ubuntu OS
  4 vCores, 4 GiB Memory
  Storage: 32 GiB
```

### Prerequisites

- A Twitter account (for scraping tweets).
- An AWS account with a configured S3 bucket, Lambda, and Redshift.
- Chrome browser (as used by Selenium).
- Python 3 environment.
- Apache Airflow for orchestrating workflows.
- Essential Python libraries: Selenium, NLTK, pandas, boto3.

## 🚀 Getting Started

1. **Repository Setup:** Clone the project repository:

```bash
git clone https://github.com/kishlayjeet/Zomato-Twitter-Sentiment-Analysis-Data-Pipeline.git
```

2. **Python Package Installation:** Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. **Configuration Setup:** Modify the config.py file to input your Twitter and AWS credentials:

```python
# AWS
aws_key = "<your_aws_access_key>"
aws_secret = "<your_aws_access_secret>"

# Twitter
auth_token = "<your_twitter_auth_token>"
```

**Note:** _You can locate the `auth_token` in your browser cookies after logging into your Twitter account._

4. **Airflow Configuration:** Adjust the `airflow.cfg` file to reference your script directory and set the S3 bucket name.

![AWS S3 Buckets](https://imgur.com/tX5nQWG.png)

5. **IAM Role:** Set up an IAM role for the Lambda function to provide:

- Permissions for S3's GetObject and DeleteObject for your specific bucket.
- Full Redshift access or specific access based on security needs.

6. **Lambda Configuration:** Assign the created role to your Lambda function.

7. **S3 Event Trigger:** Within your S3 bucket's properties, set up an event to trigger the Lambda function upon a PUT (file upload) action.

8. **Permissions:** Confirm that the Lambda function has the required permissions for S3 and Redshift. Ensure that your Redshift cluster's security group permits AWS Lambda connections.

9. **Additional Lambda Setup:** For the Lambda deployment package, include the `psycopg2` library, and consider the psycopg2-binary package for convenience.

**Note:** _For security practices while using environment variables is suitable for demonstrations, in a production setting, leverage AWS Secrets Manager or IAM roles for increased security._

## 🚀 Running the Pipeline

1. **Starting Airflow:** Launch the Airflow server:

```bash
airflow standalone
```

![Airflow Server](https://imgur.com/T9isKxa.png)

**Note:** _Ensure that your Redshift cluster is up and running and that you have created the required table._

```bash
# Redshift table generation query
CREATE TABLE IF NOT EXISTS zomato_data(
    "USER" VARCHAR(50),
    "USERNAME" VARCHAR(50),
    "CREATED_AT" TIMESTAMP,
    "LIKE_COUNT" BIGINT,
    "REPLY_COUNT" BIGINT,
    "RETWEET_COUNT" BIGINT,
    "VIEWS_COUNT" BIGINT,
    "COMPOUND" DECIMAL(10,5),
    "SENTIMENT" VARCHAR(15)
);
```

2. **Accessing Airflow:** Navigate to `http://localhost:8080` in your browser.

3. **Activating DAG:** Enable the `twitter_dag` within the Airflow UI.

4. Pipeline Execution: As per the scheduled interval, the pipeline will scrape Twitter, process the data, and store the finalized output in your Redshift warehouse.

![Process Complete](https://imgur.com/dGpKjYM.png)

## 🎨 Visualization

![Dashboard](https://imgur.com/fIa3odo.png)

## ✨ Key Points to Remember

- The pipeline is programmed for a Zomato-centric Twitter search. If you wish to collect data on a different subject, you can modify the `construct_query` function in `/twitter-data-pipeline/main.py`.
- The pipeline won't automatically save data to an S3 bucket. To store data in your chosen S3 buckets, update the `raw_data_bucket_name` and `processed_data_bucket_name` variables in `/twitter-data-pipeline/main.py` with your bucket details.
- Currently, the pipeline is set to run on daily basis. You can adjust the `schedule_interval` in the DAG definition to suit your needs, whether that means running the pipeline more or less frequently.

## 🩹 Error Handling and Troubleshooting

- Airflow provides a UI for monitoring the status of tasks and DAG runs. In case of task failure, the UI displays the error message and the traceback, which can be used to troubleshoot the issue.
- Airflow also provides the option to retry failed tasks a certain number of times before marking them as failures. This can be configured in the DAG definition.
- In case of issues with the S3 bucket, such as access denied or invalid credentials, check if the `config.py` file contains the correct AWS access key and secret key, and that the S3 bucket name is correctly configured in the `main.py` file.
- Logs for the pipeline can also be found in the `logs/` directory. These logs can be useful in troubleshooting issues with the pipeline.

## 🌱 Future Enhancements

There's always room for improvement! Here are a few areas that could be expanded upon in the future:

- Implement more advanced sentiment analysis algorithms for more accurate sentiment determination.
- Integrate with other social media platforms for more comprehensive customer feedback.
- Develop a notification system to alert when there are significant changes in sentiment trend.

## 🔐 Disclaimer

This project is intended for educational purposes. Always ensure you comply with Twitter's and Zomato's terms of service, as well as all relevant laws and regulations. Remember to ensure data privacy, security, and compliance in any production implementation.

## 💌 Author

This data pipeline is brought to you by [Kishlay](https://github.com/kishlayjeet). If you have questions, suggestions, or feedback, please don't hesitate to reach out at contact.kishlayjeet@gmail.com.
