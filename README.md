** Catalog Manager Application **
A robust Flask-based web application designed to efficiently manage product catalogs. This application provides full CRUD (Create, Read, Update, Delete) functionality, secure JWT authentication, and interactive Swagger API documentation, making it a comprehensive solution for catalog management.

✨ Features
Catalog Management: Seamlessly create, read, update, and delete product catalogs.

Secure Authentication: User authentication powered by JWT (JSON Web Tokens), with tokens securely stored in HTTP-only cookies.

Dynamic Catalog Listing:

Pagination for efficient display of large datasets.

Search functionality to quickly find specific catalogs.

Status filtering to manage catalog visibility and states.

Interactive API Documentation: Explore and test API endpoints directly through an interactive Swagger UI.

Robust Error Handling: Custom error handling for a smoother user experience.

Comprehensive Logging: Detailed logging to monitor application activities and troubleshoot issues.

🚀 Technologies Used
This project leverages a modern tech stack to deliver a performant and scalable solution:

Backend:

Python 3.x: The core programming language.

Flask: A lightweight and powerful web framework.

MySQL: Relational database for storing catalog and user data, connected via mysql-connector-python.

Flask-JWT-Extended: For robust and secure JWT authentication.

Flasgger: Integrates Swagger UI for automated API documentation.

bcrypt: Secure password hashing.

Frontend:

JavaScript Fetch API: For making asynchronous requests to the backend.

Testing:

pytest: A popular and powerful testing framework for Python.

📁 Folder Structure
Catalog_repository-Navin/
│
├── app.py                      # Flask app entry point and main configuration
├── config/
│   └── config.ini              # MySQL database and JWT configuration settings
├── dto/
│   ├── catalog.py              # Data Transfer Object (DTO) for Catalog entities
│   └── user.py                 # Data Transfer Object (DTO) for User entities
├── service/
│   ├── authentication_service.py # Business logic for user authentication
│   ├── catalog_service.py      # Business logic for catalog operations
│   └── user_service.py         # Business logic for user management
├── utils/
│   ├── logger.py               # Centralized logging setup
│   └── validation.py           # Utility functions for input validation
├── exception/
│   └── catalog_exception.py    # Custom exception classes for application-specific errors
├── static/                     # Static assets (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/                  # HTML templates for rendering web pages
│   ├── index.html              # Main Single-Page Application (SPA) template
│   ├── login.html              # User login page
│   ├── 404.html                # Custom 404 Not Found error page
│   └── 500.html                # Custom 500 Internal Server Error page
├── tests/                      # Unit and integration tests
│   ├── test_catalog_service.py # Tests for catalog business logic
│   └── test_authentication.py  # Tests for authentication services
├── requirements.txt            # Production dependencies for the application
├── dev-requirements.txt        # Development and testing dependencies
└── README.md                   # This README file
⚙️ Setup Instructions
Follow these steps to get the Catalog Manager Application up and running on your local machine.

1. Clone the Repository
Begin by cloning the project repository to your local system:

Bash

git clone https://github.com/naviinnn/Catalog_repository-Navin.git
cd Catalog_repository-Navin
2. Create & Activate a Virtual Environment (Recommended)
It's highly recommended to use a virtual environment to manage project dependencies:

Bash

python -m venv venv
Activate the virtual environment:

Linux/macOS:

Bash

source venv/bin/activate
Windows:

Bash

venv\Scripts\activate
3. Install Dependencies
Install the required Python packages for the application:

Bash

pip install -r requirements.txt
For development and testing tools, also install the development dependencies:

Bash

pip install -r dev-requirements.txt
4. Configure MySQL Database
Ensure your MySQL server is running before proceeding.

Create the database:

You'll need a database for the application to store its data. For example, create a database named sjn:

SQL

CREATE DATABASE sjn;
Note: The application's services are designed to manage the table schema based on the DTOs. However, you can also manually create tables that match your DTO fields if preferred.

Update database credentials:

Edit the config/config.ini file with your MySQL database credentials:

Ini, TOML

[mysql]
host = localhost
user = root
password = Na001
database = sjn
5. Run the Application
Once everything is set up, you can run the Flask application:

Bash

python app.py
The application will typically run on http://127.0.0.1:5000.

👨‍💻 Usage
Authentication: Navigate to /login to authenticate users.

Catalog Management SPA: After successful login, access the main Single-Page Application (SPA) for catalog management at /home.

API Security: All API endpoints are protected with JWT (JSON Web Token). These tokens are securely stored in HTTP-only cookies on the client side.

API Documentation: Explore and interact with the API endpoints via the Swagger UI at:
http://127.0.0.1:5000/apidocs/

✅ Testing
To ensure the application's functionality and stability, run the provided tests.

Prerequisites: Make sure you have installed the development dependencies, including pytest.

Run tests:

Bash

pytest
The tests are configured to use pytest fixtures, which automatically mock JWT authentication, streamlining the testing process.