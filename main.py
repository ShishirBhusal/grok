from fastapi import FastAPI
import sqlite3
from datetime import datetime
import tweepy
import os

app = FastAPI()

# Twitter API credentials
API_KEY = os.environ.get("API_KEY", "")
API_SECRET = os.environ.get("API_SECRET", "")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET", "")

# Set up Twitter client using tweepy.Client for v2 API
def get_twitter_client():
    return tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

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

# Tweet a problem using X API v2
@app.post("/tweet_hunt")
def tweet_hunt(problem: str):
    try:
        client = get_twitter_client()
        tweet = f"GrokBeast Hunt: {problem} #GrokBeast #ProblemHunting"
        response = client.create_tweet(text=tweet)
        return {"status": "Tweet sent successfully!", "tweet": tweet, "response": response}
    except Exception as e:
        return {"status": "Error sending tweet", "error": str(e)}

if __name__ == "__main__":
    init_db()  # Create DB on first run
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)