# 📚 FastAPI Book Management API

A robust and modern book management API built with [**FastAPI**](https://fastapi.tiangolo.com/). This API provides endpoints for managing books, reviews, users, and authentication with JWT.

## 🚀 Features

- Fully asynchronous architecture using FastAPI and SQLAlchemy 2.0
- User authentication using JWT (JSON Web Tokens)
- Email verification and password reset functionality
- Book management with reviews and tags
- Advanced query optimization using SQLAlchemy select options
- Redis integration for token revocation and Celery task queue
- Comprehensive test suite with pytest and coverage reporting

## 💻 Technologies Used

- **Backend**: FastAPI & SQLAlchemy 2.0
- **Database**: PostgreSQL (asyncpg)
- **Authentication**: JWT (PyJWT)
- **Email**: FastAPI-Mail
- **Task Queue**: Celery with Redis
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Monitoring**: FastAPI-SQLAlchemy-Monitor

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+** – Required for FastAPI and asyncio features
- **pip** – Python package installer for managing dependencies
- **PostgreSQL (optional)** – If using PostgreSQL as your database backend
- **Redis (optional)** – If using Redis or Celery
- **Git (optional)** – For cloning the repository
- **Docker (optional)** – Useful for running Redis or PostgreSQL containers

## 📦 Setup

To set up the project, follow these steps:

1. **Clone the repository**

   ```bash
   git clone [repository-url]
   ```

2. **Navigate to the project directory**

   ```bash
   cd [project-directory]
   ```

3. **Create and activate a virtual environment**

   - Windows:

     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

   - Linux/macOS:

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set environment variables**

   Just rename `env.txt` to `.env`:

   ```bash
   mv env.txt .env
   ```

   You can skip configuring it for now. See the [Environment Variables](#🔧-environment-variables) section if you need to customize.

6. **Run the application**

   For development:

   ```bash
   fastapi dev app/
   ```

   For production:

   ```bash
   fastapi run app/
   ```

7. **(Optional) Populate the database with sample data**

   While the application is running, open a separate terminal and run:

   ```bash
   python -m app.populate_db
   ```

## 📚 API Endpoints

### Authentication

- `POST /auth/signup` - Create new user account (Public)
- `POST /auth/login` - Login and get JWT tokens (Public)
- `GET /auth/logout` - Logout and revoke token (Authenticated)
- `GET /auth/refresh-token` - Get new access token (Authenticated)
- `GET /auth/verify` - Send verification email (Public)
- `GET /auth/verify/{token}` - Verify email address (Public)
- `POST /auth/password-reset-request` - Request password reset (Public)
- `POST /auth/password-reset-confirm/{token}` - Reset password (Public)

### Users

- `GET /users/me` - Get current user profile (Authenticated)
- `GET /users/` - List all users (Admin only)
- `GET /users/user-profile/{username}` - Get user profile (Public)
- `PUT /users/user-profile/{user_uid}` - Update user profile (Authenticated, Owner/Admin)
- `DELETE /users/user-profile/{user_uid}` - Delete user profile (Authenticated, Owner/Admin)

### Books

- `GET /books/` - List all books (Public)
- `POST /books/` - Create new book (Authenticated)
- `GET /books/{book_uid}/` - Get book details (Public)
- `PUT /books/{book_uid}/` - Update book (Authenticated, Owner/Admin)
- `DELETE /books/{book_uid}/` - Delete book (Authenticated, Owner/Admin)
- `GET /books/user/{user_uid}/` - Get user's books (Public)

### Reviews

- `GET /reviews/` - List all reviews (Public)
- `POST /reviews/book/{book_uid}` - Create new review (Authenticated)
- `GET /reviews/{review_uid}/` - Get review details (Public)
- `PUT /reviews/{review_uid}/` - Update review (Authenticated, Owner/Admin)
- `DELETE /reviews/{review_uid}/` - Delete review (Authenticated, Owner/Admin)

### Tags

- `GET /tags/{tag_uid}` - Get tag details (Public)
- `GET /tags/book/{book_uid}` - Get book's tags (Public)
- `POST /tags/book/{book_uid}` - Add tags to book (Authenticated, Owner/Admin)
- `PUT /tags/book/{book_uid}/tag/{tag_uid}` - Update book's tag (Authenticated, Owner/Admin)
- `DELETE /tags/book/{book_uid}/tag/{tag_uid}` - Remove tag from book (Authenticated, Owner/Admin)

## 📊 API Documentation

The API documentation is available at:

- Swagger UI: `/api/v1/docs`
- ReDoc: `/api/v1/redoc`

## 🔧 Environment Variables

Required environment variables in `.env` file:

### Database Configuration

DATABASE_URL examples:

- SQLite with aiosqlite: `DATABASE_URL=sqlite+aiosqlite:///bookly.db`
- PostgreSQL with asyncpg: `DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bookly`

### Redis & Celery Configuration

Options:

- `USE_REDIS=false`: In-memory token revocation (for testing)
- `USE_REDIS=true, USE_CELERY=false`: Use Redis with FastAPI background tasks
- `USE_REDIS=true, USE_CELERY=true`: Full Redis & Celery integration

Required if `USE_REDIS=true`:

- `REDIS_URL`: Redis connection URL

To start Redis and Celery:

```bash
# Start Redis (Docker)
docker run --name redis -p 6379:6379 -d redis

# Start Celery worker
celery -A app.celery_tasks.celery_app worker -l info -P gevent

# (Optional) Start Celery Flower for monitoring
celery -A app.celery_tasks.celery_app flower
```

### Email Configuration

Options:

- `USE_EMAIL=false`: Emails are printed to terminal (testing mode)
- `USE_EMAIL=true`: Real email sending enabled (requires SMTP settings)

Required if `USE_EMAIL=true`:

- `MAIL_USERNAME`: SMTP username
- `MAIL_PASSWORD`: SMTP password
- `MAIL_SERVER`: SMTP server address
- `MAIL_PORT`: SMTP server port

### SQLAlchemy Monitor

- `USE_SQLALCHEMY_MONITOR`: Enable/disable SQLAlchemy query monitoring (true/false)

### Other Configuration

- Other environment variables have default values specified in the `env.txt` file.

## 🔄 Asynchronous Architecture

The project is built with a fully asynchronous architecture:

1. **FastAPI Routes**: All endpoints are async, providing non-blocking I/O operations
2. **SQLAlchemy 2.0**: Using the new async API for database operations
3. **Database**: PostgreSQL with asyncpg driver for async database connections
4. **Background Tasks**: Email sending handled through:
   - Celery tasks (when Celery is available)
   - FastAPI background tasks (fallback)

## 🔐 Authentication & Security

1. **JWT Authentication**:

   - Access tokens for API access
   - Refresh tokens for obtaining new access tokens
   - Token revocation using Redis
   - Role-based access control (Admin/User)

2. **Email Verification**:
   - Secure token generation using `itsdangerous`
   - Secure email verification flow
   - Password reset functionality

## 📊 Database & Relationships

The database schema includes the following relationships:

1. **User-Book**: One-to-Many

   - A user can have multiple books
   - Books can be associated with a user

2. **Book-Review**: One-to-Many

   - A book can have multiple reviews
   - Reviews are associated with a book and user

3. **Book-Tag**: Many-to-Many
   - Books can have multiple tags
   - Tags can be associated with multiple books

## ⚡ Query Optimization

SQLAlchemy select options are used to optimize queries:

1. **Eager Loading**:

   - Using `joinedload` for related data
   - Preventing N+1 query problems
   - Optimizing relationship loading

2. **Selective Loading**:

   - Loading only required fields
   - Using appropriate join strategies
   - Implementing efficient filtering

3. **SQLAlchemy Monitor**:
   - Enabled via `USE_SQLALCHEMY_MONITOR` environment variable
   - Monitors and logs SQL queries
   - Helps identify performance bottlenecks
   - Provides query execution statistics

## 📧 Email Service

The email service is designed with graceful fallbacks for reliability:

- Primary: Celery tasks for async email sending
- Fallback: FastAPI background tasks

## 🔄 Redis & Celery Integration

2. **Redis Usage**:

   - Token revocation storage
   - Celery broker and result backend
   - In-memory fallback when Redis is unavailable

3. **Celery Tasks**:

   - Email sending
   - Background job processing
   - Task queue management

4. **Celery Worker**:

   - Development (Windows): Uses gevent pool (`-P gevent`)
     - Gevent provides better Windows compatibility
     - Handles async operations efficiently
   - Production: Use `eventlet` or `prefork` pool
     - Better performance in production environments
     - More stable for long-running processes

5. **Celery Flower**:
   - Web-based UI for monitoring Celery
   - Real-time task monitoring
   - Worker status and statistics
   - Task history and results
   - Resource usage metrics

## 🧪 Testing

Comprehensive test suite using:

1. **pytest & pytest-asyncio**:

   - Async test fixtures
   - Database session management
   - Mock services

2. **Test Coverage**:

   - pytest-cov for coverage reporting
   - HTML coverage reports

3. **Running Tests**:

   To run all tests, simply execute:

   ```bash
   pytest
   ```

   All necessary configurations (e.g., markers, coverage settings) are defined in the `pytest.ini` file, so no additional arguments are required.

## 📝 License

This project is licensed under the [MIT License](./LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

**Note**: This project is inspired by a YouTube tutorial series by **Ssali Jonathan**, available [here](https://www.youtube.com/playlist?list=PLEt8Tae2spYnHy378vMlPH--87cfeh33P).
