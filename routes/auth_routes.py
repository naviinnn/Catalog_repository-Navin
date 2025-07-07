# routes/auth_routes.py
from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import create_access_token, jwt_required, unset_jwt_cookies, get_jwt_identity, set_access_cookies
from flasgger.utils import swag_from
from exception.catalog_exception import ValidationError, AuthenticationError, DatabaseConnectionError
from service.authentication_service import AuthenticationService
from utils.logger import logger

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')
authentication_service = AuthenticationService()

@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username_or_email': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['username_or_email', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'data': {'type': 'object'},
                    'redirect_to': {'type': 'string'}
                }
            }
        },
        400: {'description': 'Validation Error'},
        401: {'description': 'Authentication Failed'},
        500: {'description': 'Internal Server Error'}
    }
})
def login_api():
    data = request.get_json()
    if not data:
        raise ValidationError("Request must contain valid JSON data.")

    username_or_email = data.get('username_or_email')
    password = data.get('password')

    try:
        user = authentication_service.authenticate_user(username_or_email, password)
        access_token = create_access_token(identity=str(user.user_id))
        response = jsonify({
            "message": "Login successful.",
            "data": user.to_dict(),
            "redirect_to": url_for('index_page')
        })
        set_access_cookies(response, access_token)
        return response, 200
    except AuthenticationError as e:
        return jsonify({"message": "Authentication Failed", "details": str(e)}), 401
    except (ValidationError, DatabaseConnectionError) as e:
        return jsonify({"message": "Validation Error", "details": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}", exc_info=True)
        return jsonify({"message": "Internal Server Error", "details": "An unexpected error occurred."}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['Authentication'],
    'responses': {
        200: {'description': 'Logout successful'},
        401: {'description': 'Unauthorized'}
    },
    'security': [{'Bearer': []}]
})
def logout_api():
    response = jsonify({"message": "Logout successful."})
    unset_jwt_cookies(response)
    return response, 200
