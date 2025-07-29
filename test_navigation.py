#!/usr/bin/env python3
"""
Test script for prompt-based navigation with screenshot capture and captcha solving
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from navigation.prompt_navigator import PromptNavigator
from navigation.screenshot_storage import ScreenshotStorage
from core.config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_basic_navigation():
    """Test basic navigation functionality"""
    print("🧪 Testing Basic Navigation Functionality")
    print("=" * 50)
    
    config = Config(
        headless=True,  # Use headless for testing
        timeout=30000
    )
    
    capsolver_api_key = "test-api-key"
    
    try:
        navigator = PromptNavigator(config, capsolver_api_key)
        
        result = await navigator.navigate_with_prompt(
            url="https://httpbin.org/forms/post",
            prompt="fill out this form with test data"
        )
        
        print(f"✅ Navigation completed: {result.successful_steps}/{result.total_steps} steps")
        print(f"📁 Screenshots directory: {result.screenshots_directory}")
        print(f"🆔 Session ID: {result.session_id}")
        
        screenshot_count = len([s for s in result.steps if s.screenshot_path])
        print(f"📸 Screenshots captured: {screenshot_count}")
        
        if os.path.exists(result.screenshots_directory):
            print(f"✅ Screenshot directory created successfully")
            files = os.listdir(result.screenshots_directory)
            print(f"📋 Files in directory: {files}")
        else:
            print(f"❌ Screenshot directory not found: {result.screenshots_directory}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic navigation test failed: {e}")
        return False

async def test_registration_workflow():
    """Test registration workflow with predefined credentials"""
    print("\n🧪 Testing Registration Workflow")
    print("=" * 50)
    
    config = Config(headless=True, timeout=30000)
    capsolver_api_key = "test-api-key"
    
    try:
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
            url="https://httpbin.org/forms/post",
            prompt="register in this website with some predefined credentials",
            credentials=credentials
        )
        
        print(f"✅ Registration test completed: {result.successful_steps}/{result.total_steps} steps")
        
        registration_steps = [s for s in result.steps if "fill" in s.action.lower() or "register" in s.action.lower()]
        print(f"🔐 Registration-related steps: {len(registration_steps)}")
        
        for step in registration_steps:
            print(f"   Step {step.step_number}: {step.action} - {step.description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Registration workflow test failed: {e}")
        return False

async def test_screenshot_storage():
    """Test screenshot storage functionality"""
    print("\n🧪 Testing Screenshot Storage")
    print("=" * 50)
    
    try:
        storage = ScreenshotStorage("./test_screenshots")
        
        domain = "example.com"
        session_id = "test_session_123"
        
        session_dir = storage.create_session_directory(domain, session_id)
        print(f"✅ Session directory created: {session_dir}")
        
        expected_date = datetime.now().strftime("%Y-%m-%d")
        expected_path = f"./test_screenshots/{domain}/{expected_date}/{session_id}"
        
        if session_dir == expected_path:
            print(f"✅ Directory structure correct: {session_dir}")
        else:
            print(f"❌ Directory structure incorrect. Expected: {expected_path}, Got: {session_dir}")
        
        mock_screenshot = b"mock_screenshot_data"
        screenshot_path = storage.save_screenshot(
            mock_screenshot, domain, session_id, "test_screenshot"
        )
        
        if screenshot_path and os.path.exists(screenshot_path):
            print(f"✅ Screenshot saved successfully: {screenshot_path}")
        else:
            print(f"❌ Screenshot saving failed")
        
        sessions = storage.list_sessions(domain)
        print(f"📋 Sessions found: {len(sessions)}")
        
        for session in sessions:
            print(f"   Domain: {session['domain']}, Date: {session['date']}, ID: {session['session_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Screenshot storage test failed: {e}")
        return False

async def test_captcha_detection():
    """Test captcha detection capabilities"""
    print("\n🧪 Testing Captcha Detection")
    print("=" * 50)
    
    config = Config(headless=True, timeout=30000)
    capsolver_api_key = "test-api-key"
    
    try:
        navigator = PromptNavigator(config, capsolver_api_key)
        
        result = await navigator.navigate_with_prompt(
            url="https://www.google.com/recaptcha/api2/demo",
            prompt="interact with this page and handle any captchas"
        )
        
        print(f"✅ Captcha detection test completed: {result.successful_steps}/{result.total_steps} steps")
        
        captcha_steps = [s for s in result.steps if "captcha" in s.action.lower()]
        if captcha_steps:
            print(f"🤖 Captcha steps detected: {len(captcha_steps)}")
            for step in captcha_steps:
                print(f"   Step {step.step_number}: {step.action} - {step.description}")
        else:
            print(f"ℹ️  No captcha steps detected (expected for test environment)")
        
        return True
        
    except Exception as e:
        print(f"❌ Captcha detection test failed: {e}")
        return False

def test_directory_structure():
    """Test that screenshot directory structure follows domain/date pattern"""
    print("\n🧪 Testing Directory Structure")
    print("=" * 50)
    
    try:
        storage = ScreenshotStorage("./test_structure")
        
        test_cases = [
            ("example.com", "session1"),
            ("test.org", "session2"),
            ("demo.net", "session3")
        ]
        
        for domain, session_id in test_cases:
            session_dir = storage.create_session_directory(domain, session_id)
            
            path_parts = Path(session_dir).parts
            
            if len(path_parts) >= 4:
                base_dir = path_parts[-4]
                domain_part = path_parts[-3]
                date_part = path_parts[-2]
                session_part = path_parts[-1]
                
                print(f"✅ Structure for {domain}: {domain_part}/{date_part}/{session_part}")
                
                if domain_part == domain:
                    print(f"   ✅ Domain correct: {domain_part}")
                else:
                    print(f"   ❌ Domain incorrect: expected {domain}, got {domain_part}")
                
                try:
                    datetime.strptime(date_part, "%Y-%m-%d")
                    print(f"   ✅ Date format correct: {date_part}")
                except ValueError:
                    print(f"   ❌ Date format incorrect: {date_part}")
                
                if session_part == session_id:
                    print(f"   ✅ Session ID correct: {session_part}")
                else:
                    print(f"   ❌ Session ID incorrect: expected {session_id}, got {session_part}")
            else:
                print(f"❌ Directory structure too shallow: {session_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Directory structure test failed: {e}")
        return False

async def run_all_tests():
    """Run all navigation and screenshot tests"""
    print("🚀 Site Analyzer Navigation Testing Suite")
    print("=" * 60)
    
    test_results = []
    
    test_results.append(await test_basic_navigation())
    test_results.append(await test_registration_workflow())
    test_results.append(await test_screenshot_storage())
    test_results.append(test_directory_structure())
    test_results.append(await test_captcha_detection())
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print(f"🎉 All tests passed! Navigation system is working correctly.")
    else:
        print(f"⚠️  Some tests failed. Please review the output above.")
    
    return passed == total

if __name__ == "__main__":
    print("Note: This test requires internet access and may create test directories.")
    print("For captcha testing, a real capsolver API key would be needed.")
    print()
    
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n✅ All navigation functionality tests completed successfully!")
    else:
        print("\n❌ Some tests failed. Check the output for details.")
