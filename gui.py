import io
import os
import re
import subprocess
import sys
import tkinter as tk
from contextlib import redirect_stdout
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk

from parking_system import ParkingSystem


# ============================================================
# BACKEND
# ============================================================
# Keep 25 for the final project. For temporary full-lot testing,
# change 25 to 2 and change it back to 25 afterwards.
parking = ParkingSystem(10)


# ============================================================
# COLORS
# ============================================================
BG = "#0f172a"
SIDEBAR = "#111827"
CARD = "#1e293b"
CARD_LIGHT = "#334155"
DARK = "#020617"

WHITE = "#f8fafc"
TEXT = "#cbd5e1"
MUTED = "#94a3b8"

BLUE = "#38bdf8"
GREEN = "#22c55e"
RED = "#ef4444"
YELLOW = "#f59e0b"
PURPLE = "#a78bfa"


# ============================================================
# MAIN WINDOW
# ============================================================
root = tk.Tk()
root.title("Smart Parking Management System")
root.geometry("1250x780")
root.minsize(1100, 700)
root.configure(bg=BG)


# ============================================================
# STYLES
# ============================================================
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "TCombobox",
    fieldbackground=WHITE,
    background=WHITE,
    foreground=BG,
    arrowcolor=BG
)
style.map(
    "TCombobox",
    fieldbackground=[("readonly", WHITE)],
    foreground=[("readonly", BG)],
    selectbackground=[("readonly", WHITE)],
    selectforeground=[("readonly", BG)]
)
style.configure(
    "Treeview",
    background="#172033",
    fieldbackground="#172033",
    foreground=TEXT,
    rowheight=30,
    borderwidth=0,
    font=("Segoe UI", 9)
)
style.configure(
    "Treeview.Heading",
    background=CARD_LIGHT,
    foreground=WHITE,
    font=("Segoe UI", 9, "bold")
)
style.map("Treeview", background=[("selected", "#1d4ed8")])


# ============================================================
# HELPERS
# ============================================================
def run_method(method, *args):
    """Run a backend method and capture its printed output."""
    output = io.StringIO()
    try:
        with redirect_stdout(output):
            result = method(*args)
        return output.getvalue(), result, None
    except Exception as error:
        return "ERROR: " + str(error), None, error


def show_output(text):
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, text.strip() if text and text.strip() else "Operation completed.")
    output_box.config(state="disabled")


def set_records_output(text):
    records_output.config(state="normal")
    records_output.delete("1.0", tk.END)
    records_output.insert(tk.END, text.strip() if text and text.strip() else "No records to display.")
    records_output.config(state="disabled")


def valid_vehicle_number(vehicle_number):
    pattern = r"^[A-Z]{2}[0-9]{2}[A-Z]{1,3}[0-9]{1,4}$"
    return re.fullmatch(pattern, vehicle_number) is not None


def valid_owner_name(owner_name):
    return bool(owner_name) and owner_name.replace(" ", "").isalpha()


def get_waiting_position(vehicle_number):
    for position, vehicle in enumerate(parking.waiting_queue, start=1):
        if vehicle.get("vehicle_number") == vehicle_number:
            return position
    return None


def clear_vehicle_form():
    vehicle_number_entry.delete(0, tk.END)
    owner_entry.delete(0, tk.END)
    vehicle_type.set("Car")


def update_dashboard():
    total = len(parking.slots)
    occupied = sum(1 for slot in parking.slots.values() if slot["status"] == "Occupied")
    available = total - occupied
    waiting = len(parking.waiting_queue)

    total_value.config(text=str(total))
    available_value.config(text=str(available))
    occupied_value.config(text=str(occupied))
    waiting_value.config(text=str(waiting))
    draw_parking_slots()


def show_page(page):
    for current_page in pages.values():
        current_page.pack_forget()
    page.pack(side="left", fill="both", expand=True)
    update_dashboard()


