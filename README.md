# Hospital Appointment Booking System

## 1. Project Overview

The Hospital Appointment Booking System is a backend application developed using FastAPI and MySQL. It helps patients book and manage appointments, allows doctors to manage their schedules, and provides hospital administrators with tools to manage hospital operations.

The application includes authentication, appointment management, real-time queue updates, email notifications, medical file uploads, and reporting features.

## 2. Technologies Used

- Python 3.9+
- FastAPI
- MySQL
- SQLAlchemy ORM
- Pydantic
- JWT Authentication
- Alembic
- WebSockets
- APScheduler
- SMTP Email Notifications
- Pytest
- Uvicorn

## 3. Features

### Authentication and Authorization
- User login and authentication
- JWT-based authentication
- Role-based access control

### Department Management
- Create departments
- Retrieve department information
- Update department details

### Doctor Management
- Manage doctor profiles
- Retrieve doctor information
- Manage doctor schedules
- Manage doctor leave records

### Appointment Management
- Book appointments
- View patient appointments
- Cancel appointments
- Reschedule appointments
- Validate doctor schedules and availability
- Generate appointment numbers and queue tokens
- Maintain appointment history

### Consultation Management
- Manage patient consultations
- Store consultation information

### Medical File Management
- Upload medical files
- Associate uploaded files with appointments

### Real-Time Queue
- WebSocket-based queue updates
- Notifications when appointments are booked, cancelled, or rescheduled

### Email Notifications
- Appointment booking confirmation emails
- Appointment cancellation emails
- Appointment rescheduling emails
- Appointment reminder emails

### Reports
- Daily appointment reports
- Doctor-related reports

### Automated Reminders
- Scheduled appointment reminder processing
- Reminder tracking to prevent repeated emails

## 4. Project Structure

```text
Hospital-Appointment-Booking-System/
│
├── app/
│   ├── auth/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── websockets/
│   ├── config.py
│   ├── database.py
│   └── main.py
│
├── tests/
├── .env
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

Note: The project structure above summarizes the main components. Actual files may vary.

## 5. Prerequisites

Install the following before running the application:

- Python 3.9 or later
- MySQL Server
- Git
- Visual Studio Code or another Python editor

## 6. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Hospital-Appointment-Booking-System
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your actual repository URL.

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root and configure the database, JWT, and SMTP settings required by `app/config.py`.

Example placeholders:

```env
DATABASE_URL=your_mysql_connection_string
SECRET_KEY=your_secret_key
SMTP_HOST=your_smtp_host
SMTP_PORT=your_smtp_port
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
EMAIL_FROM=your_sender_email
```

Use the exact variable names expected by your application configuration.

**Important:** Never commit real passwords, secret keys, SMTP credentials, or the `.env` file to GitHub.

### Step 5: Configure MySQL

1. Start your MySQL server.
2. Create the database configured in your environment variables.
3. Ensure the database username and password are correct.

### Step 6: Run Database Migrations

If Alembic migrations are configured for your project, run:

```bash
alembic upgrade head
```

### Step 7: Start the Application

```bash
uvicorn app.main:app --reload
```

## 7. API Documentation

After starting the application, open:

http://127.0.0.1:8000/docs

FastAPI Swagger UI allows you to test the available endpoints.

The application includes endpoints for authentication, departments, doctors, schedules, doctor leaves, appointments, history, consultations, medical files, reports, and health checks.

## 8. Email Notification Testing

The email service uses SMTP to send appointment-related notifications.

The email integration was tested using Mailtrap. Successful test messages included:

- Appointment Booking Confirmation
- Appointment Cancellation Confirmation
- Appointment Rescheduled
- Hospital Appointment Reminder Test

The scheduled reminder job checks for booked appointments scheduled for the following day that have not already received a reminder.

## 9. Running Automated Tests

Run the automated tests using:

```bash
python -m pytest tests/ -v
```

The tests completed successfully during development, with two tests passing. Additional tests are recommended for complete feature coverage.

## 10. Security

- Keep database credentials and SMTP credentials in environment variables.
- Do not upload `.env` files containing secrets.
- Do not commit passwords, access tokens, or private credentials.
- Use appropriate authentication and authorization for protected endpoints.

## 11. Future Improvements

- Expand automated test coverage.
- Add more detailed error logging.
- Improve email delivery monitoring.
- Add additional reporting and administrative features.

## 12. Conclusion

The Hospital Appointment Booking System demonstrates the use of FastAPI, MySQL, SQLAlchemy, JWT authentication, WebSockets, scheduled jobs, and SMTP email integration to build a hospital appointment management backend.