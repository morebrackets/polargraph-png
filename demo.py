#!/usr/bin/env python3
"""
Demo script showing various Polargraph converter capabilities
"""

import subprocess
import sys
from PIL import Image, ImageDraw

def run_converter(input_file, output_file, line_spacing, amplitude):
    """Run the converter with specific parameters"""
    cmd = [
        'python', 'polargraph_converter.py',
        input_file, '-o', output_file,
        '-l', str(line_spacing), '-a', str(amplitude)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ Created {output_file}")
    else:
        print(f"✗ Failed: {result.stderr}")
    return result.returncode == 0

def main():
    print("=== Polargraph Converter Demo ===\n")
    
    # Create a demo image
    print("Creating demo image...")
    img = Image.new('L', (400, 300), color=255)
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background
    for y in range(300):
        gray = int(255 - (y / 300 * 200))
        draw.line([(0, y), (400, y)], fill=gray)
    
    # Add some shapes
    draw.ellipse([100, 80, 300, 220], fill=80, outline=20)
    draw.rectangle([20, 20, 80, 80], fill=30)
    draw.polygon([(350, 250), (380, 280), (320, 280)], fill=50)
    
    img.save('demo.png')
    print("✓ Created demo.png\n")
    
    print("Generating various SVG outputs...\n")
    
    # Demo 1: Standard settings
    print("1. Standard settings (balanced)")
    run_converter('demo.png', 'demo_standard.svg', 5, 10)
    print()
    
    # Demo 2: Fine detail
    print("2. Fine detail (tight spacing, subtle waves)")
    run_converter('demo.png', 'demo_fine.svg', 2.5, 6)
    print()
    
    # Demo 3: Bold artistic
    print("3. Bold artistic (wide spacing, dramatic waves)")
    run_converter('demo.png', 'demo_bold.svg', 8, 20)
    print()
    
    # Demo 4: High collision scenario
    print("4. High amplitude (demonstrates collision prevention)")
    run_converter('demo.png', 'demo_collision_test.svg', 3, 25)
    print()
    
    print("=== Demo Complete! ===")
    print("\nGenerated files:")
    print("  demo.png - Source image")
    print("  demo_standard.svg - Balanced output")
    print("  demo_fine.svg - Fine detail")
    print("  demo_bold.svg - Bold artistic")
    print("  demo_collision_test.svg - Collision prevention demo")
    print("\nView the SVG files in a browser or SVG editor to see the results.")

if __name__ == '__main__':
    main()
