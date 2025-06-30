  # Catalog Manager Application

This is a simple web application for managing product catalogs. It provides a user interface to perform standard CRUD (Create, Read, Update, Delete) operations on catalog entries.

## Features

* **Create Catalog:** Add new catalog entries with details like name, description, start date, end date, and status.
* **View All Catalogs:** Display a list of all existing catalogs in a tabular format.
* **View Catalog by ID:** Retrieve and display details for a specific catalog using its unique ID.
* **Update Catalog by ID:** Modify the details of an existing catalog.
* **Delete Catalog by ID:** Remove a catalog entry from the system.

## Technologies Used

* **Backend:** Flask (Python web framework)
* **Database:** MySQL
* **Frontend:** HTML5, CSS3, JavaScript (using Fetch API for asynchronous communication)
* **Database Connector:** `mysql-connector-python`

## Setup Instructions

To get this project up and running on your local machine:

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd catalog_resp
    ```
2.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Database Setup (MySQL):**
    * Ensure MySQL server is running.
    * Log in to MySQL and create a database (e.g., `catalog_db`):
        ```sql
        CREATE DATABASE catalog_db;
        USE catalog_db;
        ```
    * Create the `catalog` table:
        ```sql
        CREATE TABLE catalog (
            catalog_id INT AUTO_INCREMENT PRIMARY KEY,
            catalog_name VARCHAR(30) NOT NULL,
            catalog_description VARCHAR(50),
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            status VARCHAR(20) NOT NULL
        );
        ```
    * **Update `config/config.ini`:** Open `config/config.ini` and replace `your_mysql_password` with your actual MySQL root password.
        ```ini
        [mysql]
        host = localhost
        user = root
        password = your_mysql_password
        database = catalog_db
        ```
4.  **Run the Flask Application:**
    ```bash
    python app.py
    ```
    The application will typically run on `http://127.0.0.1:5000/`.

## Usage

1.  Open your web browser and navigate to `http://127.0.0.1:5000/`.
2.  Use the buttons at the top of the page to perform different operations:
    * **"Create New Catalog"**: Opens a form to add a new entry.
    * **"View All Catalogs"**: Displays all catalogs in the table below.
    * **"Update Catalog by ID"**, **"Delete Catalog by ID"**, **"View Catalog by ID"**: Will prompt you to enter a Catalog ID in a modal window.
3.  The table will dynamically update with the results of your actions. Messages (success/error) will appear at the top.