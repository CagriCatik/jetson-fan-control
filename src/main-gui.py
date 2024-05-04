#!/usr/bin/python3

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import json
import subprocess as sp
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FanControlApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Jetson Fan Control")

        self.read_config()
        self.create_widgets()

        self.temp_history = []
        self.speed_history = []

        self.start_fan_control()

    def read_config(self):
        try:
            with open("configs/config_standard.json", "r") as file:
                config = json.load(file)
            self.FAN_OFF_TEMP = config.get("FAN_OFF_TEMP", 20)
            self.FAN_MAX_TEMP = config.get("FAN_MAX_TEMP", 50)
            self.UPDATE_INTERVAL = config.get("UPDATE_INTERVAL", 2)
            self.MAX_PERF = config.get("MAX_PERF", 0)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading config.json: {repr(e)}")
            self.FAN_OFF_TEMP = 20
            self.FAN_MAX_TEMP = 50
            self.UPDATE_INTERVAL = 2
            self.MAX_PERF = 0

    def create_widgets(self):
        self.temp_label = tk.Label(self.master, text="Current Temperature:")
        self.temp_label.pack()

        self.temp_value_label = tk.Label(self.master, text="")
        self.temp_value_label.pack()

        self.speed_label = tk.Label(self.master, text="Fan Speed:")
        self.speed_label.pack()

        self.speed_value_label = tk.Label(self.master, text="")
        self.speed_value_label.pack()

        self.load_config_button = tk.Button(self.master, text="Load Config", command=self.load_config)
        self.load_config_button.pack()

        self.plot_canvas = plt.Figure(figsize=(6, 6), dpi=100)
        
        # Temperature
        self.temp_plot_ax = self.plot_canvas.add_subplot(211)
        self.temp_plot_line, = self.temp_plot_ax.plot([], [], 'r-')
        self.temp_plot_ax.set_title('Temperature')
        self.temp_plot_ax.set_xlabel('Time')
        self.temp_plot_ax.set_ylabel('Temperature (°C)')
        
        # Fan
        self.speed_plot_ax = self.plot_canvas.add_subplot(212)
        self.speed_plot_line, = self.speed_plot_ax.plot([], [], 'b-')
        self.speed_plot_ax.set_title('Fan Speed')
        self.speed_plot_ax.set_xlabel('Time')
        self.speed_plot_ax.set_ylabel('Fan Speed')
        
        self.plot_canvas.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.plot_canvas, master=self.master)
        self.canvas.get_tk_widget().pack()

    def update_values(self):
        temp = self.read_temp()
        spd = self.fan_curve(temp)
        self.temp_value_label.config(text=f"{temp} °C")
        self.speed_value_label.config(text=f"{spd}")
        self.temp_history.append(temp)
        self.speed_history.append(spd)
        self.temp_plot_line.set_data(range(len(self.temp_history)), self.temp_history)
        self.temp_plot_ax.relim()
        self.temp_plot_ax.autoscale_view(True,True,True)
        self.speed_plot_line.set_data(range(len(self.speed_history)), self.speed_history)
        self.speed_plot_ax.relim()
        self.speed_plot_ax.autoscale_view(True,True,True)
        self.canvas.draw()

    def read_temp(self):
        try:
            with open("/sys/devices/virtual/thermal/thermal_zone0/temp", "r") as file:
                temp_raw = file.read()
            temp = int(temp_raw) / 1000
            return temp
        except Exception as e:
            messagebox.showerror("Error", f"Error reading temperature: {repr(e)}")
            return "N/A"

    def fan_curve(self, temp):
        spd = 255 * (temp - self.FAN_OFF_TEMP) / (self.FAN_MAX_TEMP - self.FAN_OFF_TEMP)
        return int(min(max(0, spd), 255))

    def set_speed(self, spd):
        try:
            with open("/sys/devices/pwm-fan/target_pwm", "w") as file:
                file.write(f"{spd}")
        except Exception as e:
            messagebox.showerror("Error", f"Error setting fan speed: {repr(e)}")

    def start_fan_control(self):
        if self.MAX_PERF > 0:
            try:
                sp.call("jetson_clocks")
            except Exception as e:
                messagebox.showerror("Error", f"Error calling jetson_clocks: {repr(e)}")

        self.thread = threading.Thread(target=self.control_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop_fan_control(self):
        try:
            self.thread.join()
        except AttributeError:
            pass

    def control_loop(self):
        while True:
            spd = self.fan_curve(self.read_temp())
            self.set_speed(spd)
            self.update_values()
            time.sleep(self.UPDATE_INTERVAL)

    def load_config(self):
        file_path = filedialog.askopenfilename(title="Select Config File", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    config = json.load(file)
                self.FAN_OFF_TEMP = config.get("FAN_OFF_TEMP", 20)
                self.FAN_MAX_TEMP = config.get("FAN_MAX_TEMP", 50)
                self.UPDATE_INTERVAL = config.get("UPDATE_INTERVAL", 2)
                self.MAX_PERF = config.get("MAX_PERF", 0)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading config file: {repr(e)}")

def main():
    root = tk.Tk()
    app = FanControlApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
