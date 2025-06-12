import tkinter as tk
from tkinter import ttk

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
        self.manual_buttons = []
        self.prioridad_var = tk.StringVar()

        # Disposición 2x2 para simular intersección
        positions = [(0,0), (0,1), (1,0), (1,1)]
        for i, semaforo in enumerate(self.controlador.semaforos):
            frame = tk.Frame(self.root, bd=4, relief=tk.RIDGE, padx=10, pady=10)
            row, col = positions[i]
            frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            self.frames.append(frame)

            # Luces grandes
            luces = []
            for j, color in enumerate(["red", "yellow", "green"]):
                lbl = tk.Label(frame, width=5, height=2, bg="grey", relief=tk.SUNKEN, bd=2)
                lbl.grid(row=j, column=0, pady=4)
                luces.append(lbl)
            self.estado_labels.append(luces)

            # Temporizador grande
            timer = tk.Label(frame, text="15s", font=("Arial", 22, "bold"))
            timer.grid(row=3, column=0, pady=8)
            self.timer_labels.append(timer)

            # Distancia
            dist_var = tk.StringVar()
            dist_label = tk.Label(frame, textvariable=dist_var, font=("Arial", 12))
            dist_label.grid(row=4, column=0, pady=2)
            self.dist_vars.append(dist_var)

            # Entrada manual para semáforos 3 y 4
            if not semaforo.sensor_real:
                entry = tk.Entry(frame, width=8, font=("Arial", 12))
                entry.grid(row=5, column=0, pady=2)
                entry.insert(0, "999")
                self.manual_entries.append(entry)
                btn = tk.Button(frame, text="Actualizar", command=lambda idx=i: self.update_manual(idx))
                btn.grid(row=6, column=0, pady=2)
                self.manual_buttons.append(btn)
            else:
                self.manual_entries.append(None)
                self.manual_buttons.append(None)

        # Mostrar cola de prioridad
        prioridad_label = tk.Label(self.root, text="Cola de prioridad (orden de atención):", font=("Arial", 12, "bold"))
        prioridad_label.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")
        prioridad_val = tk.Label(self.root, textvariable=self.prioridad_var, font=("Arial", 12))
        prioridad_val.grid(row=2, column=2, columnspan=2, pady=10, sticky="w")

        self.root.after(1000, self.update_loop)

    def update_manual(self, idx):
        # Forzar actualización de distancia manual
        try:
            val = float(self.manual_entries[idx].get())
            self.controlador.semaforos[idx].set_distancia(val)
        except Exception:
            self.manual_entries[idx].delete(0, tk.END)
            self.manual_entries[idx].insert(0, "999")

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
            # Temporizador: solo mostrar si no está en rojo
            if estado == "ROJO":
                self.timer_labels[i].config(text="")
            else:
                self.timer_labels[i].config(text=f"{semaforo.tiempo_restante}s")
            # Distancia
            self.dist_vars[i].set(f"Distancia: {semaforo.distancia:.1f}cm")
            # Fondo del frame según estado
            if estado == "VERDE":
                self.frames[i].config(bg="#d0ffd0")
            elif estado == "AMARILLO":
                self.frames[i].config(bg="#fffac0")
            elif estado == "ROJO":
                self.frames[i].config(bg="#ffd0d0")
            else:
                self.frames[i].config(bg="SystemButtonFace")

        # Mostrar cola de prioridad
        cola = getattr(self.controlador, "cola_prioridad", [])
        if cola:
            texto = " → ".join([f"S{i+1}" for i in cola])
        else:
            texto = "Vacía"
        self.prioridad_var.set(texto)

        self.root.after(1000, self.update_loop)

    def run(self):
        self.root.mainloop()
