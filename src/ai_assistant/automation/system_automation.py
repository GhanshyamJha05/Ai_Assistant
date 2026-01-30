"""
System Automation Module

Handles system-level controls:
- Screen Brightness
- WiFi / Network (Toggle, Airplane Mode)
- Volume (Wrapper around existing audio utilities)
- Power (Sleep, Shutdown - optional)
"""

import logging
import subprocess
import platform
import os
from typing import Optional, Dict, Any

# Optional dependencies
try:
    import screen_brightness_control as sbc
    BRIGHTNESS_AVAILABLE = True
except ImportError:
    BRIGHTNESS_AVAILABLE = False
    
try:
    from ai_assistant.modules.core import set_system_volume, get_system_volume, volume_up, volume_down, mute_volume, unmute_volume
    VOLUME_AVAILABLE = True
except ImportError:
    VOLUME_AVAILABLE = False

logger = logging.getLogger(__name__)

class SystemAutomation:
    """
    Handles system settings and controls
    """
    
    def __init__(self):
        """Initialize system automation"""
        logger.info("⚙️ SystemAutomation initialized")
        if not BRIGHTNESS_AVAILABLE:
            logger.warning("⚠️ 'screen_brightness_control' not installed. Brightness control will be limited.")
            
    # ===== BRIGHTNESS =====
    
    def set_brightness(self, level: int) -> bool:
        """
        Set screen brightness (0-100)
        """
        logger.info(f"🔆 Setting brightness to {level}%")
        
        if BRIGHTNESS_AVAILABLE:
            try:
                sbc.set_brightness(level)
                return True
            except Exception as e:
                logger.error(f"❌ Failed to set brightness (sbc): {e}")
        
        # Fallback using PowerShell (WmiMonitorBrightnessMethods)
        # Note: This often requires admin privileges or specific driver support
        try:
            cmd = f"(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})"
            subprocess.run(["powershell", "-Command", cmd], capture_output=True)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set brightness (powershell): {e}")
            return False

    def get_brightness(self) -> int:
        """Get current brightness level"""
        if BRIGHTNESS_AVAILABLE:
            try:
                return sbc.get_brightness()[0]
            except:
                pass
        return -1

    # ===== NETWORK / WIFI =====

    def toggle_wifi(self, enable: bool) -> bool:
        """
        Enable/Disable WiFi
        """
        action = "enable" if enable else "disable"
        logger.info(f"📶 Toggling WiFi: {action}")
        
        try:
            # Use netsh interface
            # Note: Requires knowing the interface name, usually "Wi-Fi"
            cmd = f'netsh interface set interface "Wi-Fi" {action.upper()}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
            else:
                # If "Wi-Fi" failed, try to list interfaces and guess? 
                # For now just log error
                logger.error(f"❌ WiFi toggle failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ WiFi toggle error: {e}")
            return False

    def toggle_airplane_mode(self, enable: bool) -> bool:
        """
        Toggle Airplane Mode (Windows 10/11)
        This is tricky via command line without specialized tools.
        Leaving as a placeholder or using GUI automation fallback if needed.
        """
        logger.warning("⚠️ Airplane mode toggle requires GUI automation or specific registry hacks (unreliable).")
        return False
        
    # ===== VOLUME (Wrapper) =====
    
    def set_volume(self, level: int) -> str:
        if VOLUME_AVAILABLE:
            return set_system_volume(level)
        return "Volume module not available"
        
    def volume_up(self, amount: int = 10) -> str:
        if VOLUME_AVAILABLE:
            return volume_up(amount)
        return "Volume module not available"
        
    def volume_down(self, amount: int = 10) -> str:
        if VOLUME_AVAILABLE:
            return volume_down(amount)
        return "Volume module not available"
