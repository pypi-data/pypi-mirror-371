# __init__.py
from .client import GoogleTransClient
from .ssml import GoogleTransSSML

# For backward compatibility
GoogleTransTTS = GoogleTransClient

__all__ = ["GoogleTransClient", "GoogleTransSSML", "GoogleTransTTS"]
