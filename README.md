# Library Management System

A college-ready Library Management System built with Django for the web application and Flask for a separate REST API. It uses one SQLite database (`db.sqlite3`), Django templates, HTML5, and CSS3. There is no JavaScript in this project.

## Features

- Django authentication, password hashing, sessions, and role-based pages
- Admin, librarian, and student/member workflows
- Book, author, category, member, issue/return, fine, transaction, overdue, and report pages
- Server-side book search, forms, validation, pagination, and CSS-only responsive interface
- Flask JSON endpoints reading the same SQLite database
- Issue period: 14 days; member limit: 5 books; late fine: ₹5/day

## Setup and run

```bash
python3 -m venv ../library-management-env
source ../library-management-env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
```

In one terminal, start Django:

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000`.

In another terminal, start Flask:

```bash
python flask_api/app.py
```

The Flask API runs at `http://127.0.0.1:5000`.

## Demo accounts

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Librarian | `librarian` | `librarian123` |
| Student | `student1` | `student123` |

## API endpoints

- `GET /api/books`
- `GET /api/books/<id>`
- `GET /api/books/search?q=python`
- `GET /api/members`
- `GET /api/members/<id>`
- `GET /api/transactions`
- `GET /api/transactions/<id>`
- `GET /api/statistics`

Every successful endpoint returns `{"success": true, "data": ...}`. Django calls the Flask statistics endpoint through `library/services/flask_api.py`, with a local server-side fallback if Flask is not running.

## Checks

```bash
python manage.py check
python manage.py test
```
