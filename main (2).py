from parking_system import ParkingSystem
import re


# Create the parking system
parking = ParkingSystem(100)


while True:

    print("\n====================================")
    print("       SMART PARKING SYSTEM")
    print("====================================")
    print("PARK   - Park Vehicle")
    print("EXIT   - Vehicle Exit")
    print("SEARCH - Search Vehicle")
    print("STATUS - Show Parking Status")
    print("PARKED - Show Parked Vehicles")
    print("WAIT   - Join Waiting Queue")
    print("CANCEL - Leave Waiting Queue")
    print("QUEUE  - Show Waiting Queue")
    print("CLOSE  - Exit Program")
    print("====================================")

    choice = input("What would you like to do? ").strip().upper()

    # PARK VEHICLE
    if choice == "PARK":

        print("\n--- Park Vehicle ---")

        while True:

            vehicle_number = input(
                "Enter vehicle number: "
            ).strip().upper()

            if re.fullmatch(
                r"[A-Z]{2}[0-9]{2}[A-Z]{1,3}[0-9]{1,4}",
                vehicle_number
            ):

                break

            else:

                print("Invalid vehicle number.")
                print("Example: MH01AB1234")

        while True:

            vehicle_type = input(
                "Enter vehicle type (Car/Bike): "
            ).strip().title()

            if vehicle_type in ["Car", "Bike"]:

                break

            else:

                print("Please enter only Car or Bike.")

        while True:

            owner_name = input(
                "Enter owner name: "
            ).strip()

            if owner_name.replace(" ", "").isalpha():

                break

            else:

                print("Please enter a valid name.")

        parking.park_vehicle(
            vehicle_number,
            vehicle_type,
            owner_name
        )

    # EXIT VEHICLE
    elif choice == "EXIT":

        print("\n--- Vehicle Exit ---")

        vehicle_number = input(
            "Enter vehicle number: "
        ).strip().upper()

        parking.exit_vehicle(vehicle_number)

    # SEARCH VEHICLE
    elif choice == "SEARCH":

        print("\n--- Search Vehicle ---")

        vehicle_number = input(
            "Enter vehicle number: "
        ).strip().upper()

        parking.search_vehicle(vehicle_number)

    # PARKING STATUS
    elif choice == "STATUS":

        parking.display_status()

    # PARKED VEHICLES
    elif choice == "PARKED":

        parking.display_parked_vehicles()

    # JOIN WAITING QUEUE
    elif choice == "WAIT":

        print("\n--- Join Waiting Queue ---")

        while True:

            vehicle_number = input(
                "Enter vehicle number: "
            ).strip().upper()

            if re.fullmatch(
                r"[A-Z]{2}[0-9]{2}[A-Z]{1,3}[0-9]{1,4}",
                vehicle_number
            ):

                break

            else:

                print("Invalid vehicle number.")
                print("Example: MH01AB1234")

        while True:

            vehicle_type = input(
                "Enter vehicle type (Car/Bike): "
            ).strip().title()

            if vehicle_type in ["Car", "Bike"]:

                break

            else:

                print("Please enter only Car or Bike.")

        while True:

            owner_name = input(
                "Enter owner name: "
            ).strip()

            if owner_name.replace(" ", "").isalpha():

                break

            else:

                print("Please enter a valid name.")

        parking.add_to_waiting_queue(
            vehicle_number,
            vehicle_type,
            owner_name
        )

    # CANCEL WAITING VEHICLE
    elif choice == "CANCEL":

        print("\n--- Cancel Waiting Queue ---")

        vehicle_number = input(
            "Enter vehicle number: "
        ).strip().upper()

        parking.cancel_waiting_vehicle(vehicle_number)

    # SHOW WAITING QUEUE
    elif choice == "QUEUE":

        parking.display_waiting_queue()

    # CLOSE PROGRAM
    elif choice == "CLOSE":

        print("\nThank you for using Smart Parking System!")
        print("Program closed.")

        break

    # INVALID OPTION
    else:

        print("\nInvalid option.")
        print(
            "Please enter PARK, EXIT, SEARCH, STATUS,"
            " PARKED, WAIT, CANCEL, QUEUE or CLOSE."
        )
