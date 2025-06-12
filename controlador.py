from semaforo import Semaforo

class ControladorSemaforos:
    def __init__(self, semaforos):
        self.semaforos = semaforos
        self.tiempo_amarillo = 2
        self.tiempo_rojo = 15
        self.tiempo_verde = 5
        self.indice_actual = 0  # Semáforo que tiene el turno
        self.estado = "VERDE"   # Estado global del semáforo actual
        self.en_transicion = None  # Índice del semáforo que debe pasar de amarillo a verde
        self._inicializar_semaforos()

    def _inicializar_semaforos(self):
        # Solo el primer semáforo en verde, el resto en rojo
        for i, s in enumerate(self.semaforos):
            if i == self.indice_actual:
                s.set_estado("VERDE", self.tiempo_verde)
            else:
                s.set_estado("ROJO", self.tiempo_rojo)
        self.en_transicion = None  # Reiniciar transición al inicializar

    def actualizar_distancias(self, distancias):
        for i, s in enumerate(self.semaforos):
            s.set_distancia(distancias[i])

    def tick(self):
        # Si hay un semáforo en transición (amarillo->verde), solo avanza ese
        if self.en_transicion is not None:
            sem = self.semaforos[self.en_transicion]
            if sem.estado == "AMARILLO":
                sem.tick()
                if sem.tiempo_restante == 0:
                    sem.set_estado("VERDE", self.tiempo_verde)
                    self.en_transicion = None
            # No avanzar el semáforo actual mientras hay transición
            return

        actual = self.semaforos[self.indice_actual]
        # Proceso normal del semáforo actual
        if actual.estado == "VERDE" or actual.estado == "AMARILLO":
            actual.tick()
            if actual.tiempo_restante == 0:
                if actual.estado == "VERDE":
                    actual.set_estado("AMARILLO", self.tiempo_amarillo)
                elif actual.estado == "AMARILLO":
                    actual.set_estado("ROJO", self.tiempo_rojo)
                    siguiente = self._siguiente_semaforo()
                    self.indice_actual = siguiente
                    self.semaforos[self.indice_actual].set_estado("AMARILLO", self.tiempo_amarillo)
                    self.en_transicion = self.indice_actual

        # Asegurarse que los demás semáforos estén en rojo
        for i, s in enumerate(self.semaforos):
            if i != self.indice_actual and (self.en_transicion is None or i != self.en_transicion):
                if s.estado != "ROJO" or s.tiempo_restante != self.tiempo_rojo:
                    s.set_estado("ROJO", self.tiempo_rojo)

    def _siguiente_semaforo(self):
        # Prioridad: si solo uno tiene presencia (<30cm), darle el turno
        presentes = [i for i, s in enumerate(self.semaforos) if s.distancia < 30]
        if len(presentes) == 1:
            return presentes[0]
        elif len(presentes) > 1:
            # Si varios tienen presencia, sigue el orden de llegada (circular)
            return (self.indice_actual + 1) % len(self.semaforos)
        else:
            # Nadie presente, ciclo normal
            return (self.indice_actual + 1) % len(self.semaforos)
