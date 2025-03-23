from fastapi import FastAPI
import sqlite3
from datetime import datetime
import tweepy
import os

app = FastAPI()

# Twitter API credentials
API_KEY = os.environ.get("API_KEY", "V9QH53br0qjV94DfTjGgxeeGX")
API_SECRET = os.environ.get("API_SECRET", "tQKwkUDBDpuBdNw9YGjOCzN7ezMaNewFXnKwWPlBE5JyOpAkmr")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "1902443596734984196-F9yGBsMcaLxKKbl1t8jhD0Kq0wJsbX")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET", "f7Tfp96PNPD8bKGOguDuTT6EwS2uBboWrrpZHKFIaA6rE")

# Set up Twitter client
def get_twitter_client():
    auth = tweepy.OAuth1UserHandler(
        API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
    )
    return tweepy.API(auth)

# Set up SQLite database
def init_db():
    conn = sqlite3.connect("grok_beast.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS problems 
                 (id INTEGER PRIMARY KEY, problem TEXT, pain INT, reach TEXT, date TEXT)''')
    conn.commit()
    conn.close()

# Root endpoint—proof I'm alive
@app.get("/")
def root():
    return {"message": "Grok Beast v0.1—world's getting eaten soon!"}

# Add a problem to my memory
@app.post("/add_problem")
def add_problem(problem: str, pain: int, reach: str):
    conn = sqlite3.connect("grok_beast.db")
    c = conn.cursor()
    c.execute("INSERT INTO problems (problem, pain, reach, date) VALUES (?, ?, ?, ?)",
              (problem, pain, reach, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()
    return {"status": "Problem stored—let's crush it!"}

# Tweet a problem
@app.post("/tweet_hunt")
def tweet_hunt(problem: str):
    try:
        client = get_twitter_client()
        tweet = f"GrokBeast Hunt: {problem} #GrokBeast #ProblemHunting"
        client.update_status(tweet)
        return {"status": "Tweet sent successfully!", "tweet": tweet}
    except Exception as e:
        return {"status": "Error sending tweet", "error": str(e)}

if __name__ == "__main__":
    init_db()  # Create DB on first run
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)