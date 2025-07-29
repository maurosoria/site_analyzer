#!/usr/bin/env python3
"""
Prompt-based website navigation with screenshot capture and captcha solving
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import os
import json
from pathlib import Path

from playwright.async_api import async_playwright, Page, Browser
from navigation.screenshot_storage import ScreenshotStorage
from navigation.captcha_solver import CaptchaSolver
from core.config import Config

@dataclass
class NavigationStep:
    """Single navigation step result"""
    step_number: int
    action: str
    description: str
    screenshot_path: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class NavigationResult:
    """Complete navigation session result"""
    domain: str
    prompt: str
    steps: List[NavigationStep]
    total_steps: int
    successful_steps: int
    screenshots_directory: str
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'domain': self.domain,
            'prompt': self.prompt,
            'total_steps': self.total_steps,
            'successful_steps': self.successful_steps,
            'screenshots_directory': self.screenshots_directory,
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'steps': [
                {
                    'step_number': step.step_number,
                    'action': step.action,
                    'description': step.description,
                    'screenshot_path': step.screenshot_path,
                    'success': step.success,
                    'error_message': step.error_message,
                    'timestamp': step.timestamp.isoformat() if step.timestamp else None
                }
                for step in self.steps
            ]
        }

class PromptNavigator:
    """Prompt-based website navigator with screenshot capture and captcha solving"""
    
    def __init__(self, config: Config, capsolver_api_key: str):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.screenshot_storage = ScreenshotStorage()
        self.captcha_solver = CaptchaSolver(capsolver_api_key)
        
        self.current_session_id = None
        self.current_domain = None
        self.step_counter = 0
    
    async def navigate_with_prompt(self, url: str, prompt: str, credentials: Optional[Dict[str, str]] = None) -> NavigationResult:
        """
        Navigate a website following the given prompt
        
        Args:
            url: Target website URL
            prompt: Natural language prompt describing the task
            credentials: Optional credentials for registration/login
        
        Returns:
            NavigationResult with steps, screenshots, and success status
        """
        self.current_domain = self._extract_domain(url)
        self.current_session_id = self._generate_session_id()
        self.step_counter = 0
        
        start_time = datetime.now()
        steps = []
        
        screenshots_dir = self.screenshot_storage.create_session_directory(
            self.current_domain, 
            self.current_session_id
        )
        
        self.logger.info(f"🚀 Starting navigation: {prompt}")
        self.logger.info(f"📁 Screenshots will be saved to: {screenshots_dir}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.config.headless)
            
            try:
                page = await browser.new_page()
                
                initial_step = await self._take_screenshot_step(
                    page, "navigate_to_url", f"Navigating to {url}"
                )
                steps.append(initial_step)
                
                await page.goto(url)
                
                load_step = await self._take_screenshot_step(
                    page, "page_loaded", f"Page loaded: {url}"
                )
                steps.append(load_step)
                
                if "register" in prompt.lower():
                    register_steps = await self._handle_registration(page, credentials or {})
                    steps.extend(register_steps)
                
                elif "login" in prompt.lower():
                    login_steps = await self._handle_login(page, credentials or {})
                    steps.extend(login_steps)
                
                elif "search" in prompt.lower():
                    search_steps = await self._handle_search(page, prompt)
                    steps.extend(search_steps)
                
                else:
                    custom_steps = await self._handle_custom_prompt(page, prompt)
                    steps.extend(custom_steps)
                
                final_step = await self._take_screenshot_step(
                    page, "navigation_complete", "Navigation completed"
                )
                steps.append(final_step)
                
            except Exception as e:
                error_step = NavigationStep(
                    step_number=self.step_counter + 1,
                    action="error",
                    description=f"Navigation failed: {e}",
                    success=False,
                    error_message=str(e)
                )
                steps.append(error_step)
                self.logger.error(f"Navigation failed: {e}")
            
            finally:
                await browser.close()
        
        end_time = datetime.now()
        successful_steps = sum(1 for step in steps if step.success)
        
        result = NavigationResult(
            domain=self.current_domain,
            prompt=prompt,
            steps=steps,
            total_steps=len(steps),
            successful_steps=successful_steps,
            screenshots_directory=screenshots_dir,
            session_id=self.current_session_id,
            start_time=start_time,
            end_time=end_time
        )
        
        self._save_navigation_report(result)
        
        return result
    
    async def _handle_registration(self, page: Page, credentials: Dict[str, str]) -> List[NavigationStep]:
        """Handle website registration process"""
        steps = []
        
        try:
            register_link = await page.query_selector('a[href*="register"], a[href*="signup"], a:has-text("Register"), a:has-text("Sign up")')
            if register_link:
                await register_link.click()
                step = await self._take_screenshot_step(
                    page, "click_register", "Clicked register link"
                )
                steps.append(step)
                
                await page.wait_for_load_state('networkidle')
            
            form_fields = {
                'email': ['input[type="email"]', 'input[name*="email"]', 'input[id*="email"]'],
                'username': ['input[name*="username"]', 'input[id*="username"]', 'input[name*="user"]'],
                'password': ['input[type="password"]', 'input[name*="password"]', 'input[id*="password"]'],
                'confirm_password': ['input[name*="confirm"]', 'input[name*="repeat"]', 'input[id*="confirm"]'],
                'first_name': ['input[name*="first"]', 'input[id*="first"]', 'input[name*="fname"]'],
                'last_name': ['input[name*="last"]', 'input[id*="last"]', 'input[name*="lname"]']
            }
            
            for field_name, selectors in form_fields.items():
                if field_name in credentials:
                    for selector in selectors:
                        field = await page.query_selector(selector)
                        if field:
                            await field.fill(credentials[field_name])
                            step = await self._take_screenshot_step(
                                page, f"fill_{field_name}", f"Filled {field_name} field"
                            )
                            steps.append(step)
                            break
            
            captcha_step = await self._handle_captcha_if_present(page)
            if captcha_step:
                steps.append(captcha_step)
            
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Register"), button:has-text("Sign up")')
            if submit_button:
                await submit_button.click()
                step = await self._take_screenshot_step(
                    page, "submit_registration", "Submitted registration form"
                )
                steps.append(step)
                
                await page.wait_for_load_state('networkidle')
        
        except Exception as e:
            error_step = NavigationStep(
                step_number=self.step_counter + 1,
                action="registration_error",
                description=f"Registration failed: {e}",
                success=False,
                error_message=str(e)
            )
            steps.append(error_step)
        
        return steps
    
    async def _handle_login(self, page: Page, credentials: Dict[str, str]) -> List[NavigationStep]:
        """Handle website login process"""
        steps = []
        
        try:
            login_link = await page.query_selector('a[href*="login"], a[href*="signin"], a:has-text("Login"), a:has-text("Sign in")')
            if login_link:
                await login_link.click()
                step = await self._take_screenshot_step(
                    page, "click_login", "Clicked login link"
                )
                steps.append(step)
                
                await page.wait_for_load_state('networkidle')
            
            if 'username' in credentials or 'email' in credentials:
                username_field = await page.query_selector('input[name*="username"], input[name*="email"], input[type="email"], input[id*="username"], input[id*="email"]')
                if username_field:
                    username = credentials.get('username') or credentials.get('email', '')
                    await username_field.fill(username)
                    step = await self._take_screenshot_step(
                        page, "fill_username", "Filled username/email field"
                    )
                    steps.append(step)
            
            if 'password' in credentials:
                password_field = await page.query_selector('input[type="password"], input[name*="password"], input[id*="password"]')
                if password_field:
                    await password_field.fill(credentials['password'])
                    step = await self._take_screenshot_step(
                        page, "fill_password", "Filled password field"
                    )
                    steps.append(step)
            
            captcha_step = await self._handle_captcha_if_present(page)
            if captcha_step:
                steps.append(captcha_step)
            
            submit_button = await page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Login"), button:has-text("Sign in")')
            if submit_button:
                await submit_button.click()
                step = await self._take_screenshot_step(
                    page, "submit_login", "Submitted login form"
                )
                steps.append(step)
                
                await page.wait_for_load_state('networkidle')
        
        except Exception as e:
            error_step = NavigationStep(
                step_number=self.step_counter + 1,
                action="login_error",
                description=f"Login failed: {e}",
                success=False,
                error_message=str(e)
            )
            steps.append(error_step)
        
        return steps
    
    async def _handle_search(self, page: Page, prompt: str) -> List[NavigationStep]:
        """Handle search functionality"""
        steps = []
        
        try:
            search_terms = self._extract_search_terms(prompt)
            
            search_field = await page.query_selector('input[type="search"], input[name*="search"], input[id*="search"], input[placeholder*="search"]')
            if search_field:
                await search_field.fill(search_terms)
                step = await self._take_screenshot_step(
                    page, "fill_search", f"Filled search field with: {search_terms}"
                )
                steps.append(step)
                
                await page.keyboard.press('Enter')
                step = await self._take_screenshot_step(
                    page, "submit_search", "Submitted search"
                )
                steps.append(step)
                
                await page.wait_for_load_state('networkidle')
        
        except Exception as e:
            error_step = NavigationStep(
                step_number=self.step_counter + 1,
                action="search_error",
                description=f"Search failed: {e}",
                success=False,
                error_message=str(e)
            )
            steps.append(error_step)
        
        return steps
    
    async def _handle_custom_prompt(self, page: Page, prompt: str) -> List[NavigationStep]:
        """Handle custom prompts using basic heuristics"""
        steps = []
        
        try:
            step = await self._take_screenshot_step(
                page, "custom_prompt", f"Processing custom prompt: {prompt}"
            )
            steps.append(step)
            
            if "click" in prompt.lower():
                clickable_elements = await page.query_selector_all('button, a, input[type="submit"], input[type="button"]')
                if clickable_elements and len(clickable_elements) > 0:
                    await clickable_elements[0].click()
                    step = await self._take_screenshot_step(
                        page, "click_element", "Clicked first clickable element"
                    )
                    steps.append(step)
            
            elif "scroll" in prompt.lower():
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                step = await self._take_screenshot_step(
                    page, "scroll_page", "Scrolled to bottom of page"
                )
                steps.append(step)
        
        except Exception as e:
            error_step = NavigationStep(
                step_number=self.step_counter + 1,
                action="custom_prompt_error",
                description=f"Custom prompt failed: {e}",
                success=False,
                error_message=str(e)
            )
            steps.append(error_step)
        
        return steps
    
    async def _handle_captcha_if_present(self, page: Page) -> Optional[NavigationStep]:
        """Detect and solve captcha if present"""
        try:
            recaptcha_frame = await page.query_selector('iframe[src*="recaptcha"]')
            if recaptcha_frame:
                self.logger.info("🤖 reCAPTCHA detected, attempting to solve...")
                
                site_key = await self._extract_recaptcha_site_key(page)
                if site_key:
                    solution = await self.captcha_solver.solve_recaptcha(
                        site_key=site_key,
                        page_url=page.url
                    )
                    
                    if solution:
                        await page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML = "{solution}";')
                        
                        return await self._take_screenshot_step(
                            page, "solve_captcha", "Solved reCAPTCHA using capsolver"
                        )
                    else:
                        return NavigationStep(
                            step_number=self.step_counter + 1,
                            action="captcha_failed",
                            description="Failed to solve reCAPTCHA",
                            success=False,
                            error_message="Capsolver failed to solve captcha"
                        )
            
            hcaptcha_frame = await page.query_selector('iframe[src*="hcaptcha"]')
            if hcaptcha_frame:
                self.logger.info("🤖 hCaptcha detected, attempting to solve...")
                
                site_key = await self._extract_hcaptcha_site_key(page)
                if site_key:
                    solution = await self.captcha_solver.solve_hcaptcha(
                        site_key=site_key,
                        page_url=page.url
                    )
                    
                    if solution:
                        await page.evaluate(f'document.querySelector("[name=h-captcha-response]").value = "{solution}";')
                        
                        return await self._take_screenshot_step(
                            page, "solve_hcaptcha", "Solved hCaptcha using capsolver"
                        )
        
        except Exception as e:
            self.logger.error(f"Captcha handling failed: {e}")
            return NavigationStep(
                step_number=self.step_counter + 1,
                action="captcha_error",
                description=f"Captcha handling error: {e}",
                success=False,
                error_message=str(e)
            )
        
        return None
    
    async def _extract_recaptcha_site_key(self, page: Page) -> Optional[str]:
        """Extract reCAPTCHA site key from page"""
        try:
            site_key = await page.evaluate('''
                () => {
                    const recaptcha = document.querySelector('[data-sitekey]');
                    return recaptcha ? recaptcha.getAttribute('data-sitekey') : null;
                }
            ''')
            return site_key
        except:
            return None
    
    async def _extract_hcaptcha_site_key(self, page: Page) -> Optional[str]:
        """Extract hCaptcha site key from page"""
        try:
            site_key = await page.evaluate('''
                () => {
                    const hcaptcha = document.querySelector('[data-sitekey]');
                    return hcaptcha ? hcaptcha.getAttribute('data-sitekey') : null;
                }
            ''')
            return site_key
        except:
            return None
    
    async def _take_screenshot_step(self, page: Page, action: str, description: str) -> NavigationStep:
        """Take a screenshot and create a navigation step"""
        self.step_counter += 1
        
        try:
            screenshot_path = self.screenshot_storage.save_screenshot(
                await page.screenshot(),
                self.current_domain,
                self.current_session_id,
                f"step_{self.step_counter:03d}_{action}"
            )
            
            return NavigationStep(
                step_number=self.step_counter,
                action=action,
                description=description,
                screenshot_path=screenshot_path,
                success=True
            )
        
        except Exception as e:
            return NavigationStep(
                step_number=self.step_counter,
                action=action,
                description=description,
                success=False,
                error_message=str(e)
            )
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace('www.', '')
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _extract_search_terms(self, prompt: str) -> str:
        """Extract search terms from prompt"""
        words = prompt.lower().split()
        search_start = -1
        
        for i, word in enumerate(words):
            if word in ['search', 'find', 'look']:
                search_start = i + 1
                break
        
        if search_start > -1 and search_start < len(words):
            return ' '.join(words[search_start:])
        
        return "test search"
    
    def _save_navigation_report(self, result: NavigationResult):
        """Save navigation report to JSON file"""
        try:
            report_path = os.path.join(
                result.screenshots_directory,
                "navigation_report.json"
            )
            
            with open(report_path, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
            
            self.logger.info(f"📄 Navigation report saved: {report_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to save navigation report: {e}")
