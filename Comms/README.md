## Readme For The Arduino Code

There are multiple arduino files that we have used over the development of the project, but the final file we are using for our demo is CG3002_int_serial_sequential

Upload the file **CG3002_int_serial_sequential.ino** to the arduino and connect the sensors to the appropriate pins

1) Send serial 'H' to the Arduino, the Arduino should return 'A' via serial.
2) Send 'A' via serial to the Arduino again, and the Arduino should start sending a string of sensor readings.
3) Send 'A' to acknowledge the message, and the Arduino will continue to send another string of sensor readings.
3) Repeat step 3 to get more sensor readings. Note that every message sent by the Arduino has to be acknowledged in ~1.6s. 4 consecutive unacknowledged messages would cause the Arduino to go back to handshake mode. In this case, repeat step 1.


## Readme For Raspberry Pi code

Run this command to execute all comms tasks in RPi: **./commsreader.py**

        The 1st prompt will state "Mode of operation (T for training, L for live):"

### Path 1

1) Enter **T** to collect data into a csv file.

        2nd prompt states "Create a new csv file (input d for default name)"

2) Enter **d** for default name, which is training_raw.csv

**OR**

2) Enter any other name, ending with **.csv**
      
        If a duplicate file name exists, a 3rd prompt will state "already exists. Press o to overwrite, a to append, n to choose another filename:"

3) Proceed as stated, invalid inputs will terminate the program
  
        The last prompt will state "Do you want to reset message id? y if you want to, press any other key if you do not:"

4) Enter **y** to reset the message id from Arduino. This is just for visual inspection within the console output.

### Path 2

1) Enter **L** to collect data for live recognition.

        The last prompt will state "Do you want to reset message id? y if you want to, press any other key if you do not:"

2) Enter **y** to reset the message id from Arduino. This is just for visual inspection within the console output.





