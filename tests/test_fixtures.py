from pytest_dbx import common


def test_spark(dbx_spark):
    sdf = dbx_spark.createDataFrame([[1], [2], [3]], ['a'])
    assert sdf.count() == 3


def test_dbutils(dbx_spark):
    dbutils = common.get_dbutils(dbx_spark)
    dbutils.ls('.')

    assert dbutils is not None
