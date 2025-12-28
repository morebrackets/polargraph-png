# Polargraph PNG to SVG Converter

Convert images to Polargraph SVG format optimized for pen plotters and drawing machines.

## Features

- Converts any image format to grayscale
- Generates segmented horizontal SVG paths (rows) only where content exists
- **Skips white/light background areas** - only draws lines for main image content
- Lines are broken into segments rather than continuous end-to-end strokes
- Modulates amplitude and frequency of lines based on pixel darkness
- **Automatic collision detection and prevention** - ensures lines never overlap or touch
- Clean, connected `<polyline>` elements optimized for pen plotter G-code conversion
- Configurable line spacing and amplitude scaling
- Precision-focused output for physical drawing without overlaps

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Basic usage:

```bash
python polargraph_converter.py input.png -o output.svg
```

With custom parameters:

```bash
python polargraph_converter.py input.jpg -o output.svg --line-spacing 3 --amplitude-scale 15
```

### Command Line Arguments

- `input_image` - Path to the input image file (required)
- `-o, --output` - Path to output SVG file (required)
- `-l, --line-spacing` - Vertical spacing between horizontal lines in pixels (default: 5.0)
- `-a, --amplitude-scale` - Scaling factor for wave amplitude (default: 10.0)

### Parameters Guide

**Line Spacing (`--line-spacing`)**
- Controls the vertical distance between horizontal drawing lines
- Smaller values (2-3) = denser, more detailed output
- Larger values (8-10) = sparser, faster to draw
- Recommended range: 3-8 pixels

**Amplitude Scale (`--amplitude-scale`)**
- Controls the maximum wave amplitude (vertical displacement)
- Smaller values (5-10) = subtle waves, cleaner look
- Larger values (15-25) = dramatic waves, more artistic
- Recommended range: 8-20

## How It Works

1. **Grayscale Conversion**: Input image is converted to grayscale
2. **Row Processing**: Image is processed row by row at specified line spacing
3. **Darkness Analysis**: Each pixel's darkness is calculated (0=white, 1=black)
4. **Background Filtering**: Pixels lighter than threshold (~230 gray value) are skipped
5. **Line Segmentation**: Lines are broken into segments where content exists (not continuous end-to-end)
6. **Wave Generation**: For each segment:
   - Amplitude is modulated by pixel darkness (darker = larger waves)
   - Frequency is modulated by pixel darkness (darker = more waves)
7. **Collision Detection**: Automatically checks if adjacent line segments would overlap
8. **Collision Prevention**: Segments that would touch are adjusted to maintain minimum clearance (0.8 pixels)
9. **SVG Output**: Segmented polyline elements are generated for optimal plotter performance

### Background Skipping

The converter intelligently skips white/light background areas:
- Only draws lines where pixel darkness exceeds 0.1 threshold (roughly pixels darker than 230 gray)
- Creates separate line segments for each content region
- Minimizes unnecessary pen movement over blank areas
- Reduces file size and plotting time

### Collision Prevention

The tool automatically detects when horizontal line segments would overlap or touch due to high wave amplitudes. When a collision is detected:
- The affected segment is adjusted downward to maintain minimum clearance
- A message is displayed showing how many lines were adjusted
- This ensures clean pen plotter output without overlapping strokes

Example output:
```
Collision prevention: 23/34 lines adjusted for clearance
```

## SVG Output

The generated SVG contains:
- Clean `<polyline>` elements, multiple per horizontal row (segmented)
- Lines only where content exists (skips white background)
- No overlapping paths
- Optimized for pen plotter G-code conversion
- Stroke width set to 0.5 for precision drawing
- Round line caps and joins for smooth output

## Examples

Create a detailed drawing with fine lines:
```bash
python polargraph_converter.py portrait.jpg -o portrait.svg -l 3 -a 12
```

Create a quick sketch with bold waves:
```bash
python polargraph_converter.py landscape.png -o landscape.svg -l 8 -a 20
```

Run the demo script to see various output styles:
```bash
python demo.py
```

This will generate several example SVGs showing different parameter combinations and the collision prevention system in action.

## License

MIT License