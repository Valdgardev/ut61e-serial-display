ENGLISH

# UT61E Serial Display

A minimal, monochrome display for the UNI-T UT61E digital multimeter. 

I built this because the official UNI-T software is heavy, outdated, and generally terrible. This app gives you a clean interface to read multimeter data on your PC without the bloat.

### Use Cases
- **OBS Streaming:** The high-contrast black-and-white UI is easy to capture and doesn't waste screen space.
- **Workbench setup:** Lets you keep your digital microscope feed and multimeter readings side-by-side on the same monitor.

### Features
- Minimal UI (black background, white text).
- English and Spanish language support.
- COM port auto-detection and manual selection.
- Works with the original UT-D02 RS-232 cable and standard USB-to-Serial adapters (CH340, Prolific, FTDI).
- Portable `.exe` (no installation needed).

### Download
-Download [HERE][https://example.com](https://github.com/Valdgardev/ut61e-serial-display/releases/download/V1/UT61E_Display.exe) or from the release.

### Setup
Before running the `.exe`, make sure your PC can communicate with the multimeter:

1. **Install the driver:** Install the USB-to-Serial driver for your adapter (CH340, PL2303, etc.). Windows usually handles this automatically, but check Device Manager if it doesn't.
2. **Find your COM port:** Look under "Ports (COM & LPT)" in Windows Device Manager and note the port number (e.g., `COM3`).
3. **Connect:** Open the app, select your COM port from the dropdown, and click Connect.

### Building from source
The `display.py` file contains the complete source code. If you want to modify it or build your own `.exe`, you can compile it using PyInstaller:

```bash
# Install PyInstaller
pip install pyinstaller

# Build the portable executable
python -m PyInstaller --onefile --windowed --icon="icono.ico" --name "UT61E_Display" display.py
```

Disclaimer: This project is about 50% vibecoded. I'm getting old and too lazy to write code by hand anymore, haha. 