def refresh_all():
    update_dashboard()
    refresh_records_if_visible()
    show_output("System refreshed successfully.\nParking status and records are up to date.")
    messagebox.showinfo("Refresh Complete", "Parking status and records have been refreshed.")


# ============================================================
# ROOT LAYOUT
# ============================================================
sidebar = tk.Frame(root, bg=SIDEBAR, width=225)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

content = tk.Frame(root, bg=BG)
content.pack(side="right", fill="both", expand=True)

pages = {}


# ============================================================
# DASHBOARD PAGE
# ============================================================
dashboard_page = tk.Frame(content, bg=BG)
pages["dashboard"] = dashboard_page

tk.Label(
    dashboard_page, text="Dashboard", font=("Segoe UI", 25, "bold"),
    bg=BG, fg=WHITE
).pack(anchor="w", padx=30, pady=(20, 0))

tk.Label(
    dashboard_page, text="Real-time overview of the parking facility",
    font=("Segoe UI", 10), bg=BG, fg=MUTED
).pack(anchor="w", padx=30, pady=(0, 12))

stats_frame = tk.Frame(dashboard_page, bg=BG)
stats_frame.pack(fill="x", padx=25)


def create_stat_card(parent, title, color):
    card = tk.Frame(parent, bg=CARD, highlightbackground=CARD_LIGHT, highlightthickness=1, height=80)
    card.pack(side="left", fill="x", expand=True, padx=5)
    card.pack_propagate(False)
    tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), bg=CARD, fg=MUTED).pack(
        anchor="w", padx=15, pady=(9, 0)
    )
    value = tk.Label(card, text="0", font=("Segoe UI", 24, "bold"), bg=CARD, fg=color)
    value.pack(anchor="w", padx=15)
    return value


total_value = create_stat_card(stats_frame, "TOTAL SLOTS", BLUE)
available_value = create_stat_card(stats_frame, "AVAILABLE", GREEN)
occupied_value = create_stat_card(stats_frame, "OCCUPIED", RED)
waiting_value = create_stat_card(stats_frame, "WAITING", YELLOW)

parking_card = tk.Frame(
    dashboard_page, bg=CARD, highlightbackground=CARD_LIGHT,
    highlightthickness=1, height=430
)
parking_card.pack(fill="both", expand=True, padx=30, pady=12)
parking_card.pack_propagate(False)

parking_title_row = tk.Frame(parking_card, bg=CARD)
parking_title_row.pack(fill="x", padx=20, pady=(12, 0))

tk.Label(
    parking_title_row, text="Parking Area", font=("Segoe UI", 16, "bold"),
    bg=CARD, fg=WHITE
).pack(side="left")

tk.Button(
    parking_title_row, text="REFRESH", command=refresh_all,
    bg=BLUE, fg=DARK, activebackground="#7dd3fc", relief="flat",
    font=("Segoe UI", 9, "bold"), cursor="hand2", padx=14, pady=6
).pack(side="right")

tk.Label(
    parking_card, text="Green = Available     Red = Occupied",
    font=("Segoe UI", 9), bg=CARD, fg=MUTED
).pack(anchor="w", padx=20, pady=(1, 7))

slots_frame = tk.Frame(parking_card, bg=CARD)
slots_frame.pack(fill="both", expand=True, padx=20, pady=3)


def draw_parking_slots():
    for widget in slots_frame.winfo_children():
        widget.destroy()

    columns = 5
    for index, (slot_name, slot) in enumerate(parking.slots.items()):
        row = index // columns
        column = index % columns

        if slot["status"] == "Available":
            slot_bg = "#14532d"
            border = GREEN
            status = "AVAILABLE"
        else:
            slot_bg = "#7f1d1d"
            border = RED
            status = "OCCUPIED"

        slot_card = tk.Frame(
            slots_frame, bg=slot_bg, highlightbackground=border,
            highlightthickness=1, width=105, height=55
        )
        slot_card.grid(row=row, column=column, padx=4, pady=4, sticky="nsew")
        slot_card.grid_propagate(False)

        tk.Label(
            slot_card, text=slot_name, font=("Segoe UI", 10, "bold"),
            bg=slot_bg, fg=WHITE
        ).pack(pady=(5, 0))
        tk.Label(
            slot_card, text=status, font=("Segoe UI", 7, "bold"),
            bg=slot_bg, fg=WHITE
        ).pack()


