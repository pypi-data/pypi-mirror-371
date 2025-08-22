# jphtools

A collection of random personal tools.

## CLI Usage

You can use the `jphtools` command-line interface to access various tools.

### Notebook Tools

Strip solution blocks from a Jupyter notebook:

```sh
jphtools notebook strip-answers input.ipynb output.ipynb
```

This will remove code between `# BEGIN_SOLUTION` and `# END_SOLUTION` in code cells, replacing it with `# ADD YOUR CODE HERE` in the output notebook.

### PNG Compression

Compress PNG files to reduce size for web or repository use:

```sh
# Basic compression (85% quality)
jphtools compress png image.png

# Custom quality and output path
jphtools compress png image.png -o compressed.png -q 70

# Resize and compress
jphtools compress png large-image.png --max-width 800 --max-height 600
```

Options:
- `--output, -o`: Specify output path (default: adds `_compressed` suffix)
- `--quality, -q`: Compression quality 1-100 (default: 85)
- `--max-width`: Maximum width in pixels (maintains aspect ratio)
- `--max-height`: Maximum height in pixels (maintains aspect ratio)
