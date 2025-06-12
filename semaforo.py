class Semaforo:
    ESTADOS = ["ROJO", "AMARILLO", "VERDE"]

    def __init__(self, id, sensor_real=True):
        self.id = id
        self.sensor_real = sensor_real
        self.estado = "ROJO"
        self.tiempo_restante = 15
        self.distancia = 999  # Valor inicial grande

    def set_distancia(self, distancia):
        self.distancia = distancia

    def set_estado(self, estado, tiempo):
        self.estado = estado
        self.tiempo_restante = tiempo

    def tick(self):
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1

    def __str__(self):
        return f"Semáforo {self.id+1}: {self.estado} ({self.tiempo_restante}s) Distancia: {self.distancia:.1f}cm"
