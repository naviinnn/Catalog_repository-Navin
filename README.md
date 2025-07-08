# 📦 Catalog Manager Application

A robust Flask-based web application to efficiently manage product catalogs.  
It provides full **CRUD** (Create, Read, Update, Delete) functionality, secure **JWT authentication**, interactive **Swagger API documentation**, and more.

---

## 📈 Project Status

- ✅ Stable
- 🐍 Python Version: 3.x
- ⚖️ License: MIT (or specify if different)

---

## 📚 Table of Contents

- [✨ Features](#-features)
- [🚀 Technologies Used](#-technologies-used)
- [⚙️ Setup Instructions](#️-setup-instructions)
- [👨‍💻 Usage](#-usage)
- [📁 Folder Structure](#-folder-structure)
- [✅ Testing](#-testing)
- [🤝 Contributing](#-contributing)
- [🪪 License](#-license)

---

## ✨ Features

- 📋 **Catalog Management**: Create, read, update, and delete product catalogs.
- 🔒 **Secure Authentication**: JWT-based user authentication with HTTP-only cookies.
- 🔍 **Advanced Search**: Pagination, search, and status filtering for catalogs.
- 📄 **Interactive API Docs**: Explore and test endpoints with Swagger UI.
- ⚙️ **Robust Error Handling**: Custom error responses for a smoother UX.
- 📜 **Comprehensive Logging**: Track and debug application activity.
- 🧪 **Testing Suite**: Automated tests with `pytest`.

---

## 🚀 Technologies Used

| Technology               | Purpose                      |
|--------------------------|------------------------------|
| Python 3.x               | Core programming language    |
| Flask                    | Web framework                |
| MySQL                    | Relational database          |
| mysql-connector-python   | MySQL driver for Python      |
| Flask-JWT-Extended       | JWT authentication           |
| Flasgger                 | Swagger API documentation    |
| bcrypt                   | Password hashing             |
| JavaScript (Fetch API)   | Frontend API interaction     |
| pytest                   | Testing framework            |

---

## ⚙️ Setup Instructions

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/naviinnn/Catalog_repository-Navin.git
cd Catalog_repository-Navin
```

---

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

```
Catalog_repository-Navin/
├── app.py                         # Main Flask entry point
├── config/
│   └── config.ini                 # DB & JWT config
├── dto/
│   ├── catalog.py                 # Catalog DTO
│   └── user.py                    # User DTO
├── service/
│   ├── authentication_service.py  # Auth logic
│   ├── catalog_service.py         # Catalog logic
│   └── user_service.py            # User logic
├── utils/
│   ├── logger.py                  # Logging
│   └── validation.py              # Input validation
├── exception/
│   └── catalog_exception.py       # Custom exceptions
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── index.html                 # Main SPA
│   ├── login.html                 # Login page
│   ├── 404.html                   # Not Found
│   └── 500.html                   # Server Error
├── tests/
│   ├── test_catalog_service.py
│   └── test_authentication.py
├── requirements.txt              # Prod dependencies
├── dev-requirements.txt          # Dev/test dependencies
└── README.md
```

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

