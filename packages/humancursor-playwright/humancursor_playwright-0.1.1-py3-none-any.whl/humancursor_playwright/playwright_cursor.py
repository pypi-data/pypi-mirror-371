import asyncio
import random
from typing import Union

from humancursor_playwright.utilities.playwright_adjuster import PlaywrightAdjuster


class PlaywrightCursor:
    def __init__(self, page):
        """
        Initialize PlaywrightCursor with a Playwright page
        
        Args:
            page: Playwright Page instance
        """
        self.page = page
        self.human = PlaywrightAdjuster(page)
        self.origin_coordinates = [0, 0]

    async def move_to(
        self,
        element_or_pos,
        relative_position: list = None,
        absolute_offset: bool = False,
        origin_coordinates=None,
        steady=False
    ):
        """Moves to element or coordinates with human curve"""
        if not await self.scroll_into_view_of_element(element_or_pos):
            return False
            
        if origin_coordinates is None:
            origin_coordinates = self.origin_coordinates
            
        self.origin_coordinates = await self.human.move_to(
            element_or_pos,
            origin_coordinates=origin_coordinates,
            absolute_offset=absolute_offset,
            relative_position=relative_position,
            steady=steady
        )
        return self.origin_coordinates

    async def click_on(
        self,
        element_or_pos,
        number_of_clicks: int = 1,
        click_duration: float = 0,
        relative_position: list = None,
        absolute_offset: bool = False,
        origin_coordinates=None,
        steady=False,
        button: str = 'left'
    ):
        """Moves to element or coordinates with human curve, and clicks on it a specified number of times, default is 1"""
        await self.move_to(
            element_or_pos,
            origin_coordinates=origin_coordinates,
            absolute_offset=absolute_offset,
            relative_position=relative_position,
            steady=steady
        )
        await self.click(number_of_clicks=number_of_clicks, click_duration=click_duration, button=button)
        return True

    async def click(self, number_of_clicks: int = 1, click_duration: float = 0, button: str = 'left'):
        """Performs the click action"""
        for _ in range(number_of_clicks):
            if click_duration:
                # Click and hold for specified duration
                await self.page.mouse.down(button=button)
                await asyncio.sleep(click_duration)
                await self.page.mouse.up(button=button)
            else:
                # Regular click
                await self.page.mouse.click(self.origin_coordinates[0], self.origin_coordinates[1], button=button)
                
            # Add small delay between multiple clicks
            if number_of_clicks > 1:
                await asyncio.sleep(random.uniform(0.05, 0.15))
        return True

    async def move_by_offset(self, x: int, y: int, steady=False):
        """Moves the cursor with human curve, by specified number of x and y pixels"""
        self.origin_coordinates = await self.human.move_to([x, y], absolute_offset=True, steady=steady)
        return True

    async def drag_and_drop(
        self,
        drag_from_element,
        drag_to_element=None,
        drag_from_relative_position: list = None,
        drag_to_relative_position: list = None,
        steady=False
    ):
        """Moves to element or coordinates, clicks and holds, dragging it to another element, with human curve"""
        # Move to source element
        if drag_from_relative_position is None:
            await self.move_to(drag_from_element)
        else:
            await self.move_to(
                drag_from_element, relative_position=drag_from_relative_position
            )

        # Start drag
        await self.page.mouse.down()

        if drag_to_element is None:
            # Just release if no target element
            await self.page.mouse.up()
        else:
            # Move to target element
            if drag_to_relative_position is None:
                await self.move_to(drag_to_element, steady=steady)
            else:
                await self.move_to(
                    drag_to_element, relative_position=drag_to_relative_position, steady=steady
                )
            
            # Release
            await self.page.mouse.up()

        return True

    async def control_scroll_bar(
        self,
        scroll_bar_element,
        amount_by_percentage: float,
        orientation: str = "horizontal",
        steady=False
    ):
        """Adjusts any scroll bar on the webpage, by the amount you want in float number from 0 to 1
        representing percentage of fullness, orientation of the scroll bar must also be defined by user
        horizontal or vertical"""
        direction = True if orientation == "horizontal" else False

        await self.move_to(scroll_bar_element)
        
        # Start drag on scrollbar
        await self.page.mouse.down()
        
        # Move to target position
        if direction:
            await self.move_to(
                scroll_bar_element,
                relative_position=[amount_by_percentage, random.randint(0, 100) / 100],
                steady=steady
            )
        else:
            await self.move_to(
                scroll_bar_element,
                relative_position=[random.randint(0, 100) / 100, amount_by_percentage],
                steady=steady
            )

        # Release
        await self.page.mouse.up()
        return True

    async def scroll_into_view_of_element(self, element):
        """Scrolls the element into viewport, if not already in it"""
        # Check if element has locator methods (works for both Playwright and Patchright)
        if hasattr(element, 'scroll_into_view_if_needed') and hasattr(element, 'bounding_box'):
            try:
                # Use Playwright's built-in scroll into view
                await element.scroll_into_view_if_needed()
                # Add a small delay for smooth scrolling
                await asyncio.sleep(random.uniform(0.8, 1.4))
                return True
            except Exception as e:
                print(f"Error scrolling element into view: {e}")
                return False
        elif isinstance(element, list):
            # If coordinates are provided directly, assume no scrolling is needed
            return True
        else:
            print("Incorrect Element or Coordinates values!")
            return False

    async def show_cursor(self):
        """Shows a red dot cursor on the page to visualize movements"""
        await self.page.evaluate('''
        (function() {
            let dot;
            function displayRedDot(event) {
              // Get the cursor position
              const x = event.clientX;
              const y = event.clientY;

              if (!dot) {
                // Create a new div element for the red dot if it doesn't exist
                dot = document.createElement("div");
                // Style the dot with CSS
                dot.style.position = "fixed";
                dot.style.width = "5px";
                dot.style.height = "5px";
                dot.style.borderRadius = "50%";
                dot.style.backgroundColor = "red";
                dot.style.zIndex = "999999";
                dot.style.pointerEvents = "none";
                // Add the dot to the page
                document.body.appendChild(dot);
              }

              // Update the dot's position
              dot.style.left = x + "px";
              dot.style.top = y + "px";
            }

            // Add event listener to update the dot's position on mousemove
            document.addEventListener("mousemove", displayRedDot);
        })();
        ''')

    async def hide_cursor(self):
        """Hides the red dot cursor if it was shown"""
        await self.page.evaluate('''
        (function() {
            const existingDots = document.querySelectorAll('[style*="background-color: red"][style*="position: fixed"]');
            existingDots.forEach(dot => dot.remove());
        })();
        ''')