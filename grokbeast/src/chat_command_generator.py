#!/usr/bin/env python3
import json
import os
import time
import re
import random
import argparse
import requests
from datetime import datetime
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).parent.parent
COMMANDS_FILE = BASE_DIR / "cache" / "commands.json"
RESPONSE_FILE = BASE_DIR / "cache" / "response.json"
CHAT_INSTRUCTIONS_FILE = BASE_DIR / "cache" / "chat_instructions.txt"
CACHE_DIR = BASE_DIR / "cache"
COMMAND_HISTORY_FILE = CACHE_DIR / "command_history.json"

# Ensure cache directory exists
CACHE_DIR.mkdir(exist_ok=True)

def load_command_history():
    """Load previous command history"""
    if os.path.exists(COMMAND_HISTORY_FILE):
        try:
            with open(COMMAND_HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return []

def save_command_history(command):
    """Save command to history"""
    history = load_command_history()
    history.append({
        "command": command,
        "timestamp": datetime.now().isoformat()
    })
    # Keep only the last 100 commands
    history = history[-100:]
    with open(COMMAND_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def parse_chat_instruction(instruction):
    """
    Parse a natural language instruction from the chat into a structured command
    """
    instruction = instruction.strip().lower()
    
    # Generate a random command ID
    cmd_id = f"cmd_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Handle status commands
    if any(term in instruction for term in ["status", "what's up", "how are you", "check status", "system status"]):
        return {
            "type": "status",
            "id": cmd_id,
            "params": {}
        }
    
    # Handle hunt commands
    if any(term in instruction for term in ["hunt", "find", "search", "look for"]):
        # Extract sources
        sources = ["reddit", "web"]  # Default sources
        if "reddit" in instruction:
            sources = ["reddit"]
        if "web" in instruction:
            if "reddit" not in sources:
                sources.append("reddit")
        
        # Extract count
        count_match = re.search(r'(\d+)\s+(problem|issue|bug)', instruction)
        count = 3  # Default count
        if count_match:
            count = int(count_match.group(1))
        
        # Check if we should tweet
        should_tweet = "tweet" in instruction
        
        # Build the hunt problems command
        if should_tweet:
            return {
                "type": "hunt_problems",
                "id": cmd_id,
                "params": {
                    "sources": sources,
                    "count": count,
                    "should_tweet": True
                }
            }
        else:
            return {
                "type": "hunt_problems",
                "id": cmd_id,
                "params": {
                    "sources": sources,
                    "count": count
                }
            }
    
    # Handle start agent swarm commands
    if any(term in instruction for term in ["swarm", "agent swarm", "start swarm", "beast mode"]):
        # Extract model
        model_id = "gpt2"  # Default model
        if "phi" in instruction:
            model_id = "microsoft/phi-2"
        
        # Extract count
        count_match = re.search(r'(\d+)', instruction)
        count = 3  # Default count
        if count_match:
            count = int(count_match.group(1))
        
        return {
            "type": "start_agent_swarm",
            "id": cmd_id,
            "params": {
                "sources": ["reddit", "web"],
                "count": count,
                "model_id": model_id
            }
        }
    
    # Handle tweet commands
    if any(term in instruction for term in ["tweet", "post", "share"]):
        # Extract problem text
        problem_text = instruction
        
        # Remove command words
        for word in ["tweet", "post", "share", "about", "that", "please", "could you"]:
            problem_text = problem_text.replace(word, "")
        
        problem_text = problem_text.strip()
        
        if len(problem_text) < 5:
            problem_text = "New capability discovered! Check out this AI-powered problem hunter!"
        
        return {
            "type": "tweet_problem",
            "id": cmd_id,
            "params": {
                "problem": problem_text
            }
        }
    
    # Handle shell commands
    if instruction.startswith("run ") or instruction.startswith("execute "):
        command = instruction.replace("run ", "").replace("execute ", "")
        
        return {
            "type": "shell",
            "id": cmd_id,
            "params": {
                "command": command,
                "capture_output": True
            }
        }
    
    # When all else fails, just start a problem hunt with defaults
    return {
        "type": "start_agent_swarm",
        "id": cmd_id,
        "params": {
            "sources": ["reddit", "web"],
            "count": 3,
            "model_id": "gpt2"
        }
    }

def main():
    """Main function to parse arguments and run the appropriate command"""
    parser = argparse.ArgumentParser(description="GrokBeast v5 Command Interface")
    parser.add_argument("--web", action="store_true", help="Start web interface")
    parser.add_argument("--port", type=int, default=5000, help="Port for web interface")
    parser.add_argument("--command", type=str, help="Command to execute", default=None)
    
    args = parser.parse_args()
    
    # Print welcome message
    print("\n" + "="*70)
    print("🦖 GROK 3 BEAST MODE ACTIVATED 🦖")
    print("Starting GrokBeast v5 - Ready to hunt problems!")
    print("="*70 + "\n")
    
    if args.web:
        print(f"Starting web interface on port {args.port}...")
        print(f"Connect to http://localhost:{args.port} to interact!")
        print("Web interface launched! Let's get started!\n")
        start_web_server(args.port)
    elif args.command:
        print(f"Executing command: {args.command}")
        try:
            command = parse_chat_instruction(args.command)
            with open(COMMANDS_FILE, 'w') as f:
                json.dump(command, f)
            
            print(f"Command sent: {json.dumps(command, indent=2)}")
            
            # Wait for response
            response = wait_for_response(command)
            print(f"Response received: {json.dumps(response, indent=2)}")
            
            # Print success message
            print("\nCOMMAND EXECUTED SUCCESSFULLY! 🔥")
            if response.get("result") and response.get("status") == "success":
                print("Mission accomplished!")
            else:
                print("Operation completed with some issues. Check the response for details.")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            print("\nOperation failed. Please try again with different wording.")
    else:
        print("Interactive console mode - type your commands!")
        print("Type 'exit' to quit.\n")
        
        try:
            while True:
                user_input = input("You: ")
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("\nShutting down... Goodbye!")
                    break
                
                # Get a response to the input
                try:
                    from agent_model import AgentModel
                    agent = AgentModel(model_id="gpt2")
                    response = agent.chat_response(user_input)
                    print(f"Grok 3: {response}")
                except ImportError:
                    print("Grok 3: Can't access the language model right now!")
                
                # Parse and execute command
                try:
                    command = parse_chat_instruction(user_input)
                    
                    print(f"\nExecuting command: {json.dumps(command, indent=2)}")
                    
                    with open(COMMANDS_FILE, 'w') as f:
                        json.dump(command, f)
                    
                    # Wait for response
                    response = wait_for_response(command)
                    if response.get("status") == "success":
                        print("Command executed successfully! 🔥")
                    else:
                        print(f"Command error: {response.get('error', 'Unknown error')}")
                    
                except Exception as e:
                    print(f"Error executing command: {str(e)}")
        
        except KeyboardInterrupt:
            print("\nShutting down... Goodbye!")

def start_web_server(port):
    """Start a Flask web server for command input"""
    try:
        from flask import Flask, request, jsonify, render_template
        
        app = Flask(__name__, 
                   template_folder=str(BASE_DIR / "templates"),
                   static_folder=str(BASE_DIR / "static"))
        
        @app.route('/')
        def home():
            return render_template('index.html')
        
        @app.route('/api/chat', methods=['POST'])
        def chat():
            try:
                data = request.json
                user_message = data.get('message', '').strip()
                
                if not user_message:
                    return jsonify({
                        'response': "Please enter a message so I can help you!",
                        'command': None
                    })
                
                # Initialize the agent model for responses
                from agent_model import AgentModel
                agent = AgentModel(model_id="gpt2")
                
                # Check if this is a command first
                command = None
                command_keywords = ['hunt', 'search', 'find', 'tweet', 'status', 'start', 'check', 'run', 'execute']
                if any(cmd in user_message.lower() for cmd in command_keywords):
                    command = parse_chat_instruction(user_message)
                
                # Generate a response with error handling
                try:
                    response = agent.chat_response(user_message)
                    
                    # Safety checks on response
                    if not response or len(response) < 5:
                        response = "Ready to help! What would you like me to do?"
                    
                    # Prevent recursive prefixes
                    import re
                    response = re.sub(r'(Grok 3:?\s*)+', '', response)
                    
                    # Limit response length
                    if len(response) > 500:
                        response = response[:497] + "..."
                except Exception as e:
                    print(f"Error generating response: {str(e)}")
                    response = "Error generating response. Please try again."
                
                return jsonify({
                    'response': response,
                    'command': command
                })
            except Exception as e:
                print(f"Error in chat endpoint: {str(e)}")
                return jsonify({
                    'response': f"Error: {str(e)[:50]}... Please try again.",
                    'command': None
                })
                
        @app.route('/api/command', methods=['POST'])
        def process_command():
            try:
                data = request.json
                instruction = data.get('instruction')
                command = data.get('command')
                
                # If we received a raw instruction, parse it
                if instruction and not command:
                    command = parse_chat_instruction(instruction)
                
                if not command:
                    return jsonify({
                        "error": "No valid command or instruction provided"
                    })
                
                # Save command to history
                save_command_history(command)
                
                # Write command to file
                with open(COMMANDS_FILE, 'w') as f:
                    json.dump(command, f, indent=2)
                
                # Wait for response
                response = wait_for_response(command)
                
                # Style the response
                if response.get("result") and isinstance(response["result"], dict):
                    if "problems" in response["result"]:
                        problems = response["result"]["problems"]
                        if problems and isinstance(problems, list):
                            for problem in problems:
                                if "tweet" in problem and not any(marker in problem["tweet"] for marker in ["Here", "Analysis", "Update", "Status"]):
                                    from agent_model import AgentModel
                                    agent = AgentModel()
                                    problem["tweet"] = agent.grok_speak("tweet", problem["tweet"])
                
                return jsonify(response)
            except Exception as e:
                print(f"Error processing command: {str(e)}")
                return jsonify({
                    "error": f"Error processing command: {str(e)}"
                })
        
        @app.route('/api/history', methods=['GET'])
        def get_history():
            history = load_command_history()
            return jsonify(history)
        
        print(f"🦖 GrokBeast v5 running at http://localhost:{port}")
        app.run(host='0.0.0.0', port=port)
        
    except ImportError:
        print("Flask is required for web server mode. Install with: pip install flask")
        return

if __name__ == "__main__":
    main() 