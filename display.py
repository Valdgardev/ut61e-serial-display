import serial
import serial.tools.list_ports
import threading
import queue
import time
import tkinter as tk
from tkinter import ttk

DEFAULT_PORT = 'COM2'
DEFAULT_LANG = 'es'  # 'es' o 'en'

TRANSLATIONS = {
    'es': {
        'port_label': 'Puerto:',
        'connect': '⚡ Conectar',
        'disconnect': '⏹ Desconectar',
        'disconnected': 'Desconectado',
        'opening': 'Abriendo',
        'connected': 'Conectado a',
        'error': 'Error',
        'invalid_port': 'Puerto inválido',
        'no_ports': 'Sin puertos',
        'diode': 'DIODO',
        'continuity': 'CONTINUIDAD',
        'lang_label': 'Idioma:',
        'lang_es': 'Español',
        'lang_en': 'English',
    },
    'en': {
        'port_label': 'Port:',
        'connect': '⚡ Connect',
        'disconnect': '⏹ Disconnect',
        'disconnected': 'Disconnected',
        'opening': 'Opening',
        'connected': 'Connected to',
        'error': 'Error',
        'invalid_port': 'Invalid port',
        'no_ports': 'No ports',
        'diode': 'DIODE',
        'continuity': 'CONTINUITY',
        'lang_label': 'Lang:',
        'lang_es': 'Español',
        'lang_en': 'English',
    }
}

class UT61E_Reader(threading.Thread):
    """Hilo que lee datos del multímetro."""
    
    def __init__(self, port, data_queue, status_callback):
        super().__init__(daemon=True)
        self.port = port
        self.queue = data_queue
        self.running = False
        self.ser = None
        self.status_callback = status_callback
        
        self.mode_map = {
            0x1: { 0: ("V", 4) },
            0x5: { 0: ("Ω", 2) },
            0xB: { 0: ("V", 4), 1: ("V", 3), 2: ("V", 2), 3: ("V", 1), 4: ("mV", 2) },
            0x3: { 0: ("Ω", 2), 1: ("kΩ", 4), 2: ("kΩ", 3), 3: ("kΩ", 2),
                   4: ("MΩ", 4), 5: ("MΩ", 3), 6: ("MΩ", 2) },
            0x6: { 0: ("nF", 3), 1: ("nF", 2), 2: ("µF", 4), 3: ("µF", 3),
                   4: ("µF", 2), 5: ("mF", 4), 6: ("mF", 3), 7: ("mF", 2) },
            0xD: { 0: ("µA", 2), 1: ("µA", 1) },
            0xF: { 0: ("mA", 3), 1: ("mA", 2) },
            0x0: { 0: ("A", 3) },
            0x2: { 0: ("Hz", 2), 1: ("Hz", 1), 2: ("kHz", 3), 3: ("kHz", 2),
                   4: ("MHz", 4), 5: ("MHz", 3), 6: ("MHz", 2) }
        }
    
    def run(self):
        self.running = True
        try:
            self.status_callback(f"{TRANSLATIONS.get('es', {}).get('opening', 'Opening')} {self.port}...", "yellow")
            self.ser = serial.Serial(
                port=self.port,
                baudrate=19200,
                bytesize=serial.SEVENBITS,
                parity=serial.PARITY_ODD,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.5,
                dsrdtr=False, rtscts=False, xonxoff=False
            )
            self.ser.dtr = True
            self.ser.rts = False
            time.sleep(0.3)
            
            self.status_callback(f"{TRANSLATIONS.get('es', {}).get('connected', 'Connected to')} {self.port}", "lightgreen")
            
            buffer = bytearray()
            
            while self.running:
                byte = self.ser.read(1)
                if len(byte) == 1:
                    buffer.append(byte[0])
                    
                    if len(buffer) >= 14 and buffer[-2:] == bytearray([0x0D, 0x0A]):
                        packet = buffer[-14:]
                        buffer.clear()
                        decoded = self.decode_packet(packet)
                        if decoded:
                            while not self.queue.empty():
                                try: self.queue.get_nowait()
                                except queue.Empty: break
                            self.queue.put(decoded)
                            
        except serial.SerialException as e:
            self.status_callback(f"{TRANSLATIONS.get('es', {}).get('error', 'Error')}: {e}", "red")
            self.queue.put({'error': str(e)})
        except Exception as e:
            self.status_callback(f"{TRANSLATIONS.get('es', {}).get('error', 'Error')}: {e}", "red")
        finally:
            if self.ser and self.ser.is_open:
                self.ser.dtr = False
                self.ser.rts = True
                self.ser.close()
            if self.running:
                self.status_callback(TRANSLATIONS.get('es', {}).get('disconnected', 'Disconnected'), "gray")
    
    def decode_packet(self, packet):
        try:
            range_val = packet[0] & 0x07
            mode_val = packet[6] & 0x0F
            is_negative = bool(packet[7] & 0x04)
            is_ol = bool(packet[7] & 0x01)
            is_ac = bool(packet[10] & 0x04)
            is_dc = bool(packet[10] & 0x08)
            is_auto = bool(packet[10] & 0x02)
            
            if mode_val == 0x01:
                mode_code = "DIODE"
            elif mode_val == 0x05:
                mode_code = "CONTINUITY"
            else:
                flags = []
                if is_ac: flags.append("AC")
                if is_dc: flags.append("DC")
                if is_auto: flags.append("AUTO")
                mode_code = " ".join(flags) if flags else "MAN"
            
            def get_digit(b):
                val = b & 0x0F
                return str(val) if val <= 9 else '0'
            
            digits_str = "".join(get_digit(b) for b in packet[1:6])
            
            if is_ol:
                return {'value': "OL", 'unit': "", 'mode_code': mode_code}
            
            unit_str, dp = "", 0
            if mode_val in self.mode_map and range_val in self.mode_map[mode_val]:
                unit_str, dp = self.mode_map[mode_val][range_val]
            else:
                unit_str = "?"
            
            try:
                val_int = int(digits_str.replace(' ', '0'))
                display_val = f"{val_int / (10 ** dp):.10g}"
                if is_negative: display_val = "-" + display_val
            except ValueError:
                display_val = "Err"
            
            return {'value': display_val, 'unit': unit_str, 'mode_code': mode_code}
        except:
            return None
    
    def stop(self):
        self.running = False
        if self.ser and self.ser.is_open:
            try: self.ser.close()
            except: pass


