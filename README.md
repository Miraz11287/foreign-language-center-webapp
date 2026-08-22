# LangCenter

Web application for a foreign language learning center with class registration, scheduling, and student performance tracking.

## Features

- **Authentication & roles** — Admin / Teacher / Student with separate access levels
- **Course catalog** — browse courses with search by keyword, language, and level; ratings and comments
- **Schedule** — weekly timetable with filters by language, level, and teacher
- **Enrollment** — students sign up for lessons with seat limits, cancel anytime
- **Course materials** — teachers upload text and files (PDF, DOCX, images); students download
- **Grading** — teachers mark attendance and score per student; export grades to CSV
- **Progress tracking** — students see their stats and attendance history
- **Notifications** — in-app notifications with toast popups and live badge
- **Teacher requests** — students can request teacher status; admin approves or rejects

## Tech Stack

| Layer    | Technology                         |
|----------|------------------------------------|
| Backend  | Python 3.12, Flask 3, SQLAlchemy   |
| Database | PostgreSQL 16                      |
| Auth     | Flask-Login, Flask-WTF (CSRF)      |
| Frontend | Jinja2, custom CSS (sketchy style) |
| DevOps   | Docker, Docker Compose             |

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
│   │   ├── models/          # User, Course, Lesson, Enrollment, Grade, Notification, ...
│   │   ├── auth/            # Register, login, logout, profile
│   │   ├── admin/           # Admin panel (CRUD: users, courses, lessons)
│   │   ├── teacher/         # Grade lessons, export CSV
│   │   ├── notifications/   # In-app notifications, toast polling
│   │   ├── main/            # Catalog, schedule, enrollment, progress
│   │   ├── templates/
│   │   └── static/
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── .env.example
```

## User Roles

| Role    | Access                                                        |
|---------|---------------------------------------------------------------|
| Admin   | Full access: manage courses, lessons, users, approve requests |
| Teacher | Add materials, grade students, mark attendance, export CSV    |
| Student | Browse catalog, enroll, view schedule, track progress         |
