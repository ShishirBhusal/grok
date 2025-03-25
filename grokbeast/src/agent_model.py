import os
import json
import logging
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from typing import Optional, Dict, Any
import torch
import random
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GrokBeast")

# File paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "config" / "config.json"
COMMAND_EXAMPLES_FILE = BASE_DIR / "config" / "command_examples.json"

class GrokAgent:
    """GrokBeast AI agent for problem hunting and command generation"""
    
    def __init__(self):
        self.use_fallback = False
        self.device = "cuda" if os.getenv("GROK_USE_CUDA", "1") == "1" else "cpu"
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.personality_templates = {}
        self.fallback_responses = {}
        
        # Check if fallback mode is enabled
        if os.getenv("GROK_USE_FALLBACK") == "1":
            logger.info("Starting GrokBeast in fallback mode")
            self.use_fallback = True
            self._setup_templates()
            return
            
        try:
            self._setup_templates()
            self._load_model()
        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            self.use_fallback = True
            
    def _setup_templates(self):
        """Set up personality templates and fallback responses"""
        # Personality templates
        self.grok_templates = {
            "problem_intros": [
                "Found this interesting problem: ",
                "Users are reporting: ",
                "Problem detected: ",
                "Issue found: ",
                "Pain point identified: "
            ],
            "success_phrases": [
                "Task completed!",
                "Mission accomplished!",
                "Operation successful!",
                "Goal achieved!",
                "Objective reached!"
            ],
            "hunting_phrases": [
                "Scanning for problems...",
                "Problem hunting activated",
                "Searching for issues...",
                "Analyzing user feedback...",
                "Hunting mode: active"
            ],
            "tweet_intros": [
                "Breaking news: ",
                "Update: ",
                "Alert: ",
                "Report: ",
                "Analysis: "
            ],
            "chat_responses": [
                "Here's what I found: {msg}",
                "Analysis complete: {msg}",
                "Results: {msg}",
                "Update: {msg}",
                "Status: {msg}",
            ],
            "chat_templates": [
                "I'm analyzing this {topic} situation",
                "Processing {topic} data",
                "Handling {topic} request",
                "Engaging with {topic}",
                "Processing {topic} information",
                "Analyzing {topic} data",
                "Working on {topic}",
                "Processing {topic} request"
            ]
        }
        
        # Add fallback responses for common user messages
        self.fallback_responses = {
            "hello": ["Hello! How can I help you today?", 
                    "Greetings! What would you like me to do?",
                    "Hi there! Ready to assist!"],
            "help": ["I can help you hunt problems, tweet, or chat. What would you like?",
                    "I'm here to help! Want me to find problems? Hunt bugs? Just say the word!",
                    "I can hunt problems, tweet, or chat - what would you prefer?"],
            "thanks": ["You're welcome!",
                    "Glad I could help!",
                    "Anytime!"],
            "status": ["All systems operational",
                    "Everything is running smoothly",
                    "All functions at 100%"]
        }
    
    def grok_speak(self, message_type, base_text=None):
        """Convert standard text to personality style text
        
        Args:
            message_type (str): Type of message (problem, success, hunting, tweet)
            base_text (str): Text to convert
            
        Returns:
            str: Styled text
        """
        # Safety for None values
        if base_text is None:
            if message_type == "success":
                return random.choice(self.grok_templates["success_phrases"])
            elif message_type == "hunting":
                return random.choice(self.grok_templates["hunting_phrases"])
            else:
                return "System ready"
        
        if message_type == "problem" and base_text:
            return random.choice(self.grok_templates["problem_intros"]) + base_text
        elif message_type == "success":
            return random.choice(self.grok_templates["success_phrases"])
        elif message_type == "hunting":
            return random.choice(self.grok_templates["hunting_phrases"])
        elif message_type == "tweet" and base_text:
            # Add emphasis and hashtags
            words = base_text.split()
            if len(words) > 3:
                # Capitalize 1-3 random words for emphasis
                for _ in range(min(3, len(words))):
                    idx = random.randint(0, len(words) - 1)
                    if len(words[idx]) > 3:  # Only capitalize substantial words
                        words[idx] = words[idx].upper()
            
            # Add hashtags at the end if none exist
            if "#" not in base_text:
                hashtags = ["#GrokBeast", "#ProblemHunting", "#AI", "#Tech"]
                random.shuffle(hashtags)
                words.extend(hashtags[:2])  # Add 2 random hashtags
            
            tweet = random.choice(self.grok_templates["tweet_intros"]) + " ".join(words)
            
            # Occasionally add emoji
            if random.random() < 0.3:
                tweet = "🔍 " + tweet
            
            return tweet
        else:
            return base_text
    
    def generate(self, prompt, max_length=512, temperature=0.7, top_p=0.9, grok_style=False):
        """Generate text from a prompt
        
        Args:
            prompt (str): Input prompt
            max_length (int): Maximum length of generated text
            temperature (float): Sampling temperature
            top_p (float): Nucleus sampling parameter
            grok_style (bool): Whether to apply personality style to the output
            
        Returns:
            str: Generated text
        """
        try:
            if self.pipeline:
                # Add system prompt if grok_style is True
                if grok_style:
                    grok_prompt = (
                        "You are an energetic AI assistant. "
                        "Keep responses short, punchy and full of energy.\n\n"
                        f"Prompt: {prompt}\n\nResponse:"
                    )
                else:
                    grok_prompt = prompt
                
                # Use shorter sequences and simpler parameters
                response = self.pipeline(
                    grok_prompt,
                    max_length=min(max_length, 256),  # Limit max length
                    do_sample=True,
                    temperature=temperature,
                    num_return_sequences=1,
                )[0]["generated_text"]
                
                # Return only the newly generated text (remove the prompt)
                generated_text = response[len(grok_prompt):].strip()
                
                # Apply style transformation if needed
                if grok_style and not generated_text.startswith(("Here", "Analysis", "Update", "Status")):
                    # If the model didn't generate in style, apply our template
                    generated_text = self.grokify_text(generated_text)
                
                return generated_text
            else:
                # Fallback simple response
                fallbacks = [
                    "Task completed successfully!",
                    "Operation finished!",
                    "Request processed!",
                    "Task handled!",
                    "Operation complete!"
                ]
                return random.choice(fallbacks)
        except Exception as e:
            logger.error(f"Error in text generation: {e}")
            return f"Error encountered: {str(e)}"
    
    def grokify_text(self, text):
        """Convert regular text to personality style
        
        Args:
            text (str): Regular text
            
        Returns:
            str: Styled text
        """
        # Add intros
        intros = ["Here's what I found: ", "Analysis: ", "Update: ", "Status: ", "Results: "]
        
        # Add emphasis
        text = text.replace(".", "!").replace(",", " -")
        
        # Uppercase random words for emphasis (about 20% of words)
        words = text.split()
        for i in range(len(words)):
            if random.random() < 0.2 and len(words[i]) > 3:
                words[i] = words[i].upper()
        
        # Add endings
        endings = [" Task complete!", " Operation successful!", " Analysis complete!", " Update complete!", ""]
        
        return random.choice(intros) + " ".join(words) + random.choice(endings)
            
    def hunt_problems(self, source_text, count=3):
        """Extract problems from source text
        
        Args:
            source_text (str): Text to extract problems from
            count (int): Number of problems to extract
            
        Returns:
            list: List of extracted problems
        """
        # Instead of complex generation, extract problems using a rule-based approach
        problems = []
        
        # Look for problem indicators in the text
        lines = source_text.split('\n')
        for line in lines:
            if any(kw in line.lower() for kw in ["problem", "pain", "frustrat", "struggle", "need", "can't", "difficult"]):
                problem_text = line.strip()
                # Remove numbering and quotes
                for prefix in ["- ", "1. ", "2. ", "3. ", "4. ", "5. ", '"', "'"]:
                    if problem_text.startswith(prefix):
                        problem_text = problem_text[len(prefix):].strip()
                
                if len(problem_text) > 10:  # Ensure it's a substantial problem
                    pain_level = random.randint(5, 9)  # Random pain level
                    problem_data = {
                        "problem": problem_text,
                        "pain": pain_level,
                        "reach": random.choice(["Consumer", "SMB", "Enterprise"]),
                        "grok_comment": self.grok_speak("problem", problem_text)
                    }
                    problems.append(problem_data)
            
            if len(problems) >= count:
                break
                        
        # If we don't have enough problems, create some generic ones
        while len(problems) < count:
            generic_problem = f"Generic problem #{len(problems)+1}"
            problems.append({
                "problem": generic_problem,
                "pain": 5,
                "reach": "General",
                "grok_comment": self.grok_speak("problem", generic_problem)
            })
            
        return problems

    def rank_problems(self, problems):
        """Rank a list of problems by importance
        
        Args:
            problems (list): List of problem dictionaries
            
        Returns:
            list: Ranked list of problems
        """
        if not problems:
            return []
            
        # Simple sorting by pain level
        ranked = sorted(problems, key=lambda x: x.get("pain", 0), reverse=True)
        
        # Add comments about the ranking
        for i, problem in enumerate(ranked):
            rank_comment = ""
            if i == 0:
                rank_comment = f"Top priority! Pain level: {problem['pain']}/10"
            elif i == 1:
                rank_comment = f"Second priority! Pain level: {problem['pain']}/10"
            else:
                rank_comment = f"Problem #{i+1} - Pain level: {problem['pain']}/10"
            
            problem["rank_comment"] = rank_comment
            
        return ranked
            
    def create_tweet(self, problem):
        """Create a tweet about a problem
        
        Args:
            problem (dict): Problem dictionary
            
        Returns:
            str: Tweet text
        """
        # Simple template-based tweet generation
        templates = [
            "Are you experiencing {problem}? This affects many {reach} users. What solutions have you found?",
            "Many {reach} users report: {problem}. How does this impact you?",
            "{problem} - this affects {reach} users daily. What's your experience?",
            "Problem identified: {problem}. Pain level: {pain}/10. Does this resonate with {reach} users?"
        ]
        
        template = random.choice(templates)
        tweet_base = template.format(
            problem=problem.get("problem", "this problem"),
            pain=problem.get("pain", 5),
            reach=problem.get("reach", "General")
        )
        
        # Apply style to the tweet
        tweet = self.grok_speak("tweet", tweet_base)
        
        # Ensure it's within Twitter limits
        return tweet[:280]
    
    def chat_response(self, user_input):
        """Generate a chat response
        
        Args:
            user_input (str): User's chat message
            
        Returns:
            str: Response
        """
        # Clean the input for safety
        clean_input = user_input.strip().lower()
        
        # Check for fallback responses based on keywords
        for key, responses in self.fallback_responses.items():
            if key in clean_input:
                return random.choice(responses)
        
        # If we're in fallback mode, use template-based responses
        if self.use_fallback or not self.pipeline:
            # Extract topic keywords from user input
            words = clean_input.split()
            nouns = [w for w in words if len(w) > 3 and w not in ["what", "when", "where", "which", "who", "why", "how"]]
            
            # Default topic if no good keywords found
            topic = "request" if not nouns else random.choice(nouns)
            
            # Generate a response from templates
            template = random.choice(self.grok_templates["chat_templates"])
            response = template.format(topic=topic)
            wrapper = random.choice(self.grok_templates["chat_responses"])
            return wrapper.format(msg=response)
            
        # Use the actual model if available
        try:
            # Create a simple prompt with the system message and user input
            prompt = f"You are an energetic AI assistant. Keep responses short and engaging.\n\nUser: {clean_input}\n\nResponse:"
            
            # Generate response
            response = self.pipeline(
                prompt,
                max_length=len(prompt) + 150,  # Limit max length
                do_sample=True,
                temperature=0.8,
                num_return_sequences=1,
            )[0]["generated_text"]
            
            # Extract only the response part
            generated_text = response.split("Response:")[-1].strip()
            
            # If the response doesn't have energy, apply our template
            if not any(marker in generated_text for marker in ["Here", "Analysis", "Update", "Status"]):
                generated_text = self.grokify_text(generated_text)
            
            # Clean up any recursive prefixes that might have slipped through
            generated_text = re.sub(r'(Grok 3:?\s*)+', '', generated_text)
            
            # Limit response length
            if len(generated_text) > 500:
                generated_text = generated_text[:497] + "..."
                
            return generated_text
        except Exception as e:
            logger.error(f"Error in chat response: {e}")
            return f"Error encountered: {str(e)}"


# Test the model
if __name__ == "__main__":
    agent = GrokAgent()
    print(f"Model initialized: {agent.model_id} on {agent.device}")
    
    # Test problem hunting
    test_text = """
    Many developers struggle with debugging complex code. They often waste hours trying to find simple issues.
    Project managers can't accurately estimate how long tasks will take. This leads to missed deadlines.
    Remote teams have difficulty collaborating effectively across time zones.
    """
    
    problems = agent.hunt_problems(test_text)
    print("\nExtracted problems:")
    for p in problems:
        print(f"- {p['grok_comment']}")
    
    # Test ranking
    ranked = agent.rank_problems(problems)
    print("\nRanked problems:")
    for p in ranked:
        print(f"- {p['rank_comment']}")
    
    # Test tweet creation
    if problems:
        tweet = agent.create_tweet(problems[0])
        print(f"\nGenerated tweet: {tweet}")
    
    # Test chat response
    chat_response = agent.chat_response("Can you hunt for some bugs?")
    print(f"\nChat response: {chat_response}") 