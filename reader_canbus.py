import os
import time
import can
import datetime

current_time = datetime.datetime.now()

# Format the time to the desired format
formatted_time = current_time.strftime("%d_%b_%y_%H_%M_%S").upper()
path_folder = "/readed_data/"
excel_name = formatted_time + ".xlsx"
csv_name = formatted_time + ".csv"


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
            print(result)
    
    except KeyboardInterrupt:
        # Stop the tasks when Ctrl+C is pressed
        print("Tasks terminated.")


