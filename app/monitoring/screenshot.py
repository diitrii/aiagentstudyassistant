from datetime import datetime
from pathlib import Path

import mss


def capture_full_screen(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"screenshot_{timestamp}.png"

    with mss.mss() as sct:
        sct.shot(output=str(output_path))

    return output_path