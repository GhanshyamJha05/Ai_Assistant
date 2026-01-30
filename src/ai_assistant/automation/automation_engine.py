"""
Automation Engine - Multi-Strategy UI Automation
Provides multiple strategies to interact with Windows applications.
Automatically falls back to alternative methods if primary method fails.
"""

import logging
import time
from typing import Optional, Tuple, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class AutomationEngine:
    """
    Multi-strategy automation engine for Windows applications.
    
    Strategies (in order of preference):
    1. pywinauto (UI Automation) - Best for Windows apps
    2. pyautogui (Coordinate-based) - Fallback for simple actions
    3. Computer Vision (Template matching) - When text-based fails
    4. Accessibility API - For complex UI trees
    
    Each method automatically falls back to the next if it fails.
    """
    
    def __init__(self):
        """Initialize automation engine with all available strategies."""
        logger.info("Initializing Automation Engine")
        
        # Check availability of each strategy
        self.pywinauto_available = self._check_pywinauto()
        self.pyautogui_available = self._check_pyautogui()
        self.cv_available = self._check_cv()
        
        logger.info(f"Available strategies: "
                   f"pywinauto={self.pywinauto_available}, "
                   f"pyautogui={self.pyautogui_available}, "
                   f"cv={self.cv_available}")
    
    def _check_pywinauto(self) -> bool:
        """Check if pywinauto is available."""
        try:
            import pywinauto
            return True
        except ImportError:
            logger.warning("pywinauto not available")
            return False
    
    def _check_pyautogui(self) -> bool:
        """Check if pyautogui is available."""
        try:
            import pyautogui
            return True
        except ImportError:
            logger.warning("pyautogui not available")
            return False
    
    def _check_cv(self) -> bool:
        """Check if computer vision libraries are available."""
        try:
            import cv2
            import numpy as np
            from PIL import Image
            return True
        except ImportError:
            logger.warning("Computer vision libraries not available")
            return False
    
    # ===== STRATEGY 1: pywinauto (Windows UI Automation) =====
    
    def find_window(self, title_pattern: str, exact_match: bool = False):
        """
        Find application window by title.
        
        Args:
            title_pattern: Title or part of title to search for
            exact_match: If True, requires exact match
        
        Returns:
            Window object or None
        """
        if not self.pywinauto_available:
            return None
        
        try:
            from pywinauto import Application
            from pywinauto.findwindows import ElementNotFoundError
            
            # Try UIA backend first (better for modern apps)
            try:
                if exact_match:
                    app = Application(backend="uia").connect(title=title_pattern, timeout=5)
                else:
                    app = Application(backend="uia").connect(title_re=f".*{title_pattern}.*", timeout=5)
                
                return app.top_window()
            
            except:
                # Fallback to win32 backend (older apps)
                try:
                    if exact_match:
                        app = Application(backend="win32").connect(title=title_pattern, timeout=5)
                    else:
                        app = Application(backend="win32").connect(title_re=f".*{title_pattern}.*", timeout=5)
                    
                    return app.top_window()
                except:
                    pass
            
            return None
        
        except Exception as e:
            logger.debug(f"Failed to find window '{title_pattern}': {e}")
            return None
    
    def find_element(self, window, element_type: str, text: str = None, auto_id: str = None):
        """
        Find UI element in window.
        
        Args:
            window: Window object from find_window()
            element_type: Type of element (Button, Edit, List, etc.)
            text: Text to search for (optional)
            auto_id: Automation ID (optional)
        
        Returns:
            Element object or None
        """
        if not self.pywinauto_available or not window:
            return None
        
        try:
            # Build search criteria
            criteria = {'control_type': element_type}
            
            if text:
                criteria['title'] = text
            
            if auto_id:
                criteria['auto_id'] = auto_id
            
            # Search for element
            element = window.child_window(**criteria)
            
            return element if element.exists() else None
        
        except Exception as e:
            logger.debug(f"Failed to find element (type={element_type}, text={text}): {e}")
            return None
    
    def click_element(self, element) -> bool:
        """
        Click UI element.
        
        Args:
            element: Element to click
        
        Returns:
            True if successful, False otherwise
        """
        if not element:
            return False
        
        try:
            element.click()
            time.sleep(0.3)  # Small delay for UI to respond
            return True
        
        except Exception as e:
            logger.debug(f"Failed to click element: {e}")
            return False
    
    def type_text(self, element, text: str, interval: float = 0.05) -> bool:
        """
        Type text into element.
        
        Args:
            element: Input element
            text: Text to type
            interval: Delay between keystrokes
        
        Returns:
            True if successful
        """
        if not element:
            return False
        
        try:
            # Clear existing text first
            element.set_focus()
            time.sleep(0.2)
            
            # Type text
            element.type_keys(text, with_spaces=True, pause=interval)
            time.sleep(0.2)
            
            return True
        
        except Exception as e:
            logger.debug(f"Failed to type text: {e}")
            return False
    
    def get_ui_tree(self, window) -> List[Dict[str, Any]]:
        """
        Get all UI elements in window.
        
        Returns:
            List of element dictionaries
        """
        if not self.pywinauto_available or not window:
            return []
        
        elements = []
        try:
            for child in window.descendants():
                try:
                    elements.append({
                        'type': child.element_info.control_type,
                        'name': child.window_text(),
                        'automation_id': child.element_info.automation_id,
                        'visible': child.is_visible(),
                        'enabled': child.is_enabled(),
                        'rectangle': child.rectangle()
                    })
                except:
                    pass
        except Exception as e:
            logger.debug(f"Failed to get UI tree: {e}")
        
        return elements
    
    def close_window(self, window) -> bool:
        """Close a window."""
        if not window:
            return False
        
        try:
            window.close()
            return True
        except:
            return False
    
    # ===== STRATEGY 2: pyautogui (Coordinate/Keyboard) =====
    
    def click_at_coordinates(self, x: int, y: int) -> bool:
        """Click at specific screen coordinates."""
        if not self.pyautogui_available:
            return False
        
        try:
            import pyautogui
            pyautogui.click(x, y)
            time.sleep(0.3)
            return True
        except Exception as e:
            logger.debug(f"Failed to click at ({x}, {y}): {e}")
            return False
    
    def type_in_active_window(self, text: str) -> bool:
        """
        Type text in currently active window.
        
        This is a generic fallback when we can't identify the input field.
        """
        if not self.pyautogui_available:
            return False
        
        try:
            import pyautogui
            
            # Small delay to ensure window is active
            time.sleep(0.3)
            
            # Type text
            pyautogui.write(text, interval=0.05)
            
            return True
        except Exception as e:
            logger.debug(f"Failed to type in active window: {e}")
            return False
    
    def press_hotkey(self, *keys) -> bool:
        """Press keyboard shortcut."""
        if not self.pyautogui_available:
            return False
        
        try:
            import pyautogui
            pyautogui.hotkey(*keys)
            time.sleep(0.2)
            return True
        except Exception as e:
            logger.debug(f"Failed to press hotkey {keys}: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Press a single key."""
        if not self.pyautogui_available:
            return False
        
        try:
            import pyautogui
            pyautogui.press(key)
            time.sleep(0.2)
            return True
        except Exception as e:
            logger.debug(f"Failed to press key '{key}': {e}")
            return False
    
    # ===== STRATEGY 3: Computer Vision =====
    
    def find_element_by_image(self, template_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        Find UI element using template matching.
        
        Args:
            template_path: Path to template image
            confidence: Matching confidence (0.0 to 1.0)
        
        Returns:
            (x, y) coordinates or None
        """
        if not self.cv_available:
            return None
        
        try:
            import cv2
            import numpy as np
            from PIL import ImageGrab
            
            # Capture screenshot
            screenshot = ImageGrab.grab()
            screenshot_np = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # Load template
            template = cv2.imread(template_path)
            if template is None:
                logger.error(f"Failed to load template: {template_path}")
                return None
            
            # Match template
            result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= confidence:
                # Get center of match
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                return (center_x, center_y)
            
            return None
        
        except Exception as e:
            logger.debug(f"Template matching failed: {e}")
            return None
    
    def read_screen_text(self, region: Tuple[int, int, int, int] = None) -> str:
        """
        Read text from screen using OCR.
        
        Args:
            region: (left, top, right, bottom) or None for full screen
        
        Returns:
            Detected text
        """
        try:
            import pytesseract
            from PIL import ImageGrab
            
            # Capture screenshot
            screenshot = ImageGrab.grab(bbox=region)
            
            # OCR
            text = pytesseract.image_to_string(screenshot)
            
            return text.strip()
        
        except Exception as e:
            logger.debug(f"OCR failed: {e}")
            return ""
    
    def find_text_on_screen(self, search_text: str) -> bool:
        """
        Check if specific text is visible on screen.
        
        Returns:
            True if found, False otherwise
        """
        screen_text = self.read_screen_text()
        return search_text.lower() in screen_text.lower()
    
    # ===== HIGH-LEVEL HELPERS =====
    
    def focus_window(self, window) -> bool:
        """Bring window to foreground."""
        if not window:
            return False
        
        try:
            window.set_focus()
            time.sleep(0.3)
            return True
        except:
            return False
    
    def get_window_rect(self, window) -> Optional[Tuple[int, int, int, int]]:
        """Get window rectangle (left, top, right, bottom)."""
        if not window:
            return None
        
        try:
            rect = window.rectangle()
            return (rect.left, rect.top, rect.right, rect.bottom)
        except:
            return None
    
    def screenshot_window(self, window, save_path: str = None):
        """Take screenshot of window."""
        try:
            from PIL import ImageGrab
            
            rect = self.get_window_rect(window)
            if not rect:
                return None
            
            screenshot = ImageGrab.grab(bbox=rect)
            
            if save_path:
                screenshot.save(save_path)
            
            return screenshot
        
        except Exception as e:
            logger.debug(f"Failed to screenshot window: {e}")
            return None
    
    # ===== SMART FALLBACK METHODS =====
    
    def smart_click(self, window, element_text: str) -> bool:
        """
        Smart click that tries multiple strategies.
        
        1. Try to find element by text (pywinauto)
        2. Try to find button by text
        3. Try template matching if template exists
        4. Give up
        """
        # Strategy 1: Find as generic element
        element = self.find_element(window, "Button", element_text)
        if element:
            if self.click_element(element):
                return True
        
        # Strategy 2: Try different element types
        for elem_type in ["Button", "MenuItem", "CheckBox", "RadioButton"]:
            element = self.find_element(window, elem_type, element_text)
            if element and self.click_element(element):
                return True
        
        # Strategy 3: Template matching (if template exists)
        template_dir = Path(__file__).parent / "templates"
        template_path = template_dir / f"{element_text.lower().replace(' ', '_')}.png"
        
        if template_path.exists():
            coords = self.find_element_by_image(str(template_path))
            if coords:
                return self.click_at_coordinates(*coords)
        
        logger.warning(f"Could not click '{element_text}' using any strategy")
        return False
    
    def smart_type(self, window, text: str, search_for_input: bool = True) -> bool:
        """
        Smart type that tries multiple strategies.
        
        1. Try to find Edit/Input element and type
        2. Fallback to typing in active window
        """
        if search_for_input:
            # Try to find input field
            element = self.find_element(window, "Edit")
            if element:
                if self.type_text(element, text):
                    return True
        
        # Fallback: Type in active window (assumes it's focused)
        self.focus_window(window)
        return self.type_in_active_window(text)


# Singleton instance  
_engine_instance = None

def get_automation_engine() -> AutomationEngine:
    """Get singleton instance of Automation Engine."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = AutomationEngine()
    return _engine_instance
