import argparse
import json
from pathlib import Path
import sys

# Try to use the 'rich' library for better-looking output, but fall back gracefully if not installed.
try:
    from rich.progress import track
    from rich.console import Console
    console = Console()
    CAN_USE_RICH = True
except ImportError:
    # Fallback function if 'rich' is not available
    def track(sequence, description=""):
        n = len(sequence)
        for i, item in enumerate(sequence):
            sys.stdout.write(f"\r{description} {i+1}/{n}")
            sys.stdout.flush()
            yield item
        sys.stdout.write("\n")
    # Create a mock console object that just uses the standard print function
    console = type('obj', (object,), {'print': print})
    CAN_USE_RICH = False

def write_chunk(output_dir: Path, file_index: int, entries: list):
    """Writes a list of entries to a numbered .jsonl file."""
    if not entries:
        return
    output_file = output_dir / f"{file_index}.jsonl"
    try:
        with output_file.open('w', encoding='utf-8') as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception as e:
        console.print(f"[red]Error writing to output file {output_file}: {e}[/red]")

def create_dataset(input_dir: str, output_dir: str, chunk_size: int = 10000):
    """
    Scans a directory for .avif files and their corresponding .txt files
    to create a .jsonl dataset for training, split into multiple files.

    Args:
        input_dir: The root directory to search for images.
        output_dir: The path for the output directory.
        chunk_size: The number of entries per .jsonl file.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.is_dir():
        console.print(f"[red]Error: Input directory not found at '{input_dir}'[/red]")
        return

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    console.print(f"Output will be saved to: [cyan]{output_path.resolve()}[/cyan]")

    console.print(f"Scanning for .avif files in: [cyan]{input_path.resolve()}[/cyan]")
    avif_files = list(input_path.rglob('*.avif'))

    if not avif_files:
        console.print("[yellow]No .avif files found.[/yellow]")
        return

    console.print(f"Found {len(avif_files)} .avif files. Processing...\n")

    chunk_entries = []
    not_found_count = 0
    total_entries_written = 0
    file_index = 1
    files_created = 0

    for avif_path in track(avif_files, description="Processing files..."):
        txt_path = avif_path.with_suffix('.txt')

        if txt_path.exists():
            try:
                instruction_text = txt_path.read_text(encoding='utf-8').strip()
                if instruction_text:
                    entry = {
                        "task_type": "t2i",
                        "instruction": instruction_text,
                        "output_image": avif_path.resolve().as_posix()
                    }
                    chunk_entries.append(entry)

                    if len(chunk_entries) >= chunk_size:
                        write_chunk(output_path, file_index, chunk_entries)
                        files_created += 1
                        total_entries_written += len(chunk_entries)
                        chunk_entries.clear()
                        file_index += 1
                else:
                    console.print(f"[yellow]Warning: Skipping empty .txt file for {avif_path.name}[/yellow]")

            except Exception as e:
                console.print(f"[red]Error reading {txt_path}: {e}[/red]")
        else:
            not_found_count += 1

    # Write any remaining entries in the last chunk
    if chunk_entries:
        write_chunk(output_path, file_index, chunk_entries)
        files_created += 1
        total_entries_written += len(chunk_entries)

    console.print(f"\n[bold green]Finished dataset creation.[/bold green]")
    console.print(f"Total entries written: {total_entries_written}")
    console.print(f"Total files created: {files_created}")
    if not_found_count > 0:
        console.print(f"[yellow]Warning: Skipped {not_found_count} images due to missing .txt files.[/yellow]")


def main():
    parser = argparse.ArgumentParser(
        description="Create a .jsonl dataset from a directory of images and text files.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-i", "--input_dir", type=str, required=True,
        help="Path to the root directory containing .avif and .txt files."
    )
    parser.add_argument(
        "-o", "--output_dir", type=str, required=True,
        help="Path to the output directory where .jsonl files will be saved."
    )
    parser.add_argument(
        "-s", "--chunk_size", type=int, default=10000,
        help="Number of entries per .jsonl file. Default: 10000"
    )

    args = parser.parse_args()
    create_dataset(args.input_dir, args.output_dir, args.chunk_size)


if __name__ == "__main__":
    if not CAN_USE_RICH:
        print("Warning: 'rich' library not found. Progress bar will be basic.")
        print("You can install it for a better experience: pip install rich")
    main()