#!/usr/bin/env python
import datetime, time
import serial
import sys, os
import csv
import operator
import collections
#from prediction import predict
#from sklearn.externals import joblib
#from keras.models import model_from_json
#import os
#from keras import optimizers
#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

Sample = collections.namedtuple('sample', ['acc_rh_x', 'acc_rh_y', 'acc_rh_z',
    'gyro_rh_x', 'gyro_rh_y', 'gyro_rh_z',
    'acc_lh_x', 'acc_lh_y', 'acc_lh_z',
    'gyro_lh_x', 'gyro_lh_y', 'gyro_lh_z',
    'acc_leg_x', 'acc_leg_y', 'acc_leg_z',
    'gyro_leg_x', 'gyro_leg_y', 'gyro_leg_z'])

# Functions
def Handshake_Operation():
    print('Entering Handshake Mode:')
    wait_flag = 0
    while handshake_complete == False:
        ser.write('H')
        if wait_flag == 0:
            print('Awaiting response from Arduino...')
            wait_flag = 1
        response = ser.read()
        if response == ('A'):
            print('Handshake complete')
            return True

def isPrintable(data):
    for char in data:
        if (ord(char) <= 31 or ord(char) >= 127):
            return False
    return True

def finalPrediction(prediction):
    predict_dict = {'wipers':0, 'number7':0, 'chicken':0, 'sidestep':0, 'turnclap':0}
    for result in prediction:
        if result in predict_dict.keys():
            predict_dict[result] += 1
        else:
            print('Unknown results: ' + result)
    return max(predict_dict.iteritems(), key=operator.itemgetter(1))[0]

# Initialization
handshake_complete = False
message_id = 0
handshake = ('H').encode()
ack = ('A').encode
nack = ('N').encode

print(str(datetime.datetime.now()))
print('Initiate Connection to Raspberry Pi 3...')
ser = serial.Serial('/dev/cu.usbmodem14601', 115200, timeout=1)
print('Connected to Raspberry Pi 3')
if Handshake_Operation():
    handshake_complete = True

# Import model
'''
model = model_from_json(open('model_architecture.json').read())
model.load_weights('model_weights.h5')
encoder = joblib.load('encoder.sav')
sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
'''

# Prepare csv file
input_filename = raw_input('Create a new csv file (input d for default name):')
if input_filename == 'd':
    input_filename = 'training_raw.csv'
file_action = 'w'
while os.path.exists(input_filename):
    user_input = raw_input(input_filename + ' already exists. Press o to overwrite, a to append, n to choose another filename:')
    if user_input == 'o':
        print(input_filename + ' contents will be overwritten.')
        break
    elif user_input == 'a':
        print(input_filename + ' will be appended.')
        file_action = 'a'
        break
    elif user_input == 'n':
        input_filename = raw_input('Choose another filename:')
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


currentTime = datetime.datetime.now()
message = ser.readline()
current_milli_time = lambda: int(round(time.time() * 1000))
previous_millis = current_milli_time()
samples = []
startIndex = 0
endIndex = 130
prediction_mlp = []
prediction_rf = []
csv_file = open(input_filename, 'a')
while 1:
    match_flag = False
    message = ser.readline() 
    if message != '':
        print("Message: %s" % message)
    #     previous_millis = current_milli_time()
    #     transmitted_checksum = message.split('|')[-1]
    #     msg_full = str(message.rsplit('|', 1)[0])
    #     msg_checksum = 0
    #     if isPrintable(msg_full):
    #         for char in msg_full:
    #             msg_checksum ^= int(ord(char))
    #         if str(transmitted_checksum).strip() == str(msg_checksum).strip():
    #             #print("Checksum matches")
    #             print("Message: %s" % msg_full)
    #             match_flag = True
    #             ser.write('A')
    #         else:
    #             print('Checksums do not match: %s, %s' % (transmitted_checksum, msg_checksum))
    #             print(message)
    #             # Resend data
    #             ser.write('N')
    #     else: 
    #         print('Message contains non-ASCII character(s)')
    #         print('Message may be corrupted')   
    #     '''
    #     '''

    #     if match_flag == True:
    #         # message_id = msg_full.split('|')[0]
    #         #print('Message ID: %s' % message_id)
    #        # measurement = msg_full.split('|')[-1]
    #         #print('Measurements: %s' % measurement)
    #         message_content = msg_full.split('|')[1:-1]
            #print('Message Contents: %s' % message_content)
           # row_content = ''
           # row_content += (message_id + ',')
            #for i in range(1, 4):
             #   index = 0
                # Search for device ID and append data in incremental order
              #  while not message_content[index][0] == str(i) and index < len(message_content):
               #     index += 1
               # row_content += (message_content[index][2:] + ',')
            # Remove last comma
            #row_content = row_content[:-1]
            #print(row_content)
            # csv_file.write(row_content + '\n')
            #print('data values written')
    else:
        current_millis = current_milli_time()
        diff_millis = current_millis - previous_millis
        if diff_millis > 4000:
            handshake_complete = False
            if Handshake_Operation():
                handshake_complete = True

            '''
            component = (message_content.strip() for x in line.split(','))
            samples.append(Sample(acc_rh_x=next(component),
                acc_rh_y=next(component),
                acc_rh_z=next(component),
                gyro_rh_x=next(component),
                gyro_rh_y=next(component),
                gyro_rh_z=next(component),
                acc_lh_x=next(component),
                acc_lh_y=next(component),
                acc_lh_z=next(component),
                gyro_lh_x=next(component),
                gyro_lh_y=next(component),
                gyro_lh_z=next(component),
                acc_leg_x=next(component),
                acc_leg_y=next(component),
                acc_leg_z=next(component),
                gyro_leg_x=next(component),
                gyro_leg_y=next(component),
                gyro_leg_z=next(component)))
            
            if len(samples) >= endIndex:
                mlp_result, rf_result = prediction.predict(samples[startIndex:endIndex-1])
                incrementAmt = (endIndex-startIndex)/2
                startIndex += incrementAmt
                endIndex += incrementAmt
                prediction_mlp.append(mlp_results)
                if len(prediction_mlp) > 2:
                    print('MLP: ' + finalPrediction(prediction_mlp))
                prediction_rf.append(rf_results)
                if len(prediction_rf) > 2:
                    print('RF: ' + finalPrediction(prediction_rf))
            '''
            
csv_file.close()

