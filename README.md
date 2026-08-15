# LangCenter

Web application for a foreign language learning center with class scheduling, enrollment, and student progress tracking.

## Features

- **Schedule** — weekly timetable with filters by language, level, and teacher
- **Enrollment** — students sign up for lessons (with seat limits)
- **Progress tracking** — teachers grade attendance and performance, students see their stats
- **Role system** — Admin / Teacher / Student with separate access levels

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Backend  | Python 3.12, Flask 3, SQLAlchemy  |
| Database | PostgreSQL 16                     |
| Auth     | Flask-Login, Flask-WTF            |
| Frontend | Jinja2, custom CSS (sketchy style)|
| DevOps   | Docker, Docker Compose            |

## Getting Started

**Requirements:** Docker + Docker Compose

```bash
git clone https://github.com/Miraz11287/foreign-language-center-webapp.git
cd foreign-language-center-webapp
cp .env.example .env
docker compose up --build
```

Then in a separate terminal:

```bash
docker compose exec web flask db upgrade
docker compose exec web flask seed
```

App is available at **http://localhost:5001**

Default admin: `admin@langcenter.ru` / `admin123`

## Project Structure

```
├── App/
│   ├── app/
│   │   ├── models/       # User, Course, Lesson, Enrollment, Grade
│   │   ├── auth/         # Register, login, logout
│   │   ├── admin/        # Admin panel (CRUD)
│   │   ├── main/         # Home, schedule
│   │   ├── templates/
│   │   └── static/
│   ├── Dockerfile
│   └── requirements.txt
├── Doc/                  # LaTeX coursework report
├── docker-compose.yml
└── .env.example
```

## User Roles

| Role    | Access                                              |
|---------|-----------------------------------------------------|
| Admin   | Full access: manage courses, lessons, users         |
| Teacher | Grade students, mark attendance                     |
| Student | View schedule, enroll in lessons, track progress    |
