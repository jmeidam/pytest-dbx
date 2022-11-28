# pytest-dbx

Pytest plugin for testing dbx (https://github.com/databrickslabs/dbx) projects.

## Fixtures

In unit tests you can use the spark fixture to have spark session available as in Databricks

```python
def test_function(spark):
    sdf = spark.createDataFrame([[1], [2], [3]], ['a'])
    assert sdf.count() == 3
```

The `dbutils_fixture` and `mlflow_local` are automatically used.
