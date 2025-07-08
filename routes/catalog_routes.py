from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger.utils import swag_from
from utils.validation import validate_alphanumeric_string, validate_future_date, validate_status
from dto.catalog import Catalog
from exception.catalog_exception import ValidationError, DataNotFoundError, DatabaseConnectionError
from service.catalog_service import CatalogService
from utils.logger import logger
from datetime import datetime

catalog_bp = Blueprint('catalog_bp', __name__, url_prefix='/api/catalogs')
catalog_service = CatalogService()

def serialize_catalog_for_json(catalog_data: dict) -> dict:
    """
    Convert date fields in catalog data to string format for JSON serialization.

    Args:
        catalog_data (dict): Catalog information with possible date objects.

    Returns:
        dict: Catalog data with dates formatted as 'YYYY-MM-DD', or None if input is empty.
    """
    if not catalog_data:
        return None
    serialized_data = catalog_data.copy()
    for key in ['start_date', 'end_date']:
        if key in serialized_data and hasattr(serialized_data[key], 'strftime'):
            serialized_data[key] = serialized_data[key].strftime('%Y-%m-%d')
    return serialized_data

@catalog_bp.route('', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Catalog'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'start_date': {'type': 'string', 'format': 'date'},
                    'end_date': {'type': 'string', 'format': 'date'},
                    'status': {'type': 'string'}
                },
                'required': ['name', 'description', 'start_date', 'end_date', 'status']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Catalog created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'data': {'type': 'object', 'properties': {'catalog_id': {'type': 'integer'}}}
                }
            }
        },
        400: {'description': 'Validation Error'},
        401: {'description': 'Unauthorized'},
        500: {'description': 'Internal Server Error'}
    },
    'security': [{'Bearer': []}]
})
def add_catalog_api():
    """
    Handle API request to add a new catalog.

    Validates input JSON, checks date logic, creates a catalog, and returns success response.

    Returns:
        Flask Response: JSON message with new catalog ID and HTTP status 201.
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        raise ValidationError("Request must contain valid JSON data.")

    name = validate_alphanumeric_string(data.get('name'), "Name", max_length=30)
    description = validate_alphanumeric_string(data.get('description'), "Description", max_length=50)
    start_date = validate_future_date(data.get('start_date'), "Start Date")
    end_date = validate_future_date(data.get('end_date'), "End Date")
    status = validate_status(data.get('status'))

    if datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d'):
        raise ValidationError("End Date cannot be before Start Date.")

    new_catalog = Catalog(name=name, description=description,
                          start_date=start_date, end_date=end_date, status=status)

    catalog_id = catalog_service.create_catalog(new_catalog, current_user_id)
    return jsonify({"message": "Catalog created successfully.", "data": {"catalog_id": catalog_id}}), 201


@catalog_bp.route('/<int:catalog_id>', methods=['GET'])
@jwt_required(optional=True)
@swag_from({
    'tags': ['Catalog'],
    'parameters': [
        {
            'name': 'catalog_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the catalog to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Catalog retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'catalog_id': {'type': 'integer'},
                            'catalog_name': {'type': 'string'},
                            'catalog_description': {'type': 'string'},
                            'start_date': {'type': 'string'},
                            'end_date': {'type': 'string'},
                            'status': {'type': 'string'}
                        }
                    }
                }
            }
        },
        404: {'description': 'Catalog not found'},
        500: {'description': 'Internal Server Error'}
    }
})
def get_catalog_by_id_api(catalog_id):
    """
    Retrieve and return catalog data by ID as JSON response.

    Handles not found, database, and unexpected errors with appropriate HTTP status codes.

    Args:
        catalog_id (int): ID of the catalog to retrieve.

    Returns:
        Flask Response: JSON with catalog data or error message.
    """
    try:
        catalog_data = catalog_service.get_catalog_by_id(catalog_id)
        serialized_catalog = serialize_catalog_for_json(catalog_data)
        return jsonify({"message": "Catalog retrieved successfully.", "data": serialized_catalog}), 200
    except DataNotFoundError as e:
        return jsonify({"message": "Not Found", "details": str(e)}), 404
    except DatabaseConnectionError as e:
        logger.critical(f"Database Connection Error: {e}", exc_info=True)
        return jsonify({"message": "Database Error", "details": "Database operation failed."}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"message": "Internal Server Error", "details": "An unexpected error occurred."}), 500


@catalog_bp.route('', methods=['GET'])
@jwt_required(optional=True)
@swag_from({
    'tags': ['Catalog'],
    'parameters': [
        {
            'name': 'search',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Search term for catalog name/description'
        },
        {
            'name': 'status',
            'in': 'query',
            'type': 'string',
            'enum': ['active', 'inactive'],
            'required': False,
            'description': 'Filter by catalog status'
        },
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 1,
            'description': 'Page number for pagination'
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 10,
            'description': 'Number of items per page'
        }
    ],
    'responses': {
        200: {
            'description': 'List of catalogs retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'catalog_id': {'type': 'integer'},
                                'catalog_name': {'type': 'string'},
                                'catalog_description': {'type': 'string'},
                                'start_date': {'type': 'string'},
                                'end_date': {'type': 'string'},
                                'status': {'type': 'string'}
                            }
                        }
                    },
                    'total_catalogs': {'type': 'integer'},
                    'page': {'type': 'integer'},
                    'per_page': {'type': 'integer'}
                }
            }
        },
        500: {'description': 'Internal Server Error'}
    }
})
def get_all_catalogs_api():
    """
    Retrieve paginated catalog list with optional search and status filtering.

    Returns catalog data with pagination info as JSON response.

    Returns:
        Flask Response: JSON containing catalogs list, total count, and pagination details.
    """
    search_term = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip().lower()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    allowed_filter_statuses = ['active', 'inactive']

    try:
        total_catalogs = catalog_service.count_catalogs(
            search_term=search_term,
            status_filter=status_filter if status_filter in allowed_filter_statuses else None
        )
        catalogs_data = catalog_service.get_all_catalog(
            search_term=search_term,
            status_filter=status_filter if status_filter in allowed_filter_statuses else None,
            page=page,
            per_page=per_page
        )
        serialized_catalogs = [serialize_catalog_for_json(c) for c in catalogs_data]

        return jsonify({
            "message": "Catalogs retrieved successfully.",
            "data": serialized_catalogs,
            "total_catalogs": total_catalogs,
            "page": page,
            "per_page": per_page
        }), 200
    except DatabaseConnectionError as e:
        logger.critical(f"Database Connection Error: {e}", exc_info=True)
        return jsonify({"message": "Database Error", "details": "Database operation failed."}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"message": "Internal Server Error", "details": "An unexpected error occurred."}), 500


@catalog_bp.route('/<int:catalog_id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Catalog'],
    'parameters': [
        {
            'name': 'catalog_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Catalog ID to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'start_date': {'type': 'string', 'format': 'date'},
                    'end_date': {'type': 'string', 'format': 'date'},
                    'status': {'type': 'string'}
                },
                'required': ['name', 'description', 'start_date', 'end_date', 'status']
            }
        }
    ],
    'responses': {
        200: {'description': 'Catalog updated successfully'},
        400: {'description': 'Validation Error'},
        404: {'description': 'Catalog not found'},
        500: {'description': 'Internal Server Error'}
    },
    'security': [{'Bearer': []}]
})
def update_catalog_api(catalog_id):
    """
    Update catalog details by ID from JSON request data.

    Validates input, performs update, and returns success or error JSON response.

    Args:
        catalog_id (int): ID of the catalog to update.

    Returns:
        Flask Response: JSON message indicating update status.
    """
    data = request.get_json()
    if not data:
        raise ValidationError("Request must contain valid JSON data.")

    name = validate_alphanumeric_string(data.get('name'), "Name", max_length=30)
    description = validate_alphanumeric_string(data.get('description'), "Description", max_length=50)
    start_date = validate_future_date(data.get('start_date'), "Start Date")
    end_date = validate_future_date(data.get('end_date'), "End Date")
    status = validate_status(data.get('status'))

    if datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d'):
        raise ValidationError("End Date cannot be before Start Date.")

    updated_catalog = Catalog(name=name, description=description,
                              start_date=start_date, end_date=end_date, status=status)

    try:
        catalog_service.update_catalog_by_id(catalog_id, updated_catalog)
        return jsonify({"message": f"Catalog ID {catalog_id} updated successfully."}), 200
    except ValidationError as e:
        return jsonify({"message": "Validation Error", "details": str(e)}), 400
    except DataNotFoundError as e:
        return jsonify({"message": "Not Found", "details": str(e)}), 404
    except DatabaseConnectionError as e:
        logger.critical(f"Database Connection Error: {e}", exc_info=True)
        return jsonify({"message": "Database Error", "details": "Database operation failed."}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"message": "Internal Server Error", "details": "An unexpected error occurred."}), 500


@catalog_bp.route('/<int:catalog_id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Catalog'],
    'parameters': [
        {
            'name': 'catalog_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Catalog ID to delete'
        }
    ],
    'responses': {
        200: {'description': 'Catalog deleted successfully'},
        404: {'description': 'Catalog not found'},
        500: {'description': 'Internal Server Error'}
    },
    'security': [{'Bearer': []}]
})
def delete_catalog_api(catalog_id):
    try:
        catalog_service.delete_catalog_by_id(catalog_id)
        return jsonify({"message": f"Catalog ID {catalog_id} deleted successfully."}), 200
    except DataNotFoundError as e:
        return jsonify({"message": "Not Found", "details": str(e)}), 404
    except DatabaseConnectionError as e:
        logger.critical(f"Database Connection Error: {e}", exc_info=True)
        return jsonify({"message": "Database Error", "details": "Database operation failed."}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"message": "Internal Server Error", "details": "An unexpected error occurred."}), 500
