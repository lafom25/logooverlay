# Logo Overlay App

A simple Tkinter GUI to overlay a PNG logo onto a video using FFmpeg.

## Key files
- `logo_overlay_app.py` — main application implementation
- `build/` — build outputs

## Requirements
- Python 3.8+ (tkinter is used and is included with standard Python installs on most platforms)
- FFmpeg executable (place `ffmpeg.exe` next to `logo_overlay_app.py`)

## Usage
1. Ensure `ffmpeg.exe` and `logo.png` are in the same folder as `logo_overlay_app.py`.
2. Run:
   ```sh
   python logo_overlay_app.py
   ```
3. In the GUI, choose an input video and an output folder, select MP4 or MXF, then click "Gắn Logo".

## Notes
- No external Python packages are required; FFmpeg is required for video processing.
- The app updates progress by parsing ffmpeg stderr output; ensure ffmpeg prints progress information.

## License
- Add your preferred license here.
