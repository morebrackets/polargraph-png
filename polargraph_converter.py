#!/usr/bin/env python3
"""
Polargraph SVG Converter
Converts images to SVG format optimized for pen plotter/Polargraph drawing.
"""

import argparse
import math
import random
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


def generate_wave_line_segments(y, width, darkness_values, line_spacing, amplitude_scale, 
                                darkness_threshold=0.1, organic=False, random_seed=None):
    """
    Generate wavy horizontal line segments based on pixel darkness values.
    Only creates line segments where darkness exceeds threshold (skips white background).
    
    Args:
        y: Y coordinate of the line
        width: Image width
        darkness_values: List of darkness values for each x position
        line_spacing: Vertical spacing between lines
        amplitude_scale: Scaling factor for wave amplitude
        darkness_threshold: Minimum darkness to draw a line (0.1 = skip pixels lighter than ~230 gray)
        organic: If True, adds randomness and easing for hand-drawn look
        random_seed: Optional seed for reproducible randomness (used with y coordinate)
        
    Returns:
        List of line segments, where each segment is a list of (x, y) coordinate tuples
    """
    segments = []
    current_segment = []
    
    # Set random seed based on y position for consistent but varied results
    if organic and random_seed is not None:
        random.seed(random_seed + int(y * 1000))
    
    # Generate organic variation parameters for this line
    organic_phase_offset = random.uniform(0, 2 * math.pi) if organic else 0
    organic_freq_variation = random.uniform(0.8, 1.2) if organic else 1.0
    
    for x in range(width):
        darkness = darkness_values[x]
        
        # Skip white/light background areas
        if darkness < darkness_threshold:
            # End current segment if we have one
            if current_segment:
                segments.append(current_segment)
                current_segment = []
            continue
        
        # Modulate amplitude based on darkness
        # Darker pixels create larger wave amplitudes
        amplitude = darkness * amplitude_scale
        
        # Create wave with frequency modulation
        # Darker areas have higher frequency (more waves)
        base_frequency = 0.1
        frequency = base_frequency + (darkness * 0.2)
        
        # Apply organic frequency variation
        if organic:
            frequency *= organic_freq_variation
        
        # Calculate wave offset
        wave_offset = amplitude * math.sin(x * frequency + organic_phase_offset)
        
        # Add organic randomness to y position
        if organic:
            # Add subtle random wobble (max 0.5 pixels)
            random_wobble = random.uniform(-0.5, 0.5) * darkness
            wave_offset += random_wobble
            
            # Add easing for smoother, more natural transitions
            # Use a subtle ease-in-out based on position in the wave cycle
            ease_factor = (math.sin(x * frequency * 2) * 0.3 + 1.0)
            wave_offset *= ease_factor
        
        # Calculate final y position
        final_y = y + wave_offset
        
        current_segment.append((x, final_y))
    
    # Don't forget the last segment
    if current_segment:
        segments.append(current_segment)
    
    return segments


def check_segment_collision(prev_segments, curr_segments, min_clearance=1.0):
    """
    Check if any segments from two consecutive lines are too close or touching.
    
    Args:
        prev_segments: List of line segments from previous line
        curr_segments: List of line segments from current line
        min_clearance: Minimum required distance between lines
        
    Returns:
        Tuple of (has_collision, min_distance_found)
    """
    if not prev_segments or not curr_segments:
        return False, float('inf')
    
    min_distance = float('inf')
    
    # Check each current segment against all previous segments
    for curr_segment in curr_segments:
        for prev_segment in prev_segments:
            # Check overlapping x ranges
            curr_x_min = curr_segment[0][0]
            curr_x_max = curr_segment[-1][0]
            prev_x_min = prev_segment[0][0]
            prev_x_max = prev_segment[-1][0]
            
            # Check if segments overlap in x dimension
            if curr_x_max >= prev_x_min and curr_x_min <= prev_x_max:
                # Check vertical distance at overlapping points
                for curr_x, curr_y in curr_segment:
                    # Find corresponding point in prev_segment
                    for prev_x, prev_y in prev_segment:
                        if abs(curr_x - prev_x) < 1:  # Same x position (within 1 pixel)
                            distance = abs(curr_y - prev_y)
                            min_distance = min(min_distance, distance)
    
    has_collision = min_distance < min_clearance
    return has_collision, min_distance


