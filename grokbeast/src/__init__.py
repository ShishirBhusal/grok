"""
GrokBeast v5 - A problem hunting AI assistant
"""

from .agent_model import GrokAgent
from .chat_command_generator import parse_chat_instruction, execute_command

__version__ = "5.0.0"
__all__ = ["GrokAgent", "parse_chat_instruction", "execute_command"] 