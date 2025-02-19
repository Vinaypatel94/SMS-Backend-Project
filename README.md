 1. Initialize Alembic -> alembic init migrations
 2. Generate a New Migration -> alembic revision -m "Describe migration change here"
 3. Apply Migrations (Upgrade the Database) -> alembic upgrade head
 5. View Current Database Version->  alembic current
 6. viev migration history -> alembic history
 7. Show Pending Migrations -> alembic heads 
 8.  Reset Database Migrations (Use with Caution!) ->alembic downgrade base , alembic upgrade head





