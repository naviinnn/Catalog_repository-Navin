from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import os
import sys
from datetime import date, datetime, timedelta
import configparser
from utils.logger import logger


# JWT specific imports
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, set_access_cookies, unset_jwt_cookies, verify_jwt_in_request

# Add project root to sys.path for module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dto.catalog import Catalog
from dto.user import User
from service.catalog_service import CatalogService
from service.user_service import UserService
from service.authentication_service import AuthenticationService
from exception.catalog_exception import ValidationError, DataNotFoundError, DatabaseConnectionError, AuthenticationError
from utils.validation import validate_alphanumeric_string, validate_date, validate_future_date, validate_status

app = Flask(__name__)

# Load JWT secret key from config.ini
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'config.ini')
if not os.path.exists(config_path):
    logger.critical(f"FATAL ERROR: Configuration file not found at: {config_path}")
    sys.exit(1)
config.read(config_path)

app.config["JWT_SECRET_KEY"] = config.get('jwt', 'secret_key', fallback='super_secret_jwt_key_change_this')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1) # Token valid for 1 hour
app.config["JWT_TOKEN_LOCATION"] = ["cookies"] # Store JWT in cookies
app.config["JWT_COOKIE_SECURE"] = False # Set to True in production with HTTPS
app.config["JWT_COOKIE_CSRF_PROTECT"] = True # Enable CSRF protection for cookies
app.config["JWT_SESSION_COOKIE"] = True # Make the JWT cookie a session cookie for "logout on tab close"

jwt = JWTManager(app)

catalog_service = CatalogService()
user_service = UserService()
authentication_service = AuthenticationService()

# --- Custom Error Handlers ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Internal Server Error: {e}", exc_info=True)
    return render_template('500.html'), 500

@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({"message": "Validation Error", "details": str(e)}), 400

@app.errorhandler(DataNotFoundError)
def handle_data_not_found_error(e):
    return jsonify({"message": "Not Found", "details": str(e)}), 404

@app.errorhandler(DatabaseConnectionError)
def handle_database_error(e):
    logger.critical(f"Database Connection Error: {e}", exc_info=True)
    return jsonify({"message": "Database Error", "details": "Could not connect to the database or a database operation failed."}), 500

@app.errorhandler(AuthenticationError)
def handle_authentication_error(e):
    return jsonify({"message": "Authentication Failed", "details": str(e)}), 401

@app.errorhandler(Exception)
def handle_general_exception(e):
    app.logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    return jsonify({"message": "Internal Server Error", "details": "An unexpected error occurred. Please try again later."}), 500

# --- Helper for JSON serialization of Catalog objects ---
def serialize_catalog_for_json(catalog_data: dict) -> dict:
    """Serializes catalog data, converting date objects to string format."""
    if not catalog_data:
        return None
    serialized_data = catalog_data.copy()
    for key in ['start_date', 'end_date']:
        if key in serialized_data and isinstance(serialized_data[key], (date, datetime)):
            serialized_data[key] = serialized_data[key].strftime('%Y-%m-%d')
    return serialized_data

# --- Frontend Routes ---
from flask_jwt_extended import verify_jwt_in_request, exceptions

@app.route('/')
def root_route():
    """
    Redirect to /home if user is authenticated with valid JWT cookie,
    else redirect to login page.
    """
    try:
        verify_jwt_in_request()
        return redirect(url_for('index_page'))
    except exceptions.NoAuthorizationError:
        return redirect(url_for('login_page'))


@app.route('/home')
@jwt_required() # This route now requires JWT authentication
def index_page() -> str:
    """
    Renders the main single-page application (SPA) HTML template.
    Accessible only after successful login.
    """
    return render_template('index.html')

@app.route('/login')
def login_page():
    """
    Renders the login page. This route will ALWAYS render login.html.
    """
    return render_template('login.html')

# --- User Authentication API Endpoints ---
@app.route('/api/login', methods=['POST'])
def login_api():
    """Authenticates a user and sets JWT cookies upon successful login."""
    data = request.get_json()
    if not data:
        raise ValidationError("Request must contain JSON data.")

    username_or_email = data.get('username_or_email')
    password = data.get('password')

    try:
        user = authentication_service.authenticate_user(username_or_email, password)
        access_token = create_access_token(identity=str(user.user_id))
        response = jsonify({"message": "Login successful.", "data": user.to_dict(), "redirect_to": url_for('index_page')})
        set_access_cookies(response, access_token)
        return response, 200
    except AuthenticationError as e:
        return handle_authentication_error(e)
    except (ValidationError, DatabaseConnectionError) as e:
        return handle_validation_error(e)
    except Exception as e:
        return handle_general_exception(e)

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout_api():
    """Logs out the current user by unsetting JWT cookies."""
    response = jsonify({"message": "Logout successful.", "redirect_to": url_for('login_page')})
    unset_jwt_cookies(response)
    return response, 200