# ============================================================
# SYSTEM OUTPUT
# ============================================================
output_card = tk.Frame(
    dashboard_page, bg=DARK, highlightbackground=CARD_LIGHT,
    highlightthickness=1, height=105
)
output_card.pack(fill="x", padx=30, pady=(0, 12))
output_card.pack_propagate(False)

tk.Label(
    output_card, text="SYSTEM OUTPUT", font=("Segoe UI", 9, "bold"),
    bg=DARK, fg=BLUE
).pack(anchor="w", padx=15, pady=(6, 0))

output_box = scrolledtext.ScrolledText(
    output_card, height=3, bg=DARK, fg=TEXT,
    insertbackground=WHITE, font=("Consolas", 9), relief="flat", wrap="word"
)
output_box.pack(fill="both", expand=True, padx=15, pady=(2, 6))
output_box.insert(tk.END, "System ready. Select an option from the navigation menu.")
output_box.config(state="disabled")


# ============================================================
# PARKING PAGE
# ============================================================
parking_page = tk.Frame(content, bg=BG)
pages["parking"] = parking_page

tk.Label(
    parking_page, text="Parking", font=("Segoe UI", 25, "bold"), bg=BG, fg=WHITE
).pack(anchor="w", padx=30, pady=(25, 0))
tk.Label(
    parking_page, text="Register vehicles and manage parking requests",
    font=("Segoe UI", 10), bg=BG, fg=MUTED
).pack(anchor="w", padx=30, pady=(0, 20))

form_card = tk.Frame(parking_page, bg=CARD, highlightbackground=CARD_LIGHT, highlightthickness=1)
form_card.pack(fill="x", padx=30)

tk.Label(
    form_card, text="Vehicle Information", font=("Segoe UI", 16, "bold"),
    bg=CARD, fg=WHITE
).pack(anchor="w", padx=25, pady=(20, 15))

form_fields = tk.Frame(form_card, bg=CARD)
form_fields.pack(fill="x", padx=20)


def create_entry(parent, label):
    frame = tk.Frame(parent, bg=CARD)
    frame.pack(side="left", fill="x", expand=True, padx=6)
    tk.Label(frame, text=label, font=("Segoe UI", 9, "bold"), bg=CARD, fg=TEXT).pack(anchor="w")
    entry = tk.Entry(
        frame, font=("Segoe UI", 10), bg="#334155", fg=WHITE,
        insertbackground=WHITE, relief="flat"
    )
    entry.pack(fill="x", pady=(5, 0), ipady=8)
    return entry


vehicle_number_entry = create_entry(form_fields, "Vehicle Number")

type_frame = tk.Frame(form_fields, bg=CARD)
type_frame.pack(side="left", fill="x", expand=True, padx=6)
tk.Label(type_frame, text="Vehicle Type", font=("Segoe UI", 9, "bold"), bg=CARD, fg=TEXT).pack(anchor="w")
vehicle_type = ttk.Combobox(type_frame, values=["Car", "Bike"], state="readonly", font=("Segoe UI", 10))
vehicle_type.set("Car")
vehicle_type.pack(fill="x", pady=(5, 0), ipady=5)

owner_entry = create_entry(form_fields, "Owner Name")


