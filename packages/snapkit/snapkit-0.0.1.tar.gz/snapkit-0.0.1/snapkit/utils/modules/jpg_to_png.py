import argparse
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os
import sys


def convert_image(file_path: Path, output_dir: Path) -> tuple[bool, str, str, Path]:
    try:
        with Image.open(file_path) as img:
            img = img.convert("RGB")
            output_file = output_dir / (file_path.stem + ".png")
            img.save(output_file, format="PNG")
        return True, "Success", "", file_path
    except Exception as e:
        return False, type(e).__name__, str(e), file_path


def jpg_to_png(input_dir: str, output_dir: str, max_threads: int = os.cpu_count()) -> None:
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_path}")
    output_path.mkdir(parents=True, exist_ok=True)

    valid_extensions = ('.jpg', '.jpeg')
    image_files = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() in valid_extensions]

    total_files = len(list(input_path.iterdir()))
    total_accepted = len(image_files)

    if total_accepted == 0:
        print("No JPEG files found in the input directory.")
        return

    failed = []
    success_count = 0

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(convert_image, file_path, output_path) for file_path in image_files]

        for future in tqdm(as_completed(futures), total=len(futures), desc=f"Progress [{max_threads} threads]", unit=" file"):
            success, exc_type, full_err_msg, file_path = future.result()
            if success:
                success_count += 1
            else:
                failed.append((file_path.name, exc_type, str(file_path.resolve()), full_err_msg))

    if failed:
        errors_file = output_path / "errors.txt"
        with errors_file.open('w') as f:
            f.write("# Failed Image Conversion Report\n")
            f.write(f"# Total failures: {len(failed)} (Total files {total_files}, total accepted format {total_accepted})\n\n")
            for name, exc_type, abs_path, full_msg in failed:
                f.write(f"{name}, {exc_type}, {abs_path}, {full_msg}\n")
        errors_file_path = f", failed list saved to: {str(errors_file.resolve())}"
    else:
        errors_file_path = ""

    print(
        f"\nProcessed: "
        f"{total_accepted}/{total_files} images, {success_count}/{total_accepted} success, "
        f"{len(failed)}/{total_accepted} failure"
        f"{errors_file_path}"
    )

def cli(argv=None):
    parser = argparse.ArgumentParser(description="Convert JPEG/JPG images to PNG format.")
    parser.add_argument("--source", required=True, help="Input directory")
    parser.add_argument("--destination", required=True, help="Output directory")
    parser.add_argument("--threads", type=int, default=os.cpu_count(), help="Number of threads (default: CPU count)")

    if argv is None:
        argv = sys.argv[1:]

    args = parser.parse_args(argv)
    jpg_to_png(args.source, args.destination, args.threads)