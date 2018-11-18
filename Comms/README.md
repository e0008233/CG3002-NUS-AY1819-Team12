## Readme For The Arduino Code

There are multiple arduino files that we have used over the development of the project, but the final file we are using for our demo is CG3002_int_serial_sequential

Upload the file **CG3002_int_serial_sequential.ino** to the arduino and connect the sensors to the appropriate pins

1) Send serial 'H' to the Arduino, the Arduino should return 'A' via serial.
2) Send 'A' via serial to the Arduino again, and the Arduino should start sending a string of sensor readings.
3) Send 'A' to acknowledge the message, and the Arduino will continue to send another string of sensor readings.
3) Repeat step 3 to get more sensor readings. Note that every message sent by the Arduino has to be acknowledged in ~1.6s. 4 consecutive unacknowledged messages would cause the Arduino to go back to handshake mode. In this case, repeat step 1.
