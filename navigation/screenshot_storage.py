#!/usr/bin/env python3
"""
Screenshot storage management for prompt-based navigation
"""

import os
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging

class ScreenshotStorage:
    """Manages screenshot storage with domain and date organization"""
    
    def __init__(self, base_directory: str = "./navigation_screenshots"):
        self.base_directory = Path(base_directory)
        self.logger = logging.getLogger(__name__)
        
        self.base_directory.mkdir(exist_ok=True)
    
    def create_session_directory(self, domain: str, session_id: str) -> str:
        """
        Create directory structure for a navigation session
        
        Args:
            domain: Website domain (e.g., 'example.com')
            session_id: Unique session identifier
        
        Returns:
            Path to the session directory
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        session_dir = self.base_directory / domain / date_str / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"📁 Created session directory: {session_dir}")
        
        return str(session_dir)
    
    def save_screenshot(self, screenshot_data: bytes, domain: str, session_id: str, filename: str) -> str:
        """
        Save screenshot to the appropriate directory
        
        Args:
            screenshot_data: Raw screenshot bytes from Playwright
            domain: Website domain
            session_id: Session identifier
            filename: Screenshot filename (without extension)
        
        Returns:
            Full path to the saved screenshot
        """
        try:
            session_dir = self.get_session_directory(domain, session_id)
            
            if not filename.endswith('.png'):
                filename += '.png'
            
            screenshot_path = os.path.join(session_dir, filename)
            
            with open(screenshot_path, 'wb') as f:
                f.write(screenshot_data)
            
            self.logger.debug(f"📸 Screenshot saved: {screenshot_path}")
            
            return screenshot_path
        
        except Exception as e:
            self.logger.error(f"Failed to save screenshot: {e}")
            return ""
    
    def get_session_directory(self, domain: str, session_id: str) -> str:
        """Get the directory path for a session"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return str(self.base_directory / domain / date_str / session_id)
    
    def list_sessions(self, domain: Optional[str] = None) -> list:
        """
        List all navigation sessions
        
        Args:
            domain: Optional domain filter
        
        Returns:
            List of session information dictionaries
        """
        sessions = []
        
        try:
            if domain:
                domain_dirs = [self.base_directory / domain] if (self.base_directory / domain).exists() else []
            else:
                domain_dirs = [d for d in self.base_directory.iterdir() if d.is_dir()]
            
            for domain_dir in domain_dirs:
                domain_name = domain_dir.name
                
                for date_dir in domain_dir.iterdir():
                    if not date_dir.is_dir():
                        continue
                    
                    date_str = date_dir.name
                    
                    for session_dir in date_dir.iterdir():
                        if not session_dir.is_dir():
                            continue
                        
                        session_id = session_dir.name
                        
                        screenshots = list(session_dir.glob("*.png"))
                        report_file = session_dir / "navigation_report.json"
                        
                        sessions.append({
                            'domain': domain_name,
                            'date': date_str,
                            'session_id': session_id,
                            'directory': str(session_dir),
                            'screenshot_count': len(screenshots),
                            'has_report': report_file.exists(),
                            'screenshots': [str(s) for s in screenshots]
                        })
        
        except Exception as e:
            self.logger.error(f"Failed to list sessions: {e}")
        
        return sessions
    
    def get_session_screenshots(self, domain: str, session_id: str) -> list:
        """Get all screenshots for a specific session"""
        try:
            session_dir = Path(self.get_session_directory(domain, session_id))
            
            if not session_dir.exists():
                return []
            
            screenshots = list(session_dir.glob("*.png"))
            screenshots.sort()  # Sort by filename
            
            return [str(s) for s in screenshots]
        
        except Exception as e:
            self.logger.error(f"Failed to get session screenshots: {e}")
            return []
    
    def cleanup_old_sessions(self, days_to_keep: int = 30):
        """Remove sessions older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_str = cutoff_date.strftime("%Y-%m-%d")
            
            removed_count = 0
            
            for domain_dir in self.base_directory.iterdir():
                if not domain_dir.is_dir():
                    continue
                
                for date_dir in domain_dir.iterdir():
                    if not date_dir.is_dir():
                        continue
                    
                    if date_dir.name < cutoff_str:
                        import shutil
                        shutil.rmtree(date_dir)
                        removed_count += 1
                        self.logger.info(f"🗑️  Removed old session directory: {date_dir}")
            
            self.logger.info(f"🧹 Cleanup complete: removed {removed_count} old session directories")
        
        except Exception as e:
            self.logger.error(f"Failed to cleanup old sessions: {e}")
