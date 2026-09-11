"""
Apache Airflow Data Pipeline DAG
Module 16: Data Engineering Basics - ETL Pipeline Orchestration
Covers: Data ingestion, preprocessing, feature engineering, validation
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default DAG arguments
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['data-team@ticketing.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2)
}

# Define DAG
dag = DAG(
    dag_id='movie_ticketing_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for movie ticketing data',
    schedule_interval='@daily',
    catchup=False,
    tags=['etl', 'data-engineering', 'movie-ticketing']
)

# ==================== Data Ingestion Tasks ====================

def ingest_transaction_data(**context):
    """
    Ingest transaction data from database
    
    Covers: Data ingestion, connection management
    """
    logger.info("Starting transaction data ingestion...")
    
    try:
        # In production: Connect to database
        # from sqlalchemy import create_engine
        # engine = create_engine('postgresql://user:password@host:5432/db')
        # df = pd.read_sql('SELECT * FROM transactions WHERE date = current_date', engine)
        
        # Mock data for demonstration
        n_records = 1000
        data = pd.DataFrame({
            'transaction_id': range(1, n_records + 1),
            'user_id': np.random.randint(1, 500, n_records),
            'movie_id': np.random.randint(1, 100, n_records),
            'amount': np.random.lognormal(4, 1.5, n_records),
            'timestamp': pd.date_range('2024-01-01', periods=n_records, freq='h'),
            'device_type': np.random.choice(['web', 'mobile', 'app'], n_records),
            'location': np.random.choice(['US', 'EU', 'Asia'], n_records)
        })
        
        # Save to CSV for downstream tasks
        data.to_csv('/tmp/raw_transactions.csv', index=False)
        
        logger.info(f"Ingested {len(data)} transaction records")
        
        # Push metadata to XCom for downstream tasks
        context['task_instance'].xcom_push(key='record_count', value=len(data))
        context['task_instance'].xcom_push(key='ingestion_timestamp', value=datetime.now().isoformat())
        
        return f"Successfully ingested {len(data)} records"
        
    except Exception as e:
        logger.error(f"Transaction data ingestion failed: {str(e)}")
        raise

def ingest_user_data(**context):
    """
    Ingest user profile data
    """
    logger.info("Starting user data ingestion...")
    
    try:
        # Mock user data
        user_data = pd.DataFrame({
            'user_id': range(1, 501),
            'email': [f'user{i}@example.com' for i in range(1, 501)],
            'country': np.random.choice(['US', 'UK', 'CA', 'AU'], 500),
            'signup_date': pd.date_range('2023-01-01', periods=500, freq='D'),
            'subscription_type': np.random.choice(['free', 'premium'], 500)
        })
        
        user_data.to_csv('/tmp/raw_users.csv', index=False)
        
        logger.info(f"Ingested {len(user_data)} user records")
        context['task_instance'].xcom_push(key='user_count', value=len(user_data))
        
        return f"Successfully ingested {len(user_data)} user records"
        
    except Exception as e:
        logger.error(f"User data ingestion failed: {str(e)}")
        raise

def ingest_movie_data(**context):
    """
    Ingest movie catalog data
    """
    logger.info("Starting movie data ingestion...")
    
    try:
        genres = ['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Thriller']
        movie_data = pd.DataFrame({
            'movie_id': range(1, 101),
            'title': [f'Movie {i}' for i in range(1, 101)],
            'genre': np.random.choice(genres, 100),
            'release_date': pd.date_range('2023-01-01', periods=100, freq='D'),
            'rating': np.random.uniform(5, 10, 100),
            'budget': np.random.lognormal(15, 2, 100)
        })
        
        movie_data.to_csv('/tmp/raw_movies.csv', index=False)
        
        logger.info(f"Ingested {len(movie_data)} movie records")
        context['task_instance'].xcom_push(key='movie_count', value=len(movie_data))
        
        return f"Successfully ingested {len(movie_data)} movie records"
        
    except Exception as e:
        logger.error(f"Movie data ingestion failed: {str(e)}")
        raise

# ==================== Data Preprocessing Tasks ====================

def preprocess_transactions(**context):
    """
    Clean and preprocess transaction data
    
    Covers: Data cleaning, validation, outlier detection
    """
    logger.info("Preprocessing transaction data...")
    
    try:
        df = pd.read_csv('/tmp/raw_transactions.csv')
        
        logger.info(f"Original records: {len(df)}")
        
        # Remove duplicates
        df = df.drop_duplicates()
        logger.info(f"After removing duplicates: {len(df)}")
        
        # Remove nulls
        df = df.dropna()
        logger.info(f"After removing nulls: {len(df)}")
        
        # Outlier detection (amount > 3 std deviations)
        mean_amount = df['amount'].mean()
        std_amount = df['amount'].std()
        outliers = df[df['amount'] > mean_amount + 3 * std_amount]
        
        if len(outliers) > 0:
            logger.warning(f"Found {len(outliers)} outlier transactions")
            # Flag them but don't remove (important for fraud detection)
            df['is_outlier'] = (df['amount'] > mean_amount + 3 * std_amount).astype(int)
        else:
            df['is_outlier'] = 0
        
        # Type conversions
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['amount'] = df['amount'].astype(float)
        
        df.to_csv('/tmp/preprocessed_transactions.csv', index=False)
        
        logger.info(f"Preprocessing complete. Final records: {len(df)}")
        context['task_instance'].xcom_push(key='processed_transactions', value=len(df))
        
        return "Transaction preprocessing complete"
        
    except Exception as e:
        logger.error(f"Transaction preprocessing failed: {str(e)}")
        raise

def preprocess_users(**context):
    """
    Clean and preprocess user data
    """
    logger.info("Preprocessing user data...")
    
    try:
        df = pd.read_csv('/tmp/raw_users.csv')
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Remove nulls
        df = df.dropna()
        
        # Type conversions
        df['signup_date'] = pd.to_datetime(df['signup_date'])
        
        df.to_csv('/tmp/preprocessed_users.csv', index=False)
        
        logger.info(f"User preprocessing complete. Records: {len(df)}")
        context['task_instance'].xcom_push(key='processed_users', value=len(df))
        
        return "User preprocessing complete"
        
    except Exception as e:
        logger.error(f"User preprocessing failed: {str(e)}")
        raise

# ==================== Feature Engineering Tasks ====================

def create_transaction_features(**context):
    """
    Create features from transaction data
    
    Covers: Feature engineering, feature selection
    """
    logger.info("Creating transaction features...")
    
    try:
        df = pd.read_csv('/tmp/preprocessed_transactions.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Temporal features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Amount features
        df['amount_log'] = np.log1p(df['amount'])
        df['amount_zscore'] = np.abs((df['amount'] - df['amount'].mean()) / df['amount'].std())
        
        # User features
        user_stats = df.groupby('user_id')['amount'].agg(['mean', 'std', 'max', 'count']).reset_index()
        user_stats.columns = ['user_id', 'user_avg_amount', 'user_std_amount', 'user_max_amount', 'user_transaction_count']
        
        df = df.merge(user_stats, on='user_id', how='left')
        
        # Relative amount
        df['amount_vs_user_avg'] = df['amount'] / (df['user_avg_amount'] + 1)
        
        df.to_csv('/tmp/engineered_features.csv', index=False)
        
        logger.info(f"Created {len(df.columns)} features")
        logger.info(f"Feature columns: {list(df.columns)}")
        
        context['task_instance'].xcom_push(key='feature_count', value=len(df.columns))
        
        return "Feature engineering complete"
        
    except Exception as e:
        logger.error(f"Feature engineering failed: {str(e)}")
        raise

def create_user_features(**context):
    """
    Create features from user data
    """
    logger.info("Creating user features...")
    
    try:
        df = pd.read_csv('/tmp/preprocessed_users.csv')
        
        # Account age
        df['signup_date'] = pd.to_datetime(df['signup_date'])
        df['account_age_days'] = (pd.Timestamp.now() - df['signup_date']).dt.days
        
        # Subscription encoding
        df['is_premium'] = (df['subscription_type'] == 'premium').astype(int)
        
        df.to_csv('/tmp/engineered_user_features.csv', index=False)
        
        logger.info(f"User feature engineering complete")
        
        return "User feature engineering complete"
        
    except Exception as e:
        logger.error(f"User feature engineering failed: {str(e)}")
        raise

# ==================== Data Quality Checks ====================

def validate_data_quality(**context):
    """
    Validate data quality
    
    Covers: Data validation, quality assurance
    """
    logger.info("Validating data quality...")
    
    try:
        df = pd.read_csv('/tmp/engineered_features.csv')
        
        validation_results = {
            'total_records': len(df),
            'null_counts': df.isnull().sum().to_dict(),
            'duplicate_count': df.duplicated().sum(),
            'amount_stats': {
                'min': float(df['amount'].min()),
                'max': float(df['amount'].max()),
                'mean': float(df['amount'].mean()),
                'std': float(df['amount'].std())
            }
        }
        
        # Check for issues
        issues = []
        
        if df.isnull().sum().sum() > 0:
            issues.append(f"Found {df.isnull().sum().sum()} null values")
        
        if df['amount'].min() < 0:
            issues.append(f"Found negative amounts: {len(df[df['amount'] < 0])}")
        
        if len(issues) > 0:
            logger.warning(f"Data quality issues found: {issues}")
        else:
            logger.info("Data quality checks passed")
        
        validation_results['issues'] = issues
        validation_results['status'] = 'PASS' if len(issues) == 0 else 'WARN'
        
        context['task_instance'].xcom_push(key='validation_results', value=validation_results)
        
        return f"Data validation complete. Status: {validation_results['status']}"
        
    except Exception as e:
        logger.error(f"Data validation failed: {str(e)}")
        raise

# ==================== Load to Storage ====================

def load_to_warehouse(**context):
    """
    Load processed data to data warehouse
    
    Covers: Data loading, storage management
    """
    logger.info("Loading data to warehouse...")
    
    try:
        df = pd.read_csv('/tmp/engineered_features.csv')
        
        # In production: Load to data warehouse
        # engine = create_engine('postgresql://user:password@host:5432/warehouse')
        # df.to_sql('transactions_processed', engine, if_exists='append', index=False)
        
        # For demo: Save to persistent location
        df.to_parquet('/tmp/warehouse/transactions_processed.parquet')
        
        logger.info(f"Loaded {len(df)} records to warehouse")
        
        return f"Successfully loaded {len(df)} records to warehouse"
        
    except Exception as e:
        logger.error(f"Loading to warehouse failed: {str(e)}")
        raise

# ==================== Define DAG Tasks ====================

# Ingestion tasks
ingest_transactions = PythonOperator(
    task_id='ingest_transactions',
    python_callable=ingest_transaction_data,
    dag=dag
)

ingest_users = PythonOperator(
    task_id='ingest_users',
    python_callable=ingest_user_data,
    dag=dag
)

ingest_movies = PythonOperator(
    task_id='ingest_movies',
    python_callable=ingest_movie_data,
    dag=dag
)

# Preprocessing tasks
preprocess_trans = PythonOperator(
    task_id='preprocess_transactions',
    python_callable=preprocess_transactions,
    dag=dag
)

preprocess_usr = PythonOperator(
    task_id='preprocess_users',
    python_callable=preprocess_users,
    dag=dag
)

# Feature engineering tasks
engineer_features = PythonOperator(
    task_id='create_transaction_features',
    python_callable=create_transaction_features,
    dag=dag
)

engineer_user_features = PythonOperator(
    task_id='create_user_features',
    python_callable=create_user_features,
    dag=dag
)

# Validation task
validate = PythonOperator(
    task_id='validate_data_quality',
    python_callable=validate_data_quality,
    dag=dag
)

# Loading task
load = PythonOperator(
    task_id='load_to_warehouse',
    python_callable=load_to_warehouse,
    dag=dag
)

# ==================== Define DAG Dependencies ====================

[ingest_transactions, ingest_users, ingest_movies] >> [preprocess_trans, preprocess_usr]
preprocess_trans >> engineer_features >> validate >> load
preprocess_usr >> engineer_user_features

# ==================== Summary Task ====================

def print_summary(**context):
    """Print pipeline summary"""
    logger.info("=" * 80)
    logger.info("ETL PIPELINE EXECUTION SUMMARY")
    logger.info("=" * 80)
    
    ti = context['task_instance']
    
    # Pull results from previous tasks
    processed_transactions = ti.xcom_pull(
        task_ids='preprocess_transactions',
        key='processed_transactions'
    )
    
    logger.info(f"Processed transactions: {processed_transactions}")
    logger.info(f"Pipeline execution completed at {datetime.now()}")
    
    logger.info("=" * 80)

summary = PythonOperator(
    task_id='print_summary',
    python_callable=print_summary,
    dag=dag
)

load >> summary

if __name__ == "__main__":
    logger.info("Airflow ETL DAG defined successfully")
