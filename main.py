import os
os.system("pip install -r requirements.txt")

from spark_job import run_spark_job

if __name__ == "__main__":
    run_spark_job()
