#!/usr/bin/env python3
"""
Example usage of prompt-based navigation with screenshot capture
"""

import asyncio
import logging
from navigation.prompt_navigator import PromptNavigator
from navigation.screenshot_storage import ScreenshotStorage
from core.config import Config

async def example_registration():
    """Example: Register on a website with predefined credentials"""
    
    logging.basicConfig(level=logging.INFO)
    
    config = Config(
        headless=False,  # Set to True for headless mode
        timeout=30000
    )
    
    capsolver_api_key = "your-capsolver-api-key-here"
    
    navigator = PromptNavigator(config, capsolver_api_key)
    
    credentials = {
        "email": "test@example.com",
        "username": "testuser123",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    result = await navigator.navigate_with_prompt(
        url="https://example.com",
        prompt="register in this website with some predefined credentials",
        credentials=credentials
    )
    
    print(f"\n🎯 Navigation Results:")
    print(f"Domain: {result.domain}")
    print(f"Total steps: {result.total_steps}")
    print(f"Successful steps: {result.successful_steps}")
    print(f"Screenshots directory: {result.screenshots_directory}")
    print(f"Session ID: {result.session_id}")
    
    print(f"\n📋 Step Details:")
    for step in result.steps:
        status = "✅" if step.success else "❌"
        print(f"{status} Step {step.step_number}: {step.action} - {step.description}")
        if step.screenshot_path:
            print(f"   📸 Screenshot: {step.screenshot_path}")
        if step.error_message:
            print(f"   ⚠️  Error: {step.error_message}")

async def example_login():
    """Example: Login to a website"""
    
    config = Config(headless=False, timeout=30000)
    capsolver_api_key = "your-capsolver-api-key-here"
    navigator = PromptNavigator(config, capsolver_api_key)
    
    credentials = {
        "email": "user@example.com",
        "password": "MyPassword123!"
    }
    
    result = await navigator.navigate_with_prompt(
        url="https://example.com/login",
        prompt="login to this website with credentials",
        credentials=credentials
    )
    
    print(f"Login completed: {result.successful_steps}/{result.total_steps} steps successful")

async def example_search():
    """Example: Search on a website"""
    
    config = Config(headless=False, timeout=30000)
    capsolver_api_key = "your-capsolver-api-key-here"
    navigator = PromptNavigator(config, capsolver_api_key)
    
    result = await navigator.navigate_with_prompt(
        url="https://example.com",
        prompt="search for python tutorials on this website"
    )
    
    print(f"Search completed: {result.successful_steps}/{result.total_steps} steps successful")

def list_navigation_sessions():
    """List all navigation sessions"""
    
    storage = ScreenshotStorage()
    sessions = storage.list_sessions()
    
    print(f"\n📁 Navigation Sessions ({len(sessions)} total):")
    for session in sessions:
        print(f"  Domain: {session['domain']}")
        print(f"  Date: {session['date']}")
        print(f"  Session ID: {session['session_id']}")
        print(f"  Screenshots: {session['screenshot_count']}")
        print(f"  Has Report: {session['has_report']}")
        print(f"  Directory: {session['directory']}")
        print()

async def example_with_captcha_solving():
    """Example: Navigate a site that might have captchas"""
    
    config = Config(headless=False, timeout=30000)
    
    capsolver_api_key = "your-actual-capsolver-api-key"
    
    navigator = PromptNavigator(config, capsolver_api_key)
    
    credentials = {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    
    result = await navigator.navigate_with_prompt(
        url="https://site-with-captcha.com/register",
        prompt="register in this website and solve any captchas that appear",
        credentials=credentials
    )
    
    print(f"Registration with captcha solving: {result.successful_steps}/{result.total_steps} steps successful")
    
    captcha_steps = [step for step in result.steps if "captcha" in step.action.lower()]
    if captcha_steps:
        print(f"🤖 Solved {len(captcha_steps)} captcha(s)")
        for step in captcha_steps:
            print(f"   {step.description}")

if __name__ == "__main__":
    print("🚀 Site Analyzer - Prompt-based Navigation Examples")
    print("=" * 60)
    
    print("\n1️⃣  Registration Example:")
    asyncio.run(example_registration())
    
    print("\n2️⃣  Login Example:")
    asyncio.run(example_login())
    
    print("\n3️⃣  Search Example:")
    asyncio.run(example_search())
    
    print("\n4️⃣  List Sessions:")
    list_navigation_sessions()
    
    print("\n5️⃣  Captcha Solving Example:")
    asyncio.run(example_with_captcha_solving())