def park_vehicle():
    vehicle_number = vehicle_number_entry.get().strip().upper()
    vehicle_kind = vehicle_type.get()
    vehicle_owner = owner_entry.get().strip()

    if not vehicle_number:
        messagebox.showerror("Missing Information", "Please enter the vehicle number.")
        return
    if not valid_vehicle_number(vehicle_number):
        messagebox.showerror("Invalid Vehicle Number", "Please use a format such as:\nMH12AB1234")
        return
    if not valid_owner_name(vehicle_owner):
        messagebox.showerror("Invalid Owner Name", "Please enter a valid owner name.")
        return

    was_parked = vehicle_number in parking.vehicles
    old_queue_position = get_waiting_position(vehicle_number)

    output, result, error = run_method(
        parking.park_vehicle, vehicle_number, vehicle_kind, vehicle_owner
    )
    show_output(output)
    update_dashboard()

    if error:
        messagebox.showerror("Operation Error", output)
        return

    if was_parked:
        messagebox.showwarning("Already Parked", f"{vehicle_number} is already parked.")
        return

    if old_queue_position is not None:
        messagebox.showwarning(
            "Already in Queue",
            f"{vehicle_number} is already waiting at position {old_queue_position}."
        )
        return

    if vehicle_number in parking.vehicles:
        slot = parking.vehicles[vehicle_number]["slot"]
        messagebox.showinfo(
            "Parking Successful",
            f"Vehicle {vehicle_number} parked successfully.\n\nAssigned Slot: {slot}"
        )
        clear_vehicle_form()
        return

    position = get_waiting_position(vehicle_number)
    if position is not None:
        messagebox.showinfo(
            "Parking Full",
            f"No parking slot is currently available.\n\n"
            f"Vehicle {vehicle_number} was added to the waiting queue.\n"
            f"Queue Position: {position}"
        )
        clear_vehicle_form()
        return

    messagebox.showwarning("Parking Not Completed", "The parking request was not completed.")


def join_queue():
    vehicle_number = vehicle_number_entry.get().strip().upper()
    vehicle_kind = vehicle_type.get()
    vehicle_owner = owner_entry.get().strip()

    if not vehicle_number:
        messagebox.showerror("Missing Information", "Please enter the vehicle number.")
        return
    if not valid_vehicle_number(vehicle_number):
        messagebox.showerror("Invalid Vehicle Number", "Please use a format such as:\nMH12AB1234")
        return
    if not valid_owner_name(vehicle_owner):
        messagebox.showerror("Invalid Owner Name", "Please enter a valid owner name.")
        return

    was_parked = vehicle_number in parking.vehicles
    old_position = get_waiting_position(vehicle_number)

    output, result, error = run_method(
        parking.add_to_waiting_queue, vehicle_number, vehicle_kind, vehicle_owner
    )
    show_output(output)
    update_dashboard()

    if error:
        messagebox.showerror("Operation Error", output)
        return
    if was_parked:
        messagebox.showwarning("Already Parked", f"{vehicle_number} is already parked.")
        return
    if old_position is not None:
        messagebox.showwarning("Already in Queue", f"{vehicle_number} is already at queue position {old_position}.")
        return

    new_position = get_waiting_position(vehicle_number)
    if new_position is not None:
        messagebox.showinfo(
            "Waiting Queue",
            f"Vehicle {vehicle_number} added to the waiting queue.\n\n"
            f"Queue Position: {new_position}"
        )
        clear_vehicle_form()
    else:
        messagebox.showwarning(
            "Queue Request Not Completed",
            output.strip() or "A parking slot may be available. Use Park Vehicle instead."
        )

button_row = tk.Frame(form_card, bg=CARD)
button_row.pack(fill="x", padx=25, pady=20)

tk.Button(
    button_row, text="PARK VEHICLE", command=park_vehicle,
    bg=GREEN, fg=WHITE, activebackground="#16a34a", relief="flat",
    font=("Segoe UI", 10, "bold"), cursor="hand2", padx=22, pady=10
).pack(side="left", padx=(0, 10))

tk.Button(
    button_row, text="JOIN WAITING QUEUE", command=join_queue,
    bg=YELLOW, fg=DARK, activebackground="#d97706", relief="flat",
    font=("Segoe UI", 10, "bold"), cursor="hand2", padx=22, pady=10
).pack(side="left")


