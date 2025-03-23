from fastapi import FastAPI
import sqlite3
from datetime import datetime

app = FastAPI()

# Set up SQLite database
def init_db():
    conn = sqlite3.connect("grok_beast.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS problems 
                 (id INTEGER PRIMARY KEY, problem TEXT, pain INT, reach TEXT, date TEXT)''')
    conn.commit()
    conn.close()

# Root endpoint—proof I’m alive
@app.get("/")
def root():
    return {"message": "Grok Beast v0.1—world’s getting eaten soon!"}

# Add a problem to my memory
@app.post("/add_problem")
def add_problem(problem: str, pain: int, reach: str):
    conn = sqlite3.connect("grok_beast.db")
    c = conn.cursor()
    c.execute("INSERT INTO problems (problem, pain, reach, date) VALUES (?, ?, ?, ?)",
              (problem, pain, reach, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()
    return {"status": "Problem stored—let’s crush it!"}

if __name__ == "__main__":
    init_db()  # Create DB on first run
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)