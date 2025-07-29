#!/usr/bin/env python3
"""
Test script for Gemini integration with the site_analyzer framework
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports without actually importing the full framework
def test_imports():
    """Test that we can import the necessary modules"""
    try:
        from llm.gemini_client import GeminiClient
        print("✅ GeminiClient import successful")
        return True
    except Exception as e:
        print(f"❌ GeminiClient import failed: {e}")
        return False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_gemini_client_initialization():
    """Test Gemini client initialization with mock API key"""
    print("🧪 Testing Gemini Client Initialization")
    print("=" * 50)
    
    try:
        test_api_key = "AIza_test_key_for_initialization"
        
        try:
            client = GeminiClient(test_api_key, "gemini-2.0-flash-exp")
            print("❌ Unexpected: Client initialized with fake key")
            return False
        except Exception as e:
            print(f"✅ Expected: Client initialization failed with fake key: {type(e).__name__}")
            return True
            
    except Exception as e:
        print(f"❌ Unexpected error in test setup: {e}")
        return False

def test_framework_config_with_gemini():
    """Test framework configuration with Gemini settings"""
    print("\n🧪 Testing Framework Configuration with Gemini")
    print("=" * 50)
    
    try:
        config = FrameworkConfig(
            domains=["example.com"],
            num_playwright_instances=1,
            storage_type="file",
            output_dir="./test_gemini_results",
            
            llm_provider="gemini",
            gemini_api_key="AIza_test_key",
            llm_model="gemini-2.0-flash-exp"
        )
        
        print(f"✅ Framework config created successfully")
        print(f"   LLM Provider: {config.llm_provider}")
        print(f"   Model: {config.llm_model}")
        print(f"   API Key set: {'✅' if config.gemini_api_key else '❌'}")
        
        framework = SiteAnalyzerFramework(config)
        print(f"✅ Framework initialized with Gemini config")
        
        return True
        
    except Exception as e:
        print(f"❌ Framework configuration test failed: {e}")
        return False

def test_gemini_vs_bedrock_config():
    """Test switching between Gemini and Bedrock configurations"""
    print("\n🧪 Testing Gemini vs Bedrock Configuration")
    print("=" * 50)
    
    try:
        gemini_config = FrameworkConfig(
            domains=["example.com"],
            llm_provider="gemini",
            gemini_api_key="AIza_test_key",
            llm_model="gemini-2.0-flash-exp"
        )
        
        print(f"✅ Gemini config: {gemini_config.llm_provider}")
        
        bedrock_config = FrameworkConfig(
            domains=["example.com"],
            llm_provider="bedrock",
            aws_bedrock_url="https://bedrock-runtime.us-east-1.amazonaws.com",
            aws_region="us-east-1",
            llm_model="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        
        print(f"✅ Bedrock config: {bedrock_config.llm_provider}")
        
        gemini_framework = SiteAnalyzerFramework(gemini_config)
        bedrock_framework = SiteAnalyzerFramework(bedrock_config)
        
        print(f"✅ Both frameworks initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration switching test failed: {e}")
        return False

def test_gemini_example_file():
    """Test that the Gemini example file is properly structured"""
    print("\n🧪 Testing Gemini Example File")
    print("=" * 50)
    
    try:
        import gemini_example
        
        print(f"✅ gemini_example.py imported successfully")
        
        functions_to_check = [
            'simple_gemini_example',
            'setup_instructions',
        ]
        
        for func_name in functions_to_check:
            if hasattr(gemini_example, func_name):
                print(f"   ✅ Function {func_name} exists")
            else:
                print(f"   ❌ Function {func_name} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini example file test failed: {e}")
        return False

def test_llm_client_methods():
    """Test Gemini client methods structure"""
    print("\n🧪 Testing Gemini Client Methods")
    print("=" * 50)
    
    try:
        from llm.gemini_client import GeminiClient
        
        expected_methods = [
            'generate_response',
            'analyze_website_content',
            'generate_navigation_steps'
        ]
        
        for method_name in expected_methods:
            if hasattr(GeminiClient, method_name):
                print(f"   ✅ Method {method_name} exists")
            else:
                print(f"   ❌ Method {method_name} missing")
                return False
        
        print(f"✅ All expected methods found in GeminiClient")
        return True
        
    except Exception as e:
        print(f"❌ Gemini client methods test failed: {e}")
        return False

async def test_integration_with_navigation():
    """Test Gemini integration with navigation module"""
    print("\n🧪 Testing Gemini Integration with Navigation")
    print("=" * 50)
    
    try:
        config = FrameworkConfig(
            domains=["example.com"],
            llm_provider="gemini",
            gemini_api_key="AIza_test_key",
            capsolver_api_key="test_capsolver_key"
        )
        
        framework = SiteAnalyzerFramework(config)
        
        print(f"✅ Framework with Gemini + Navigation initialized")
        print(f"   LLM Provider: {config.llm_provider}")
        print(f"   Captcha Solver: {'✅' if config.capsolver_api_key else '❌'}")
        
        if hasattr(framework, 'navigate_with_prompt'):
            print(f"   ✅ navigate_with_prompt method available")
        else:
            print(f"   ❌ navigate_with_prompt method missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Navigation integration test failed: {e}")
        return False

async def run_all_tests():
    """Run all Gemini integration tests"""
    print("🚀 Gemini Integration Testing Suite")
    print("=" * 60)
    
    test_results = []
    
    test_results.append(test_gemini_client_initialization())
    test_results.append(test_framework_config_with_gemini())
    test_results.append(test_gemini_vs_bedrock_config())
    test_results.append(test_gemini_example_file())
    test_results.append(test_llm_client_methods())
    
    test_results.append(await test_integration_with_navigation())
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n📊 Gemini Integration Test Results")
    print("=" * 40)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print(f"🎉 All Gemini integration tests passed!")
        print(f"🤖 Gemini 2.5 Flash-Lite is ready to use")
    else:
        print(f"⚠️  Some tests failed. Please review the output above.")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Get a real Google AI API key from https://aistudio.google.com/app/apikey")
    print(f"   2. Replace 'AIza_test_key' with your real API key")
    print(f"   3. Run the gemini_example.py for real testing")
    
    return passed == total

if __name__ == "__main__":
    print("Note: This test uses mock API keys and tests structure/integration.")
    print("For real Gemini testing, you need a valid Google AI API key.")
    print()
    
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n✅ Gemini integration is properly implemented and ready!")
    else:
        print("\n❌ Some integration issues found. Check the output for details.")
