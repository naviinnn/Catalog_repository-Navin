Catalog Manager Application
A robust Flask-based web application to efficiently manage product catalogs. This application provides full CRUD (Create, Read, Update, Delete) functionality, secure JWT authentication, interactive Swagger API documentation, and more.

Build Status License Python Version

📋 Table of Contents
Features
Technologies Used
Setup Instructions
Usage
Folder Structure
Testing
Contributing
License
✨ Features
📋 Catalog Management: Create, read, update, and delete product catalogs.
🔒 Secure Authentication: JWT-based user authentication with HTTP-only cookies.
🔍 Advanced Search: Pagination, search, and status filtering for catalogs.
🗂️ Interactive API Docs: Explore and test API endpoints with Swagger UI.
⚙️ Robust Error Handling: Custom error handling for a smoother user experience.
📝 Comprehensive Logging: Monitor and troubleshoot application activity.
🧪 Testing Suite: Automated tests with pytest for stability.
🚀 Technologies Used
Technology	Purpose
Python 3.x	Core programming language
Flask	Web framework
MySQL	Database
mysql-connector-python	MySQL integration
Flask-JWT-Extended	JWT-based authentication
Flasgger	Swagger UI integration
bcrypt	Password hashing
JavaScript Fetch API	Frontend requests
pytest	Testing framework
⚙️ Setup Instructions
1. Clone the Repository
bash
git clone https://github.com/naviinnn/Catalog_repository-Navin.git
cd Catalog_repository-Navin
2. Create & Activate a Virtual Environment (Recommended)
bash
python -m venv venv
Linux/macOS: source venv/bin/activate
Windows: venv\Scripts\activate
3. Install Dependencies
bash
pip install -r requirements.txt
For development/testing:
bash
pip install -r dev-requirements.txt
4. Install & Configure MySQL Database
Install MySQL if not already present.
Start your MySQL server.
Create a database (example name: sjn):
SQL
CREATE DATABASE sjn;
Update your database credentials in config/config.ini:
INI
[mysql]
host = localhost
user = root
password = <your_password>
database = sjn
5. Run the Application
bash
python app.py
The application will typically run at: http://127.0.0.1:5000
👨‍💻 Usage
Authentication: Visit /login to authenticate.
Catalog Management: After login, access /home for the main SPA.
API Security: All endpoints are JWT-protected; tokens are stored in HTTP-only cookies.
API Documentation: Explore and interact with the API via Swagger UI at http://127.0.0.1:5000/apidocs/
Example API Call with curl:

bash
curl -X POST http://127.0.0.1:5000/api/catalog \
  -H "Content-Type: application/json" \
  -d '{"name":"Sample Catalog", "description":"For testing"}'
📁 Folder Structure
Code
Catalog_repository-Navin/
│
├── app.py                    # Flask app entry point and main config
├── config/
│   └── config.ini            # MySQL and JWT configuration
├── dto/
│   ├── catalog.py            # Catalog DTO
│   └── user.py               # User DTO
├── service/
│   ├── authentication_service.py  # Auth logic
│   ├── catalog_service.py         # Catalog logic
│   └── user_service.py            # User management
├── utils/
│   ├── logger.py             # Logging setup
│   └── validation.py         # Input validation
├── exception/
│   └── catalog_exception.py  # Custom exceptions
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── index.html            # Main SPA
│   ├── login.html            # Login page
│   ├── 404.html              # Not Found page
│   └── 500.html              # Server Error page
├── tests/
│   ├── test_catalog_service.py
│   └── test_authentication.py
├── requirements.txt          # Production dependencies
├── dev-requirements.txt      # Dev/testing dependencies
└── README.md
✅ Testing
Make sure development dependencies are installed. Run all tests:

bash
pytest
Tests use pytest fixtures to mock JWT authentication automatically.

