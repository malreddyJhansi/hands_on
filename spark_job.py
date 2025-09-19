from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import udf, lower
from ssl_utils import fetch_ssl_cert
from pdf_report import generate_ssl_report
from email_utils import build_email, send_email

def run_spark_job():
    spark = SparkSession.builder.getOrCreate()

    schema = StructType([
        StructField("is_valid", BooleanType(), True),
        StructField("cert_issuer", StringType(), True),
        StructField("cert_subject", StringType(), True),
        StructField("valid_from", StringType(), True),
        StructField("valid_to", StringType(), True),
        StructField("days_to_expiry", IntegerType(), True),
        StructField("cert_status", StringType(), True),
        StructField("issue_category", StringType(), True),
        StructField("error_message", StringType(), True),
        StructField("alert_type", StringType(), True)
    ])

    fetch_ssl_cert_udf = udf(fetch_ssl_cert, schema)

    domain_df = spark.table("b_ssl_hosts_initial")
    cert_spark_df = domain_df.withColumn("cert_details", fetch_ssl_cert_udf("hostname", "port")) \
                             .select("hostname", "port", "cert_details.*")

    cert_spark_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("b_ssl_hosts_initial")

    df = spark.table("b_ssl_hosts_initial").withColumn("cert_status", lower("cert_status"))
    expired = [r.asDict() for r in df.filter(df.cert_status == "expired").collect()]
    expiring = [r.asDict() for r in df.filter(df.cert_status.like("expiring%")).collect()]
    invalid = [r.asDict() for r in df.filter(df.issue_category != "SSL_CERT_OK").collect()]

    pdf_report_path = "ssl_report.pdf"
    generate_ssl_report(expired, expiring, invalid, pdf_report_path)

    SMTP_SERVER, SMTP_PORT = "smtp.mailtrap.io", 587
    SMTP_USER, SMTP_PASS = "c08f057c9e65ac", "f337e31431c4e9"

    email_msg = build_email(
        sender="alerts@yourdomain.com",
        recipient="admin@yourdomain.com",
        subject="SSL Certificate Report",
        body="Hello Admin,\n\nPlease find attached the latest SSL Certificate Report.\n\nRegards,\nSSL Monitoring System",
        attachment_path=pdf_report_path
    )
    send_email(email_msg, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS)
