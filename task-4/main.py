import time
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

DB_URL = "mysql+mysqlconnector://user:password@localhost:3306/my_database"

# retry logic — wait for mysql to be ready
def connect(retries=10, delay=10):
    for attempt in range(1, retries + 1):
        try:
            engine = create_engine(DB_URL)
            # test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("connected to database")
            return engine
        except OperationalError:
            print(f"db not ready, attempt {attempt}/{retries}, retrying in {delay}s...")
            time.sleep(delay)
    raise RuntimeError("could not connect after max retries")

engine = connect()

# read all rows into dataframe
df = pd.read_sql("SELECT * FROM titanic", engine)

print(df.to_string())
print(f"\nrows: {len(df)}, columns: {len(df.columns)}")