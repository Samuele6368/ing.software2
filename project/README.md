# StudentExamManager

StudentExamManager is a desktop application for managing students, courses, exam sessions, enrollments and grades.  
It is entirely built with Tkinter and SQLite, offering an offline, university-level administration tool with a modular architecture and automated tests.

## Features

- Tkinter GUI with dedicated areas for students, courses/exams, enrollments, and transcripts
- SQLite backend with repeatable migrations and safe initialization utilities
- Service layer enforcing validation and business rules
- API facade used by the GUI to keep presentation and logic decoupled
- Pytest suite covering CRUD and full enrollment-to-grade workflows
- Mermaid UML diagrams (use case, class, activity, sequence)
- Cascade-safe deletions for students, courses, exams, enrollments, and grades

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

## Running the Application

```bash
python3 src/main.py
```

The GUI automatically initializes the SQLite database on first run.

## Running Tests

```bash
pytest -q
```

## Database Reset

To reset the database (for example during demos or coursework):

```python
from db.database import reset_db
reset_db()
```

This removes the current SQLite file (if any) and reapplies `src/db/migrations.sql`.

## Architecture Overview

- `src/db`: database helpers (`database.py`) and migrations
- `src/models`: dataclasses for Student, Course, Exam, Registration
- `src/services`: business logic and validation per domain
- `src/api`: facade consumed exclusively by the GUI
- `src/ui`: Tkinter interface (`app_gui.py`)
- `tests`: pytest fixtures plus unit & integration coverage

The GUI only interacts with the API layer, which delegates to services that operate on the SQLite database via the db utilities. This separation keeps code maintainable and testable.

## UML Diagrams

All diagrams live in the `UML/` folder and are written in valid Mermaid syntax:

- `use_case.md`: Student & Admin use cases (manage students/courses/exams, enroll, record grades, view transcript)
- `class_diagram.md`: entities plus relationships (including the many-to-many via registrations)
- `activity_diagram.md`: end-to-end flow from adding entities to viewing the transcript
- `sequence_diagram.md`: interaction from GUI down to the database and back

Render them with any Mermaid-compatible viewer or in Markdown editors that support Mermaid.
