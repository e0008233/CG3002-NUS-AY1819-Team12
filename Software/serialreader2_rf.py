#!/usr/bin/env python3

##################### Imports #####################
import datetime, time
import serial
import sys, os
import csv
import operator
import collections
import socket
from Crypto.Cipher import AES
from Crypto import Random
import base64

import Prediction_rf
from sklearn.externals import joblib
from keras.models import model_from_json
import os
from keras import optimizers
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

##################### Functions #####################
##### Arduino Handshake #####
def Handshake_Operation():
    print('Entering Handshake Mode:')
    wait_flag = 0
    while handshake_complete == False:
        ser.write(handshake)
        if wait_flag == 0:
            print('Awaiting response from Arduino...')
            wait_flag = 1
        response = ser.read().decode('utf-8')
        if response == 'A':
            print('Handshake complete')
            return True

##### Connect to server #####
def Connect_Server():
    global client
    while (1):
        print('Connecting to server...')
        ip_addr = '172.20.10.6'
        port = 8888
        address = (ip_addr, port)
        client = socket.socket()
        client.connect(address)
        print('Connected to server')
        break

##### Check printable ASCII data #####
def isPrintable(data):
    for char in data:
        if (ord(char) <= 31 or ord(char) >= 127):
            return False
    return True

##### Determine final prediction #####
def finalPrediction(prediction):
    predict_dict = {'Wipers':0, 'NumberSeven':0, 'Chicken':0, 'SideStep':0, 'Turnclap':0, 'Idle': 0}
    weights = [1,1,2,2,3]
    for i in range(len(prediction)):
        if prediction[i] in predict_dict.keys():
            predict_dict[prediction[i]] += int(weights[i])
    if max(predict_dict.values()) < 5:
        return 'confused'
    else:
        val = float(max(predict_dict.values())/9*100)
        print(str(val) + '% confidence')
        return max(predict_dict.items(), key=operator.itemgetter(1))[0]

##### Power Calculation #####
def calculatePower(I, V):
    global cum_power
    power = float(I) * float(V)
    cum_power += float(power)
    return power

##### AES Encryption #####
def encryptData(raw):
    BS = 16
    padding = ' '
    pad = lambda s: s + (BS - (len(s) % BS)) * padding
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encoded_data = base64.b64encode(iv + cipher.encrypt(pad(raw).encode('utf-8')))
    print (encoded_data)
    return encoded_data

##################### Variables/Constants Initialization #####################
handshake_complete = False
message_id = 0
handshake = ('H').encode('utf-8')
ack = ('A').encode('utf-8')
nack = ('N').encode('utf-8')
samples = []
startIndex = 0
endIndex = 96
currentIndex = 0
prediction_mlp = []
prediction_rf = []
cum_power = 0.0

##### Secret key #####
key = b'cg3002ispassword'
client = 0

##################### Main #####################
print(str(datetime.datetime.now()))
print('Initiate Connection to Raspberry Pi 3...')
ser = serial.Serial('/dev/serial0', 115200, timeout=1)
print('Connected to Raspberry Pi 3')
if Handshake_Operation():
    handshake_complete = True
# Connect_Server()

mode = input('Mode of operation (T for training, L for live): ')

if mode == 'T':
    # Prepare csv file
    input_filename = input('Create a new csv file (input d for default name):')
    if input_filename == 'd':
        input_filename = 'training_raw.csv'
    file_action = 'w'
    while os.path.exists(input_filename):
        user_input = input(input_filename + ' already exists. Press o to overwrite, a to append, n to choose another filename:')
        if user_input == 'o':
            print(input_filename + ' contents will be overwritten.')
            break
        elif user_input == 'a':
            print(input_filename + ' will be appended.')
            file_action = 'a'
            break
        elif user_input == 'n':
            input_filename = input('Choose another filename:')
        else:
            sys.exit('Invalid input, terminating program...')
    f = open(input_filename, file_action).close()       

    if file_action == 'w':
        with open(input_filename, file_action) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['id','acc_rh_x','acc_rh_y','acc_rh_z','gyro_rh_x','gyro_rh_y','gyro_rh_z',
            'acc_lh_x','acc_lh_y','acc_lh_z','gyro_lh_x','gyro_lh_y','gyro_lh_z',
            'acc_leg_x','acc_leg_y','acc_leg_z','gyro_leg_x','gryo_leg_y','gryo_leg_z'])
        print('csv headers initialized')

    csv_file = open(input_filename, 'a')

