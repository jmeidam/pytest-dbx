# pytest-dbx

> **Use a more maintained [`databricks-labs-pytester` plugin](https://github.com/databrickslabs/pytester) for an extensive fixture set.**

Pytest plugin for testing [dbx](https://github.com/databrickslabs/dbx)-based projects.

## Install

To use the fixtures in your project, simply add `pytest-dbx` to your project's dev-dependencies
(where you would place all your test and build dependencies).

## Fixtures

In unit tests you can use the `dbx_spark` fixture to have a spark session available as in Databricks

```python
def test_function(dbx_spark):
    sdf = dbx_spark.createDataFrame([[1], [2], [3]], ['a'])
    assert sdf.count() == 3
```

The `dbutils_fixture` and `mlflow_local` are automatically used.