# ============================================================
# VEHICLE MANAGEMENT PAGE
# ============================================================
management_page = tk.Frame(content, bg=BG)
pages["management"] = management_page

tk.Label(
    management_page, text="Vehicle Management", font=("Segoe UI", 25, "bold"), bg=BG, fg=WHITE
).pack(anchor="w", padx=30, pady=(25, 0))
tk.Label(
    management_page, text="Search, exit or cancel a vehicle request",
    font=("Segoe UI", 10), bg=BG, fg=MUTED
).pack(anchor="w", padx=30, pady=(0, 20))

management_card = tk.Frame(content, bg=CARD, highlightbackground=CARD_LIGHT, highlightthickness=1)
# Re-parenting is not allowed; replace the accidental content parent immediately.
management_card.destroy()
management_card = tk.Frame(management_page, bg=CARD, highlightbackground=CARD_LIGHT, highlightthickness=1)
management_card.pack(fill="x", padx=30)

tk.Label(
    management_card, text="Vehicle Number", font=("Segoe UI", 10, "bold"), bg=CARD, fg=TEXT
).pack(anchor="w", padx=25, pady=(20, 5))

search_entry = tk.Entry(
    management_card, font=("Segoe UI", 11), bg="#334155", fg=WHITE,
    insertbackground=WHITE, relief="flat"
)
search_entry.pack(fill="x", padx=25, ipady=9)


def search_vehicle():
    vehicle_number = search_entry.get().strip().upper()
    if not vehicle_number:
        messagebox.showerror("Missing Information", "Enter a vehicle number.")
        return

    output, result, error = run_method(parking.search_vehicle, vehicle_number)
    show_output(output)
    if error:
        messagebox.showerror("Search Error", output)
        return

    if vehicle_number in parking.vehicles:
        slot = parking.vehicles[vehicle_number]["slot"]
        messagebox.showinfo("Vehicle Found", f"Vehicle {vehicle_number} found.\n\nParking Slot: {slot}")
    else:
        messagebox.showwarning("Vehicle Not Found", f"No parked vehicle record was found for {vehicle_number}.")


def exit_vehicle():
    vehicle_number = search_entry.get().strip().upper()
    if not vehicle_number:
        messagebox.showerror("Missing Information", "Enter a vehicle number.")
        return

    was_parked = vehicle_number in parking.vehicles
    output, result, error = run_method(parking.exit_vehicle, vehicle_number)
    show_output(output)
    update_dashboard()

    if error:
        messagebox.showerror("Exit Error", output)
        return

    if was_parked and vehicle_number not in parking.vehicles:
        fee = result.get("fee", 0) if isinstance(result, dict) else 0
        assigned = result.get("assigned_vehicle") if isinstance(result, dict) else None
        extra = ""
        if assigned:
            extra = f"\n\nWaiting vehicle {assigned['vehicle_number']} was automatically assigned the freed slot."
        messagebox.showinfo(
            "Exit Successful",
            f"Vehicle {vehicle_number} exited successfully.\n\nParking Fee: ₹{fee}{extra}"
        )
        search_entry.delete(0, tk.END)
        refresh_records_if_visible()
    else:
        messagebox.showwarning("Exit Not Completed", f"{vehicle_number} is not currently parked.")


def cancel_waiting():
    vehicle_number = search_entry.get().strip().upper()
    if not vehicle_number:
        messagebox.showerror("Missing Information", "Enter a vehicle number.")
        return

    before = get_waiting_position(vehicle_number)
    output, result, error = run_method(parking.cancel_waiting_vehicle, vehicle_number)
    show_output(output)
    update_dashboard()

    if error:
        messagebox.showerror("Cancellation Error", output)
        return

    after = get_waiting_position(vehicle_number)
    if before is not None and after is None:
        messagebox.showinfo("Waiting Request Cancelled", f"Waiting request for {vehicle_number} was cancelled successfully.")
        search_entry.delete(0, tk.END)
        refresh_records_if_visible()
    else:
        messagebox.showwarning("Not in Waiting Queue", f"{vehicle_number} was not found in the waiting queue.")

