from semaforo import Semaforo

class ControladorSemaforos:
    def __init__(self, semaforos):
        self.semaforos = semaforos
        self.tiempo_amarillo = 2
        self.tiempo_rojo = 15
        self.tiempo_verde = 5
        self.indice_actual = 0
        self.estado = "VERDE"
        self.en_transicion = None
        self.en_espera = False
        self.tiempo_espera = 1
        self.contador_espera = 0
        self.cola_prioridad = []  # Cola de prioridad por orden de llegada
        self._inicializar_semaforos()

    def _inicializar_semaforos(self):
        # Solo el primer semáforo en verde, el resto en rojo
        for i, s in enumerate(self.semaforos):
            if i == self.indice_actual:
                s.set_estado("VERDE", self.tiempo_verde)
            else:
                s.set_estado("ROJO", self.tiempo_rojo)
        self.en_transicion = None  # Reiniciar transición al inicializar
        self.en_espera = False
        self.contador_espera = 0
        self.cola_prioridad = []

    def actualizar_distancias(self, distancias):
        for i, s in enumerate(self.semaforos):
            s.set_distancia(distancias[i])
        # Actualizar la cola de prioridad por orden de llegada
        for i, s in enumerate(self.semaforos):
            if s.distancia < 30 and i not in self.cola_prioridad and i != self.indice_actual:
                self.cola_prioridad.append(i)
            # Si ya no hay presencia, quitar de la cola
            if s.distancia >= 30 and i in self.cola_prioridad:
                self.cola_prioridad.remove(i)

    def tick(self):
        # Si hay un semáforo en transición (amarillo->verde), solo avanza ese
        if self.en_transicion is not None:
            sem = self.semaforos[self.en_transicion]
            if sem.estado == "AMARILLO":
                sem.tick()
                if sem.tiempo_restante == 0:
                    sem.set_estado("VERDE", self.tiempo_verde)
                    self.en_transicion = None
            return

        # Si estamos en espera, solo decrementamos el contador
        if self.en_espera:
            self.contador_espera -= 1
            if self.contador_espera <= 0:
                siguiente = self._siguiente_semaforo()
                self.indice_actual = siguiente
                self.semaforos[self.indice_actual].set_estado("AMARILLO", self.tiempo_amarillo)
                self.en_transicion = self.indice_actual
                self.en_espera = False
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
                    # Iniciar espera antes de pasar al siguiente semáforo
                    self.en_espera = True
                    self.contador_espera = self.tiempo_espera

        # Asegurarse que los demás semáforos estén en rojo
        for i, s in enumerate(self.semaforos):
            if i != self.indice_actual and (self.en_transicion is None or i != self.en_transicion):
                if s.estado != "ROJO" or s.tiempo_restante != self.tiempo_rojo:
                    s.set_estado("ROJO", self.tiempo_rojo)

    def _siguiente_semaforo(self):
        # Si hay alguien en la cola de prioridad, atenderlo primero
        if self.cola_prioridad:
            return self.cola_prioridad.pop(0)
        # Si nadie en la cola, buscar si hay presencia en algún semáforo (excepto el actual)
        presentes = [i for i, s in enumerate(self.semaforos) if s.distancia < 30 and i != self.indice_actual]
        if presentes:
            return presentes[0]
        # Si nadie presente, ciclo normal
        return (self.indice_actual + 1) % len(self.semaforos)
