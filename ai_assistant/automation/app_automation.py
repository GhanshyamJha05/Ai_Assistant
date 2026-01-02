"""
Application Automation Module

Handles automation of Windows applications including:
- Sticky Notes (reading, creating, editing)
- WhatsApp (enhanced message sending)
- Generic window management

Uses combination of:
- pyautogui for GUI automation
- pywinauto for Windows app control
- OCR for text extraction
- TTS for reading content
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any
import subprocess
import tempfile

# Windows automation
try:
    import pyautogui
    import pywinauto
    from pywinauto import Application
    WINDOWS_AUTO_AVAILABLE = True
except ImportError:
    WINDOWS_AUTO_AVAILABLE = False
    print("⚠️ Windows automation not available")

# OCR for reading notes
try:
    import pytesseract
    from PIL import Image, ImageGrab
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ OCR not available")

# Import existing WhatsApp module
try:
    from ai_assistant.modules.whatsapp import send_whatsapp_message
    WHATSAPP_MODULE_AVAILABLE = True
except ImportError:
    WHATSAPP_MODULE_AVAILABLE = False

# TTS for reciting notes
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class AppAutomation:
    """
    Generic application automation handler
    """
    
    def __init__(self):
        """Initialize app automation"""
        self.active_windows = {}
        logger.info("✅ AppAutomation initialized")
    
    def open_app(self, app_name: str) -> bool:
        """
        Open an application
        
        Args:
            app_name: Name of app to open
        
        Returns:
            Success status
        """
        logger.info(f"📱 Opening app: {app_name}")
        
        # Use existing app discovery if available
        try:
            from ai_assistant.automation.app_discovery import find_application, launch_application
            
            app_info = find_application(app_name)
            if app_info:
                return launch_application(app_info['name'])
        except ImportError:
            pass
        
        # Fallback: use subprocess
        try:
            subprocess.Popen(app_name, shell=True)
            time.sleep(2)  # Give app time to open
            logger.info(f"✅ Opened: {app_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to open app: {e}")
            return False
    
    def close_app(self, app_name: str) -> bool:
        """Close an application"""
        # Would implement app closing logic
        pass
    
    def focus_window(self, window_title: str) -> bool:
        """Focus a window by title"""
        if not WINDOWS_AUTO_AVAILABLE:
            return False
        
        try:
            # Find and focus window
            from pywinauto import Desktop
            windows = Desktop(backend="uia").windows()
            
            for window in windows:
                if window_title.lower() in window.window_text().lower():
                    window.set_focus()
                    logger.info(f"✅ Focused window: {window.window_text()}")
                    return True
            
            logger.warning(f"⚠️ Window not found: {window_title}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to focus window: {e}")
            return False


class StickyNotesAutomation(AppAutomation):
    """
    Windows Sticky Notes automation
    """
    
    APP_NAME = "Microsoft.MicrosoftStickyNotes"
    WINDOW_TITLE = "Sticky Notes"
    
    def __init__(self):
        super().__init__()
        self.tts_engine = None
        if TTS_AVAILABLE:
            self.tts_engine = pyttsx3.init()
    
    def open_sticky_notes(self) -> bool:
        """Open Sticky Notes app"""
        logger.info("📝 Opening Sticky Notes...")
        
        # Try to open via start menu search
        try:
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.typewrite('sticky notes', interval=0.1)
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(2)
            
            logger.info("✅ Sticky Notes opened")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to open Sticky Notes: {e}")
            return False
    
    def read_notes(self, speak: bool = False) -> List[str]:
        """
        Read all visible sticky notes using OCR
        
        Args:
            speak: Whether to speak the notes aloud
        
        Returns:
            List of note contents
        """
        if not OCR_AVAILABLE:
            logger.error("❌ OCR not available")
            return []
        
        logger.info("📖 Reading sticky notes...")
        
        try:
            # Focus Sticky Notes window
            self.focus_window(self.WINDOW_TITLE)
            time.sleep(1)
            
            # Take screenshot of entire screen
            screenshot = ImageGrab.grab()
            
            # Use OCR to extract text
            text = pytesseract.image_to_string(screenshot)
            
            # Split into individual notes (basic heuristic)
            notes = [line.strip() for line in text.split('\n') if line.strip()]
            notes = [note for note in notes if len(note) > 3]  # Filter short false positives
            
            logger.info(f"✅ Found {len(notes)} notes")
            
            # Speak notes if requested
            if speak and self.tts_engine and notes:
                for i, note in enumerate(notes, 1):
                    self.tts_engine.say(f"Note {i}: {note}")
                self.tts_engine.runAndWait()
            
            return notes
            
        except Exception as e:
            logger.error(f"❌ Failed to read notes: {e}")
            return []
    
    def create_note(self, content: str) -> bool:
        """
        Create a new sticky note
        
        Args:
            content: Note content
        
        Returns:
            Success status
        """
        logger.info(f"📝 Creating note: {content[:50]}...")
        
        try:
            # Open or focus Sticky Notes
            if not self.focus_window(self.WINDOW_TITLE):
                self.open_sticky_notes()
            
            time.sleep(1)
            
            # Create new note (Ctrl+N)
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(0.5)
            
            # Type content
            pyautogui.typewrite(content, interval=0.05)
            
            logger.info("✅ Note created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create note: {e}")
            return False


class WhatsAppAutomation(AppAutomation):
    """
    Enhanced WhatsApp automation
    """
    
    def send_message(self, contact: str, message: str) -> bool:
        """
        Send WhatsApp message
        
        Args:
            contact: Contact name
            message: Message text
        
        Returns:
            Success status
        """
        logger.info(f"💬 Sending WhatsApp to {contact}")
        
        # Use existing WhatsApp module
        if WHATSAPP_MODULE_AVAILABLE:
            try:
                result = send_whatsapp_message(contact, message)
                logger.info(f"✅ WhatsApp result: {result}")
                return "✅" in result
            except Exception as e:
                logger.error(f"❌ WhatsApp failed: {e}")
                return False
        else:
            logger.error("❌ WhatsApp module not available")
            return False
    
    def send_with_attachment(self, contact: str, message: str, file_path: str) -> bool:
        """Send message with attachment"""
        # Would implement attachment sending
        pass


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test Sticky Notes
    sticky = StickyNotesAutomation()
    
    # Read existing notes
    notes = sticky.read_notes(speak=True)
    print(f"\nFound {len(notes)} notes:")
    for i, note in enumerate(notes, 1):
        print(f"{i}. {note}")
    
    # Create a new note
    # sticky.create_note("Test note from automation")