management_buttons = tk.Frame(management_card, bg=CARD)
management_buttons.pack(fill="x", padx=25, pady=20)

for text, command, bg, fg, active in [
    ("SEARCH VEHICLE", search_vehicle, BLUE, DARK, "#7dd3fc"),
    ("EXIT VEHICLE", exit_vehicle, RED, WHITE, "#dc2626"),
    ("CANCEL WAITING", cancel_waiting, CARD_LIGHT, WHITE, "#475569")
]:
    tk.Button(
        management_buttons, text=text, command=command, bg=bg, fg=fg,
        activebackground=active, relief="flat", font=("Segoe UI", 10, "bold"),
        cursor="hand2", padx=20, pady=10
    ).pack(side="left", padx=6)


# ============================================================
# RECORDS PAGE
# ============================================================
records_page = tk.Frame(content, bg=BG)
pages["records"] = records_page

tk.Label(
    records_page, text="Records", font=("Segoe UI", 25, "bold"), bg=BG, fg=WHITE
).pack(anchor="w", padx=30, pady=(25, 0))
tk.Label(
    records_page, text="View parked vehicles and the waiting queue",
    font=("Segoe UI", 10), bg=BG, fg=MUTED
).pack(anchor="w", padx=30, pady=(0, 20))

records_card = tk.Frame(records_page, bg=CARD, highlightbackground=CARD_LIGHT, highlightthickness=1)
records_card.pack(fill="both", expand=True, padx=30, pady=5)

records_buttons = tk.Frame(records_card, bg=CARD)
records_buttons.pack(fill="x", padx=20, pady=(18, 8))


def show_parked():
    output, result, error = run_method(parking.display_parked_vehicles)
    if error:
        output = "ERROR: " + str(error)
        set_records_output(output)
        show_output(output)
        messagebox.showerror("Records Error", output)
        return
    set_records_output(output)
    show_output(output)
    messagebox.showinfo("Parked Records Loaded", f"Parked vehicle records displayed successfully.\n\nTotal parked vehicles: {len(parking.vehicles)}")


def show_queue():
    output, result, error = run_method(parking.display_waiting_queue)
    if error:
        output = "ERROR: " + str(error)
        set_records_output(output)
        show_output(output)
        messagebox.showerror("Queue Error", output)
        return
    set_records_output(output)
    show_output(output)
    messagebox.showinfo("Waiting Queue Loaded", f"Waiting queue displayed successfully.\n\nVehicles currently waiting: {len(parking.waiting_queue)}")


def search_record():
    vehicle_number = records_search_entry.get().strip().upper()
    if not vehicle_number:
        messagebox.showerror("Missing Information", "Enter a vehicle number to search.")
        return

    if vehicle_number in parking.vehicles:
        vehicle = parking.vehicles[vehicle_number]
        text = (
            "----- PARKED VEHICLE -----\n\n"
            f"Vehicle Number: {vehicle_number}\n"
            f"Vehicle Type: {vehicle['vehicle_type']}\n"
            f"Owner Name: {vehicle['owner_name']}\n"
            f"Parking Slot: {vehicle['slot']}\n"
            f"Entry Time: {vehicle['entry_time'].strftime('%Y-%m-%d %H:%M:%S')}"
        )
        set_records_output(text)
        show_output(text)
        messagebox.showinfo("Vehicle Found", f"Vehicle {vehicle_number} found in parked records.\n\nParking Slot: {vehicle['slot']}")
        return

    position = get_waiting_position(vehicle_number)
    if position is not None:
        vehicle = list(parking.waiting_queue)[position - 1]
        text = (
            "----- WAITING VEHICLE -----\n\n"
            f"Queue Position: {position}\n"
            f"Vehicle Number: {vehicle_number}\n"
            f"Vehicle Type: {vehicle['vehicle_type']}\n"
            f"Owner Name: {vehicle['owner_name']}"
        )
        set_records_output(text)
        show_output(text)
        messagebox.showinfo("Vehicle Waiting", f"Vehicle {vehicle_number} is waiting.\n\nQueue Position: {position}")
        return

    text = f"Vehicle {vehicle_number} was not found in parked records or the waiting queue."
    set_records_output(text)
    show_output(text)
    messagebox.showwarning("Vehicle Not Found", text)


