import pytest
from unittest.mock import patch, MagicMock
from service.catalog_service import CatalogService
from dto.catalog import Catalog
from exception.catalog_exception import DataNotFoundError

@pytest.fixture
def catalog_service():
    return CatalogService()

@pytest.fixture
def sample_catalog():
    return Catalog(
        name="Test Catalog",
        description="Test Description",
        start_date="2025-01-01",
        end_date="2025-12-31",
        status="active"
    )

@patch('service.catalog_service.get_connection')
def test_create_catalog(mock_conn, catalog_service, sample_catalog):
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 42
    mock_conn.return_value.cursor.return_value = mock_cursor

    result = catalog_service.create_catalog(sample_catalog, user_id=1)

    assert result == 42
    mock_cursor.execute.assert_called_once()

@patch('service.catalog_service.get_connection')
def test_get_catalog_by_id_success(mock_conn, catalog_service):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "catalog_id": 1,
        "catalog_name": "Test",
        "catalog_description": "Desc",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "status": "active",
        "user_id": 1
    }
    mock_conn.return_value.cursor.return_value = mock_cursor

    result = catalog_service.get_catalog_by_id(1)

    assert result["catalog_id"] == 1
    mock_cursor.execute.assert_called_once()

@patch('service.catalog_service.get_connection')
def test_get_catalog_by_id_not_found(mock_conn, catalog_service):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.return_value.cursor.return_value = mock_cursor

    with pytest.raises(DataNotFoundError):
        catalog_service.get_catalog_by_id(99)

@patch('service.catalog_service.get_connection')
def test_get_all_catalog(mock_conn, catalog_service):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"catalog_id": 1, "catalog_name": "Test 1"},
        {"catalog_id": 2, "catalog_name": "Test 2"},
    ]
    mock_conn.return_value.cursor.return_value = mock_cursor

    result = catalog_service.get_all_catalog(search_term="Test", status_filter="active", page=1, per_page=10)

    assert len(result) == 2
    mock_cursor.execute.assert_called_once()

@patch('service.catalog_service.get_connection')
def test_count_catalogs(mock_conn, catalog_service):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {'COUNT(*)': 5}
    mock_conn.return_value.cursor.return_value = mock_cursor

    count = catalog_service.count_catalogs(search_term="Test", status_filter="active")

    assert count == 5
    mock_cursor.execute.assert_called_once()

@patch('service.catalog_service.get_connection')
def test_update_catalog_by_id_success(mock_conn, catalog_service, sample_catalog):
    mock_cursor = MagicMock()
    # Simulate existing catalog for get_catalog_by_id
    mock_cursor.fetchone.return_value = {"catalog_id": 1}
    # Simulate successful update (1 row affected)
    mock_cursor.execute.side_effect = [None, None]
    mock_cursor.rowcount = 1
    mock_conn.return_value.cursor.return_value = mock_cursor

    result = catalog_service.update_catalog_by_id(1, sample_catalog)

    assert result is True
    assert mock_cursor.execute.call_count >= 2

@patch('service.catalog_service.get_connection')
def test_update_catalog_by_id_not_found(mock_conn, catalog_service, sample_catalog):
    mock_cursor = MagicMock()
    # Simulate catalog exists
    mock_cursor.fetchone.return_value = {"catalog_id": 1}
    # Simulate no rows updated
    mock_cursor.rowcount = 0
    mock_conn.return_value.cursor.return_value = mock_cursor

    with patch.object(CatalogService, 'get_catalog_by_id', return_value={"catalog_id": 1}):
        with pytest.raises(DataNotFoundError):
            catalog_service.update_catalog_by_id(1, sample_catalog)

@patch('service.catalog_service.get_connection')
def test_delete_catalog_by_id_success(mock_conn, catalog_service):
    mock_cursor = MagicMock()
    # Simulate catalog exists
    mock_cursor.fetchone.return_value = {"catalog_id": 1}
    # Simulate 1 row deleted
    mock_cursor.rowcount = 1
    mock_conn.return_value.cursor.return_value = mock_cursor

    with patch.object(CatalogService, 'get_catalog_by_id', return_value={"catalog_id": 1}):
        result = catalog_service.delete_catalog_by_id(1)
        assert result is True

@patch('service.catalog_service.get_connection')
def test_delete_catalog_by_id_not_found(mock_conn, catalog_service):
    mock_cursor = MagicMock()
    # Simulate catalog exists
    mock_cursor.fetchone.return_value = {"catalog_id": 1}
    # Simulate 0 rows deleted
    mock_cursor.rowcount = 0
    mock_conn.return_value.cursor.return_value = mock_cursor

    with patch.object(CatalogService, 'get_catalog_by_id', return_value={"catalog_id": 1}):
        with pytest.raises(DataNotFoundError):
            catalog_service.delete_catalog_by_id(1)
