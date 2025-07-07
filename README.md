** Catalog Manager Application **
A Flask-based web application to manage product catalogs with full CRUD functionality, JWT authentication, and Swagger API documentation.

Features
Create, read, update, delete catalogs

User authentication with JWT tokens stored securely in cookies

Pagination, search, and status filtering for catalogs

Interactive Swagger UI for API exploration

Custom error handling and logging

Technologies Used
Python 3.x, Flask

MySQL with mysql-connector-python

Flask-JWT-Extended for authentication

Flasgger for Swagger UI docs

JavaScript Fetch API for frontend requests

pytest for testing

bcrypt for password hashing

Folder Structure
graphql
Copy
Edit
Catalog_repository-Navin/
│
├── app.py                    # Flask app entry point
├── config/
│   └── config.ini            # MySQL and JWT configuration
├── dto/
│   ├── catalog.py            # Catalog data model (DTO)
│   └── user.py               # User data model (DTO)
├── service/
│   ├── authentication_service.py  # Auth logic
│   ├── catalog_service.py          # Catalog business logic
│   └── user_service.py             # User management logic
├── utils/
│   ├── logger.py             # Logging setup
│   └── validation.py         # Input validators
├── exception/
│   └── catalog_exception.py  # Custom exceptions
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── index.html            # Main SPA template
│   ├── login.html            # Login page
│   ├── 404.html              # 404 error page
│   └── 500.html              # 500 error page
├── tests/
│   ├── test_catalog_service.py
│   └── test_authentication.py
├── requirements.txt          # Production dependencies
├── dev-requirements.txt      # Development/testing dependencies
└── README.md
Setup Instructions
1. Clone the repo
bash
Copy
Edit
git clone https://github.com/naviinnn/Catalog_repository-Navin.git
cd Catalog_repository-Navin
2. Create & activate a virtual environment (recommended)
bash
Copy
Edit
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
3. Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
For development and testing tools, also run:

bash
Copy
Edit
pip install -r dev-requirements.txt
4. Configure MySQL database
Make sure MySQL server is running.

Create the database (example name: sjn):

sql
Copy
Edit
CREATE DATABASE sjn;
The table schema will be managed by your service or you can manually create it matching DTO fields.

Update your database credentials in config/config.ini:

ini
Copy
Edit
[mysql]
host = localhost
user = root
password = Na001
database = sjn
5. Run the app
bash
Copy
Edit
python app.py
The app runs on http://127.0.0.1:5000.

Usage
Visit /login to authenticate.

After login, access /home to use the catalog management SPA.

API endpoints are protected with JWT; tokens stored securely in cookies.

Explore API documentation and try endpoints via Swagger UI at:
http://127.0.0.1:5000/apidocs/

Testing
Make sure dev dependencies are installed (pytest).

Run tests with:

bash
Copy
Edit
pytest
Tests use pytest fixtures to mock JWT authentication automatically.