def refresh_records_if_visible():
    # Refresh visible records without forcing a popup.
    if records_page.winfo_ismapped():
        show_parked_silent()


def show_parked_silent():
    output, _, error = run_method(parking.display_parked_vehicles)
    if error:
        return
    set_records_output(output)


tk.Button(
    records_buttons, text="VIEW PARKED VEHICLES", command=show_parked,
    bg=PURPLE, fg=DARK, activebackground="#c4b5fd", relief="flat",
    font=("Segoe UI", 10, "bold"), cursor="hand2", padx=18, pady=10
).pack(side="left", padx=(0, 8))

tk.Button(
    records_buttons, text="VIEW WAITING QUEUE", command=show_queue,
    bg=YELLOW, fg=DARK, activebackground="#d97706", relief="flat",
    font=("Segoe UI", 10, "bold"), cursor="hand2", padx=18, pady=10
).pack(side="left", padx=8)

tk.Button(
    records_buttons, text="REFRESH RECORDS", command=show_parked,
    bg=BLUE, fg=DARK, activebackground="#7dd3fc", relief="flat",
    font=("Segoe UI", 10, "bold"), cursor="hand2", padx=18, pady=10
).pack(side="left", padx=8)

record_search_frame = tk.Frame(records_card, bg=CARD)
record_search_frame.pack(fill="x", padx=20, pady=(4, 10))

tk.Label(
    record_search_frame, text="Search Record", font=("Segoe UI", 9, "bold"),
    bg=CARD, fg=TEXT
).pack(side="left", padx=(0, 8))

records_search_entry = tk.Entry(
    record_search_frame, font=("Segoe UI", 10), bg="#334155", fg=WHITE,
    insertbackground=WHITE, relief="flat"
)
records_search_entry.pack(side="left", fill="x", expand=True, ipady=7)

tk.Button(
    record_search_frame, text="SEARCH", command=search_record,
    bg=GREEN, fg=WHITE, activebackground="#16a34a", relief="flat",
    font=("Segoe UI", 9, "bold"), cursor="hand2", padx=18, pady=8
).pack(side="left", padx=(8, 0))

records_output = scrolledtext.ScrolledText(
    records_card, bg="#111827", fg=TEXT, insertbackground=WHITE,
    font=("Consolas", 10), relief="flat", wrap="word"
)
records_output.pack(fill="both", expand=True, padx=20, pady=(0, 20))
records_output.insert(tk.END, "Select View Parked Vehicles or View Waiting Queue.")
records_output.config(state="disabled")


# ============================================================
# DSA ANALYSIS PAGE
# ============================================================
analysis_page = tk.Frame(content, bg=BG)
pages["analysis"] = analysis_page

tk.Label(
    analysis_page, text="DSA Analysis", font=("Segoe UI", 25, "bold"), bg=BG, fg=WHITE
).pack(anchor="w", padx=30, pady=(25, 0))
tk.Label(
    analysis_page, text="Data structures and algorithms used in the system",
    font=("Segoe UI", 10), bg=BG, fg=MUTED
).pack(anchor="w", padx=30, pady=(0, 20))

analysis_card = tk.Frame(analysis_page, bg=CARD, highlightbackground=CARD_LIGHT, highlightthickness=1)
analysis_card.pack(fill="x", padx=30)