# --- Catalog API Endpoints (Protected by Authentication only) ---
@app.route('/api/catalogs', methods=['POST'])
@jwt_required()
def add_catalog_api() -> tuple[jsonify, int]:
    """API endpoint to create a new catalog entry, associated with the logged-in user."""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        raise ValidationError("Request must contain JSON data.")

    try:
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
    except ValidationError as e:
        return handle_validation_error(e)
    except DatabaseConnectionError as e:
        return handle_database_error(e)
    except Exception as e:
        return handle_general_exception(e)

@app.route('/api/catalogs/<int:catalog_id>', methods=['GET'])
@jwt_required(optional=True)
def get_catalog_by_id_api(catalog_id: int) -> tuple[jsonify, int]:
    """API endpoint to retrieve a single catalog by ID. Publicly viewable, but shows ownership if logged in."""
    try:
        catalog_data = catalog_service.get_catalog_by_id(catalog_id)
        serialized_catalog = serialize_catalog_for_json(catalog_data)
        return jsonify({"message": "Catalog retrieved successfully.", "data": serialized_catalog}), 200
    except DataNotFoundError as e:
        return handle_data_not_found_error(e)
    except DatabaseConnectionError as e:
        return handle_database_error(e)
    except Exception as e:
        return handle_general_exception(e)

@app.route('/api/catalogs', methods=['GET'])
@jwt_required(optional=True)
def get_all_catalogs_api() -> tuple[jsonify, int]:
    """
    API endpoint to retrieve all catalog entries with optional search term, status filter,
    and pagination parameters.
    """
    search_term = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip().lower()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int) # Default to 10 items per page

    # Define allowed statuses for filtering
    allowed_filter_statuses = ['active', 'inactive']

    try:
        # Get total count of catalogs matching search/filter criteria (before pagination)
        total_catalogs = catalog_service.count_catalogs(
            search_term=search_term,
            status_filter=status_filter if status_filter in allowed_filter_statuses else None
        )

        # Fetch paginated data
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
        return handle_database_error(e)
    except Exception as e:
        return handle_general_exception(e)

@app.route('/api/catalogs/<int:catalog_id>', methods=['PUT'])
@jwt_required()
def update_catalog_api(catalog_id: int) -> tuple[jsonify, int]:
    """API endpoint to update an existing catalog entry by its ID, protected by JWT."""
    data = request.get_json()
    if not data:
        raise ValidationError("Request must contain JSON data.")

    try:
        name = validate_alphanumeric_string(data.get('name'), "Name", max_length=30)
        description = validate_alphanumeric_string(data.get('description'), "Description", max_length=50)
        start_date = validate_future_date(data.get('start_date'), "Start Date")
        end_date = validate_future_date(data.get('end_date'), "End Date")
        status = validate_status(data.get('status'))

        if datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d'):
            raise ValidationError("End Date cannot be before Start Date.")

        updated_catalog = Catalog(name=name, description=description,
                                  start_date=start_date, end_date=end_date, status=status)

        catalog_service.update_catalog_by_id(catalog_id, updated_catalog)
        return jsonify({"message": f'Catalog ID {catalog_id} updated successfully.'}), 200
    except (ValidationError, DataNotFoundError, DatabaseConnectionError) as e:
        if isinstance(e, ValidationError): return handle_validation_error(e)
        if isinstance(e, DataNotFoundError): return handle_data_not_found_error(e)
        return handle_database_error(e)
    except Exception as e:
        return handle_general_exception(e)

@app.route('/api/catalogs/<int:catalog_id>', methods=['DELETE'])
@jwt_required()
def delete_catalog_api(catalog_id: int) -> tuple[jsonify, int]:
    """API endpoint to delete a catalog entry by its ID, protected by JWT."""
    try:
        catalog_service.delete_catalog_by_id(catalog_id)
        return jsonify({"message": f'Catalog ID {catalog_id} deleted successfully.'}), 200
    except (DataNotFoundError, DatabaseConnectionError) as e:
        if isinstance(e, DataNotFoundError): return handle_data_not_found_error(e)
        return handle_database_error(e)
    except Exception as e:
        return handle_general_exception(e)

if __name__ == '__main__':
    config_path_check = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'config.ini')
    if not os.path.exists(config_path_check):
        logger.critical(f"FATAL ERROR: Database configuration file not found at '{config_path_check}'.")
        logger.critical("Please ensure 'config.ini' exists in the 'config' directory and is properly configured.")
        sys.exit(1)

    app.run(debug=True, port=5000)