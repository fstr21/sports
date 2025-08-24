import asyncio
import os
from typing import Dict, Any, Optional
from pathlib import Path
import tempfile
from playwright.async_api import async_playwright
from jinja2 import Template
import logging

logger = logging.getLogger(__name__)

class HTMLToImageConverter:
    """Convert HTML templates to images using Playwright"""
    
    def __init__(self):
        self.browser = None
        self.playwright = None
        
    async def start_browser(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            # Use chromium for best rendering quality
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            logger.info("Playwright browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start Playwright browser: {e}")
            raise
    
    async def close_browser(self):
        """Close Playwright browser"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Playwright browser closed")
        except Exception as e:
            logger.error(f"Error closing Playwright browser: {e}")
    
    async def render_html_to_image(
        self, 
        html_content: str, 
        width: int = 850, 
        height: Optional[int] = None,
        format: str = "png"
    ) -> bytes:
        """
        Render HTML content to image bytes
        
        Args:
            html_content: HTML string to render
            width: Image width in pixels
            height: Image height in pixels (auto if None)
            format: Image format ('png' or 'jpeg')
        
        Returns:
            Image bytes
        """
        if not self.browser:
            await self.start_browser()
            
        try:
            page = await self.browser.new_page()
            
            # Set viewport size
            await page.set_viewport_size({
                "width": width, 
                "height": height or 1200
            })
            
            # Load HTML content
            await page.set_content(html_content, wait_until="networkidle")
            
            # Wait for fonts to load
            await page.wait_for_timeout(1000)
            
            # Take screenshot
            if height:
                # Fixed height
                screenshot = await page.screenshot(
                    type=format,
                    full_page=False,
                    clip={
                        "x": 0,
                        "y": 0, 
                        "width": width,
                        "height": height
                    }
                )
            else:
                # Full page screenshot
                screenshot = await page.screenshot(
                    type=format,
                    full_page=True
                )
            
            await page.close()
            return screenshot
            
        except Exception as e:
            logger.error(f"Error rendering HTML to image: {e}")
            raise
    
    async def generate_baseball_analysis_image(
        self, 
        template_data: Dict[str, Any], 
        template_path: Optional[str] = None
    ) -> bytes:
        """
        Generate baseball analysis image from template data
        
        Args:
            template_data: Dictionary containing template variables
            template_path: Path to HTML template file
        
        Returns:
            PNG image bytes
        """
        try:
            # Default template path
            if not template_path:
                current_dir = Path(__file__).parent.parent
                template_path = current_dir / "templates" / "baseball_analysis.html"
            
            # Load template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Render template with data
            template = Template(template_content)
            rendered_html = template.render(**template_data)
            
            # Convert to image - much larger for Discord preview
            image_bytes = await self.render_html_to_image(
                rendered_html,
                width=3600,  # Tripled from 1200 to 3600 for maximum Discord preview
                format="png"
            )
            
            logger.info(f"Generated baseball analysis image ({len(image_bytes)} bytes)")
            return image_bytes
            
        except Exception as e:
            logger.error(f"Error generating baseball analysis image: {e}")
            raise

# Global converter instance
_converter_instance = None

async def get_html_converter() -> HTMLToImageConverter:
    """Get or create global HTML converter instance"""
    global _converter_instance
    if not _converter_instance:
        _converter_instance = HTMLToImageConverter()
        await _converter_instance.start_browser()
    return _converter_instance

async def cleanup_html_converter():
    """Cleanup global HTML converter instance"""
    global _converter_instance
    if _converter_instance:
        await _converter_instance.close_browser()
        _converter_instance = None

async def create_baseball_analysis_image(template_data: Dict[str, Any]) -> bytes:
    """
    Convenience function to create baseball analysis image
    
    Args:
        template_data: Dictionary with template variables
    
    Returns:
        PNG image bytes
    """
    converter = await get_html_converter()
    return await converter.generate_baseball_analysis_image(template_data)