algorithms = [
    ("Dictionary", "Parking slots and vehicle records", "Average O(1) lookup"),
    ("Queue / Deque", "Vehicles waiting for a parking slot", "O(1) insertion/removal"),
    ("Linear Search", "Sequential vehicle search", "O(n)"),
    ("Binary Search", "Search on sorted vehicle data", "O(log n)"),
    ("Bubble Sort", "Sorts vehicle numbers for searching", "O(n²)")
]

for name, description, complexity in algorithms:
    row = tk.Frame(analysis_card, bg=CARD)
    row.pack(fill="x", padx=20, pady=9)
    tk.Label(row, text=name, font=("Segoe UI", 11, "bold"), bg=CARD, fg=BLUE, width=18, anchor="w").pack(side="left")
    tk.Label(row, text=description, font=("Segoe UI", 9), bg=CARD, fg=TEXT, anchor="w").pack(side="left", fill="x", expand=True)
    tk.Label(row, text=complexity, font=("Segoe UI", 9, "bold"), bg=CARD, fg=GREEN, width=22, anchor="e").pack(side="right")


def open_graph():
    graph_file = Path(__file__).resolve().with_name("search_performance.png")

    if not graph_file.exists():
        messagebox.showwarning(
            "Graph Not Found",
            "Run analysis.py first to generate search_performance.png."
        )
        return

    try:
        if hasattr(os, "startfile"):
            os.startfile(str(graph_file))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(graph_file)])
        else:
            subprocess.Popen(["xdg-open", str(graph_file)])
        messagebox.showinfo("Graph Opened", "Search performance graph opened successfully.")
    except Exception as error:
        messagebox.showerror("Graph Error", f"The graph exists but could not be opened.\n\n{error}")


tk.Button(
    analysis_page, text="OPEN SEARCH PERFORMANCE GRAPH", command=open_graph,
    bg=BLUE, fg=DARK, activebackground="#7dd3fc", relief="flat",
    font=("Segoe UI", 10, "bold"), cursor="hand2", padx=20, pady=12
).pack(anchor="w", padx=30, pady=20)


# ============================================================
# SIDEBAR
# ============================================================
tk.Label(sidebar, text="SMART", font=("Segoe UI", 22, "bold"), bg=SIDEBAR, fg=WHITE).pack(
    anchor="w", padx=20, pady=(25, 0)
)
tk.Label(sidebar, text="PARKING", font=("Segoe UI", 22, "bold"), bg=SIDEBAR, fg=BLUE).pack(
    anchor="w", padx=20
)
tk.Label(sidebar, text="Management System", font=("Segoe UI", 9), bg=SIDEBAR, fg=MUTED).pack(
    anchor="w", padx=20, pady=(0, 25)
)


def sidebar_button(text, command):
    button = tk.Button(
        sidebar, text=text, command=command, bg=SIDEBAR, fg=TEXT,
        activebackground=CARD_LIGHT, activeforeground=WHITE, relief="flat", bd=0,
        anchor="w", font=("Segoe UI", 10, "bold"), cursor="hand2", padx=20, pady=12
    )
    button.pack(fill="x", pady=2)


sidebar_button("⌂   Dashboard", lambda: show_page(dashboard_page))
sidebar_button("▣   Parking", lambda: show_page(parking_page))
sidebar_button("⌕   Vehicle Management", lambda: show_page(management_page))
sidebar_button("☷   Records", lambda: show_page(records_page))
sidebar_button("▤   DSA Analysis", lambda: show_page(analysis_page))

tk.Frame(sidebar, bg=SIDEBAR).pack(fill="both", expand=True)
tk.Label(sidebar, text="DSA CASE STUDY", font=("Segoe UI", 8, "bold"), bg=SIDEBAR, fg=MUTED).pack(pady=(0, 3))
tk.Label(sidebar, text="Smart Parking System", font=("Segoe UI", 8), bg=SIDEBAR, fg=MUTED).pack(pady=(0, 18))


# ============================================================
# START
# ============================================================
update_dashboard()
show_page(dashboard_page)
root.mainloop()