def adjust_segments_for_clearance(curr_segments, prev_segments, min_clearance=1.0):
    """
    Adjust current line segments to maintain minimum clearance from previous line segments.
    
    Args:
        curr_segments: List of line segments from current line to adjust
        prev_segments: List of line segments from previous line
        min_clearance: Minimum required distance between lines
        
    Returns:
        Adjusted list of line segments
    """
    if not prev_segments:
        return curr_segments
    
    adjusted_segments = []
    
    for curr_segment in curr_segments:
        adjusted_segment = []
        
        for x, y in curr_segment:
            adjusted_y = y
            
            # Check against all previous segments
            for prev_segment in prev_segments:
                # Find closest point in previous segment at similar x
                for prev_x, prev_y in prev_segment:
                    if abs(x - prev_x) < 1:  # Same x position
                        # Ensure current point stays below previous with minimum clearance
                        if adjusted_y < prev_y + min_clearance:
                            adjusted_y = prev_y + min_clearance
                        break
            
            adjusted_segment.append((x, adjusted_y))
        
        adjusted_segments.append(adjusted_segment)
    
    return adjusted_segments


def generate_svg(grayscale_img, line_spacing=5, amplitude_scale=10, organic=False, output_path=None):
    """
    Generate SVG from grayscale image with segmented horizontal paths.
    Only generates lines where content exists (skips white/light background).
    Automatically adjusts spacing to prevent line collisions.
    
    Args:
        grayscale_img: PIL Image in grayscale mode
        line_spacing: Vertical spacing between horizontal lines
        amplitude_scale: Scaling factor for wave amplitude
        organic: If True, adds randomness and easing for hand-drawn look
        output_path: Path to save the SVG file (optional)
        
    Returns:
        SVG content as string
    """
    width, height = grayscale_img.size
    
    # Calculate SVG dimensions with some padding
    svg_width = width
    svg_height = height
    
    # Random seed for organic mode (use consistent seed for reproducible results)
    random_seed = 42 if organic else None
    
    # Start SVG content
    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">',
        f'  <desc>Polargraph SVG - Generated from image{"with organic style" if organic else " with collision prevention"}</desc>',
        '  <g fill="none" stroke="black" stroke-width="0.5" stroke-linecap="round" stroke-linejoin="round">'
    ]
    
    # Track previous line segments for collision detection
    prev_line_segments = None
    collision_count = 0
    total_lines = 0
    
    # Generate horizontal lines
    # Use floating point arithmetic for line_spacing, convert to int for pixel access
    y = 0
    while y < height:
        total_lines += 1
        y_int = int(y)
        
        # Get pixel darkness values for this row
        darkness_values = []
        for x in range(width):
            pixel_value = grayscale_img.getpixel((x, y_int))
            darkness = get_pixel_darkness(pixel_value)
            darkness_values.append(darkness)
        
        # Generate wavy line segments based on darkness (skips white background)
        segments = generate_wave_line_segments(y, width, darkness_values, line_spacing, 
                                              amplitude_scale, organic=organic, random_seed=random_seed)
        
        # Skip this row if no segments were generated (all white)
        if not segments:
            y += line_spacing
            continue
        
        # Check for collision with previous line and adjust if needed
        min_clearance = 0.8  # Minimum spacing to prevent pen overlap
        if prev_line_segments:
            has_collision, min_dist = check_segment_collision(prev_line_segments, segments, min_clearance)
            if has_collision:
                collision_count += 1
                segments = adjust_segments_for_clearance(segments, prev_line_segments, min_clearance)
        
        # Create SVG polyline elements for each segment
        for segment in segments:
            if len(segment) >= 2:  # Only draw if segment has at least 2 points
                points_str = ' '.join([f'{x:.2f},{y:.2f}' for x, y in segment])
                svg_lines.append(f'    <polyline points="{points_str}"/>')
        
        # Store current segments for next iteration
        prev_line_segments = segments
        
        # Move to next line
        y += line_spacing
    
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
    
    parser.add_argument(
        '--organic',
        action='store_true',
        help='Enable organic/hand-drawn style with randomness and easing'
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
    if args.organic:
        print("Organic mode: ENABLED (hand-drawn style with randomness)")
    
    print("Generating SVG...")
    generate_svg(
        grayscale_img,
        line_spacing=args.line_spacing,
        amplitude_scale=args.amplitude_scale,
        organic=args.organic,
        output_path=args.output
    )
    
    print("Done!")


if __name__ == '__main__':
    main()
