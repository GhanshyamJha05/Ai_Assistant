# Dynamic Application Discovery Module
"""
This module scans the system to discover all installed applications
and provides intelligent app launching based on voice commands.
"""

import os
import winreg
import json
import webbrowser
import time
import subprocess
import glob
import json
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
from pathlib import Path
import time
import sqlite3
from typing import Dict, List, Tuple
from datetime import datetime

class AppDiscovery:
    def __init__(self):
        # Get the project root directory (2 levels up from this file)
        project_root = Path(__file__).parent.parent.parent
        config_dir = project_root / "config"
        
        # Ensure config directory exists
        config_dir.mkdir(exist_ok=True)
        
        # Set paths relative to config directory
        self.apps_cache_file = str(config_dir / "discovered_apps.json")
        self.usage_db_file = str(config_dir / "app_usage.db")
        self.apps_database = {}
        self._is_refreshing = False
        self._last_refresh_time = None
        
        # Load cache first for fast startup
        self.load_cache()
        self._init_usage_database()
        
        # Start background refresh
        self._start_background_refresh()
    
    def scan_installed_applications(self) -> Dict[str, str]:
        """
        Scan apps from EXACT same sources as Windows Settings > Apps & Features.
        This is the definitive list of installed applications on Windows.
        
        Discovery Sources (same as Settings):
        1. Registry Uninstall keys (Desktop apps)
        2. AppX/MSIX packages (Store/Modern apps)
        
        WHY THIS IS THE BEST APPROACH:
        - Shows exact same apps as Settings > Apps & Features
        - No missing apps or extra hidden apps
        - Official Windows application registry
        - What users expect to see
        """
        print("⚙️ Scanning from Windows Settings > Apps & Features sources...")
        apps = {}
        
        # Method 1: Registry Uninstall Keys (Desktop Apps)
        print("  📋 Reading Registry Uninstall Keys (Desktop Apps)...")
        apps.update(self._scan_apps_and_features_registry())
        
        # Method 2: AppX Packages (Microsoft Store Apps)
        print("  🏪 Reading AppX Packages (Store Apps)...")
        apps.update(self._scan_appx_packages())
        
        # Save to cache
        self.apps_database = apps
        self.save_cache()
        
        print(f"✅ Discovery complete! Found {len(apps)} apps (same as Settings).")
        return apps
    
    # REMOVED: PowerShell Get-StartApps - not needed, using Windows Settings > Apps & Features sources
    
    def _open_via_windows_search(self, app_name: str) -> bool:
        """
        Fallback method: Open app by typing its name in Windows Search.
        This mimics user behavior: Win Key -> Type Name -> Enter
        """
        if not PYAUTOGUI_AVAILABLE:
            print("  ⚠️ pyautogui not available for Windows Search fallback.")
            return False
            
        print(f"  🔍 Attempting to open '{app_name}' via Windows Search...")
        try:
            # 1. Press Windows Key to open Start Menu
            pyautogui.press('win')
            time.sleep(0.5) # Wait for animation
            
            # 2. Type the application name
            pyautogui.write(app_name, interval=0.05)
            time.sleep(1.0) # Wait for search results to populate
            
            # 3. Press Enter to launch the top result
            pyautogui.press('enter')
            print(f"  ✅ Executed Windows Search launch for '{app_name}'")
            return True
        except Exception as e:
            print(f"  ❌ Windows Search launch failed: {e}")
            return False

    def _scan_apps_and_features_registry(self) -> Dict[str, str]:
        r"""
        Scan Registry Uninstall keys - EXACT same source as Settings > Apps & Features.
        This finds all desktop applications installed via installers.
        
        Registry Locations (same as Windows Settings uses):
        - HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall (64-bit apps)
        - HKLM\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall (32-bit apps)
        - HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall (user apps)
        """
        apps = {}
        
        # Registry paths that Settings > Apps & Features reads from
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        
        for root_key, reg_path in registry_paths:
            try:
                with winreg.OpenKey(root_key, reg_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    # Read DisplayName - this is what shows in Settings
                                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    
                                    # Skip if no name or it's an update/component
                                    if not display_name or any(skip in display_name.lower() for skip in 
                                        ['update', 'hotfix', 'security update', 'kb']):
                                        continue
                                    
                                    # Try to get SystemComponent flag - if 1, it's hidden from Settings
                                    try:
                                        system_component = winreg.QueryValueEx(subkey, "SystemComponent")[0]
                                        if system_component == 1:
                                            continue  # Skip system components
                                    except FileNotFoundError:
                                        pass  # No SystemComponent key means it's visible
                                    
                                    # Try to get ParentKeyName - if exists, it's a sub-component
                                    try:
                                        parent = winreg.QueryValueEx(subkey, "ParentKeyName")[0]
                                        if parent:
                                            continue  # Skip sub-components
                                    except FileNotFoundError:
                                        pass
                                    
                                    # Store the app name (we use Windows Search to launch, so path doesn't matter)
                                    app_key = display_name.lower().strip()
                                    if app_key and app_key not in apps:
                                        apps[app_key] = display_name  # Store display name as "path"
                                        
                                except (FileNotFoundError, OSError):
                                    continue
                        except OSError:
                            continue
            except Exception as e:
                continue  # Skip if can't access registry path
        
        return apps
    
    def _scan_appx_packages(self) -> Dict[str, str]:
        """
        Scan AppX/MSIX packages - Microsoft Store apps (same as Settings > Apps & Features).
        Uses PowerShell Get-AppxPackage which is what Windows Settings uses internally.
        """
        apps = {}
        try:
            # PowerShell command to get AppX packages (same as Settings uses)
            cmd = 'powershell -NoProfile -NonInteractive -Command "Get-AppxPackage | Where-Object {$_.Name -notlike \"*DeletedAllUserPackages*\" -and $_.SignatureKind -eq \"Store\"} | Select-Object Name,PackageFamilyName | ConvertTo-Json"'
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    
                    # Handle single item vs list
                    if isinstance(data, dict):
                        data = [data]
                    
                    for item in data:
                        if 'Name' in item:
                            # Extract friendly name from package name
                            name = item['Name']
                            
                            # Convert package name to friendly display name
                            # e.g., "Microsoft.WindowsCalculator" -> "Calculator"
                            friendly_name = name.split('.')[-1] if '.' in name else name
                            
                            # Remove common suffixes
                            friendly_name = friendly_name.replace('App', '').replace('UWP', '').strip()
                            
                            if friendly_name and len(friendly_name) > 2:
                                app_key = friendly_name.lower()
                                if app_key not in apps:
                                    apps[app_key] = friendly_name
                                    
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"  ⚠️ AppX scan failed: {e}")
        
        return apps
    
    # REMOVED: Start Menu scanning - not needed, using Windows Settings > Apps & Features sources
    
    # REMOVED: Shortcut resolution - not needed, we use Windows Search to launch all apps
    
    def save_cache(self):
        """Save discovered apps to cache file"""
        try:
            with open(self.apps_cache_file, 'w') as f:
                json.dump(self.apps_database, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def load_cache(self):
        """Load discovered apps from cache file"""
        try:
            if os.path.exists(self.apps_cache_file):
                with open(self.apps_cache_file, 'r') as f:
                    data = json.load(f)
                    
                # Handle different cache formats
                if isinstance(data, dict):
                    if 'applications' in data:
                        # New complex format - extract app data
                        self.apps_database = {}
                        for app in data['applications']:
                            app_name = app['name'].lower().replace(' ', '_')
                            self.apps_database[app_name] = app['path']
                    else:
                        # Old simple format - use as is
                        self.apps_database = data
                else:
                    self.apps_database = {}
        except Exception as e:
            print(f"Error loading cache: {e}")
            self.apps_database = {}
    
    def _start_background_refresh(self):
        """Start background thread to refresh app list"""
        import threading
        thread = threading.Thread(target=self._background_refresh, daemon=True)
        thread.start()
    
    def _background_refresh(self):
        """Background refresh of app database"""
        try:
            self._is_refreshing = True
            print("🔄 Background app refresh started...")
            
            # Scan for apps
            new_apps = self.scan_installed_applications()
            
            # Update timestamp
            from datetime import datetime
            self._last_refresh_time = datetime.now()
            
            print(f"✅ Background refresh complete! Found {len(new_apps)} apps")
        except Exception as e:
            print(f"⚠️ Background refresh failed: {e}")
        finally:
            self._is_refreshing = False
    
    def _init_usage_database(self):
        """Initialize SQLite database for tracking app usage."""
        try:
            with sqlite3.connect(self.usage_db_file) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS app_launches (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        app_name TEXT NOT NULL,
                        app_path TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        success BOOLEAN DEFAULT 1
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_app_launches_name 
                    ON app_launches(app_name)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_app_launches_timestamp 
                    ON app_launches(timestamp DESC)
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS app_frequency (
                        app_name TEXT PRIMARY KEY,
                        launch_count INTEGER DEFAULT 0,
                        last_launched DATETIME,
                        avg_daily_launches REAL DEFAULT 0.0
                    )
                """)
                
                conn.commit()
        except Exception as e:
            print(f"Error initializing usage database: {e}")
    
    def track_app_launch(self, app_name: str, app_path: str = "", success: bool = True):
        """Track an application launch for usage statistics."""
        try:
            with sqlite3.connect(self.usage_db_file) as conn:
                # Record launch
                conn.execute("""
                    INSERT INTO app_launches (app_name, app_path, success)
                    VALUES (?, ?, ?)
                """, (app_name, app_path, success))
                
                # Update frequency table
                conn.execute("""
                    INSERT INTO app_frequency (app_name, launch_count, last_launched)
                    VALUES (?, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT(app_name) DO UPDATE SET
                        launch_count = launch_count + 1,
                        last_launched = CURRENT_TIMESTAMP
                """, (app_name,))
                
                conn.commit()
        except Exception as e:
            print(f"Error tracking app launch: {e}")
    
    def get_most_used_apps(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most frequently used applications."""
        try:
            with sqlite3.connect(self.usage_db_file) as conn:
                cursor = conn.execute("""
                    SELECT app_name, launch_count
                    FROM app_frequency
                    ORDER BY launch_count DESC
                    LIMIT ?
                """, (limit,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting most used apps: {e}")
            return []
    
    def get_recent_apps(self, limit: int = 10) -> List[Tuple[str, str]]:
        """Get recently launched applications."""
        try:
            with sqlite3.connect(self.usage_db_file) as conn:
                cursor = conn.execute("""
                    SELECT DISTINCT app_name, MAX(timestamp) as last_time
                    FROM app_launches
                    WHERE success = 1
                    GROUP BY app_name
                    ORDER BY last_time DESC
                    LIMIT ?
                """, (limit,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting recent apps: {e}")
            return []
    
    def _split_camel_case(self, text: str) -> str:
        """Split camelCase and PascalCase words with spaces."""
        import re
        # Insert space before capital letters (except at start)
        result = re.sub(r'(?<!^)(?=[A-Z])', ' ', text)
        result = result.lower()
        
        # Also try to split known compound words in lowercase
        # This handles cases like "microsoftstickynotes" -> "microsoft sticky notes"
        compound_patterns = [
            (r'microsoft', 'microsoft '),
            (r'sticky', ' sticky '),
            (r'notes', ' notes '),
            (r'google', 'google '),
            (r'chrome', ' chrome '),
            (r'spotify', ' spotify '),
            (r'adobe', 'adobe '),
            (r'reader', ' reader '),
            (r'player', ' player '),
            (r'media', ' media '),
            (r'video', ' video '),
            (r'music', ' music '),
        ]
        
        for pattern, replacement in compound_patterns:
            result = re.sub(pattern, replacement, result)
        
        # Clean up extra spaces
        result = ' '.join(result.split())
        return result
    
    def find_app(self, app_name: str) -> str:
        """Find application by name using advanced fuzzy matching with usage-based ranking."""
        app_name_lower = app_name.lower().strip()
        
        # Normalize the search query (remove special chars, handle spaces)
        normalized_query = app_name_lower.replace('.', ' ').replace('_', ' ').replace('-', ' ')
        
        # Get usage statistics for ranking boost
        # Optimization: Don't fetch if no matches found yet
        
        # 0. DIRECT LOOKUP CHECK (Fastest)
        if normalized_query in self.apps_database:
             return self.apps_database[normalized_query]
        
        # 1. Direct Lookup (Legacy/Mapped names)
        # Check standard app names that might not be normalized
        if app_name_lower in self.apps_database:
            return self.apps_database[app_name_lower]
        if app_name in self.apps_database:
            return self.apps_database[app_name]

        # Get usage statistics for ranking boost
        most_used = {name.lower(): count for name, count in self.get_most_used_apps(100)}
        
        matches = []
        
        for db_name, db_path in self.apps_database.items():
            # Normalize database name for comparison
            # First split camelCase, then replace special chars
            normalized_db_name = self._split_camel_case(db_name)
            normalized_db_name = normalized_db_name.replace('.', ' ').replace('_', ' ').replace('-', ' ')
            
            score = self._calculate_match_score(normalized_query, normalized_db_name, most_used.get(db_name, 0))
            if score > 0:
                matches.append((score, db_name, db_path))
        
        if not matches:
            return ""
        
        # Sort by score (highest first)
        matches.sort(reverse=True, key=lambda x: x[0])
        
        # Only return if the score is good enough (minimum threshold of 30)
        best_match = matches[0]
        if best_match[0] >= 30:  # score threshold
            return best_match[2]
        else:
            return ""  # No good match found
    
    def _calculate_match_score(self, query: str, app_name: str, usage_count: int = 0) -> int:
        """Calculate match score for fuzzy search with usage-based ranking."""
        score = 0
        
        # Exact match (highest priority)
        if query == app_name:
            score += 100
        
        # Direct substring match
        if query in app_name:
            score += 50
            # Boost if match is at the start
            if app_name.startswith(query):
                score += 20
        
        # Reverse substring match
        if app_name in query:
            score += 40
        
        # Word-based matching - check if ALL query words are present
        query_words = set(query.split())
        app_words = set(app_name.split())
        
        # Check if all query words exist in app name (important for multi-word searches)
        if query_words and query_words.issubset(app_words):
            score += 80  # High score for containing all words
        
        # Some query words present (partial match)
        common_words = query_words & app_words
        if common_words and not query_words.issubset(app_words):
            score += len(common_words) * 10
        
        # Character-level fuzzy matching (Levenshtein-like)
        if score == 0:  # Only if no other matches
            similarity = self._string_similarity(query, app_name)
            if similarity > 0.7:
                score += int(similarity * 20)
        
        # Boost by usage frequency (logarithmic scale)
        if usage_count > 0:
            import math
            score += int(math.log(usage_count + 1) * 5)
        
        return score
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity (0.0 to 1.0) using simple approach."""
        if not s1 or not s2:
            return 0.0
        
        # Convert to sets of character bigrams
        def get_bigrams(s):
            return set(s[i:i+2] for i in range(len(s) - 1))
        
        bigrams1 = get_bigrams(s1)
        bigrams2 = get_bigrams(s2)
        
        if not bigrams1 or not bigrams2:
            return 0.0
        
        intersection = len(bigrams1 & bigrams2)
        union = len(bigrams1 | bigrams2)
        
        return intersection / union if union > 0 else 0.0
    
    def search_apps(self, query: str, limit: int = 10) -> List[Tuple[str, str, int]]:
        """Search for apps with scoring and ranking."""
        query_lower = query.lower().strip()
        most_used = {name.lower(): count for name, count in self.get_most_used_apps(100)}
        
        matches = []
        for db_name, db_path in self.apps_database.items():
            score = self._calculate_match_score(query_lower, db_name, most_used.get(db_name, 0))
            if score > 0:
                matches.append((db_name, db_path, score))
        
        # Sort by score and return top matches
        matches.sort(reverse=True, key=lambda x: x[2])
        return matches[:limit]
    
    def get_all_apps(self) -> Dict[str, str]:
        """Get all discovered applications"""
        return self.apps_database
    
    def get_apps_for_api(self) -> List[Dict[str, str]]:
        """Get applications formatted for API responses"""
        apps_list = []
        
        # Performance Optimization: Query usage stats ONCE before the loop
        most_used = dict(self.get_most_used_apps(200)) # Increased limit
        
        for app_name, app_path in self.apps_database.items():
            usage_count = most_used.get(app_name, 0)
            
            # Categorize app
            category = self._categorize_app(app_name)
            
            apps_list.append({
                "name": app_name.replace('_', ' ').title(),
                "path": app_path,
                "category": category,
                "usage": usage_count,
                "description": self._generate_description(app_name)
            })
        
        # Sort by usage count
        apps_list.sort(key=lambda x: x['usage'], reverse=True)
        return apps_list
    
    def _categorize_app(self, app_name: str) -> str:
        """Categorize application by name"""
        app_lower = app_name.lower()
        
        if any(word in app_lower for word in ['chrome', 'firefox', 'edge', 'browser']):
            return "Browser"
        elif any(word in app_lower for word in ['notepad', 'word', 'excel', 'powerpoint', 'office', 'sticky', 'onenote']):
            return "Productivity"
        elif any(word in app_lower for word in ['code', 'visual', 'studio', 'terminal', 'cmd', 'powershell']):
            return "Development"
        elif any(word in app_lower for word in ['vlc', 'media', 'music', 'video', 'spotify']):
            return "Media"
        elif any(word in app_lower for word in ['mail', 'discord', 'slack', 'teams']):
            return "Communication"
        elif any(word in app_lower for word in ['calculator', 'notepad', 'paint', 'control', 'task']):
            return "System Tools"
        else:
            return "Other"
    
    def _generate_description(self, app_name: str) -> str:
        """Generate description for application"""
        descriptions = {
            'chrome': 'Google Chrome web browser',
            'firefox': 'Mozilla Firefox web browser',
            'edge': 'Microsoft Edge web browser',
            'notepad': 'Simple text editor',
            'calculator': 'Windows calculator utility',
            'paint': 'Microsoft Paint image editor',
            'word': 'Microsoft Word document editor',
            'excel': 'Microsoft Excel spreadsheet application',
            'powerpoint': 'Microsoft PowerPoint presentation software',
            'code': 'Visual Studio Code editor',
            'terminal': 'Command line interface',
            'cmd': 'Command prompt',
            'powershell': 'PowerShell command interface',
            'vlc': 'VLC multimedia player',
            'spotify': 'Music streaming application',
            'discord': 'Voice and text communication platform',
            'control': 'Windows Control Panel',
            'task_manager': 'Windows Task Manager',
            'file_explorer': 'Windows File Explorer'
        }
        
        app_lower = app_name.lower().replace(' ', '_')
        return descriptions.get(app_lower, f"{app_name.replace('_', ' ').title()} application")

    def refresh_database(self) -> int:
        """Refresh the applications database"""
        old_count = len(self.apps_database)
        self.scan_installed_applications()
        new_count = len(self.apps_database)
        return new_count - old_count# Global instance
app_discovery = AppDiscovery()

def discover_applications() -> str:
    """Main function to discover all applications"""
    try:
        apps = app_discovery.scan_installed_applications()
        return f"Successfully discovered {len(apps)} applications on your system."
    except Exception as e:
        return f"Error during application discovery: {e}"

def smart_open_application(app_name: str) -> str:
    """Intelligently open any application by name with usage tracking."""
    print(f"🚀 Smart app launcher: Looking for '{app_name}'...")
    
    # Validate app_name to prevent injection
    if len(app_name) > 200:
        return "❌ Application name is too long"
    
    # First, try to find in discovered apps
    app_path = app_discovery.find_app(app_name)
    
    if app_path:
        # Check if this is a browser proxy (web app, not native)
        is_browser_proxy = any(x in app_path.lower() for x in ['chrome_proxy', 'chrome.exe --app', 'msedge.exe --app'])
        
        # For Spotify specifically, prefer web version if only browser proxy exists
        if is_browser_proxy and 'spotify' in app_name.lower():
            try:
                import webbrowser
                webbrowser.open('https://open.spotify.com')
                app_discovery.track_app_launch(app_name, 'https://open.spotify.com', success=True)
                return f"✅ Opened {app_name} in web browser (native app not installed)"
            except Exception as e:
                app_discovery.track_app_launch(app_name, "", success=False)
                return f"❌ Failed to open {app_name}: {e}"
        
        try:
            # UNIVERSAL METHOD: Windows Search (Win+Type+Enter)
            # This is the most reliable way to launch ANY app - exactly how users do it manually
            # Works for: Store apps, Desktop apps, PWAs, System apps, everything!
            print(f"  🔍 Launching '{app_name}' via Windows Search (Universal Method)...")
            if app_discovery._open_via_windows_search(app_name):
                app_discovery.track_app_launch(app_name, app_path, success=True)
                return f"✅ Launching {app_name} via Windows Search"
            else:
                # If Windows Search failed (pyautogui not available), return error
                app_discovery.track_app_launch(app_name, app_path, success=False)
                return f"❌ Windows Search unavailable - install pyautogui: pip install pyautogui"
        except Exception as e:
            print(f"  ❌ Launch failed: {e}")
            app_discovery.track_app_launch(app_name, app_path, success=False)
            return f"❌ Failed to launch {app_name}: {e}"
    else:
        # If not found, try Windows Search first (User Requested Fallback)
        if app_discovery._open_via_windows_search(app_name):
            return f"I couldn't find {app_name} in my list, but I'm opening it via Windows Search."

        # If not found, try web fallbacks
        web_fallbacks = {
            'youtube music': 'https://music.youtube.com',
            'spotify': 'https://open.spotify.com',
            # 'whatsapp': 'https://web.whatsapp.com', # REMOVED: User prefers system launch failure over web fallback
            'discord': 'https://discord.com/app',
            'slack': 'https://app.slack.com',
            'zoom': 'https://zoom.us/join',
            'teams': 'https://teams.microsoft.com'
        }
        
        app_lower = app_name.lower()
        if app_lower in web_fallbacks:
            try:
                # Use webbrowser module for security
                import webbrowser
                webbrowser.open(web_fallbacks[app_lower])
                app_discovery.track_app_launch(app_name, web_fallbacks[app_lower], success=True)
                return f"✅ Opened {app_name} web version (desktop app not found)"
            except Exception as e:
                app_discovery.track_app_launch(app_name, "", success=False)
                return f"❌ Failed to open {app_name}: {e}"
        
        app_discovery.track_app_launch(app_name, "", success=False)
        return f"❌ Could not find '{app_name}' on your system. Try saying the full application name or check if it's installed."

def refresh_app_database() -> str:
    """Refresh the application database"""
    try:
        new_apps = app_discovery.refresh_database()
        total_apps = len(app_discovery.get_all_apps())
        return f"Database refreshed! Found {new_apps} new apps. Total: {total_apps} applications."
    except Exception as e:
        return f"Error refreshing database: {e}"

def list_installed_apps() -> str:
    """List all discovered applications"""
    apps = app_discovery.get_all_apps()
    if not apps:
        return "No applications discovered yet. Run application discovery first."
    
    app_list = "\n".join([f"• {name.title()}" for name in sorted(apps.keys())][:50])  # Limit to 50
    total = len(apps)
    
    return f"Found {total} applications (showing first 50):\n{app_list}"

def get_apps_for_web() -> List[Dict[str, str]]:
    """Get applications formatted for web API responses"""
    return app_discovery.get_apps_for_api()

def get_app_usage_stats() -> str:
    """Get application usage statistics."""
    most_used = app_discovery.get_most_used_apps(10)
    recent = app_discovery.get_recent_apps(10)
    
    report = "📊 APPLICATION USAGE STATISTICS\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    report += "🔥 MOST USED APPS:\n"
    for i, (app_name, count) in enumerate(most_used, 1):
        report += f"{i}. {app_name.title()}: {count} launches\n"
    
    report += "\n⏰ RECENTLY USED:\n"
    for i, (app_name, last_time) in enumerate(recent, 1):
        report += f"{i}. {app_name.title()} (Last: {last_time})\n"
    
    return report

# EXPORT ALIASES for backend compatibility
get_installed_apps = get_apps_for_web
refresh_app_list = refresh_app_database

def search_apps_by_name(query: str) -> str:
    """Search for applications by name."""
    results = app_discovery.search_apps(query, limit=10)
    
    if not results:
        return f"No applications found matching '{query}'"
    
    report = f"🔍 SEARCH RESULTS for '{query}':\n"
    for i, (name, path, score) in enumerate(results, 1):
        report += f"{i}. {name.title()} (Score: {score})\n   Path: {path}\n"
    
    return report