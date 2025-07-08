# Catalog Manager Application

A robust Flask-based web application to efficiently manage product catalogs. This application provides full CRUD (Create, Read, Update, Delete) functionality, secure JWT authentication, interactive Swagger API documentation, and more.

---

## 📋 Table of Contents

- [Features](#-features)  
- [Technologies Used](#-technologies-used)  
- [Setup Instructions](#-setup-instructions)  
- [Usage](#-usage)  
- [Folder Structure](#-folder-structure)  
- [Testing](#-testing)  
  

---

## ✨ Features

- 📋 **Catalog Management:** Create, read, update, and delete product catalogs.  
- 🔒 **Secure Authentication:** JWT-based user authentication with HTTP-only cookies.  
- 🔍 **Advanced Search:** Pagination, search, and status filtering for catalogs.  
- 🗂️ **Interactive API Docs:** Explore and test API endpoints with Swagger UI.  
- ⚙️ **Robust Error Handling:** Custom error handling for a smoother user experience.  
- 📝 **Comprehensive Logging:** Monitor and troubleshoot application activity using custom logging.  
- 🧪 **Testing Suite:** Automated tests with pytest for stability.  

---
---

## 🚀 Technologies Used

| Technology                                          | Purpose                            |
|---------------------------------------------------- |---------------------------------- -|
| Python 3.x                                          | Core programming language          |
| Flask                                               | Web framework                      |
| MySQL                                               | Database                           |
| mysql-connector-python                              | MySQL integration                  |
| Flask-JWT-Extended                                  | JWT-based authentication           |
| Flasgger                                            | Swagger UI integration             |
| bcrypt                                              | Password hashing                   |
| JavaScript Fetch API                                | Frontend HTTP requests             |
| pytest                                              | Testing framework                  |
| Python logging module + custom logger               | Application logging and monitoring |

---
---

## ⚙️ Setup Instructions

### 1. Clone the repository

   ```bash
   git clone https://github.com/naviinnn/Catalog_repository-Navin.git
   cd Catalog_repository-Navin
 ```

### 2. Create & Activate a Virtual Environment (Recommended)

#### 🐧 On Linux/macOS:
```bash
python -m venv venv
source venv/bin/activate
```

#### 🪟 On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3. Install Dependencies

#### 📦 For production:
```bash
pip install -r requirements.txt
```

#### 🧪 For development & testing:
```bash
pip install -r dev-requirements.txt
```

---

### 4. Install & Configure MySQL Database

#### 🛠️ Steps:
1. Install MySQL (if not already installed).
2. Start your MySQL server.
3. Open your MySQL client or command line and run:

```sql
CREATE DATABASE sjn;
```

4. Edit your database config in `config/config.ini`:

```ini
[mysql]
host = localhost
user = root
password = <your_password>
database = sjn
```

> 🔒 **Note**: Replace `<your_password>` with your actual MySQL root password.

---

### 5. Run the Application

```bash
python app.py
```

Once running, open your browser and go to:

🌐 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 👨‍💻 Usage

- 🔐 **Login**: Access `/login` to authenticate.
- 📋 **Dashboard**: After logging in, access `/home` to manage catalogs.
- 🔐 **API Security**: All API routes are protected using JWT stored in HTTP-only cookies.
- 📘 **Swagger UI**: Explore and test all APIs at [http://127.0.0.1:5000/apidocs/](http://127.0.0.1:5000/apidocs/)

### 🔁 Sample API Call (via `curl`)

```bash
curl -X POST http://127.0.0.1:5000/api/catalog \
  -H "Content-Type: application/json" \
  -d '{"name":"Sample Catalog", "description":"For testing"}'
```

---

## 📁 Folder Structure

Catalog_Manager - Navin/
├── app.py                         # Main Flask application entry point
├── config/
│   └── config.ini                 # Configuration for MySQL and JWT
├── dto/
│   ├── catalog.py                 # Catalog data transfer object (DTO)
│   ├── user.py                    # User DTO
│   └── __init__.py
├── exception/
│   └── catalog_exception.py       # Custom exception classes
├── logs/
│   └── catalog_manager.log        # Application log file
├── routes/
│   ├── auth_routes.py             # Authentication-related routes
│   ├── catalog_routes.py          # Catalog-related routes
├── service/
│   ├── authentication_service.py # Business logic for authentication
│   ├── catalog_service.py         # Business logic for catalogs
│   ├── user_service.py            # User-related business logic
│   └── __init__.py
├── static/
│   ├── css/
│   │   └── style.css              # CSS styles
│   └── js/
│       └── script.js              # Frontend JavaScript
├── swagger/
│   ├── app.py                    # Swagger-related Flask app config
│   └── swagger_config.yml        # Swagger configuration
├── templates/
│   ├── index.html                # Main SPA page
│   ├── login.html                # Login page
│   ├── 404.html                  # Not found page
│   └── 500.html                  # Server error page
├── tests/
│   ├── conftest.py               # Pytest fixtures and setup
│   ├── test_app.py               # Tests for main app features
│   ├── test_authentication_service.py
│   ├── test_catalog_service.py
│   ├── test_db_connection.py
│   ├── test_dto.py
│   ├── test_user_service.py
│   ├── test_validation.py
│   └── __init__.py
├── utils/
│   ├── db_get_connection.py      # DB connection helper
│   ├── logger.py                 # Custom logging configuration
│   ├── validation.py             # Input validation functions
│   └── __init__.py
├── requirements.txt              # Production dependencies
├── dev-requirements.txt          # Development and testing dependencies
├── pytest.ini                   # Pytest config file
├── README.md                    # Project documentation


---

## ✅ Testing

Ensure development dependencies are installed:

```bash
pip install -r dev-requirements.txt
```

Then run all unit tests:

```bash
pytest
```

- Uses `pytest` fixtures for mocking and isolation.
- Tests cover both service and authentication logic.

---

