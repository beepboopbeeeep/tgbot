from typing import Dict, Any
import json
from pathlib import Path

class LanguageManager:
    """Manager for handling multiple languages"""
    
    def __init__(self):
        self.languages = {
            'en': self._load_language('en'),
            'fa': self._load_language('fa')
        }
        self.default_language = 'en'
    
    def _load_language(self, lang_code: str) -> Dict[str, Any]:
        """Load language file"""
        try:
            lang_path = Path(__file__).parent.parent / 'locales' / f'{lang_code}.py'
            with open(lang_path, 'r', encoding='utf-8') as f:
                # Execute the Python file to get the variables
                lang_vars = {}
                exec(f.read(), lang_vars)
                return lang_vars
        except Exception as e:
            print(f"Error loading language {lang_code}: {e}")
            return {}
    
    def get_text(self, key: str, language: str = None, **kwargs) -> str:
        """Get text in specified language"""
        if language is None:
            language = self.default_language
        
        if language not in self.languages:
            language = self.default_language
        
        text = self.languages[language].get(key, key)
        
        # Format text with provided arguments
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    
    def get_button_text(self, button_key: str, language: str = None) -> str:
        """Get button text in specified language"""
        return self.get_text(f'BTN_{button_key.upper()}', language)
    
    def is_supported(self, language: str) -> bool:
        """Check if language is supported"""
        return language in self.languages
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        return {
            'en': 'English',
            'fa': 'فارسی'
        }
    
    def get_language_name(self, code: str) -> str:
        """Get language name by code"""
        return self.get_supported_languages().get(code, code)
    
    def format_list(self, items: list, language: str = None) -> str:
        """Format a list according to language rules"""
        if not items:
            return ""
        
        if len(items) == 1:
            return str(items[0])
        
        if language == 'fa':
            # Persian formatting
            if len(items) == 2:
                return f"{items[0]} و {items[1]}"
            else:
                return ", ".join(items[:-1]) + f" و {items[-1]}"
        else:
            # English formatting
            if len(items) == 2:
                return f"{items[0]} and {items[1]}"
            else:
                return ", ".join(items[:-1]) + f", and {items[-1]}"

# Global language manager instance
language_manager = LanguageManager()

def _(key: str, language: str = None, **kwargs) -> str:
    """Shorthand function for getting text"""
    return language_manager.get_text(key, language, **kwargs)

def get_button_text(button_key: str, language: str = None) -> str:
    """Shorthand function for getting button text"""
    return language_manager.get_button_text(button_key, language)