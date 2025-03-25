# GrokBeast v5 🦖

A powerful problem-hunting AI assistant that uses local language models to help identify and solve problems. Built with GPT-2 and a rule-based fallback system for maximum reliability.

## Features

- 🤖 Local AI-powered problem hunting
- 🚀 Fast response times with GPT-2
- 💪 Fallback system for low-resource environments
- 🌐 Web interface for easy interaction
- 🔄 Command parsing and execution
- 📊 System status monitoring
- 🎨 Modern, responsive UI

## Requirements

- Python 3.8 or higher
- CUDA-capable GPU (optional, for faster inference)
- 4GB+ RAM
- 2GB+ VRAM (if using GPU)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/grokbeast.git
cd grokbeast
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example environment file and configure it:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage

### Starting the Server

1. Normal mode (with GPT-2):
```bash
python -m grokbeast.src.chat_command_generator
```

2. Fallback mode (rule-based only):
```bash
python -m grokbeast.src.chat_command_generator --fallback
```

3. Using the provided scripts:
- Windows: `scripts\start_grok3.bat` or `scripts\start_grok3_fallback.bat`
- Linux/Mac: `scripts\start_grok3.sh`

### Web Interface

1. Open your browser and navigate to `http://localhost:5000`
2. Use the chat interface to interact with GrokBeast
3. Click "Status" to check system status
4. Click "Hunt Problems" to start a problem hunt

### Command Examples

- `status`: Check system status
- `hunt for 3 problems and tweet the best one`: Start a problem hunt
- `help`: Show available commands
- `clear`: Clear chat history

## Configuration

### Environment Variables

- `GROK_USE_CUDA`: Enable/disable CUDA (1/0)
- `GROK_USE_FALLBACK`: Use rule-based responses only (1/0)
- `GROK_MODEL_ID`: Model ID from Hugging Face
- `GROK_PORT`: Web server port
- `GROK_HOST`: Web server host

### Optional API Keys

If you want to use Twitter integration:
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_SECRET`

## Development

### Project Structure

```
grokbeast/
├── src/                    # Source code
│   ├── __init__.py
│   ├── agent_model.py     # AI model implementation
│   └── chat_command_generator.py  # Command handling
├── config/                # Configuration files
│   ├── config.json       # Main configuration
│   └── command_examples.json  # Example commands
├── scripts/              # Start scripts
│   ├── start_grok3.bat   # Windows start script
│   ├── start_grok3.sh    # Linux/Mac start script
│   └── start_grok3_fallback.bat  # Windows fallback mode
├── static/              # Static files (CSS, JS, etc.)
├── templates/           # HTML templates
├── tests/              # Test files
├── .env.example        # Example environment variables
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── setup.py
```

### Running Tests

```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Hugging Face Transformers](https://github.com/huggingface/transformers)
- Inspired by Grok AI
- Created by Stark 