#!/usr/bin/env python3
"""
Polargraph SVG Converter
Converts images to SVG format optimized for pen plotter/Polargraph drawing.
"""

import argparse
import math
import sys
from pathlib import Path
from PIL import Image


def convert_to_grayscale(image_path):
    """
    Load an image and convert it to grayscale.
    
    Args:
        image_path: Path to the input image
        
    Returns:
        PIL Image object in grayscale mode
    """
    try:
        img = Image.open(image_path)
        return img.convert('L')
    except Exception as e:
        print(f"Error loading image: {e}", file=sys.stderr)
        sys.exit(1)


def get_pixel_darkness(gray_value):
    """
    Convert grayscale value to darkness factor (0=white, 1=black).
    
    Args:
        gray_value: Grayscale pixel value (0-255)
        
    Returns:
        Darkness factor between 0 and 1
    """
    return 1.0 - (gray_value / 255.0)


def generate_wave_line(y, width, darkness_values, line_spacing, amplitude_scale):
    """
    Generate a wavy horizontal line based on pixel darkness values.
    
    Args:
        y: Y coordinate of the line
        width: Image width
        darkness_values: List of darkness values for each x position
        line_spacing: Vertical spacing between lines
        amplitude_scale: Scaling factor for wave amplitude
        
    Returns:
        List of (x, y) coordinate tuples for the polyline
    """
    points = []
    
    for x in range(width):
        darkness = darkness_values[x]
        
        # Modulate amplitude based on darkness
        # Darker pixels create larger wave amplitudes
        amplitude = darkness * amplitude_scale
        
        # Create wave with frequency modulation
        # Darker areas have higher frequency (more waves)
        base_frequency = 0.1
        frequency = base_frequency + (darkness * 0.2)
        
        # Calculate wave offset
        wave_offset = amplitude * math.sin(x * frequency)
        
        # Calculate final y position
        final_y = y + wave_offset
        
        points.append((x, final_y))
    
    return points


def check_line_collision(prev_line_points, curr_line_points, min_clearance=1.0):
    """
    Check if two consecutive lines are too close or touching.
    
    Args:
        prev_line_points: List of (x, y) points from previous line
        curr_line_points: List of (x, y) points from current line
        min_clearance: Minimum required distance between lines
        
    Returns:
        Tuple of (has_collision, min_distance_found)
    """
    if not prev_line_points:
        return False, float('inf')
    
    min_distance = float('inf')
    
    # Check vertical distance at each x position
    for i in range(min(len(prev_line_points), len(curr_line_points))):
        prev_y = prev_line_points[i][1]
        curr_y = curr_line_points[i][1]
        distance = abs(curr_y - prev_y)
        min_distance = min(min_distance, distance)
    
    has_collision = min_distance < min_clearance
    return has_collision, min_distance


def adjust_line_for_clearance(curr_line_points, prev_line_points, min_clearance=1.0):
    """
    Adjust current line points to maintain minimum clearance from previous line.
    
    Args:
        curr_line_points: List of (x, y) points from current line to adjust
        prev_line_points: List of (x, y) points from previous line
        min_clearance: Minimum required distance between lines
        
    Returns:
        Adjusted list of (x, y) points
    """
    if not prev_line_points:
        return curr_line_points
    
    adjusted_points = []
    
    for i in range(len(curr_line_points)):
        x, y = curr_line_points[i]
        
        if i < len(prev_line_points):
            prev_y = prev_line_points[i][1]
            
            # Ensure current line stays below previous line with minimum clearance
            if y < prev_y + min_clearance:
                y = prev_y + min_clearance
        
        adjusted_points.append((x, y))
    
    return adjusted_points


