import os
os.system("pip install -r requirements.txt")

from spark_job import run_spark_job

if _name_ == "_main_":
    run_spark_job()
