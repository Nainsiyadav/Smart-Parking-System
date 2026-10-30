from datetime import datetime
from collections import deque


class ParkingSystem:
    """Core parking logic using dictionaries and a FIFO deque."""

    def __init__(self, total_slots=100):
        self.slots = {}

        for i in range(1, total_slots + 1):
            slot_name = "A" + str(i)
            self.slots[slot_name] = {
                "status": "Available",
                "vehicle": None
            }

        # Currently parked vehicles: fast dictionary lookup.
        self.vehicles = {}

        # Waiting vehicles: FIFO queue.
        self.waiting_queue = deque()

    def _waiting_position(self, vehicle_number):
        for position, vehicle in enumerate(self.waiting_queue, start=1):
            if vehicle["vehicle_number"] == vehicle_number:
                return position
        return None

    # ------------------------------------------------------------
    # PARK VEHICLE
    # ------------------------------------------------------------
    def park_vehicle(self, vehicle_number, vehicle_type, owner_name):
        if vehicle_number in self.vehicles:
            print("This vehicle is already parked.")
            return False

        if self._waiting_position(vehicle_number) is not None:
            print("This vehicle is already in the waiting queue.")
            return False

        empty_slot = None
        for slot_name in self.slots:
            if self.slots[slot_name]["status"] == "Available":
                empty_slot = slot_name
                break

        if empty_slot is None:
            self.waiting_queue.append({
                "vehicle_number": vehicle_number,
                "vehicle_type": vehicle_type,
                "owner_name": owner_name
            })
            print("Parking is full.")
            print("Vehicle has been added to the waiting queue.")
            print("Queue Position:", self._waiting_position(vehicle_number))
            return False

        self._assign_vehicle_to_slot(
            vehicle_number,
            vehicle_type,
            owner_name,
            empty_slot
        )

        print("\nVehicle parked successfully!")
        print("Parking Slot:", empty_slot)
        print("Entry Time:", self.vehicles[vehicle_number]["entry_time"].strftime("%Y-%m-%d %H:%M:%S"))
        return True

    def _assign_vehicle_to_slot(self, vehicle_number, vehicle_type, owner_name, slot_name):
        entry_time = datetime.now()

        self.slots[slot_name]["status"] = "Occupied"
        self.slots[slot_name]["vehicle"] = vehicle_number

        self.vehicles[vehicle_number] = {
            "vehicle_type": vehicle_type,
            "owner_name": owner_name,
            "slot": slot_name,
            "entry_time": entry_time
        }

    # ------------------------------------------------------------
    # VEHICLE EXIT
    # ------------------------------------------------------------
    def exit_vehicle(self, vehicle_number):
        if vehicle_number not in self.vehicles:
            print("Vehicle not found.")
            return None

        vehicle = self.vehicles[vehicle_number]
        exit_time = datetime.now()

        total_seconds = (exit_time - vehicle["entry_time"]).total_seconds()
        hours = total_seconds / 3600
        fee = max(20, int(hours * 20))

        slot_name = vehicle["slot"]

        self.slots[slot_name]["status"] = "Available"
        self.slots[slot_name]["vehicle"] = None
        del self.vehicles[vehicle_number]

        print("\nVehicle exited successfully.")
        print("Vehicle Number:", vehicle_number)
        print("Parking Slot:", slot_name)
        print("Parking Fee: Rs.", fee)

        assigned_vehicle = self.add_waiting_vehicle(slot_name)
        if assigned_vehicle:
            print(
                "Waiting vehicle",
                assigned_vehicle["vehicle_number"],
                "has been assigned slot",
                slot_name
            )

        return {
            "vehicle_number": vehicle_number,
            "slot": slot_name,
            "fee": fee,
            "assigned_vehicle": assigned_vehicle
        }

    # ------------------------------------------------------------
    # WAITING QUEUE PROCESSING
    # ------------------------------------------------------------
    def add_waiting_vehicle(self, slot_name):
        if not self.waiting_queue:
            return None

        vehicle = self.waiting_queue.popleft()
        self._assign_vehicle_to_slot(
            vehicle["vehicle_number"],
            vehicle["vehicle_type"],
            vehicle["owner_name"],
            slot_name
        )
        return vehicle

    def add_to_waiting_queue(self, vehicle_number, vehicle_type, owner_name):
        if vehicle_number in self.vehicles:
            print("This vehicle is already parked.")
            return False

        if self._waiting_position(vehicle_number) is not None:
            print("This vehicle is already in the waiting queue.")
            return False

        # A waiting request is meaningful when all slots are occupied.
        if any(slot["status"] == "Available" for slot in self.slots.values()):
            print("A parking slot is available. Please use Park Vehicle.")
            return False

        self.waiting_queue.append({
            "vehicle_number": vehicle_number,
            "vehicle_type": vehicle_type,
            "owner_name": owner_name
        })

        print("Vehicle has been added to the waiting queue.")
        print("Queue Position:", self._waiting_position(vehicle_number))
        return True

    def cancel_waiting_vehicle(self, vehicle_number):
        for vehicle in list(self.waiting_queue):
            if vehicle["vehicle_number"] == vehicle_number:
                self.waiting_queue.remove(vehicle)
                print("Waiting request cancelled.")
                return True

        print("Vehicle not found in waiting queue.")
        return False

    # ------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------
    def search_vehicle(self, vehicle_number):
        if vehicle_number not in self.vehicles:
            print("Vehicle not found.")
            return None

        vehicle = self.vehicles[vehicle_number]

        print("\n----- Vehicle Details -----")
        print("Vehicle Number:", vehicle_number)
        print("Vehicle Type:", vehicle["vehicle_type"])
        print("Owner Name:", vehicle["owner_name"])
        print("Parking Slot:", vehicle["slot"])
        print("Entry Time:", vehicle["entry_time"].strftime("%Y-%m-%d %H:%M:%S"))
        return vehicle

    # ------------------------------------------------------------
    # DISPLAY STATUS / RECORDS
    # ------------------------------------------------------------
    def display_status(self):
        print("\n----- PARKING STATUS -----")

        for slot_name, slot in self.slots.items():
            if slot["status"] == "Available":
                print(slot_name, "-> Available")
            else:
                print(slot_name, "-> Occupied by", slot["vehicle"])

        print("Vehicles waiting:", len(self.waiting_queue))

    def display_parked_vehicles(self):
        print("\n----- PARKED VEHICLES -----")

        if not self.vehicles:
            print("No vehicles are currently parked.")
            return

        for vehicle_number, vehicle in self.vehicles.items():
            print(
                vehicle_number,
                "-",
                vehicle["vehicle_type"],
                "-",
                vehicle["owner_name"],
                "- Slot:",
                vehicle["slot"]
            )

    def display_waiting_queue(self):
        print("\n----- WAITING QUEUE -----")

        if not self.waiting_queue:
            print("No vehicles are waiting.")
            return

        for position, vehicle in enumerate(self.waiting_queue, start=1):
            print(
                position,
                ".",
                vehicle["vehicle_number"],
                "-",
                vehicle["vehicle_type"],
                "-",
                vehicle["owner_name"]
            )
