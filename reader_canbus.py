import time
import datetime
import csv
import os
import can
from multiprocessing import Process, Queue


current_time = datetime.datetime.now()
# Format the time to the desired format
formatted_time = current_time.strftime("%d_%b_%y_%H").upper()
path_folder = "readed_data/" + str(formatted_time) + "H"
csv_name = path_folder + ".csv"

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


def save_to_csv(queue_csv, queue_led):
    counter = 0
    csv_exists = os.path.isfile(csv_name)
    try:
        with open(csv_name, 'a', newline='') as csvfile:
            while True:
                if queue_csv.empty():
                    #print(f"Skipping 1 second ...")
                    time.sleep(0.01)
                    continue
                counter += 1
                dict_ = queue_csv.get()
                writer = csv.DictWriter(csvfile, fieldnames=dict_.keys())
                if not csv_exists:
                    # If file doesn't exist, write headers
                    writer.writeheader()
                    csv_exists = True
                # Write the dictionary values
                writer.writerow(dict_)
                print(f"{counter}")
                if(counter >= 10):
                    queue_led.put(counter)
                    counter = 0

    except Exception as e:
        print(f"Error in save_to_csv():\n{e}\n")


def blink_led(qeue_led):
    init_time = int(time.time())
    status = 0
    try:
        while True:
            time_actual = int(time.time()) - init_time
            #print(f"Blink_led time = {time_actual}")
            if qeue_led.empty():
                time.sleep(0.01)
                continue
            temp = qeue_led.get()
            status = not status
            print(f"Status = {status} - {temp}")
            #time.sleep(1)

    except Exception as e:
        print(f"Error in blink_led():\n{e}\n")


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
    # Create a queue function
    q_csv = Queue()
    q_led = Queue()

    # Process to save in a .csv file
    p1 = Process(target = save_to_csv, args=(q_csv,q_led, ))
    # Process to blink led
    p2 = Process(target = blink_led, args = (q_led, ))
    
    # Start the process
    p1.start()
    p2.start()
    
    test = "{'Timestamp': '1693345961.231976', 'Id': '0cfedf00', 'DL': '90 c0 12 ff ff ff ff ff'}"
    try:
        while True:
            msg = can0.recv( 2 )
            if msg is None:
                time.sleep(2)
                continue
            msg = str(msg)
            q_csv.put(decoder_canbus(msg)) 
    
    except KeyboardInterrupt:
        # Stop the tasks when Ctrl+C is pressed
        p1.join()
        p1.terminate()
        p2.join()
        p2.terminate()
        print("Tasks terminated.")