class DisplayApp:
    def __init__(self, root):
        self.root = root
        self.data_queue = queue.Queue()
        self.reader = None
        self.language = DEFAULT_LANG
        
        self.root.title("UT61E Display")
        self.root.configure(bg="black")
        self.root.geometry("700x280")
        self.root.resizable(False, False)
        
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"700x280+{(sw-700)//2}+{(sh-280)//2}")
        
        self.top_frame = tk.Frame(root, bg="#222222", pady=6)
        self.top_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        tk.Label(self.top_frame, text=TRANSLATIONS[self.language]['lang_label'],
                 font=("Consolas", 11), fg="white", bg="#222222").pack(side="left", padx=(10, 5))
        
        self.lang_var = tk.StringVar(value=TRANSLATIONS[self.language][f'lang_{self.language}'])
        self.lang_combo = ttk.Combobox(self.top_frame, textvariable=self.lang_var,
                                        values=[TRANSLATIONS['es']['lang_es'], TRANSLATIONS['en']['lang_en']],
                                        width=10, state="readonly")
        self.lang_combo.pack(side="left", padx=5)
        self.lang_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        tk.Frame(self.top_frame, width=1, height=20, bg="#444444").pack(side="left", padx=10, fill="y")
        
        tk.Label(self.top_frame, text=TRANSLATIONS[self.language]['port_label'],
                 font=("Consolas", 11), fg="white", bg="#222222").pack(side="left", padx=5)
        
        self.port_var = tk.StringVar(value=DEFAULT_PORT)
        self.port_combo = ttk.Combobox(self.top_frame, textvariable=self.port_var,
                                        width=10, state="readonly")
        self.port_combo.pack(side="left", padx=5)
        
        self.btn_refresh = tk.Button(self.top_frame, text="🔄", command=self.refresh_ports,
                                      font=("Consolas", 11), bg="#444444", fg="white",
                                      relief="flat", cursor="hand2")
        self.btn_refresh.pack(side="left", padx=2)
        
        self.btn_connect = tk.Button(self.top_frame, text=TRANSLATIONS[self.language]['connect'],
                                      command=self.toggle_connection,
                                      font=("Consolas", 11, "bold"),
                                      bg="#006600", fg="white", relief="flat", cursor="hand2")
        self.btn_connect.pack(side="left", padx=15)
        
        self.status_label = tk.Label(self.top_frame, text=TRANSLATIONS[self.language]['disconnected'],
                                      font=("Consolas", 10), fg="gray", bg="#222222")
        self.status_label.pack(side="right", padx=10)
        
        self.frame = tk.Frame(root, bg="black")
        self.frame.pack(expand=True, fill="both", padx=20, pady=10)
        
        self.value_label = tk.Label(self.frame, text="----", font=("Consolas", 72, "bold"),
                                     fg="white", bg="black", anchor="e")
        self.value_label.pack(side="left", fill="both", expand=True)
        
        self.right_frame = tk.Frame(self.frame, bg="black")
        self.right_frame.pack(side="right", fill="y", padx=(20, 0))
        
        self.unit_label = tk.Label(self.right_frame, text="", font=("Consolas", 36, "bold"),
                                    fg="white", bg="black", anchor="e")
        self.unit_label.pack(anchor="e")
        
        self.mode_label = tk.Label(self.right_frame, text="", font=("Consolas", 18),
                                    fg="#888888", bg="black", anchor="e")
        self.mode_label.pack(anchor="e", pady=(10, 0))
        
        
        self.refresh_ports()
        self.update_display()
    
    def on_language_change(self, event=None):
        """Cambia el idioma según la selección."""
        selected = self.lang_var.get()
        if selected == TRANSLATIONS['es']['lang_es']:
            self.language = 'es'
        else:
            self.language = 'en'
        
        self.update_ui_texts()
        
        if self.reader and self.reader.is_alive():
            self.btn_connect.config(text=TRANSLATIONS[self.language]['disconnect'])
        else:
            self.btn_connect.config(text=TRANSLATIONS[self.language]['connect'])
    
    def update_ui_texts(self):
        """Actualiza todos los textos de la UI según el idioma."""
        t = TRANSLATIONS[self.language]
        
        for widget in self.top_frame.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget('text') in [
                TRANSLATIONS['es']['port_label'], TRANSLATIONS['en']['port_label'],
                TRANSLATIONS['es']['lang_label'], TRANSLATIONS['en']['lang_label']
            ]:
                
                pass
        
        
        for widget in self.top_frame.winfo_children():
            if isinstance(widget, tk.Label):
                text = widget.cget('text')
                if text in [TRANSLATIONS['es']['port_label'], TRANSLATIONS['en']['port_label']]:
                    widget.config(text=t['port_label'])
                elif text in [TRANSLATIONS['es']['lang_label'], TRANSLATIONS['en']['lang_label']]:
                    widget.config(text=t['lang_label'])
                elif text == TRANSLATIONS['es']['disconnected'] or text == TRANSLATIONS['en']['disconnected']:
                    if not (self.reader and self.reader.is_alive()):
                        widget.config(text=t['disconnected'])
        
        if self.reader and self.reader.is_alive():
            self.btn_connect.config(text=t['disconnect'])
        else:
            self.btn_connect.config(text=t['connect'])
    
    def refresh_ports(self):
        """Lista los puertos COM disponibles."""
        ports = [p.device for p in serial.tools.list_ports.comports()]
        if not ports:
            ports = [TRANSLATIONS[self.language]['no_ports']]
        self.port_combo['values'] = ports
        if self.port_var.get() not in ports:
            self.port_var.set(ports[0] if ports else "")
    
    def toggle_connection(self):
        """Conecta o desconecta según el estado actual."""
        t = TRANSLATIONS[self.language]
        
        if self.reader and self.reader.is_alive():
            self.reader.stop()
            self.reader.join(timeout=2)
            self.reader = None
            self.btn_connect.config(text=t['connect'], bg="#006600")
        else:
            port = self.port_var.get()
            if not port or port == t['no_ports']:
                self.status_callback(t['invalid_port'], "red")
                return
            self.reader = UT61E_Reader(port, self.data_queue, self.status_callback)
            self.reader.start()
            self.btn_connect.config(text=t['disconnect'], bg="#AA0000")
    
    def status_callback(self, msg, color):
        self.root.after(0, lambda: self.status_label.config(text=msg, fg=color))
    
    def translate_mode(self, mode_code):
        """Traduce los códigos de modo al idioma actual."""
        t = TRANSLATIONS[self.language]
        if mode_code == "DIODE":
            return t['diode']
        elif mode_code == "CONTINUITY":
            return t['continuity']
        return mode_code  
    
    def update_display(self):
        try:
            while True:
                data = self.data_queue.get_nowait()
                
                if 'error' in data:
                    self.value_label.config(text="ERR")
                    self.unit_label.config(text="")
                    self.mode_label.config(text="")
                else:
                    self.value_label.config(text=data['value'])
                    self.unit_label.config(text=data['unit'])
                    # Traducir el modo según el idioma seleccionado
                    mode_translated = self.translate_mode(data.get('mode_code', ''))
                    self.mode_label.config(text=mode_translated)
        except queue.Empty:
            pass
        
        self.root.after(100, self.update_display)


def main():
    root = tk.Tk()
    app = DisplayApp(root)
    
    def on_close():
        if app.reader and app.reader.is_alive():
            app.reader.stop()
            app.reader.join(timeout=2)
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()