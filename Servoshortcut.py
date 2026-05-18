import tkinter as tk
from tkinter import messagebox, filedialog
import os
import subprocess
import sys

# Standard library imports
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import LETTER
    PDF_ENABLED = True
except ImportError:
    PDF_ENABLED = False

class NanoStudioV6:
    def __init__(self, root):
        self.root = root
        self.root.title("Nano Servo Studio Ultra - Dual Synchronized Servos")
        self.root.geometry("1150x900")
        self.root.configure(bg="#0f172a")

        # Application State
        self.servo1_pin = tk.StringVar(value="9")
        self.servo2_pin = tk.StringVar(value="10")
        self.on_btn_pin = tk.StringVar(value="2")
        self.off_btn_pin = tk.StringVar(value="3")
        self.gnd_pin = tk.StringVar(value="GND")
        self.v5_pin = tk.StringVar(value="5V")
        
        # Dual Angle State
        self.on_degrees = tk.StringVar(value="90")
        self.off_degrees = tk.StringVar(value="0")
        
        self.active_selection = tk.StringVar(value="servo1")

        self.pin_buttons = {}
        self.create_widgets()

    def repair_libraries(self):
        try:
            messagebox.showinfo("Repair", "Attempting to install PDF engine...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "reportlab"])
            messagebox.showinfo("Success", "Complete! Please RESTART the app.")
        except Exception as e:
            messagebox.showerror("Error", f"Repair failed: {e}")

    def create_widgets(self):
        sidebar = tk.Frame(self.root, bg="#1e293b", width=340)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="DUAL SERVO DESIGNER", bg="#1e293b", fg="#38bdf8", font=("Arial", 16, "bold")).pack(pady=(30, 20))

        # --- SERVO GROUP ---
        servo_group = tk.LabelFrame(sidebar, text=" SERVO SETTINGS ", bg="#1e293b", fg="#38bdf8", font=("Arial", 10, "bold"), padx=10, pady=10)
        servo_group.pack(fill="x", padx=20, pady=5)

        modes = [
            ("Servo 1 Signal (Orange)", "servo1", "#f97316"),
            ("Servo 2 Signal (Yellow)", "servo2", "#fbbf24"),
            ("Common 5V (Red)", "v5", "#dc2626"),
            ("Common GND (Brown)", "gnd", "#78350f")
        ]
        for text, val, color in modes:
            tk.Radiobutton(servo_group, text=text, variable=self.active_selection, value=val, indicatoron=0, 
                           bg="#334155", fg="white", selectcolor=color, font=("Arial", 9, "bold")).pack(fill="x", pady=2)

        # --- BUTTON & ANGLE GROUP ---
        btn_group = tk.LabelFrame(sidebar, text=" BUTTON & SYNC SETTINGS ", bg="#1e293b", fg="#4ade80", font=("Arial", 10, "bold"), padx=10, pady=10)
        btn_group.pack(fill="x", padx=20, pady=5)
        
        tk.Label(btn_group, text="Button 1 (Turn Right) Angle:", bg="#1e293b", fg="white", font=("Arial", 8)).pack(anchor="w")
        tk.Entry(btn_group, textvariable=self.on_degrees, bg="#334155", fg="white", borderwidth=0, justify="center").pack(pady=(2,5), fill="x")
        tk.Radiobutton(btn_group, text="Map Button 1 Pin (Red)", variable=self.active_selection, value="on_btn", 
                       indicatoron=0, bg="#334155", fg="white", selectcolor="#ef4444", font=("Arial", 9, "bold")).pack(fill="x", pady=2)

        tk.Frame(btn_group, height=1, bg="#475569").pack(fill="x", pady=10)

        tk.Label(btn_group, text="Button 2 (Turn Left) Angle:", bg="#1e293b", fg="white", font=("Arial", 8)).pack(anchor="w")
        tk.Entry(btn_group, textvariable=self.off_degrees, bg="#334155", fg="white", borderwidth=0, justify="center").pack(pady=(2,5), fill="x")
        tk.Radiobutton(btn_group, text="Map Button 2 Pin (Black)", variable=self.active_selection, value="off_btn", 
                       indicatoron=0, bg="#334155", fg="white", selectcolor="#000000", font=("Arial", 9, "bold")).pack(fill="x", pady=2)

        # --- ACTIONS ---
        tk.Button(sidebar, text="GENERATE ARDUINO CODE", command=self.generate_code, bg="#38bdf8", fg="#0f172a", font=("Arial", 10, "bold"), borderwidth=0).pack(pady=(40, 5), padx=20, fill="x")
        tk.Button(sidebar, text="SAVE WIRING PDF", command=self.generate_pdf, bg="#a855f7", fg="white", font=("Arial", 10, "bold"), borderwidth=0).pack(pady=5, padx=20, fill="x")

        if not PDF_ENABLED:
            tk.Button(sidebar, text="⚠ REPAIR PDF ENGINE", command=self.repair_libraries, bg="#f43f5e", fg="white", font=("Arial", 9, "bold"), borderwidth=0).pack(pady=10, padx=20, fill="x")

        # Main Area
        main_area = tk.Frame(self.root, bg="#0f172a")
        main_area.pack(side="right", expand=True, fill="both")
        tk.Label(main_area, text="DUAL SYNC SERVO DESIGNER", bg="#0f172a", fg="white", font=("Arial", 22, "bold")).pack(pady=20)
        
        self.canvas = tk.Canvas(main_area, width=800, height=500, bg="#0f172a", highlightthickness=0)
        self.canvas.pack(expand=True)

        self.canvas.create_rectangle(100, 120, 700, 380, fill="#1e293b", outline="#334155", width=4) 
        self.canvas.create_rectangle(380, 210, 460, 290, fill="#0f172a", outline="#334155")
        self.canvas.create_text(420, 250, text="NANO V3", fill="#334155", font=("Arial", 9, "bold"))
        self.canvas.create_rectangle(50, 215, 110, 285, fill="#94a3b8")

        top_row = ["D12", "D11", "D10", "D9", "D8", "D7", "D6", "D5", "D4", "D3", "D2", "GND", "RST", "RX0", "TX1"]
        bot_row = ["D13", "3V3", "REF", "A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "5V", "RST", "GND", "VIN"]

        for i, pin in enumerate(top_row): self.create_interactive_pin(150 + (i * 38), 120, pin)
        for i, pin in enumerate(bot_row): self.create_interactive_pin(150 + (i * 38), 380, pin)

        self.update_colors()

    def create_interactive_pin(self, x, y, label):
        btn = tk.Button(self.root, text=label, font=("Arial", 7, "bold"), width=3, relief="flat", command=lambda p=label: self.assign_pin(p))
        self.canvas.create_window(x, y, window=btn)
        self.pin_buttons[label] = btn
        
    def assign_pin(self, pin_label):
        mode = self.active_selection.get()
        clean = pin_label.replace("D", "").replace("A", "")
        used_pins = [self.servo1_pin.get(), self.servo2_pin.get(), self.on_btn_pin.get(), self.off_btn_pin.get()]
        
        if mode in ["servo1", "servo2", "on_btn", "off_btn"] and clean in used_pins:
            messagebox.showwarning("Conflict", f"Pin {pin_label} is already assigned!")
            return

        if mode == "servo1": self.servo1_pin.set(clean)
        elif mode == "servo2": self.servo2_pin.set(clean)
        elif mode == "on_btn": self.on_btn_pin.set(clean)
        elif mode == "off_btn": self.off_btn_pin.set(clean)
        elif mode == "gnd": self.gnd_pin.set(pin_label)
        elif mode == "v5": self.v5_pin.set(pin_label)
        self.update_colors()

    def update_colors(self):
        for label, btn in self.pin_buttons.items(): btn.config(bg="#475569", fg="white")
        def get_btn(p): return f"D{p}" if p.isdigit() else p
        if get_btn(self.servo1_pin.get()) in self.pin_buttons: self.pin_buttons[get_btn(self.servo1_pin.get())].config(bg="#f97316")
        if get_btn(self.servo2_pin.get()) in self.pin_buttons: self.pin_buttons[get_btn(self.servo2_pin.get())].config(bg="#fbbf24")
        if get_btn(self.on_btn_pin.get()) in self.pin_buttons: self.pin_buttons[get_btn(self.on_btn_pin.get())].config(bg="#ef4444")
        if get_btn(self.off_btn_pin.get()) in self.pin_buttons: self.pin_buttons[get_btn(self.off_btn_pin.get())].config(bg="#000000")
        if self.gnd_pin.get() in self.pin_buttons: self.pin_buttons[self.gnd_pin.get()].config(bg="#78350f")
        if self.v5_pin.get() in self.pin_buttons: self.pin_buttons[self.v5_pin.get()].config(bg="#dc2626")

    def generate_code(self):
        code = f"""#include <Servo.h>

Servo servoLeft;
Servo servoRight;

const int btnRight = {self.on_btn_pin.get()};
const int btnLeft = {self.off_btn_pin.get()};

const int srv1Pin = {self.servo1_pin.get()};
const int srv2Pin = {self.servo2_pin.get()};

const int angleRight = {self.on_degrees.get()};
const int angleLeft = {self.off_degrees.get()};

void setup() {{
  servoLeft.attach(srv1Pin);
  servoRight.attach(srv2Pin);
  
  pinMode(btnRight, INPUT_PULLUP);
  pinMode(btnLeft, INPUT_PULLUP);
  
  // Initialize both to Left position
  servoLeft.write(angleLeft);
  servoRight.write(angleLeft);
}}

void loop() {{
  if(digitalRead(btnRight) == LOW) {{ 
    servoLeft.write(angleRight); 
    servoRight.write(angleRight); 
  }}
  if(digitalRead(btnLeft) == LOW) {{ 
    servoLeft.write(angleLeft); 
    servoRight.write(angleLeft); 
  }}
}}"""
        f = filedialog.asksaveasfile(defaultextension=".ino", filetypes=[("Arduino Files", "*.ino")])
        if f: f.write(code); f.close(); messagebox.showinfo("Success", "Sync Code Exported!")

    def generate_pdf(self):
        if not PDF_ENABLED: return
        f_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not f_path: return
        try:
            c = canvas.Canvas(f_path, pagesize=LETTER)
            c.setFont("Helvetica-Bold", 20); c.drawString(100, 750, "Dual Sync Servo Wiring Blueprint")
            y = 680
            data = [
                ("Servo 1 Signal", f"Pin {self.servo1_pin.get()}"),
                ("Servo 2 Signal", f"Pin {self.servo2_pin.get()}"),
                ("Button Right (Btn 1)", f"Pin {self.on_btn_pin.get()}"),
                ("Button Left (Btn 2)", f"Pin {self.off_btn_pin.get()}"),
                ("Common GROUND", self.gnd_pin.get()),
                ("Common 5V POWER", self.v5_pin.get())
            ]
            for label, val in data:
                c.setFont("Helvetica-Bold", 12); c.drawString(100, y, label)
                c.setFont("Helvetica", 12); c.drawString(300, y, f": {val}")
                y -= 30
            c.save(); messagebox.showinfo("Success", "PDF Exported!")
        except Exception as e: messagebox.showerror("Error", f"Failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NanoStudioV6(root); root.mainloop()pip install reportlab