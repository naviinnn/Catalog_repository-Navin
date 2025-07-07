import pytest
from mysql.connector import Error as MySQLError
from exception.catalog_exception import DatabaseConnectionError
from utils.db_get_connection import get_connection


def test_get_connection_success(monkeypatch):
    class DummyConfig:
        def get(self, section, option):
            return {
                ('mysql', 'host'): 'localhost',
                ('mysql', 'user'): 'root',
                ('mysql', 'password'): 'pass',
                ('mysql', 'database'): 'test_db'
            }[(section, option)]

        def read(self, path):
            pass

    monkeypatch.setattr('utils.db_get_connection.ConfigParser', lambda: DummyConfig())
    monkeypatch.setattr('utils.db_get_connection.mysql.connector.connect', lambda **kwargs: 'mock_connection')
    monkeypatch.setattr('utils.db_get_connection.os.path.exists', lambda path: True)

    connection = get_connection()
    assert connection == 'mock_connection'


def test_get_connection_missing_config_file(monkeypatch):
    monkeypatch.setattr('utils.db_get_connection.os.path.exists', lambda path: False)

    with pytest.raises(DatabaseConnectionError):  # changed from FileNotFoundError
        get_connection()



def test_get_connection_mysql_error(monkeypatch):
    monkeypatch.setattr('utils.db_get_connection.os.path.exists', lambda path: True)

    class DummyConfig:
        def get(self, section, option):
            return 'some_value'

        def read(self, path):
            pass

    monkeypatch.setattr('utils.db_get_connection.ConfigParser', lambda: DummyConfig())
    monkeypatch.setattr('utils.db_get_connection.mysql.connector.connect', lambda **kwargs: (_ for _ in ()).throw(MySQLError("Connection failed")))

    with pytest.raises(DatabaseConnectionError) as excinfo:
        get_connection()
    assert "Connection failed" in str(excinfo.value)


def test_get_connection_unexpected_exception(monkeypatch):
    monkeypatch.setattr('utils.db_get_connection.os.path.exists', lambda path: True)

    class DummyConfig:
        def get(self, section, option):
            if option == 'host':
                raise Exception("Unexpected config error")
            return 'some_value'

        def read(self, path):
            pass

    monkeypatch.setattr('utils.db_get_connection.ConfigParser', lambda: DummyConfig())

    with pytest.raises(DatabaseConnectionError) as excinfo:
        get_connection()
    assert "Unexpected connection error" in str(excinfo.value)
