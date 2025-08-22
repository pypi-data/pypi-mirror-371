import random
import pytweening


async def generate_random_curve_parameters(page, from_point, to_point):
    """Generates random parameters for the curve"""
    # Get window size using Playwright's viewport or evaluate
    viewport_size = page.viewport_size
    if viewport_size:
        window_width = viewport_size['width']
        window_height = viewport_size['height']
    else:
        # Fallback to evaluate if viewport_size is not available
        window_size = await page.evaluate("""
            () => ({
                width: window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth,
                height: window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight
            })
        """)
        window_width = window_size["width"]
        window_height = window_size["height"]
    
    # Calculate distance between points
    distance = ((from_point[0] - to_point[0]) ** 2 + (from_point[1] - to_point[1]) ** 2) ** 0.5
    
    # Adjust parameters based on distance
    if distance < 100:
        offset_boundary_x = random.randint(10, 20)
        offset_boundary_y = random.randint(10, 20)
        knots_count = random.randint(1, 2)
    elif distance < 300:
        offset_boundary_x = random.randint(20, 40)
        offset_boundary_y = random.randint(20, 40)
        knots_count = random.randint(2, 3)
    else:
        offset_boundary_x = random.randint(40, 80)
        offset_boundary_y = random.randint(40, 80)
        knots_count = random.randint(3, 4)
    
    # Ensure offsets don't go beyond window boundaries
    offset_boundary_x = min(offset_boundary_x, window_width // 4)
    offset_boundary_y = min(offset_boundary_y, window_height // 4)
    
    # Generate random distortion parameters
    distortion_mean = random.uniform(0.8, 1.2)
    distortion_st_dev = random.uniform(0.8, 1.2)
    distortion_frequency = random.uniform(0.3, 0.7)
    
    # Choose a random tweening function
    tween_functions = [
        pytweening.easeInOutQuad,
        pytweening.easeOutQuad,
        pytweening.easeInOutSine,
        pytweening.easeInOutCubic,
        pytweening.easeInOutQuint
    ]
    tween = random.choice(tween_functions)
    
    # Determine target points based on distance
    target_points = max(int(distance / 5), 50)
    target_points = min(target_points, 200)  # Cap at 200 points
    
    return (
        offset_boundary_x,
        offset_boundary_y,
        knots_count,
        distortion_mean,
        distortion_st_dev,
        distortion_frequency,
        tween,
        target_points,
    )


async def calculate_absolute_offset(locator, relative_position, bbox=None):
    """Calculates the absolute offset based on relative position for a Playwright locator"""
    if bbox is None:
        # Get element bounding box using Playwright's bounding_box method
        bbox = await locator.bounding_box()
        
    if bbox is None:
        raise ValueError("Could not get bounding box for element")
    
    element_width = bbox["width"]
    element_height = bbox["height"]
    
    x_exact_off = element_width * relative_position[0]
    y_exact_off = element_height * relative_position[1]
    
    return [x_exact_off, y_exact_off]