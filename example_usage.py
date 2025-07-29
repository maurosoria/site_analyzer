#!/usr/bin/env python3
"""
Simple and elegant example for running the site_analyzer framework
with multiple Playwright instances, load balancing, and LLM integration
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from core.config import Config
from core.analyzer import SiteAnalyzer
from storage.factory import StorageFactory
from enumeration.factory import EnumerationFactory
from lib.logging_utils import init_logging, highlight
from navigation.prompt_navigator import PromptNavigator

@dataclass
class FrameworkConfig:
    """Configuration for the site analyzer framework"""
    domains: List[str]
    
    num_playwright_instances: int = 3
    headless: bool = True
    timeout: int = 30000
    
    storage_type: str = "file"  # file, mongodb, sql
    output_dir: str = "./results"
    
    security_trails_api_key: Optional[str] = None
    
    aws_bedrock_url: Optional[str] = None
    aws_region: str = "us-east-1"
    llm_model: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    capsolver_api_key: Optional[str] = None
    
    enumerators: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.enumerators is None:
            self.enumerators = ["web_scanner", "dns_enumeration", "security_trails"]

class SiteAnalyzerFramework:
    """Main framework class for elegant site analysis"""
    
    def __init__(self, config: FrameworkConfig):
        self.config = config
        self.playwright_pool = []
        self.results = []
        
        init_logging(debug=False)
        
        self.core_config = Config(
            headless=config.headless,
            timeout=config.timeout,
            security_trails_api_key=config.security_trails_api_key,
            aws_bedrock_url=config.aws_bedrock_url,
            aws_region=config.aws_region,
            llm_model=config.llm_model
        )
        
        storage_config = {
            'type': config.storage_type,
            'output_dir': config.output_dir
        }
        self.storage = StorageFactory.create_storage(storage_config)
        
        highlight("Site Analyzer Framework Initialized", "SUCCESS")
        print(f"📊 Domains to analyze: {len(config.domains)}")
        print(f"🎭 Playwright instances: {config.num_playwright_instances}")
        print(f"💾 Storage type: {config.storage_type}")
        print(f"🤖 LLM integration: {'✅' if config.aws_bedrock_url else '❌'}")
        print(f"🔓 Captcha solving: {'✅' if config.capsolver_api_key else '❌'}")
    
    async def analyze_domains(self) -> List[Dict[str, Any]]:
        """Analyze all domains with load balancing across Playwright instances"""
        highlight("Starting Domain Analysis", "INFO")
        
        semaphore = asyncio.Semaphore(self.config.num_playwright_instances)
        
        tasks = []
        for domain in self.config.domains:
            task = self._analyze_single_domain(domain, semaphore)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logging.error(f"Failed to analyze {self.config.domains[i]}: {result}")
            else:
                successful_results.append(result)
                self.storage.store(result)
        
        highlight(f"Analysis Complete: {len(successful_results)}/{len(self.config.domains)} successful", "FINAL")
        return successful_results
    
    async def _analyze_single_domain(self, domain: str, semaphore: asyncio.Semaphore):
        """Analyze a single domain with semaphore-based load balancing"""
        async with semaphore:
            try:
                print(f"🔍 Analyzing: {domain}")
                
                analyzer = SiteAnalyzer(self.core_config)
                
                result = analyzer.analyze(
                    target=domain,
                    enumerators=self.config.enumerators,
                    storage_config={'type': self.config.storage_type, 'output_dir': self.config.output_dir}
                )
                
                print(f"✅ Completed: {domain}")
                return result
                
            except Exception as e:
                print(f"❌ Failed: {domain} - {e}")
                raise e
    
    def get_results_summary(self) -> Dict[str, Any]:
        """Get a summary of all analysis results"""
        if not self.results:
            return {"message": "No results available"}
        
        summary = {
            "total_domains": len(self.config.domains),
            "successful_analyses": len(self.results),
            "total_emails": sum(len(r.data.get('emails', [])) for r in self.results),
            "total_urls": sum(len(r.data.get('urls', [])) for r in self.results),
            "total_endpoints": sum(len(r.data.get('endpoints', [])) for r in self.results),
            "domains_analyzed": [r.target for r in self.results]
        }
        
        return summary
    
    async def navigate_with_prompt(self, url: str, prompt: str, credentials: Optional[Dict[str, str]] = None):
        """Navigate a website using natural language prompts"""
        if not self.config.capsolver_api_key:
            raise ValueError("Capsolver API key required for navigation with captcha solving")
        
        navigator = PromptNavigator(self.core_config, self.config.capsolver_api_key)
        
        result = await navigator.navigate_with_prompt(url, prompt, credentials)
        
        highlight(f"Navigation completed: {result.successful_steps}/{result.total_steps} steps successful", "SUCCESS")
        print(f"📁 Screenshots saved to: {result.screenshots_directory}")
        
        return result

def simple_example():
    """Simple example with a single domain"""
    config = FrameworkConfig(
        domains=["example.com"],
        num_playwright_instances=2,
        storage_type="file",
        output_dir="./simple_results"
    )
    
    framework = SiteAnalyzerFramework(config)
    results = asyncio.run(framework.analyze_domains())
    
    print("\n📋 Results Summary:")
    for result in results:
        print(f"  Domain: {result.get('target', 'Unknown')}")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Emails found: {len(result.get('data', {}).get('emails', []))}")
        print(f"  URLs found: {len(result.get('data', {}).get('urls', []))}")

def advanced_example_with_llm():
    """Advanced example with multiple domains and LLM integration"""
    config = FrameworkConfig(
        domains=["example.com", "test.com", "demo.org"],
        num_playwright_instances=5,
        storage_type="file",
        output_dir="./advanced_results",
        security_trails_api_key="your-api-key-here",
        aws_bedrock_url="https://bedrock-runtime.us-east-1.amazonaws.com",
        aws_region="us-east-1",
        enumerators=["web_scanner", "dns_enumeration", "security_trails"]
    )
    
    framework = SiteAnalyzerFramework(config)
    results = asyncio.run(framework.analyze_domains())
    
    summary = framework.get_results_summary()
    print("\n📊 Advanced Analysis Summary:")
    print(f"  Total domains: {summary['total_domains']}")
    print(f"  Successful: {summary['successful_analyses']}")
    print(f"  Total emails: {summary['total_emails']}")
    print(f"  Total URLs: {summary['total_urls']}")
    print(f"  Total endpoints: {summary['total_endpoints']}")

def load_balanced_example():
    """Example demonstrating load balancing with many domains"""
    domains = [f"site{i}.example.com" for i in range(1, 21)]  # 20 domains
    
    config = FrameworkConfig(
        domains=domains,
        num_playwright_instances=8,  # 8 concurrent instances
        storage_type="file",
        output_dir="./load_balanced_results",
        headless=True,
        timeout=20000
    )
    
    framework = SiteAnalyzerFramework(config)
    
    print(f"🚀 Starting load-balanced analysis of {len(domains)} domains")
    print(f"⚖️  Using {config.num_playwright_instances} Playwright instances")
    
    start_time = asyncio.get_event_loop().time()
    results = asyncio.run(framework.analyze_domains())
    end_time = asyncio.get_event_loop().time()
    
    print(f"\n⏱️  Analysis completed in {end_time - start_time:.2f} seconds")
    print(f"📈 Average time per domain: {(end_time - start_time) / len(domains):.2f} seconds")

async def navigation_example():
    """Example demonstrating prompt-based navigation with screenshot capture"""
    config = FrameworkConfig(
        domains=["example.com"],
        num_playwright_instances=1,
        storage_type="file",
        output_dir="./navigation_results",
        capsolver_api_key="your-capsolver-api-key-here"  # User should provide real key
    )
    
    framework = SiteAnalyzerFramework(config)
    
    print("\n🔐 Registration Example:")
    credentials = {
        "email": "test@example.com",
        "username": "testuser123",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        result = await framework.navigate_with_prompt(
            url="https://example.com/register",
            prompt="register in this website with some predefined credentials",
            credentials=credentials
        )
        
        print(f"✅ Registration: {result.successful_steps}/{result.total_steps} steps completed")
        print(f"📸 Screenshots: {len([s for s in result.steps if s.screenshot_path])}")
        
        captcha_steps = [s for s in result.steps if "captcha" in s.action.lower()]
        if captcha_steps:
            print(f"🤖 Captchas solved: {len(captcha_steps)}")
    
    except Exception as e:
        print(f"❌ Registration failed: {e}")
    
    print("\n🔑 Login Example:")
    login_credentials = {
        "email": "user@example.com",
        "password": "MyPassword123!"
    }
    
    try:
        result = await framework.navigate_with_prompt(
            url="https://example.com/login",
            prompt="login to this website with credentials",
            credentials=login_credentials
        )
        
        print(f"✅ Login: {result.successful_steps}/{result.total_steps} steps completed")
    
    except Exception as e:
        print(f"❌ Login failed: {e}")
    
    print("\n🔍 Search Example:")
    try:
        result = await framework.navigate_with_prompt(
            url="https://example.com",
            prompt="search for python tutorials on this website"
        )
        
        print(f"✅ Search: {result.successful_steps}/{result.total_steps} steps completed")
    
    except Exception as e:
        print(f"❌ Search failed: {e}")

if __name__ == "__main__":
    print("🎯 Site Analyzer Framework Examples")
    print("=" * 50)
    
    print("\n1️⃣  Simple Example:")
    simple_example()
    
    print("\n🚀 Navigation Example:")
    asyncio.run(navigation_example())
