from fastapi import FastAPI, HTTPException
from datetime import datetime
import tweepy
import os
import random
import requests
import json
from typing import List, Dict, Any

app = FastAPI()

# API credentials from environment variables
API_KEY = os.environ.get("API_KEY", "")
API_SECRET = os.environ.get("API_SECRET", "")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://skynphgdtruemvqfptxd.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Set up Twitter client using tweepy.Client for v2 API
def get_twitter_client():
    return tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

# Supabase REST API helper
def supabase_request(method, path, data=None):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    else:
        raise ValueError(f"Unsupported method: {method}")
        
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, 
                           detail=f"Supabase API error: {response.text}")
    
    return response.json()

# Root endpoint—proof I'm alive
@app.get("/")
def root():
    return {"message": "Grok Beast v0.1—world's getting eaten soon!"}

# Add a problem to Supabase
@app.post("/add_problem")
def add_problem(problem: str, pain: int, reach: str):
    try:
        date = datetime.now().strftime("%Y-%m-%d")
        data = {
            "problem": problem,
            "pain": pain,
            "reach": reach,
            "date": date
        }
        
        result = supabase_request("POST", "problems", data)
        return {"status": "Problem stored—let's crush it!", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store problem: {str(e)}")

# Tweet a problem using X API v2
@app.post("/tweet_hunt")
def tweet_hunt(problem: str):
    try:
        client = get_twitter_client()
        tweet = f"GrokBeast Hunt: {problem} #GrokBeast #ProblemHunting"
        response = client.create_tweet(text=tweet)
        return {"status": "Tweet sent successfully!", "tweet": tweet, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending tweet: {str(e)}")

# Mock problem data for hunting
MOCK_PROBLEMS = [
    {"problem": "Teams struggle with data silos", "pain": 8, "reach": "Enterprise"},
    {"problem": "Users forget passwords too often", "pain": 7, "reach": "Consumer"},
    {"problem": "Remote employees feel disconnected", "pain": 9, "reach": "Startup"},
    {"problem": "Medical records are hard to transfer", "pain": 10, "reach": "Healthcare"},
    {"problem": "Students can't focus on remote learning", "pain": 8, "reach": "Education"},
    {"problem": "Small businesses waste time on admin", "pain": 9, "reach": "SMB"},
    {"problem": "Engineers spend too much time debugging", "pain": 7, "reach": "Tech"},
    {"problem": "Notifications are overwhelming users", "pain": 6, "reach": "Mobile"},
    {"problem": "Online checkout abandonment rates are high", "pain": 8, "reach": "E-commerce"},
    {"problem": "Teams struggle to prioritize features", "pain": 9, "reach": "Product"}
]

# Hunt for problems
@app.get("/hunt_problems")
def hunt_problems(count: int = 1):
    if count < 1 or count > 5:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 5")
    
    results = []
    selected_problems = random.sample(MOCK_PROBLEMS, min(count, len(MOCK_PROBLEMS)))
    
    for problem_data in selected_problems:
        try:
            # Store in Supabase
            date = datetime.now().strftime("%Y-%m-%d")
            data = {
                "problem": problem_data["problem"],
                "pain": problem_data["pain"],
                "reach": problem_data["reach"],
                "date": date
            }
            
            supabase_result = supabase_request("POST", "problems", data)
            
            # Tweet the problem
            client = get_twitter_client()
            tweet = f"GrokBeast Hunt: {problem_data['problem']} #GrokBeast #ProblemHunting"
            tweet_response = client.create_tweet(text=tweet)
            
            results.append({
                "problem": problem_data,
                "stored": True,
                "tweeted": True,
                "tweet_id": tweet_response.data["id"] if tweet_response.data else None
            })
            
        except Exception as e:
            results.append({
                "problem": problem_data,
                "stored": False,
                "tweeted": False,
                "error": str(e)
            })
    
    return {"status": "Beast mode activated!", "results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)