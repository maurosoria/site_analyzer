"""
Google Gemini client for LLM integration
"""

import logging
from typing import Optional, Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for Google Gemini API integration"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google AI API key
            model_name: Gemini model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"Gemini client initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def generate_response(self, prompt: str, **kwargs) -> Optional[str]:
        """
        Generate response using Gemini
        
        Args:
            prompt: Input prompt for the model
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response text or None if failed
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get('temperature', 0.7),
                    max_output_tokens=kwargs.get('max_tokens', 1000),
                    top_p=kwargs.get('top_p', 0.8),
                    top_k=kwargs.get('top_k', 40)
                )
            )
            
            if response.text:
                logger.debug(f"Gemini response generated successfully")
                return response.text
            else:
                logger.warning("Gemini returned empty response")
                return None
                
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return None
    
    def analyze_website_content(self, content: str, analysis_type: str = "security") -> Optional[Dict[str, Any]]:
        """
        Analyze website content using Gemini
        
        Args:
            content: Website content to analyze
            analysis_type: Type of analysis (security, framework, etc.)
            
        Returns:
            Analysis results or None if failed
        """
        prompts = {
            "security": f"""
            Analyze this website content for security issues, exposed endpoints, 
            sensitive information, and potential vulnerabilities:
            
            {content[:4000]}
            
            Return a JSON response with:
            - endpoints: list of API endpoints found
            - secrets: list of potential secrets/tokens
            - vulnerabilities: list of security issues
            - frameworks: detected frameworks/libraries
            """,
            
            "framework": f"""
            Analyze this website content to detect JavaScript frameworks, 
            libraries, and technologies used:
            
            {content[:4000]}
            
            Return a JSON response with:
            - framework: main framework (React, Angular, Vue, etc.)
            - version: framework version if detectable
            - libraries: list of detected libraries
            - build_tools: detected build tools (webpack, vite, etc.)
            """,
            
            "navigation": f"""
            Analyze this website content to understand the navigation structure
            and suggest automation steps:
            
            {content[:4000]}
            
            Return a JSON response with:
            - forms: list of forms with their fields
            - buttons: important buttons and their purposes
            - navigation: main navigation elements
            - automation_steps: suggested steps for automation
            """
        }
        
        prompt = prompts.get(analysis_type, prompts["security"])
        
        try:
            response = self.generate_response(prompt)
            if response:
                import json
                import re
                
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response
                
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    logger.warning("Gemini response was not valid JSON")
                    return {"raw_response": response}
            return None
            
        except Exception as e:
            logger.error(f"Website content analysis failed: {e}")
            return None
    
    def generate_navigation_steps(self, url: str, goal: str, page_content: str) -> Optional[list]:
        """
        Generate navigation steps for a specific goal
        
        Args:
            url: Target URL
            goal: Navigation goal (e.g., "register with credentials")
            page_content: Current page content
            
        Returns:
            List of navigation steps or None if failed
        """
        prompt = f"""
        You are helping automate website navigation. Given this information:
        
        URL: {url}
        Goal: {goal}
        Page Content: {page_content[:2000]}
        
        Generate a list of specific automation steps to achieve the goal.
        Return a JSON array of steps, each with:
        - action: type of action (click, type, wait, etc.)
        - selector: CSS selector or description of element
        - value: value to input (if applicable)
        - description: human-readable description
        
        Example:
        [
            {{"action": "click", "selector": "a[href='/register']", "description": "Click register link"}},
            {{"action": "type", "selector": "input[name='email']", "value": "{{email}}", "description": "Enter email"}},
            {{"action": "click", "selector": "button[type='submit']", "description": "Submit form"}}
        ]
        """
        
        try:
            response = self.generate_response(prompt)
            if response:
                import json
                import re
                
                json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response
                
                try:
                    steps = json.loads(json_str)
                    if isinstance(steps, list):
                        return steps
                    else:
                        logger.warning("Gemini returned non-list response for navigation steps")
                        return None
                except json.JSONDecodeError:
                    logger.warning("Gemini navigation response was not valid JSON")
                    return None
            return None
            
        except Exception as e:
            logger.error(f"Navigation steps generation failed: {e}")
            return None
