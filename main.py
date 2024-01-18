import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import serial
import threading
import time

ser = serial.Serial('COM8', 115200)
start_time = time.time()

def read_from_stm():
    global global_pid_value
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').rstrip()
            print(f"Otrzymano dane: {line}")
            try:
                parts = line.split(', ')
                if len(parts) > 0 and ": " in parts[0]:
                    sensor_val_str = parts[0].split(': ')[1]
                    sensor_val = float(sensor_val_str)
                    y_values.append(sensor_val)
                    # Zapisz czas w sekundach od startu
                    current_time = time.time() - start_time
                    x_values.append(current_time)

                    pid_value = parts[-1].split(': ')[1]
                    global_pid_value.set(pid_value)
                else:
                    print("Nieprawidłowy format danych")
            except ValueError as e:
                print(f"Błąd podczas parsowania danych: {line}. Szczegóły błędu: {e}")

def write_to_stm():
    while True:
        command = f"Set Kp:{kp.get()} Ki:{ki.get()} Kd:{kd.get()} Setpoint:{set_point.get()}\n"
        ser.write(command.encode('utf-8'))
        time.sleep(1)

def reset_plot():
    global start_time
    start_time = time.time()  # Resetuj czas startu
    x_values.clear()
    y_values.clear()
    ax.clear()
    ax.axhline(y=set_point.get(), color='r', linestyle='-', label="Wartość zadana")
    ax.legend()
    canvas.draw()

def update_plot():
    while True:
        time.sleep(0.1)

        if len(x_values) == len(y_values) and len(x_values) > 0:
            ax.clear()
            ax.set_title("Balancing Car")
            ax.set_xlabel("Czas (s)")
            ax.set_ylabel("Wartość z czujnika")
            ax.plot(x_values, y_values, label="Czujnik")
            ax.axhline(y=set_point.get(), color='r', linestyle='-', label="Wartość zadana")
            ax.axhline(y=set_point.get() + 1.9, color='g', linestyle='--', label="5% Odchył")
            ax.axhline(y=set_point.get() - 1.9, color='g', linestyle='--')
            ax.legend()
            canvas.draw()

root = tk.Tk()
root.title("Balancing Car")
global_pid_value = tk.StringVar(value="0.0")

kp = tk.DoubleVar(value=10.0)
ki = tk.DoubleVar(value=0.1)
kd = tk.DoubleVar(value=0.0)
set_point = tk.DoubleVar(value=4)

fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
widget = canvas.get_tk_widget()
widget.grid(row=0, column=0, columnspan=4)

tk.Label(root, text="Kp:").grid(row=1, column=0)
tk.Scale(root, variable=kp, from_=10, to=100, resolution=1, orient=tk.HORIZONTAL).grid(row=1, column=1)
tk.Label(root, text="Ki:").grid(row=2, column=0)
tk.Scale(root, variable=ki, from_=0.001, to=0.01, resolution=0.001, orient=tk.HORIZONTAL).grid(row=2, column=1)
tk.Label(root, text="Kd:").grid(row=3, column=0)
tk.Scale(root, variable=kd, from_=0, to=50, resolution=1, orient=tk.HORIZONTAL).grid(row=3, column=1)

tk.Label(root, text="Wartość zadana:").grid(row=4, column=0)
tk.Scale(root, variable=set_point, from_=5, to=43, resolution=1, orient=tk.HORIZONTAL).grid(row=4, column=1)

tk.Label(root, text="Wartość regulatora PID:").grid(row=5, column=0)
tk.Label(root, textvariable=global_pid_value).grid(row=5, column=1)

reset_button = tk.Button(root, text="Resetuj wykres", command=reset_plot)
reset_button.grid(row=6, column=0, columnspan=4)

x_values = []
y_values = []

threading.Thread(target=read_from_stm, daemon=True).start()
threading.Thread(target=write_to_stm, daemon=True).start()
threading.Thread(target=update_plot, daemon=True).start()

root.mainloop()
