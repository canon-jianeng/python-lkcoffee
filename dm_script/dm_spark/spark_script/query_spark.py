
from pyspark import sql
from pyspark import SparkConf, SparkContext


spark = sql.SparkSession.builder.appName('kudu_read').getOrCreate()

df = spark.read.format("org.apache.kudu.spark.kudu") \
                .option("kudu.table", "rtdw_dataplatform.dm_shop_spec_order_data") \
                .option('kudu.master', "10.218.18.85:7051,10.218.18.77:7051,10.218.23.112:7051") \
                .load()
print(df)
