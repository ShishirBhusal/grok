@echo off
echo =================================================================
echo 🦖 GROK 3 FALLBACK MODE ACTIVATED 🦖
echo =================================================================
echo.
echo Starting Grok 3 in lightweight mode - perfect for multitasking!
echo Web interface will be available at: http://localhost:5000
echo.
echo This mode:
echo - Doesn't load GPT-2 (saves 500MB+ VRAM)
echo - Uses rule-based responses
echo - Perfect for when your GPU is busy
echo.
echo Press Ctrl+C to stop when you're done.
echo.
set GROK_USE_FALLBACK=1
python chat_command_generator.py --web --port=5000 