def generate_svg(grayscale_img, line_spacing=5, amplitude_scale=10, output_path=None):
    """
    Generate SVG from grayscale image with continuous horizontal paths.
    Automatically adjusts spacing to prevent line collisions.
    
    Args:
        grayscale_img: PIL Image in grayscale mode
        line_spacing: Vertical spacing between horizontal lines
        amplitude_scale: Scaling factor for wave amplitude
        output_path: Path to save the SVG file (optional)
        
    Returns:
        SVG content as string
    """
    width, height = grayscale_img.size
    
    # Calculate SVG dimensions with some padding
    svg_width = width
    svg_height = height
    
    # Start SVG content
    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">',
        '  <desc>Polargraph SVG - Generated from image with collision prevention</desc>',
        '  <g fill="none" stroke="black" stroke-width="0.5" stroke-linecap="round" stroke-linejoin="round">'
    ]
    
    # Track previous line for collision detection
    prev_line_points = None
    collision_count = 0
    total_lines = 0
    
    # Generate horizontal lines
    for y in range(0, height, line_spacing):
        total_lines += 1
        
        # Get pixel darkness values for this row
        darkness_values = []
        for x in range(width):
            pixel_value = grayscale_img.getpixel((x, y))
            darkness = get_pixel_darkness(pixel_value)
            darkness_values.append(darkness)
        
        # Generate wavy line based on darkness
        points = generate_wave_line(y, width, darkness_values, line_spacing, amplitude_scale)
        
        # Check for collision with previous line and adjust if needed
        min_clearance = 0.8  # Minimum spacing to prevent pen overlap
        if prev_line_points:
            has_collision, min_dist = check_line_collision(prev_line_points, points, min_clearance)
            if has_collision:
                collision_count += 1
                points = adjust_line_for_clearance(points, prev_line_points, min_clearance)
        
        # Create SVG polyline element
        points_str = ' '.join([f'{x:.2f},{y:.2f}' for x, y in points])
        svg_lines.append(f'    <polyline points="{points_str}"/>')
        
        # Store current line for next iteration
        prev_line_points = points
    
    # Close SVG tags
    svg_lines.extend([
        '  </g>',
        '</svg>'
    ])
    
    svg_content = '\n'.join(svg_lines)
    
    # Save to file if output path is provided
    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            print(f"SVG saved to: {output_path}")
            if collision_count > 0:
                print(f"Collision prevention: {collision_count}/{total_lines} lines adjusted for clearance")
        except Exception as e:
            print(f"Error saving SVG: {e}", file=sys.stderr)
            sys.exit(1)
    
    return svg_content


def main():
    """Main entry point for the Polargraph SVG converter."""
    parser = argparse.ArgumentParser(
        description='Convert an image to Polargraph SVG format optimized for pen plotters.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s input.png -o output.svg
  %(prog)s photo.jpg -o drawing.svg -l 3 -a 15
  %(prog)s image.png -o result.svg --line-spacing 8 --amplitude-scale 12
        '''
    )
    
    parser.add_argument(
        'input_image',
        type=str,
        help='Path to input image file'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help='Path to output SVG file'
    )
    
    parser.add_argument(
        '-l', '--line-spacing',
        type=float,
        default=5.0,
        help='Vertical spacing between horizontal lines in pixels (default: 5.0)'
    )
    
    parser.add_argument(
        '-a', '--amplitude-scale',
        type=float,
        default=10.0,
        help='Scaling factor for wave amplitude (default: 10.0)'
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    input_path = Path(args.input_image)
    if not input_path.exists():
        print(f"Error: Input file does not exist: {args.input_image}", file=sys.stderr)
        sys.exit(1)
    
    # Validate parameters
    if args.line_spacing <= 0:
        print("Error: Line spacing must be greater than 0", file=sys.stderr)
        sys.exit(1)
    
    if args.amplitude_scale < 0:
        print("Error: Amplitude scale must be non-negative", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loading image: {args.input_image}")
    grayscale_img = convert_to_grayscale(args.input_image)
    
    print(f"Image size: {grayscale_img.size[0]}x{grayscale_img.size[1]}")
    print(f"Line spacing: {args.line_spacing}")
    print(f"Amplitude scale: {args.amplitude_scale}")
    
    print("Generating SVG...")
    generate_svg(
        grayscale_img,
        line_spacing=int(args.line_spacing),
        amplitude_scale=args.amplitude_scale,
        output_path=args.output
    )
    
    print("Done!")


if __name__ == '__main__':
    main()
