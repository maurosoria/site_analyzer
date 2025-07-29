#!/usr/bin/env python3
"""
Example demonstrating JavaScript framework detection and DOM pattern analysis
"""

import asyncio
from typing import Dict, Any
from example_usage import FrameworkConfig, SiteAnalyzerFramework

def framework_detection_example():
    """Example focusing on JavaScript framework detection"""
    
    test_sites = {
        "React": ["reactjs.org", "create-react-app.dev"],
        "Angular": ["angular.io", "material.angular.io"], 
        "Vue.js": ["vuejs.org", "nuxtjs.org"],
        "Mixed": ["github.com", "stackoverflow.com"]
    }
    
    all_domains = []
    for framework_type, domains in test_sites.items():
        all_domains.extend(domains)
    
    config = FrameworkConfig(
        domains=all_domains,
        num_playwright_instances=4,
        storage_type="file",
        output_dir="./framework_detection_results",
        enumerators=["web_scanner"]  # Focus on web scanning for framework detection
    )
    
    print("🔍 JavaScript Framework Detection Example")
    print("=" * 50)
    print(f"📊 Analyzing {len(all_domains)} sites for framework detection")
    print(f"🎭 Using {config.num_playwright_instances} Playwright instances")
    
    framework = SiteAnalyzerFramework(config)
    results = asyncio.run(framework.analyze_domains())
    
    print("\n📋 Framework Detection Results:")
    print("=" * 50)
    
    framework_stats = {}
    security_stats = {"high_risk": 0, "medium_risk": 0, "low_risk": 0}
    
    for result in results:
        domain = result.get('target', 'Unknown')
        frameworks = result.get('data', {}).get('frameworks', [])
        dom_patterns = result.get('data', {}).get('dom_patterns', [])
        security_score = result.get('data', {}).get('security_score', {})
        
        print(f"\n🌐 {domain}")
        
        if frameworks:
            print("  📦 Frameworks detected:")
            for fw in frameworks:
                print(f"    • {fw['name']} {fw.get('version', 'unknown')} (confidence: {fw['confidence']:.2f})")
                
                fw_name = fw['name']
                if fw_name not in framework_stats:
                    framework_stats[fw_name] = 0
                framework_stats[fw_name] += 1
        else:
            print("  📦 No frameworks detected")
        
        risk_level = security_score.get('risk_level', 'UNKNOWN')
        print(f"  🔒 Security risk: {risk_level}")
        
        if risk_level in ['HIGH', 'MEDIUM', 'LOW']:
            security_stats[f"{risk_level.lower()}_risk"] += 1
        
        high_severity = [p for p in dom_patterns if p['severity'] == 'high']
        if high_severity:
            print(f"  ⚠️  High-risk patterns: {len(high_severity)}")
    
    print("\n📊 Overall Statistics:")
    print("=" * 30)
    
    print("🏗️  Framework Distribution:")
    for framework, count in sorted(framework_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {framework}: {count} sites")
    
    print("\n🔒 Security Risk Distribution:")
    for risk_type, count in security_stats.items():
        if count > 0:
            print(f"  • {risk_type.replace('_', ' ').title()}: {count} sites")

def advanced_framework_analysis():
    """Advanced example with detailed framework analysis"""
    
    config = FrameworkConfig(
        domains=["example.com"],  # Replace with actual test domain
        num_playwright_instances=1,
        storage_type="file",
        output_dir="./detailed_framework_analysis"
    )
    
    framework = SiteAnalyzerFramework(config)
    results = asyncio.run(framework.analyze_domains())
    
    if results:
        result = results[0]
        data = result.get('data', {})
        
        print("🔬 Detailed Framework Analysis")
        print("=" * 40)
        
        frameworks = data.get('frameworks', [])
        for fw in frameworks:
            print(f"\n📦 {fw['name']} (v{fw.get('version', 'unknown')})")
            print(f"   Confidence: {fw['confidence']:.2f}")
            print(f"   Indicators: {len(fw['indicators'])}")
            for indicator in fw['indicators'][:3]:  # Show first 3
                print(f"     • {indicator}")
            if len(fw['indicators']) > 3:
                print(f"     ... and {len(fw['indicators']) - 3} more")
        
        dom_patterns = data.get('dom_patterns', [])
        if dom_patterns:
            print(f"\n🔍 DOM Patterns Found: {len(dom_patterns)}")
            
            by_severity = {}
            for pattern in dom_patterns:
                severity = pattern['severity']
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(pattern)
            
            for severity in ['high', 'medium', 'info']:
                if severity in by_severity:
                    print(f"\n  {severity.upper()} severity:")
                    for pattern in by_severity[severity]:
                        print(f"    • {pattern['name']}: {pattern['count']} matches")
                        print(f"      {pattern['description']}")
        
        security_score = data.get('security_score', {})
        if security_score:
            print(f"\n🔒 Security Analysis:")
            print(f"   Risk Level: {security_score.get('risk_level', 'Unknown')}")
            print(f"   Score: {security_score.get('normalized_score', 0):.1f}/100")
            
            breakdown = security_score.get('severity_breakdown', {})
            if breakdown:
                print("   Pattern breakdown:")
                for severity, count in breakdown.items():
                    if count > 0:
                        print(f"     • {severity}: {count}")

if __name__ == "__main__":
    print("🎯 JavaScript Framework Detection Examples")
    print("=" * 50)
    
    print("\n1️⃣  Framework Detection Example:")
    framework_detection_example()
