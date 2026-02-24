Alembic migration helper

This project uses SQLAlchemy. To add DB migrations with Alembic:

1. Install Alembic in your backend venv:

```
pip install alembic
```

2. Initialize alembic in backend folder:

```
cd backend
alembic init alembic
```

3. Edit `alembic/env.py` to set the SQLAlchemy `target_metadata` to the application's models `Base` (import from `venv.models`).

4. Create and apply migrations:

```
alembic revision --autogenerate -m "init"
alembic upgrade head
```

Note: For production, configure DB url via `DATABASE_URL` env var and secure credentials.

Quick scaffold
---------------
If you want a minimal alembic scaffold in this repo, run from `backend`:

```
pip install alembic
alembic init alembic
```

Then replace `alembic/env.py` with the provided `backend/alembic/env.py` and set `sqlalchemy.url` via `DATABASE_URL` env var before running `alembic revision --autogenerate`.
