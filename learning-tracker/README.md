# Learning Tracker

A Python app to track the courses you are learning (Udemy, Coursera, Treehouse, YouTube, Mimo, IELTS and French), with progress, streaks, deadlines, IELTS scores and a suggested weekly timeline.

The design lives in the Learning Tracker Planning Pack (PRD, TRD, schema, DPIA, policies). This code follows it.

## Where the build is

| Phase | What | Status |
| --- | --- | --- |
| 1. Foundation | Project setup, SQLite database, schema, seeded platforms | Done |
| 2. Core tracking | Courses, sessions, progress, streak and weekly hours maths, categories and languages | Next |
| 3. Dashboard | Streamlit dashboard, behind pace warnings | |
| 4. IELTS and targets | Score entry, charts, test countdown | |
| 5. Timeline and polish | Suggested plan, CSV export, backup, accessibility checks, phone layout | |
| 6. Wishlist | Wishlist, free or paid tags, costs and currencies, resource suggestions | |
| 7. Cloud | GitHub, Supabase login and Postgres, deployment, Codespaces | |

## Set up

You need Python 3.12 or newer.

```bash
python -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

## Create the database

```bash
python -m learning_tracker.db
```

This creates `data/learning_tracker.db`, builds every table and adds the seven platforms. It is safe to run again: nothing is duplicated or lost.

To use a different database, set `LEARNING_TRACKER_DB` to a SQLAlchemy URL, for example `sqlite:///my.db`. In the cloud this will point at Postgres, and the key will live in the host's secrets store, never in the code.

## Run the tests

```bash
pytest
```

## What is in the database

| Table | Holds |
| --- | --- |
| platforms | Udemy, Coursera, Treehouse, YouTube, Mimo, IELTS, French, each with a badge colour and icon |
| courses | Title, platform, heading, total lessons or hours, start and target end dates, priority, status |
| sessions | Date, minutes, lessons done, note, for one course |
| ielts_scores | Practice or real test, four skill bands and the overall band |
| targets | Goals such as weekly hours or an IELTS band |

Rules the database enforces, so bad data cannot get in:

- Minutes and lessons done cannot be negative
- A course must end after it starts, and total units must be above zero
- Priority is 1 to 3, status is active, paused or done, units are lessons or hours
- IELTS bands run from 0 to 9 in steps of 0.5, and the overall band is worked out for you using the official rounding (an average of 6.25 becomes 6.5, 6.75 becomes 7.0)
- Deleting a course deletes its sessions
- A session cannot point at a course that does not exist

Progress, streaks and weekly hours are not stored. They are calculated from sessions in phase 2, so they can never be out of date.

## Folder map

```
learning_tracker/
  config.py     where the database lives
  models.py     the tables
  db.py         creates the database and seeds it
  seed.py       the seven platforms
  ielts.py      the overall band rule
tests/          49 tests
```

## Privacy

`data/` and `*.db` are in `.gitignore`, so your study records never reach GitHub. Please keep patient or practice information out of this app entirely.
