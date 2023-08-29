import os
import time
import can
import datetime
import csv

current_time = datetime.datetime.now()

# Format the time to the desired format
formatted_time = current_time.strftime("%d_%b_%y_%H").upper()
path_folder = "readed_data/"
excel_name = path_folder + str(formatted_time) + ".xlsx"
csv_name = path_folder + str(formatted_time) + "H" + ".csv"

csv_exists = os.path.isfile(csv_name)
excel_exists = os.path.isfile(excel_name)
print(f"\nPath csv = {csv_name}\n")

def decoder_canbus(can_data):
    struct = [item for item in can_data.split(" ") if item]
    pos_time = 1
    pos_id = 3
    pos_data = 8
    time_data = struct[pos_time]
    id_data = struct[pos_id]
    hex_array = struct[pos_data:pos_data+8]
    data_data = " ".join(hex_array)
    dictionary = {
        'Timestamp'     : time_data,
        'Id'            : id_data,
        'DL'            : data_data
    }
    return dictionary

time.sleep(0.5)
can0 = None
while can0 is None:
    try:
        can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan')
        print("Sucessfully open CAN BUS port")
    except Exception as e:
        print(e)
        time.sleep(30)


if __name__ == "__main__":
    try:
        while True:
            msg = can0.recv( 2 )
            if msg is None:
                time.sleep(2)
                continue
            msg = str(msg)
            result = decoder_canbus(msg)

            with open(csv_name, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=result.keys())
                if not csv_exists:
                    # If file doesn't exist, write headers
                    writer.writeheader()
                    csv_exists = True
                # Write the dictionary values
                writer.writerow(result)
                print("data_added")
    
    except KeyboardInterrupt:
        # Stop the tasks when Ctrl+C is pressed
        print("Tasks terminated.")


