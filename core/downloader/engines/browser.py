# core/downloader/engines/browser.py
import asyncio
from playwright.async_api import async_playwright
from core.state.models import Job
from core.state.persistence import write_trace
import config

async def download_interception(job: Job) -> bool:
    """Uses Playwright to intercept media network requests."""
    write_trace(job.work_dir, "[BROWSER] Launching headless interceptor...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=config.DEFAULT_UA)
        page = await context.new_page()
        
        # Intercept request to find media URL
        media_url = None
        def handle_response(response):
            nonlocal media_url
            if any(ext in response.url for ext in [".m3u8", ".mp4"]):
                media_url = response.url
        
        page.on("response", handle_response)
        
        try:
            await page.goto(job.url, timeout=30000)
            await asyncio.sleep(5) # Wait for JS to render
        except Exception as e:
            write_trace(job.work_dir, f"[BROWSER] Page load error: {e}")
        finally:
            await browser.close()
            
        if media_url:
            write_trace(job.work_dir, f"[BROWSER] Found media via intercept: {media_url}")
            # Update job URL and re-run through manager or treat as direct download
            job.url = media_url
            return True
            
    return False
