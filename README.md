# SpendWise

A polished personal expense tracker built with Django, SQLite, Django Templates, Bootstrap 5 and Bootstrap Icons.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

The app uses SQLite through Django ORM. The database is stored at `db.sqlite3` in the project root. Running `python manage.py migrate` creates the database tables and applies all migrations; no separate database server or credentials are required.

Open http://127.0.0.1:8000/ and register an account. Financial records are scoped to the authenticated user.

The built-in demo account is:

- Username: `demo_user`
- Password: `SpendWiseDemo123!`

The `seed_demo` command is safe to run repeatedly and refreshes the demo account with colorful categories, current-month budgets, and sample expenses.

## Verification

```bash
python manage.py check
python manage.py test
```