ser.write(ack)  # start receiving data from arduino
currentTime = datetime.datetime.now()
message = ser.readline()
current_milli_time = lambda: int(round(time.time() * 1000))
previous_millis = current_milli_time()
freq1_millis = current_milli_time()
while 1:
    match_flag = False
    message = ser.readline().decode() 
    if message != '':
        previous_millis = current_milli_time()
        transmitted_checksum = message.split('|')[-1]
        msg_full = str(message.rsplit('|', 1)[0])
        msg_checksum = 0
        if isPrintable(msg_full):
            for char in msg_full:
                msg_checksum ^= int(ord(char))
            if str(transmitted_checksum).strip() == str(msg_checksum).strip():
                #print("Checksum matches")
                #print("Message: %s" % msg_full)
                match_flag = True
                ser.write(ack)
            else:
                print('Checksums do not match: %s, %s' % (transmitted_checksum, msg_checksum))
                print(message)
                # Resend data
                ser.write(nack)
        else: 
            print('Message contains non-ASCII character(s)')
            print('Message may be corrupted')   

        if match_flag == True:
            ##### Retrieve Message ID #####
            message_id = msg_full.split('|')[0]
            #print('Message ID: %s' % message_id)

            ##### Retrieve Current & Voltage #####
            measurement = msg_full.split('|')[-1]
            voltage = float(measurement.split(',')[1])
            current = float(measurement.split(',')[0])
            power = calculatePower(voltage,current)
            #print('Measurements: %s' % measurement)

            ##### Retrieve Sensor Data #####
            message_content = msg_full.split('|')[1:-1]
            #print('Message Contents: %s' % message_content)

            ##### Formatting row for csv ######
            row_content = ''
            row_content += (message_id + ',')
            for i in range(1, 4):
                index = 0
                # Search for device ID and append data in incremental order
                while not message_content[index][0] == str(i) and index < len(message_content):
                    index += 1
                row_content += (message_content[index][2:] + ',')
            # Removes last comma
            row_content = row_content[:-1]
            #print(row_content)
            

            ##### Formatting data to fit in buffer for live mode ######
            sample_content = row_content.split(',')[1:]
            
            ##### Training mode #####
            if mode == 'T':
                csv_file.write(row_content + '\n')
            #print('data values written')

            ##### Live mode #####
            elif mode == 'L':
                samples.append([])
                for component in sample_content:
                    samples[currentIndex].append(component)
                if len(samples[currentIndex]) != 18:
                    print('Insufficient data in sample')
                currentIndex += 1

                if len(samples) >= endIndex:
                    # Check frequency
                    freq2_millis = current_milli_time()
                    freq = float(endIndex-startIndex) / float((freq2_millis - freq1_millis)/1000)
                    print('Frequency: ' + str(freq))
                    freq1_millis = current_milli_time()

                    #mlp_result, rf_result = prediction.predict(samples[startIndex:endIndex-1])
                    mlp_result = Prediction_rf.predict(samples[int(startIndex):int(endIndex)])
                    #print(str(startIndex) + ' ' + str(endIndex) + ' ' + str(currentIndex))
                    incrementAmt = (endIndex-startIndex)/2
                    startIndex += incrementAmt
                    endIndex += incrementAmt
                    prediction_mlp.append(mlp_result)
                    if len(prediction_mlp) > 4:
                        predicted_move = finalPrediction(prediction_mlp)
                        if predicted_move != 'confused':
                            print('MLP Final: ' + predicted_move)
                            server_message = '#' + predicted_move + '|' + str(voltage) + '|' + str(current) + '|' + str(power) + '|' + str(cum_power)
                            client.send(encryptData(server_message))
                        else:
                            print('Discarded due to confusion!')
                        prediction_mlp = []
                    #prediction_rf.append(rf_results)
                    #if len(prediction_rf) > 2:
                    #   print('RF: ' + finalPrediction(prediction_rf))
                    #    prediction_rf = []

    else:
        current_millis = current_milli_time()
        diff_millis = current_millis - previous_millis
        if diff_millis > 4000:
            handshake_complete = False
            if Handshake_Operation():
                handshake_complete = True
                ser.write(ack)
            
if mode == 'T':
    csv_file.close()

