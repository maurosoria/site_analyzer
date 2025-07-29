#!/usr/bin/env python3
"""
Captcha solving integration using capsolver API
"""

import asyncio
import aiohttp
import logging
from typing import Optional, Dict, Any
import time

class CaptchaSolver:
    """Capsolver API integration for solving captchas"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.capsolver.com"
        self.logger = logging.getLogger(__name__)
    
    async def solve_recaptcha(self, site_key: str, page_url: str, version: str = "v2") -> Optional[str]:
        """
        Solve reCAPTCHA using capsolver
        
        Args:
            site_key: reCAPTCHA site key
            page_url: URL of the page containing the captcha
            version: reCAPTCHA version (v2 or v3)
        
        Returns:
            Captcha solution token or None if failed
        """
        try:
            self.logger.info(f"🤖 Solving reCAPTCHA {version} for site: {page_url}")
            
            task_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "ReCaptchaV2TaskProxyless" if version == "v2" else "ReCaptchaV3TaskProxyless",
                    "websiteURL": page_url,
                    "websiteKey": site_key
                }
            }
            
            if version == "v3":
                task_data["task"]["minScore"] = 0.3
                task_data["task"]["pageAction"] = "submit"
            
            task_id = await self._create_task(task_data)
            if not task_id:
                return None
            
            solution = await self._get_task_result(task_id)
            
            if solution:
                self.logger.info("✅ reCAPTCHA solved successfully")
                return solution
            else:
                self.logger.error("❌ Failed to solve reCAPTCHA")
                return None
        
        except Exception as e:
            self.logger.error(f"reCAPTCHA solving error: {e}")
            return None
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """
        Solve hCaptcha using capsolver
        
        Args:
            site_key: hCaptcha site key
            page_url: URL of the page containing the captcha
        
        Returns:
            Captcha solution token or None if failed
        """
        try:
            self.logger.info(f"🤖 Solving hCaptcha for site: {page_url}")
            
            task_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "HCaptchaTaskProxyless",
                    "websiteURL": page_url,
                    "websiteKey": site_key
                }
            }
            
            task_id = await self._create_task(task_data)
            if not task_id:
                return None
            
            solution = await self._get_task_result(task_id)
            
            if solution:
                self.logger.info("✅ hCaptcha solved successfully")
                return solution
            else:
                self.logger.error("❌ Failed to solve hCaptcha")
                return None
        
        except Exception as e:
            self.logger.error(f"hCaptcha solving error: {e}")
            return None
    
    async def solve_funcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """
        Solve FunCaptcha using capsolver
        
        Args:
            site_key: FunCaptcha site key
            page_url: URL of the page containing the captcha
        
        Returns:
            Captcha solution token or None if failed
        """
        try:
            self.logger.info(f"🤖 Solving FunCaptcha for site: {page_url}")
            
            task_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "FunCaptchaTaskProxyless",
                    "websiteURL": page_url,
                    "websitePublicKey": site_key
                }
            }
            
            task_id = await self._create_task(task_data)
            if not task_id:
                return None
            
            solution = await self._get_task_result(task_id)
            
            if solution:
                self.logger.info("✅ FunCaptcha solved successfully")
                return solution
            else:
                self.logger.error("❌ Failed to solve FunCaptcha")
                return None
        
        except Exception as e:
            self.logger.error(f"FunCaptcha solving error: {e}")
            return None
    
    async def _create_task(self, task_data: Dict[str, Any]) -> Optional[str]:
        """Create a captcha solving task"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/createTask",
                    json=task_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status != 200:
                        self.logger.error(f"Failed to create task: HTTP {response.status}")
                        return None
                    
                    result = await response.json()
                    
                    if result.get("errorId") == 0:
                        task_id = result.get("taskId")
                        self.logger.debug(f"Task created: {task_id}")
                        return task_id
                    else:
                        self.logger.error(f"Task creation failed: {result.get('errorDescription')}")
                        return None
        
        except Exception as e:
            self.logger.error(f"Failed to create task: {e}")
            return None
    
    async def _get_task_result(self, task_id: str, max_wait_time: int = 120) -> Optional[str]:
        """Get the result of a captcha solving task"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/getTaskResult",
                        json={
                            "clientKey": self.api_key,
                            "taskId": task_id
                        },
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        
                        if response.status != 200:
                            self.logger.error(f"Failed to get task result: HTTP {response.status}")
                            return None
                        
                        result = await response.json()
                        
                        if result.get("errorId") == 0:
                            status = result.get("status")
                            
                            if status == "ready":
                                solution = result.get("solution", {})
                                
                                if "gRecaptchaResponse" in solution:
                                    return solution["gRecaptchaResponse"]
                                elif "token" in solution:
                                    return solution["token"]
                                elif "userAgent" in solution:
                                    return solution["userAgent"]
                                else:
                                    self.logger.error("Unknown solution format")
                                    return None
                            
                            elif status == "processing":
                                self.logger.debug(f"Task {task_id} still processing...")
                                await asyncio.sleep(3)
                                continue
                            
                            else:
                                self.logger.error(f"Task failed with status: {status}")
                                return None
                        
                        else:
                            self.logger.error(f"Task result error: {result.get('errorDescription')}")
                            return None
            
            self.logger.error(f"Task {task_id} timed out after {max_wait_time} seconds")
            return None
        
        except Exception as e:
            self.logger.error(f"Failed to get task result: {e}")
            return None
    
    async def get_balance(self) -> Optional[float]:
        """Get account balance from capsolver"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/getBalance",
                    json={"clientKey": self.api_key},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status != 200:
                        return None
                    
                    result = await response.json()
                    
                    if result.get("errorId") == 0:
                        return float(result.get("balance", 0))
                    else:
                        self.logger.error(f"Balance check failed: {result.get('errorDescription')}")
                        return None
        
        except Exception as e:
            self.logger.error(f"Failed to get balance: {e}")
            return None
