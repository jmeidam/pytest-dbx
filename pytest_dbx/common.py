from pyspark.sql import SparkSession


def get_dbutils(spark: SparkSession):
    """Used for grabbing dbutils from the scope, or returning None without raising errors

    Note that this function is also used in the dbutils fixture and referred to by name.
    Renaming or relocating this function will cause unit tests to fail.

    :param spark:
        Spark session
    """
    try:
        from pyspark.dbutils import DBUtils  # noqa

        if "dbutils" not in locals():
            utils = DBUtils(spark)
            return utils
        else:
            return locals().get("dbutils")
    except ImportError:
        return None
