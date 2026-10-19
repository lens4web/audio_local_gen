import os
import sys
import time
import requests
from pathlib import Path
from typing import Callable, Optional

def download_file(
    url: str,
    destination: Path,
    description: str = "",
    progress_callback: Optional[Callable[[int, int, float], None]] = None,
    chunk_size: int = 1024 * 1024,
) -> bool:
    """
    Downloads a file with streaming chunks and progress tracking.
    destination: Path object pointing to local file path.
    progress_callback: callback(downloaded_bytes, total_bytes, percent)
    """
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    temp_path = destination.with_suffix(destination.suffix + ".tmp")

    headers = {}
    downloaded_bytes = 0
    if temp_path.exists():
        downloaded_bytes = temp_path.stat().st_size
        headers["Range"] = f"bytes={downloaded_bytes}-"

    response = requests.get(url, headers=headers, stream=True, timeout=30)

    # Check if server supports range or sends full file
    if response.status_code == 206:
        # Partial content resumed
        total_length = downloaded_bytes + int(response.headers.get("content-length", 0))
        mode = "ab"
    elif response.status_code == 200:
        # Full content
        downloaded_bytes = 0
        total_length = int(response.headers.get("content-length", 0))
        mode = "wb"
    else:
        # If range was not satisfiable or other error
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        downloaded_bytes = 0
        total_length = int(response.headers.get("content-length", 0))
        mode = "wb"

    start_time = time.time()
    last_print = 0

    with open(temp_path, mode) as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded_bytes += len(chunk)
                percent = (downloaded_bytes / total_length * 100) if total_length > 0 else 0
                
                if progress_callback:
                    progress_callback(downloaded_bytes, total_length, percent)

                current_time = time.time()
                if current_time - last_print > 1.0 or downloaded_bytes == total_length:
                    last_print = current_time
                    mb_downloaded = downloaded_bytes / (1024 * 1024)
                    mb_total = total_length / (1024 * 1024)
                    print(f"\r[{description or destination.name}] {mb_downloaded:.1f}/{mb_total:.1f} MB ({percent:.1f}%)", end="", flush=True)

    print()
    temp_path.rename(destination)
    return True
