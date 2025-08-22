import click
from jphtools.notebooks import strip_solutions_from_notebook
from jphtools.png import compress_png, format_size

@click.group()
def cli():
    """jphtools: A collection of personal tools."""
    pass

@cli.group()
def notebook():
    """Notebook-related tools."""
    pass

@notebook.command("strip-answers")
@click.argument("input_path")
@click.argument("output_path")
def strip_answers(input_path, output_path):
    """Strip solution blocks from a Jupyter notebook."""
    strip_solutions_from_notebook(input_path, output_path)

@cli.group()
def compress():
    """Image compression tools."""
    pass

@compress.command("png")
@click.argument("input_path")
@click.option("--output", "-o", help="Output path (default: adds _compressed suffix)")
@click.option("--quality", "-q", default=85, type=int, help="Compression quality 1-100 (default: 85)")
@click.option("--max-width", type=int, help="Maximum width in pixels")
@click.option("--max-height", type=int, help="Maximum height in pixels")
def compress_png_cmd(input_path, output, quality, max_width, max_height):
    """Compress a PNG file to reduce file size."""
    try:
        output_path, original_size, compressed_size, compression_ratio = compress_png(
            input_path, output, quality, max_width, max_height
        )
        
        click.echo(f"✓ Compressed: {input_path} → {output_path}")
        click.echo(f"  Original:   {format_size(original_size)}")
        click.echo(f"  Compressed: {format_size(compressed_size)}")
        click.echo(f"  Saved:      {compression_ratio:.1f}%")
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    cli()
