Installation & Setup
Follow these steps to set up the project on your local machine:

1. Create a Virtual Environment
Isolating your dependencies is highly recommended:

Bash
# For Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# For Windows
python -m venv .venv
.venv\Scripts\activate

####
2. Install Required Dependencies



####
Running the Application
To start the development server with auto-reload enabled:

Bash
uvicorn main:app --reload
Once the server is running, you can access the following:

API Root: http://127.0.0.1:8000

Swagger UI Docs: http://127.0.0.1:8000/docs (Best for testing endpoints)