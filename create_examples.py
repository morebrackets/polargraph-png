#!/usr/bin/env python3
"""
Example script showing how to use the polargraph converter
"""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import os

# Create examples directory
os.makedirs('examples', exist_ok=True)

# Example 1: Simple gradient
print("Creating gradient example...")
img = Image.new('L', (300, 200), color=255)
draw = ImageDraw.Draw(img)
for x in range(300):
    gray = int(255 - (x / 300 * 255))
    draw.line([(x, 0), (x, 200)], fill=gray)
img.save('examples/gradient.png')

# Convert to SVG
subprocess.run([
    'python', 'polargraph_converter.py',
    'examples/gradient.png',
    '-o', 'examples/gradient.svg',
    '-l', '5',
    '-a', '12'
])

# Example 2: Circles pattern
print("\nCreating circles example...")
img = Image.new('L', (300, 200), color=255)
draw = ImageDraw.Draw(img)
for i in range(5):
    for j in range(3):
        x = 60 + i * 60
        y = 60 + j * 60
        radius = 25
        gray = int(50 + (i * 40))
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=gray)
img.save('examples/circles.png')

# Convert to SVG
subprocess.run([
    'python', 'polargraph_converter.py',
    'examples/circles.png',
    '-o', 'examples/circles.svg',
    '-l', '4',
    '-a', '10'
])

# Example 3: Text
print("\nCreating text example...")
img = Image.new('L', (400, 150), color=255)
draw = ImageDraw.Draw(img)
# Draw some simple text using basic shapes
draw.rectangle([50, 40, 100, 110], fill=100)
draw.rectangle([120, 40, 170, 110], fill=80)
draw.ellipse([190, 40, 240, 110], fill=60)
draw.polygon([(260, 110), (310, 110), (285, 40)], fill=40)
img.save('examples/shapes.png')

# Convert to SVG
subprocess.run([
    'python', 'polargraph_converter.py',
    'examples/shapes.png',
    '-o', 'examples/shapes.svg',
    '-l', '3',
    '-a', '15'
])

print("\nExamples created in 'examples/' directory!")
print("View the .svg files to see the Polargraph output.")
