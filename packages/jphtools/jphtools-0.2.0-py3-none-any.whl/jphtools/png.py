import os
from pathlib import Path
from PIL import Image, ImageOps
import click


def compress_png(input_path, output_path=None, quality=85, max_width=None, max_height=None):
    """
    Compress a PNG file with various optimization options.
    
    Args:
        input_path: Path to input PNG file
        output_path: Path for output file (defaults to input_path with _compressed suffix)
        quality: Quality for optimization (1-100, higher = better quality)
        max_width: Maximum width to resize to (maintains aspect ratio)
        max_height: Maximum height to resize to (maintains aspect ratio)
    
    Returns:
        tuple: (output_path, original_size, compressed_size, compression_ratio)
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if not input_path.suffix.lower() == '.png':
        raise ValueError("Input file must be a PNG")
    
    # Default output path
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_compressed{input_path.suffix}"
    else:
        output_path = Path(output_path)
    
    # Get original file size
    original_size = input_path.stat().st_size
    
    # Open and process image
    with Image.open(input_path) as img:
        # Convert to RGB if necessary (for better compression)
        if img.mode in ('RGBA', 'LA'):
            # Keep transparency for RGBA images
            processed_img = img
        else:
            processed_img = img.convert('RGB')
        
        # Resize if dimensions specified
        if max_width or max_height:
            # Calculate new dimensions maintaining aspect ratio
            current_width, current_height = processed_img.size
            
            if max_width and max_height:
                # Fit within both constraints
                ratio = min(max_width / current_width, max_height / current_height)
            elif max_width:
                ratio = max_width / current_width
            else:  # max_height
                ratio = max_height / current_height
            
            if ratio < 1:  # Only resize if we're making it smaller
                new_width = int(current_width * ratio)
                new_height = int(current_height * ratio)
                processed_img = processed_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Optimize and save
        save_kwargs = {
            'format': 'PNG',
            'optimize': True,
        }
        
        # For RGB images, we can use additional compression
        if processed_img.mode == 'RGB':
            # Convert to palette mode for better compression if quality is lower
            if quality < 90:
                processed_img = processed_img.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        
        processed_img.save(output_path, **save_kwargs)
    
    # Get compressed file size
    compressed_size = output_path.stat().st_size
    compression_ratio = (1 - compressed_size / original_size) * 100
    
    return str(output_path), original_size, compressed_size, compression_ratio


def format_size(size_bytes):
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"