import tkinter as tk
from tkinter import ttk
import threading
import random
import time

class SemaforosGUI:
    def __init__(self, controlador, sensor_reader=None):
        self.controlador = controlador
        self.sensor_reader = sensor_reader
        self.root = tk.Tk()
        self.root.title("Semáforos Inteligentes")
        self.frames = []
        self.dist_vars = []
        self.timer_labels = []
        self.estado_labels = []
        self.manual_entries = []

        for i, semaforo in enumerate(self.controlador.semaforos):
            frame = ttk.LabelFrame(self.root, text=f"Semáforo {i+1}")
            frame.grid(row=0, column=i, padx=10, pady=10)
            self.frames.append(frame)

            # Luces
            self.estado_labels.append([
                tk.Label(frame, width=4, height=2, bg="grey"),
                tk.Label(frame, width=4, height=2, bg="grey"),
                tk.Label(frame, width=4, height=2, bg="grey")
            ])
            for j, color in enumerate(["red", "yellow", "green"]):
                self.estado_labels[i][j].grid(row=j, column=0, pady=2)

            # Temporizador
            timer = tk.Label(frame, text="15s", font=("Arial", 14))
            timer.grid(row=3, column=0, pady=5)
            self.timer_labels.append(timer)

            # Distancia
            dist_var = tk.StringVar()
            dist_label = tk.Label(frame, textvariable=dist_var)
            dist_label.grid(row=4, column=0, pady=2)
            self.dist_vars.append(dist_var)

            # Entrada manual para semáforos 3 y 4
            if not semaforo.sensor_real:
                entry = tk.Entry(frame, width=6)
                entry.grid(row=5, column=0, pady=2)
                entry.insert(0, "999")
                self.manual_entries.append(entry)
            else:
                self.manual_entries.append(None)

        self.root.after(1000, self.update_loop)

    def update_loop(self):
        # Obtener distancias de sensores reales y manuales
        distancias = []
        if self.sensor_reader:
            reales = self.sensor_reader.get_distancias()
        else:
            reales = [999, 999]
        for i, semaforo in enumerate(self.controlador.semaforos):
            if semaforo.sensor_real:
                distancias.append(reales[i])
            else:
                try:
                    dist = float(self.manual_entries[i].get())
                except:
                    dist = 999
                distancias.append(dist)
        self.controlador.actualizar_distancias(distancias)

        # Tick de controlador
        self.controlador.tick()

        # Actualizar GUI
        for i, semaforo in enumerate(self.controlador.semaforos):
            # Luces
            estado = semaforo.estado
            colores = ["grey", "grey", "grey"]
            if estado == "ROJO":
                colores[0] = "red"
            elif estado == "AMARILLO":
                colores[1] = "yellow"
            elif estado == "VERDE":
                colores[2] = "green"
            for j in range(3):
                self.estado_labels[i][j].config(bg=colores[j])
            # Temporizador
            self.timer_labels[i].config(text=f"{semaforo.tiempo_restante}s")
            # Distancia
            self.dist_vars[i].set(f"Distancia: {semaforo.distancia:.1f}cm")

        self.root.after(1000, self.update_loop)

    def run(self):
        self.root.mainloop()
