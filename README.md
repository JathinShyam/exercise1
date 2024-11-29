# Django Onboarding Project

This project is a Django-based application designed to demonstrate fundamental features of web development, including creating custom models, building APIs, implementing JWT authentication, optimizing database queries, and enhancing the user experience with custom validations and pagination.

## Features

### 1. **Model Design**

- **Country, State, and City Models**:  
  Three key models have been created to represent a geographical hierarchy.  
  - `Country`: Represents a country with fields like name and code.
  - `State`: Represents a state/province, linked to a specific country.
  - `City`: Represents a city, linked to a specific state.

### 2. **Data Insertion and Queries**

- Bulk data insertion for all models (Country, State, and City).
- Basic queries to fetch and display all records from the models.

### 3. **Custom User Model**

- Created a `CustomUser` model to manage users with additional fields, extending the base `AbstractUser`.
- Ensured that the custom user model is fully integrated into the project with appropriate user management.

### 4. **User Authentication (JWT)**

- Implemented **JWT Authentication** for secure API access.  
  - **Signin** and **Signout** functionality were added for the users, enabling seamless session management.

### 5. **CRUD APIs**

- **User CRUD APIs**:  
  Created class-based views to manage user data (Create, Read, Update, Delete).
  
- **Country, State, and City CRUD APIs**:  
  Designed CRUD operations for the geographical models, allowing for easy management of Countries, States, and Cities.

### 6. **Authentication and Permissions**

- Added **Authentication** and **Permission Classes** to secure API endpoints.
  - Ensured only authorized users can access sensitive data.
  - Used custom permission logic where necessary.

### 7. **Custom Validations and Constraints**

- **Custom Constraints**:  
  Enforced specific rules and relationships within the models, such as ensuring valid state-country relationships and enforcing unique constraints where needed.
  
- **Custom Validations**:  
  Included custom validation logic on models to ensure data integrity.

### 8. **Optimized Database Queries**

- Used **`prefetch_related`** and **`select_related`** to optimize database queries and reduce the number of queries during data retrieval.
- Verified query performance improvements using **django-silk**, ensuring efficient and fast response times for the API.

### 9. **Custom Pagination**

- Defined **Custom Pagination** for APIs, ensuring that large sets of data are returned in manageable chunks to improve the performance and user experience.

### 10. **Additional Features**

- **Documentation**:  
  Added **API Documentation** using **OpenAPI Schema** and **DRF Spectacular** to automatically generate user-friendly API documentation. This makes it easy for developers to understand and interact with the API endpoints.

- **Throttling**:  
  Implemented **Throttling** to prevent performance issues due to excessive requests, ensuring fair usage and protecting the system from abuse.

---

### Installation

To run the project locally, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/JathinShyam/exercise1.git
2. Navigate to the project directory:

   ```bash
   cd exercise1
3. Set up a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
5. Apply migrations:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
6. Create a superuser (optional):

   ```bash
   python manage.py createsuperuser
7. Run the development server:

   ```bash
   python manage.py runserver
The API will now be available at http://127.0.0.1:8000/.
