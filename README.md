📘 Smart Task Analyzer

A lightweight smart-prioritization tool built with Django (backend) and HTML/CSS/JS (frontend). It takes a list of tasks—each with due dates, effort, importance, and dependencies—and produces a ranked priority list using a custom scoring algorithm.

🚀 Features

Intelligent Task Scoring (urgency, importance, effort, dependencies)

Strategy modes: Balanced, Deadline-driven, Fastest-wins

REST-like API: /api/tasks/analyze/ and /api/tasks/suggest/

Simple Frontend UI with color‑coded priority cards

📂 Project Structure
task-analyzer/
├── backend/ # Django project
├── tasks/ # App with models, scoring engine, API views
├── frontend/ # Standalone HTML/CSS/JS frontend
├── db.sqlite3
├── manage.py
└── requirements.txt

⚙️ Backend Setup
1. Create and activate virtual environment

Mac/Linux:
python3 -m venv venv
source venv/bin/activate

Windows:
python -m venv venv
venv\Scripts\activate

2. Install dependencies
pip install -r requirements.txt

3. Initialize Django project (if not created yet)
django-admin startproject backend .
python manage.py startapp tasks

Add 'tasks' to INSTALLED_APPS in backend/settings.py.

4. Apply migrations
python manage.py makemigrations
python manage.py migrate

6. Run backend
python manage.py runserver

### Screenshots
## Api running
<img width="1919" height="766" alt="image" src="https://github.com/user-attachments/assets/59709c3c-08cd-4dfb-99af-b841c01bfa28" />

## Analyze
<img width="1826" height="930" alt="image" src="https://github.com/user-attachments/assets/aff9826c-aeea-4d53-a0df-4f9a21742ae3" />

## top 3 Suggestions
<img width="1505" height="911" alt="image" src="https://github.com/user-attachments/assets/b480b736-434e-4691-9e82-e15e8389148b" />

### Screen Recording
https://github.com/user-attachments/assets/3c2a5f1d-9e1c-4e2f-9cf4-dcdb6316cd5a
