from pytest_dbx import common


def test_spark(spark):
    sdf = spark.createDataFrame([[1], [2], [3]], ['a'])
    assert sdf.count() == 3


def test_dbutils(spark):
    dbutils = common.get_dbutils(spark)
    dbutils.ls('.')

    assert dbutils is not None
