"""
Intent Recognition System
Understands user commands in multiple languages without LLM training
"""

import re
from typing import Dict, List, Tuple, Optional
from difflib import get_close_matches


class IntentRecognizer:
    """
    Recognizes user intent from natural language commands.
    Handles English, Hindi, and Hinglish without requiring LLM training.
    """
    
    def __init__(self):
        # Intent patterns: maps intents to trigger keywords
        self.intent_patterns = {
            'open_app': {
                'english': ['open', 'launch', 'start', 'run', 'execute'],
                'hindi': ['kholo', 'chalao', 'shuru', 'karo', 'kro', 'on'],
                'hinglish': ['khol do', 'chalu karo', 'on karo', 'on kro']
            },
            'close_app': {
                'english': ['close', 'quit', 'exit', 'terminate', 'kill'],
                'hindi': ['band', 'bandh', 'bandh karo', 'band karo', 'off']
            },
            'search': {
                'english': ['search', 'google', 'find', 'look for', 'lookup'],
                'hindi': ['dhundo', 'khojo', 'search karo', 'dhundho']
            },
            'volume': {
                'english': ['volume', 'sound'],
                'hindi': ['awaaz', 'awaz', 'volume']
            }
        }
        
        # App name variations and aliases
        self.app_aliases = {
            'whatsapp': ['whatsapp', 'whats app', 'whats', 'wa', 'whatsap'],
            'chrome': ['chrome', 'google chrome', 'browser'],
            'notepad': ['notepad', 'note pad', 'text editor'],
            'calculator': ['calculator', 'calc', 'kalkulator'],
            'spotify': ['spotify', 'music', 'spot'],
            'excel': ['excel', 'ms excel', 'spreadsheet'],
            'word': ['word', 'ms word', 'document'],
            'powerpoint': ['powerpoint', 'ppt', 'presentation'],
            'vlc': ['vlc', 'vlc player', 'video player'],
            'telegram': ['telegram', 'tele'],
            'discord': ['discord', 'disc'],
            'vscode': ['vscode', 'vs code', 'visual studio code', 'code'],
            'brave': ['brave', 'brave browser'],
            'firefox': ['firefox', 'fire fox', 'mozilla'],
            'edge': ['edge', 'microsoft edge'],
            'paint': ['paint', 'mspaint', 'ms paint'],
            'photoshop': ['photoshop', 'ps', 'adobe photoshop'],
            'outlook': ['outlook', 'email', 'mail'],
            'teams': ['teams', 'microsoft teams'],
            'zoom': ['zoom', 'zoom meeting'],
            'obs': ['obs', 'obs studio'],
            'steam': ['steam', 'steam app'],
            'youtube': ['youtube', 'you tube', 'yt']
        }
        
        # Build reverse lookup for quick access
        self.alias_to_canonical = {}
        for canonical_name, aliases in self.app_aliases.items():
            for alias in aliases:
                self.alias_to_canonical[alias.lower()] = canonical_name
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text by removing special characters and extra spaces.
        """
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove punctuation except hyphens and underscores
        text = re.sub(r'[^\w\s\-_]', ' ', text)
        
        # Normalize multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def extract_intent(self, command: str) -> Tuple[Optional[str], Dict]:
        """
        Extract intent from command.
        Returns: (intent_type, context_dict)
        """
        normalized = self.normalize_text(command)
        words = normalized.split()
        
        # Check for each intent pattern
        for intent, patterns in self.intent_patterns.items():
            for lang, keywords in patterns.items():
                for keyword in keywords:
                    # Handle multi-word keywords
                    if ' ' in keyword:
                        if keyword in normalized:
                            return intent, {'trigger': keyword, 'language': lang}
                    else:
                        if keyword in words:
                            return intent, {'trigger': keyword, 'language': lang}
        
        return None, {}
    
    def extract_app_name(self, command: str, intent: str = None) -> Optional[str]:
        """
        Extract app name from command, handling various formats.
        """
        normalized = self.normalize_text(command)
        
        # Remove common filler words
        filler_words = ['please', 'karo', 'kro', 'do', 'kar', 'the', 'a', 'an']
        
        # If intent is open_app, remove action words
        if intent == 'open_app':
            action_words = ['open', 'launch', 'start', 'run', 'kholo', 'chalao', 
                          'chalu', 'shuru', 'on', 'karo', 'kro']
            
            # Create pattern to extract app name
            for action in action_words:
                # Pattern: "action + app_name" or "app_name + action"
                pattern1 = rf'{action}\s+(.+)'
                pattern2 = rf'(.+)\s+{action}'
                
                match = re.search(pattern1, normalized)
                if match:
                    app_candidate = match.group(1).strip()
                    # Remove trailing filler words
                    for filler in filler_words:
                        app_candidate = app_candidate.replace(filler, '').strip()
                    
                    if app_candidate:
                        return self.normalize_app_name(app_candidate)
                
                match = re.search(pattern2, normalized)
                if match:
                    app_candidate = match.group(1).strip()
                    for filler in filler_words:
                        app_candidate = app_candidate.replace(filler, '').strip()
                    
                    if app_candidate:
                        return self.normalize_app_name(app_candidate)
        
        # Fallback: Try to find any known app name in the command
        return self.find_app_in_text(normalized)
    
    def normalize_app_name(self, app_name: str) -> str:
        """
        Normalize app name to canonical form using fuzzy matching.
        Handles misspellings, spaces, and variations.
        """
        app_name = app_name.lower().strip()
        
        # Direct match in alias lookup
        if app_name in self.alias_to_canonical:
            return self.alias_to_canonical[app_name]
        
        # Remove spaces and try again (whats app -> whatsapp)
        no_space = app_name.replace(' ', '')
        if no_space in self.alias_to_canonical:
            return self.alias_to_canonical[no_space]
        
        # Try fuzzy matching against all aliases
        all_aliases = list(self.alias_to_canonical.keys())
        close_matches = get_close_matches(app_name, all_aliases, n=1, cutoff=0.7)
        
        if close_matches:
            return self.alias_to_canonical[close_matches[0]]
        
        # Try fuzzy matching without spaces
        close_matches = get_close_matches(no_space, all_aliases, n=1, cutoff=0.7)
        if close_matches:
            return self.alias_to_canonical[close_matches[0]]
        
        # If no match found, return original (cleaned)
        return app_name
    
    def find_app_in_text(self, text: str) -> Optional[str]:
        """
        Find any known app name in the text.
        """
        text_lower = text.lower()
        
        # Try to find exact matches first
        for canonical_name, aliases in self.app_aliases.items():
            for alias in aliases:
                if alias in text_lower:
                    return canonical_name
        
        # Try fuzzy matching on individual words
        words = text_lower.split()
        for word in words:
            if len(word) > 2:  # Ignore very short words
                normalized = self.normalize_app_name(word)
                if normalized in self.app_aliases:
                    return normalized
        
        # Try multi-word combinations
        for i in range(len(words)):
            for j in range(i + 1, min(i + 4, len(words) + 1)):
                phrase = ' '.join(words[i:j])
                normalized = self.normalize_app_name(phrase)
                if normalized in self.app_aliases:
                    return normalized
        
        return None
    
    def parse_command(self, command: str) -> Dict:
        """
        Parse a natural language command into structured format.
        
        Returns:
        {
            'intent': 'open_app',
            'app_name': 'whatsapp',
            'original_command': 'whatsapp kholo',
            'confidence': 0.95
        }
        """
        result = {
            'intent': None,
            'app_name': None,
            'original_command': command,
            'confidence': 0.0,
            'normalized_command': self.normalize_text(command)
        }
        
        # Extract intent
        intent, context = self.extract_intent(command)
        result['intent'] = intent
        result['context'] = context
        
        if intent:
            result['confidence'] += 0.5
            
            # Extract app name for open_app intent
            if intent == 'open_app':
                app_name = self.extract_app_name(command, intent)
                result['app_name'] = app_name
                
                if app_name:
                    # Check if it's a known app
                    if app_name in self.app_aliases:
                        result['confidence'] += 0.45
                    else:
                        result['confidence'] += 0.25
        
        return result
    
    def add_app_alias(self, canonical_name: str, aliases: List[str]):
        """
        Add new app alias dynamically.
        Useful for learning user-specific app names.
        """
        canonical_name = canonical_name.lower()
        
        if canonical_name not in self.app_aliases:
            self.app_aliases[canonical_name] = []
        
        for alias in aliases:
            alias_lower = alias.lower()
            if alias_lower not in self.app_aliases[canonical_name]:
                self.app_aliases[canonical_name].append(alias_lower)
                self.alias_to_canonical[alias_lower] = canonical_name


# Example usage and tests
if __name__ == "__main__":
    recognizer = IntentRecognizer()
    
    # Test cases
    test_commands = [
        "open whatsapp",
        "whatsapp kholo",
        "whatsapp on kro",
        "whats app kholo",
        "chrome open karo",
        "calculator chalao",
        "band karo notepad",
        "close chrome",
        "google search python",
        "volume badhao",
        "awaaz kam karo",
        "spotify on karo"
    ]
    
    print("Intent Recognition Tests:\n" + "="*50)
    for cmd in test_commands:
        result = recognizer.parse_command(cmd)
        print(f"\nCommand: '{cmd}'")
        print(f"  Intent: {result['intent']}")
        print(f"  App: {result['app_name']}")
        print(f"  Confidence: {result['confidence']:.2f}")
