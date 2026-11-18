ENGLISH

# UT61E Serial Display

A minimal, monochrome display for the UNI-T UT61E digital multimeter. 

I built this because the official UNI-T software is heavy, outdated, and generally terrible. This app gives you a clean interface to read multimeter data on your PC without the bloat.


<img width="704" height="314" alt="imagen" src="https://github.com/user-attachments/assets/35c5822a-8e70-4547-8681-8f618f225ff6" />

### Use Cases
- **OBS Streaming:** The high-contrast black-and-white UI is easy to capture and doesn't waste screen space.
- **Workbench setup:** Lets you keep your digital microscope feed and multimeter readings side-by-side on the same monitor.

### Features
- Minimal UI (black background, white text).
- English and Spanish language support.
- COM port auto-detection and manual selection.
- Works with the original UT-D02 RS-232 cable and standard USB-to-Serial adapters (CH340, Prolific, FTDI).
- Portable `.exe` (no installation needed).

### Technical Details
This app is built around the **Cyrustek ES51922** chipset. If you are working with this chip and need a reference for decoding its 14-byte RS-232 protocol (19200 baud, 7O1, DTR/RTS handshake), the `decode_packet` function in `display.py` is a solid starting point.

### Download
-Download [HERE](https://github.com/Valdgardev/ut61e-serial-display/releases/download/V1/UT61E_Display.exe) or from the release.

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





ESPAÑOL

# UT61E Serial Display

Un monitor minimalista y monocromático para el multímetro UNI-T UT61E. 

Hice esto porque el software oficial de UNI-T es pesado, viejo y bastante malo. Esta app te da una interfaz limpia para leer los datos del multímetro en la PC sin complicaciones.

### Casos de uso
- **Streaming en OBS:** La interfaz en blanco y negro es fácil de capturar y no desperdicia espacio en pantalla.
- **Setup de banco de trabajo:** Permite tener la cámara del microscopio digital y las lecturas del multímetro en el mismo monitor.

### Características
- Interfaz minimalista (fondo negro, texto blanco).
- Soporte para español e inglés.
- Detección y selección manual de puertos COM.
- Funciona con el cable original UT-D02 RS-232 y adaptadores USB-a-Serial estándar (CH340, Prolific, FTDI).
- `.exe` portable (no requiere instalación).

### Descarga
-Descargalo [AQUI](https://github.com/Valdgardev/ut61e-serial-display/releases/download/V1/UT61E_Display.exe) o desde el release.

### Configuración
Antes de usar el `.exe`, asegúrate de que tu PC pueda comunicarse con el multímetro:

1. **Instalar el driver:** Instala el driver USB-a-Serial de tu adaptador (CH340, PL2303, etc.). Windows suele hacerlo solo, pero revisa el Administrador de Dispositivos si no.
2. **Encontrar tu puerto COM:** Busca en "Puertos (COM y LPT)" en el Administrador de Dispositivos y anota el número (ej. `COM3`).
3. **Conectar:** Abre la app, selecciona tu puerto COM en el menú y haz clic en Conectar.

### Compilar desde el código
El archivo `display.py` contiene todo el código fuente. Si quieres modificarlo o crear tu propio `.exe`, puedes compilarlo usando PyInstaller:

```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar el ejecutable portable
python -m PyInstaller --onefile --windowed --icon="icono.ico" --name "UT61E_Display" display.py
```
disclaimer: Este proyecto está 50% "vibecodeado". Estoy viejo y ya me da flojera escribir código a mano, haha.
