import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from humancursor_playwright import PlaywrightCursor


async def main():
    async with async_playwright() as playwright:
        # Launch browser
        browser = await playwright.chromium.launch(headless=False)
        
        # Create a new page
        page = await browser.new_page()
        
        try:
            # Navigate to a drag and drop demo page
            await page.goto("https://www.w3schools.com/html/html5_draganddrop.asp")
            
            # Initialize HumanCursor
            cursor = PlaywrightCursor(page)
            
            # Show the cursor for visualization
            await cursor.show_cursor()
            
            # Find the draggable element and drop target
            draggable = page.locator("#drag1")
            droppable = page.locator("#div2")
            
            # Wait for elements to be visible
            await draggable.wait_for()
            await droppable.wait_for()
            
            # Perform drag and drop with human-like movement
            await cursor.drag_and_drop(draggable, droppable)
            
            # Wait to see the result
            await asyncio.sleep(3)
            
        finally:
            # Close the browser
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())