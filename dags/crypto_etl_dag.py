import logging
from datetime import datetime, timedelta
import os
import sys
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path so we can import src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.sensors.sql import SqlSensor

from src.etl.extract import extract_all_coins
from src.transform.clean import clean_data
from src.transform.kpis import calculate_kpis
from src.load.load_db import load_data_to_supabase
from src.db.connection import get_engine

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'crypto_etl_daily',
    default_args=default_args,
    description='Daily ETL pipeline for Cryptocurrency Market Data',
    schedule_interval='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['crypto', 'etl', 'supabase'],
) as dag:

    def extract_cryptos(**context):
        """
        Extracts data from CoinGecko API and saves to temporary storage.
        """
        logger.info("Starting extraction task...")
        df = extract_all_coins()
        if df.empty:
            logger.error("No data extracted from CoinGecko.")
            raise ValueError("No data extracted from CoinGecko.")
        
        # Save to XCom or file (Using file for DataFrame is better)
        output_path = '/tmp/crypto_raw.pkl'
        df.to_pickle(output_path)
        logger.info(f"Extraction complete. Saved {len(df)} rows to {output_path}")
        return output_path

    def transform_prices_and_metrics(**context):
        """
        Reads raw data, cleans it, calculates KPIs, and saves processed data.
        """
        logger.info("Starting transformation task...")
        input_path = context['ti'].xcom_pull(task_ids='extract_cryptos')
        logger.info(f"Reading raw data from {input_path}...")
        raw_df = pd.read_pickle(input_path)
        
        logger.info("Cleaning data...")
        clean_df = clean_data(raw_df)
        
        logger.info("Calculating KPIs...")
        final_df = calculate_kpis(clean_df)
        
        output_path = '/tmp/crypto_processed.pkl'
        final_df.to_pickle(output_path)
        logger.info(f"Transformation complete. Saved {len(final_df)} rows to {output_path}")
        return output_path

    def load_to_supabase_task(**context):
        """
        Loads processed data into Supabase using incremental logic.
        """
        logger.info("Starting load task...")
        input_path = context['ti'].xcom_pull(task_ids='transform_prices_and_metrics')
        logger.info(f"Reading processed data from {input_path}...")
        df = pd.read_pickle(input_path)
        
        logger.info("Loading to Supabase (Incremental Mode)...")
        # We use our existing load function
        try:
            load_data_to_supabase(df, incremental=True)
            logger.info("Load complete.")
        except Exception as e:
            logger.error(f"Load failed: {e}")
            raise e

    def check_data_quality(**context):
        """
        Validates data in Supabase with multiple quality checks.
        """
        try:
            # Try Airflow Connection first
            pg_hook = PostgresHook(postgres_conn_id='supabase_conn')
            conn = pg_hook.get_conn()
            cursor = conn.cursor()
        except:
            logger.warning("Airflow Connection 'supabase_conn' not found. Using local config.")
            engine = get_engine()
            conn = engine.raw_connection()
            cursor = conn.cursor()

        logger.info("--- Running Data Quality Checks ---")

        # Check 1: Count rows
        cursor.execute("SELECT COUNT(*) FROM cryptocurrency_prices")
        count = cursor.fetchone()[0]
        logger.info(f"Check 1 - Total rows: {count}")
        if count == 0:
            logger.error("DQ Failed: Table 'cryptocurrency_prices' is empty.")
            raise ValueError("DQ Failed: Table 'cryptocurrency_prices' is empty.")
            
        # Check 2: Freshness (Data within last 48 hours)
        cursor.execute("SELECT MAX(price_timestamp) FROM cryptocurrency_prices")
        max_date = cursor.fetchone()[0]
        logger.info(f"Check 2 - Latest date in DB: {max_date}")
        
        if max_date:
            # Convert to datetime if it's a string or date object
            if isinstance(max_date, str):
                max_date = datetime.strptime(max_date, '%Y-%m-%d %H:%M:%S') # Adjust format as needed
            elif hasattr(max_date, 'to_pydatetime'): # Pandas timestamp
                max_date = max_date.to_pydatetime()
            # If it's datetime.date, convert to datetime
            if type(max_date).__name__ == 'date':
                max_date = datetime.combine(max_date, datetime.min.time())

            days_diff = (datetime.now() - max_date).days
            if days_diff > 2:
                logger.error(f"DQ Failed: Data is too old. Latest date: {max_date}, Current: {datetime.now()}")
                raise ValueError(f"DQ Failed: Data is {days_diff} days old (Threshold: 2 days).")
        
        # Check 3: Null Values in Critical Columns
        cursor.execute("""
            SELECT COUNT(*) 
            FROM cryptocurrency_prices 
            WHERE price IS NULL OR volume IS NULL OR market_cap IS NULL
        """)
        null_count = cursor.fetchone()[0]
        logger.info(f"Check 3 - Null critical values: {null_count}")
        if null_count > 0:
             logger.error("DQ Failed: Found null values in critical columns (price/volume/market_cap).")
             raise ValueError(f"DQ Failed: Found {null_count} rows with nulls in critical columns.")
        
        # Check 4: Duplicates (Coin + Date)
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT coin, price_timestamp, COUNT(*) 
                FROM cryptocurrency_prices 
                GROUP BY coin, price_timestamp 
                HAVING COUNT(*) > 1
            ) sub
        """)
        dup_count = cursor.fetchone()[0]
        logger.info(f"Check 4 - Duplicate (Coin+Date) groups: {dup_count}")
        if dup_count > 0:
            logger.error(f"DQ Failed: Found {dup_count} duplicate groups in 'cryptocurrency_prices'.")
            raise ValueError(f"DQ Failed: Found {dup_count} duplicate groups in 'cryptocurrency_prices'.")

        # Check 5: Symbol Consistency
        cursor.execute("SELECT COUNT(DISTINCT coin) FROM cryptocurrency_prices")
        unique_coins = cursor.fetchone()[0]
        logger.info(f"Check 5 - Unique Coins Tracked: {unique_coins}")
        if unique_coins < 5:
            logger.warning("WARNING: Less than 5 coins tracked. Is extraction complete?")

        logger.info("--- Data Quality Checks Completed Successfully ---")
        
        cursor.close()
        conn.close()

    # Define Tasks
    t1 = PythonOperator(
        task_id='extract_cryptos',
        python_callable=extract_cryptos,
        provide_context=True,
    )

    t2 = PythonOperator(
        task_id='transform_prices_and_metrics',
        python_callable=transform_prices_and_metrics,
        provide_context=True,
    )

    t3 = PythonOperator(
        task_id='load_to_supabase',
        python_callable=load_to_supabase_task,
        provide_context=True,
    )

    t4 = PythonOperator(
        task_id='data_quality_checks',
        python_callable=check_data_quality,
        provide_context=True,
    )

    # Define Dependencies
    t1 >> t2 >> t3 >> t4
