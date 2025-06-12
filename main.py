from semaforo import Semaforo
from controlador import ControladorSemaforos
from gui import SemaforosGUI
import threading
import serial

# Crear 4 semáforos (2 con sensor real, 2 manual)
semaforos = [
    Semaforo(0, sensor_real=True),
    Semaforo(1, sensor_real=True),
    Semaforo(2, sensor_real=False),
    Semaforo(3, sensor_real=False)
]

controlador = ControladorSemaforos(semaforos)

# Leer distancias desde ESP32 por serial
class SensorSerialReader(threading.Thread):
    def __init__(self, controlador, port='COM3', baudrate=115200):
        super().__init__(daemon=True)
        self.controlador = controlador
        self.port = port
        self.baudrate = baudrate
        self.distancias = [999, 999]  # Inicialmente grandes
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        except Exception as e:
            print(f"Error abriendo puerto serial: {e}")
            self.ser = None

    def run(self):
        while True:
            if self.ser and self.ser.in_waiting:
                try:
                    line = self.ser.readline().decode().strip()
                    # Espera líneas tipo: "23.4,45.6"
                    partes = line.split(",")
                    if len(partes) == 2:
                        self.distancias[0] = float(partes[0])
                        self.distancias[1] = float(partes[1])
                except Exception:
                    pass

    def get_distancias(self):
        return self.distancias.copy()

# Instanciar el lector de sensores
sensor_reader = SensorSerialReader(controlador)
sensor_reader.start()

# Lanzar interfaz gráfica
if __name__ == "__main__":
    gui = SemaforosGUI(controlador, sensor_reader)
    gui.run()
