import random
import asyncio

from humancursor_playwright.utilities.human_curve_generator import HumanizeMouseTrajectory
from humancursor_playwright.utilities.calculate_and_randomize import (
    generate_random_curve_parameters, 
    calculate_absolute_offset
)


class PlaywrightAdjuster:
    def __init__(self, page):
        """
        Initialize PlaywrightAdjuster with a Playwright page
        
        Args:
            page: Playwright Page instance
        """
        self.page = page
        self.origin_coordinate = [0, 0]

    async def move_to(
        self,
        element_or_pos,
        origin_coordinates=None,
        absolute_offset=False,
        relative_position=None,
        human_curve=None,
        steady=False
    ):
        """Moves the cursor, trying to mimic human behaviour!"""
        origin = origin_coordinates
        if origin_coordinates is None:
            origin = self.origin_coordinate

        pre_origin = tuple(origin)
        
        if isinstance(element_or_pos, list):
            # Handle direct coordinates
            if not absolute_offset:
                x, y = element_or_pos[0], element_or_pos[1]
            else:
                x, y = (
                    element_or_pos[0] + pre_origin[0],
                    element_or_pos[1] + pre_origin[1],
                )
        else:
            # Handle Playwright locator
            try:
                bbox = await element_or_pos.bounding_box()
            except Exception as e:
                print(f"Error obtaining bounding box for element: {e}")
                return origin
                
            if bbox is None or bbox.get("width", 0) == 0 or bbox.get("height", 0) == 0:
                print("Could not find position for", element_or_pos)
                return origin
                
            destination = {"x": bbox.get("x", 0), "y": bbox.get("y", 0)}
            
            if relative_position is None:
                # Random position within element bounds
                x_random_off = random.choice(range(20, 80)) / 100
                y_random_off = random.choice(range(20, 80)) / 100

                element_width = bbox["width"]
                element_height = bbox["height"]
                
                x, y = destination["x"] + (
                    element_width * x_random_off
                ), destination["y"] + (element_height * y_random_off)
            else:
                # Specific relative position
                abs_exact_offset = await calculate_absolute_offset(
                    element_or_pos, relative_position, bbox
                )
                x_exact_off, y_exact_off = abs_exact_offset[0], abs_exact_offset[1]
                x, y = destination["x"] + x_exact_off, destination["y"] + y_exact_off

        # Generate curve parameters
        (
            offset_boundary_x,
            offset_boundary_y,
            knots_count,
            distortion_mean,
            distortion_st_dev,
            distortion_frequency,
            tween,
            target_points,
        ) = await generate_random_curve_parameters(
            self.page, [origin[0], origin[1]], [x, y]
        )
        
        if steady:
            offset_boundary_x, offset_boundary_y = 10, 10
            distortion_mean, distortion_st_dev, distortion_frequency = 1.2, 1.2, 1
            
        if not human_curve:
            human_curve = HumanizeMouseTrajectory(
                [origin[0], origin[1]],
                [x, y],
                offset_boundary_x=offset_boundary_x,
                offset_boundary_y=offset_boundary_y,
                knots_count=knots_count,
                distortion_mean=distortion_mean,
                distortion_st_dev=distortion_st_dev,
                distortion_frequency=distortion_frequency,
                tween=tween,
                target_points=target_points,
            )

        # Move the cursor along the human-like curve using Playwright's mouse API
        for i, point in enumerate(human_curve.points):
            # Move to each point in the curve
            await self.page.mouse.move(point[0], point[1])
            
            # Add small delays to make movement more human-like
            if i < len(human_curve.points) - 1:
                await asyncio.sleep(random.uniform(0.001, 0.005))
            
            # Update the origin coordinates
            origin[0], origin[1] = point[0], point[1]

        self.origin_coordinate = [x, y]
        return [x, y]