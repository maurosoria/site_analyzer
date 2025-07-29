#!/usr/bin/env python3
"""
Example of using Gemini 2.5 Flash-Lite with the site_analyzer framework

This example demonstrates how to use Gemini for cost-effective LLM analysis.


1. Get your Google AI API key from: https://aistudio.google.com/app/apikey
2. Set environment variable: export GEMINI_API_KEY="your-api-key"
3. Install dependencies: pip install google-generativeai>=0.3.0
4. Run this example: python gemini_example.py


- Cost-effective: ~75% cheaper than other LLM providers
- Fast: Optimized for quick responses
- Powerful: Excellent for website analysis and navigation
- Easy integration: Simple API setup
"""

import asyncio
import logging
import os
from example_usage import SiteAnalyzerFramework, FrameworkConfig

logging.basicConfig(level=logging.INFO)

def simple_gemini_example():
    """Simple example using Gemini for LLM analysis"""
    print("🤖 Site Analyzer with Gemini 2.5 Flash-Lite")
    print("=" * 50)
    
    config = FrameworkConfig(
        domains=["example.com"],
        num_playwright_instances=2,
        storage_type="file",
        output_dir="./gemini_results",
        
        llm_provider="gemini",
        gemini_api_key=os.getenv('GEMINI_API_KEY', "AIza..."),  # Replace with your Google AI API key
        llm_model="gemini-2.0-flash-exp",
        
        security_trails_api_key="your-securitytrails-key",
        capsolver_api_key="your-capsolver-key"
    )
    
    framework = SiteAnalyzerFramework(config)
    
    print(f"✅ Framework initialized with Gemini")
    print(f"📊 Ready to analyze: {len(config.domains)} domains")
    print(f"🤖 LLM Provider: {config.llm_provider}")
    print(f"🧠 Model: {config.llm_model}")
    
    results = asyncio.run(framework.analyze_domains())
    
    print(f"\n📋 Analysis completed!")
    print(f"✅ Successful analyses: {len(results)}")
    
    return results

async def gemini_navigation_example():
    """Example of navigation with Gemini-powered analysis"""
    print("\n🔐 Gemini-Powered Navigation Example")
    print("=" * 50)
    
    config = FrameworkConfig(
        domains=["example.com"],
        num_playwright_instances=1,
        
        llm_provider="gemini",
        gemini_api_key=os.getenv('GEMINI_API_KEY', "AIza..."),  # Your API key
        llm_model="gemini-2.0-flash-exp",
        
        capsolver_api_key="your-capsolver-key"
    )
    
    framework = SiteAnalyzerFramework(config)
    
    credentials = {
        "email": "test@example.com",
        "username": "testuser123",
        "password": "SecurePassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        result = await framework.navigate_with_prompt(
            url="https://example.com/register",
            prompt="register in this website with predefined credentials using intelligent analysis",
            credentials=credentials
        )
        
        print(f"🎉 Navigation completed!")
        print(f"✅ Steps: {result.successful_steps}/{result.total_steps}")
        print(f"📸 Screenshots: {result.screenshots_directory}")
        
        print(f"🧠 Gemini analyzed the page and guided navigation")
        
    except Exception as e:
        print(f"❌ Navigation failed: {e}")

def setup_instructions():
    """Print setup instructions for Gemini"""
    print("\n📋 Setup Instructions for Gemini 2.5 Flash-Lite")
    print("=" * 60)
    
    print("1. 🔑 Get Google AI API Key:")
    print("   - Go to: https://aistudio.google.com/app/apikey")
    print("   - Click 'Create API Key'")
    print("   - Copy the key (starts with 'AIza...')")
    
    print("\n2. 📦 Install Dependencies:")
    print("   pip install google-generativeai")
    
    print("\n3. 🔧 Configure Framework:")
    print("""   config = FrameworkConfig(
       domains=["your-target.com"],
       llm_provider="gemini",
        gemini_api_key=os.getenv('GEMINI_API_KEY', "AIza..."),  # Your API key here
       llm_model="gemini-2.0-flash-exp"
   )""")
    
    print("\n4. 🚀 Run Analysis:")
    print("   framework = SiteAnalyzerFramework(config)")
    print("   results = asyncio.run(framework.analyze_domains())")
    
    print("\n💡 Benefits of Gemini vs AWS Bedrock:")
    print("   ✅ Easier setup (just API key)")
    print("   ✅ No AWS account needed")
    print("   ✅ Fast and reliable")
    print("   ✅ Good for web content analysis")
    print("   ✅ Cost-effective")

if __name__ == "__main__":
    print("🎯 Gemini 2.5 Flash-Lite Integration Examples")
    print("=" * 60)
    
    setup_instructions()
    
    print("\n⚠️  Note: Replace 'AIza...' with your real Google AI API key")
    print("🔗 Get your key at: https://aistudio.google.com/app/apikey")
