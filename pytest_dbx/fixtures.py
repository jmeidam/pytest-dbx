"""
Useful components that prepare SparkSession and other relevant objects.
Also creates fixtures for use in unit tests.
"""

import os
from pathlib import Path
import shutil
import tempfile
from typing import Iterator
from unittest import mock

import mlflow
import pytest
from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession
import logging
from dataclasses import dataclass


@dataclass
class FileInfoFixture:
    """
    Mocks the DBUtils FileInfo object
    """

    path: str
    name: str
    size: int
    modificationTime: int


class DBUtilsFixture:
    """
    Used for mocking the behaviour of DBUtils inside tests.
    """

    def __init__(self):
        self.fs = self

    def cp(self, src: str, dest: str, recurse: bool = False):
        """Mock behaviour of dbutils.fs.cp"""
        copy_func = shutil.copytree if recurse else shutil.copy
        copy_func(src, dest)

    def ls(self, path: str):
        """Mock behaviour of dbutils.fs.ls"""
        _paths = Path(path).glob("*")
        _objects = [
            FileInfoFixture(str(p.absolute()), p.name, p.stat().st_size, int(p.stat().st_mtime)) for p in _paths
        ]
        return _objects

    def mkdirs(self, path: str):
        """Mock behaviour of dbutils.fs.mkdirs"""
        Path(path).mkdir(parents=True, exist_ok=True)

    def mv(self, src: str, dest: str, recurse: bool = False):
        """Mock behaviour of dbutils.fs.mv"""
        copy_func = shutil.copytree if recurse else shutil.copy
        shutil.move(src, dest, copy_function=copy_func)

    def put(self, path: str, content: str, overwrite: bool = False):
        """Mock behaviour of dbutils.fs.put"""
        _f = Path(path)

        if _f.exists() and not overwrite:
            raise FileExistsError("File already exists")

        _f.write_text(content, encoding="utf-8")

    def rm(self, path: str, recurse: bool = False):
        """Mock behaviour of dbutils.fs.rm"""
        deletion_func = shutil.rmtree if recurse else os.remove
        deletion_func(path)


@pytest.fixture(scope="session")
def spark() -> SparkSession:
    """
    This fixture provides a preconfigured SparkSession with Hive and Delta support.
    After the test session, the temporary warehouse directory is deleted.

    :returns: SparkSession
    """
    logging.info("Configuring Spark session for testing environment")
    warehouse_dir = tempfile.TemporaryDirectory().name
    _builder = (
        SparkSession.builder.master("local[1]")
        .config("spark.hive.metastore.warehouse.dir", Path(warehouse_dir).as_uri())
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    )
    spark: SparkSession = configure_spark_with_delta_pip(_builder).getOrCreate()
    logging.info("Spark session configured")
    yield spark
    logging.info("Shutting down Spark session")
    spark.stop()
    if Path(warehouse_dir).exists():
        shutil.rmtree(warehouse_dir)


@pytest.fixture(scope="session", autouse=True)
def mlflow_local():
    """
    This fixture provides a local instance of mlflow with support for tracking and registry functions.
    After the test session:

        * temporary storage for tracking and registry is deleted
        * Active run will be automatically stopped to avoid verbose errors
    """
    logging.info("Configuring local MLflow instance")
    tracking_uri = tempfile.TemporaryDirectory().name
    registry_uri = f"sqlite:///{tempfile.TemporaryDirectory().name}"

    mlflow.set_tracking_uri(Path(tracking_uri).as_uri())
    mlflow.set_registry_uri(registry_uri)
    logging.info("MLflow instance configured")
    yield None

    mlflow.end_run()

    if Path(tracking_uri).exists():
        shutil.rmtree(tracking_uri)

    if Path(registry_uri).exists():
        Path(registry_uri).unlink()
    logging.info("Test session finished, unrolling the MLflow instance")


@pytest.fixture(scope="session", autouse=True)
def dbutils_fixture() -> Iterator[None]:
    """
    This fixture patches the `get_dbutils` function.
    Please note that patch is applied on a string name of the function.
    If you change the name or relocate it, patching will fail.
    """
    logging.info("Patching the DBUtils object")
    with mock.patch("pytest_dbx.common.get_dbutils", lambda _: DBUtilsFixture()):
        yield
    logging.info("Test session finished, patching completed")
