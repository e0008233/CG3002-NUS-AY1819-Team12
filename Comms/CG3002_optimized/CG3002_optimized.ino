#include <Arduino_FreeRTOS.h>
#include <semphr.h>
#include "I2Cdev.h"
#include "MPU6050.h"

#include <string.h>

int readByte = 0;
char sensorReadings1[100] = ""; 
char sensorReadings2[100] = ""; 
char sensorReadings3[100] = ""; 
char powerReadings[100] = ""; 

char fullMessage[250] = ""; 
char message[100] = "";
char hash[100] = "";

int handshakeCount = 0;

// Arduino Wire library is required if I2Cdev I2CDEV_ARDUINO_WIRE implementation
// is used in I2Cdev.h
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif

// class default I2C address is 0x68
// AD0 low = 0x68
// AD0 high = 0x69
MPU6050 accelgyro;
// MPU6050 accelgyro(0x69); // <-- use for AD0 high


#define NUMDIGITS 10000.0 // use 100000.0 for 6 digits, 1000000.0 for 7 digits
#define NUMCHAR 10 // number of digits to send

int16_t ax, ay, az;
int16_t gx, gy, gz;
int16_t ax2, ay2, az2;
int16_t gx2, gy2, gz2;
int16_t ax3, ay3, az3;
int16_t gx3, gy3, gz3;
int16_t ax4, ay4, az4;
int16_t gx4, gy4, gz4;

int16_t ogx, ogy, ogz;
int16_t oax2, oay2, oaz2;
int16_t ogx2, ogy2, ogz2;
int16_t oax3, oay3, oaz3;
int16_t ogx3, ogy3, ogz3;
int16_t oax4, oay4, oaz4;
int16_t ogx4, ogy4, ogz4;



// data scaled and updated to without decimals (to be sent to RPi)
float ax_f, ay_f, az_f;
float gx_f, gy_f, gz_f;
float ax2_f, ay2_f, az2_f;
float gx2_f, gy2_f, gz2_f;
float ax3_f, ay3_f, az3_f;
float gx3_f, gy3_f, gz3_f;
float ax4_f, ay4_f, az4_f;
float gx4_f, gy4_f, gz4_f;
int16_t currentSensor;
int16_t voltageSensor;
float currentValue;
float voltageValue;

int msgID;
int checksum;

// data in char array of size 
char ax_c[NUMCHAR], ay_c[NUMCHAR], az_c[NUMCHAR];
char gx_c[NUMCHAR], gy_c[NUMCHAR], gz_c[NUMCHAR];
char ax2_c[NUMCHAR], ay2_c[NUMCHAR], az2_c[NUMCHAR];
char gx2_c[NUMCHAR], gy2_c[NUMCHAR], gz2_c[NUMCHAR];
char ax3_c[NUMCHAR], ay3_c[NUMCHAR], az3_c[NUMCHAR];
char gx3_c[NUMCHAR], gy3_c[NUMCHAR], gz3_c[NUMCHAR];
char ax4_c[NUMCHAR], ay4_c[NUMCHAR], az4_c[NUMCHAR];
char gx4_c[NUMCHAR], gy4_c[NUMCHAR], gz4_c[NUMCHAR];
char current_c[NUMCHAR];
char voltage_c[NUMCHAR];
char power_c[NUMCHAR];
char energy_c[NUMCHAR];

#define OUTPUT_READABLE_ACCELGYRO

#define SENSOR_1 4 // Left hand IMU
#define SENSOR_2 5 // Right hand IMU
#define SENSOR_3 6
#define SENSOR_4 7
#define CURRENT A0
#define VOLTAGE A1
#define VOLTAGEREF 5.0
#define RESISTSHUNT 0.1
#define ACCELRANGE 2.0
#define GYRORANGE 250.0

void TaskReadAcc1( void *pvParameters );
void TaskReadAcc2( void *pvParameters );
void TaskReadAcc3( void *pvParameters );
void TaskReadPower( void *pvParameters );
void TransmitMessage( char [], int );

void TaskSendData( void *pvParameters );

SemaphoreHandle_t xBufferMutex;


SemaphoreHandle_t xSerialSemaphoreSensor1;
SemaphoreHandle_t xSerialSemaphoreSensor2;
SemaphoreHandle_t xSerialSemaphoreSensor3;
SemaphoreHandle_t xSerialSemaphorePower;



// ================================================================
// ===                      INITIAL SETUP                       ===
// ================================================================

void setup() {
    
   // configure Arduino LED pin for output
    pinMode(SENSOR_1, OUTPUT);
    pinMode(SENSOR_2, OUTPUT);
    pinMode(SENSOR_3, OUTPUT);
    // join I2C bus (I2Cdev library doesn't do this automatically)
    #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
    #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
        Fastwire::setup(400, true);
    #endif
    
    Serial.begin(115200);
    msgID = 0;
    checksum =0;
    // sensor 1
    digitalWrite(SENSOR_1,LOW);
    digitalWrite(SENSOR_2,HIGH);
    digitalWrite(SENSOR_3,HIGH);
    accelgyro.initialize(); // default gyro range +/- 250 degrees/sec & default accel range +/- 2g

    ogx = accelgyro.getRotationX();
    ogy = accelgyro.getRotationY();
    ogz = accelgyro.getRotationZ();



    // sensor 2
    digitalWrite(SENSOR_1,HIGH);
    digitalWrite(SENSOR_2,LOW);
    digitalWrite(SENSOR_3,HIGH);
    accelgyro.initialize();
    //oax2 = accelgyro.getAccelerationX();
    //oay2 = accelgyro.getAccelerationY();
    //oaz2 = accelgyro.getAccelerationZ();
    ogx2 = accelgyro.getRotationX();
    ogy2 = accelgyro.getRotationY();
    ogz2 = accelgyro.getRotationZ();
    
    // sensor 3
    digitalWrite(SENSOR_1,HIGH);
    digitalWrite(SENSOR_2,HIGH);
    digitalWrite(SENSOR_3,LOW);

    accelgyro.initialize();
    //oax3 = accelgyro.getAccelerationX();
    //oay3 = accelgyro.getAccelerationY();
    //oaz3 = accelgyro.getAccelerationZ();
    ogx3 = accelgyro.getRotationX();
    ogy3 = accelgyro.getRotationY();
    ogz3 = accelgyro.getRotationZ();

    
    
    while (!Serial); // wait for Leonardo enumeration, others continue immediately
    handshakeOperation();

    if ( xSerialSemaphoreSensor1 == NULL )  // Check to confirm that the Serial Semaphore has not already been created.
    {
      xSerialSemaphoreSensor1 = xSemaphoreCreateBinary(); 
      if ( ( xSerialSemaphoreSensor1 ) != NULL ) xSemaphoreGive( ( xSerialSemaphoreSensor1 ) ); 
    }
    if ( xSerialSemaphorePower == NULL )  // Check to confirm that the Serial Semaphore has not already been created.
    {
      xSerialSemaphorePower = xSemaphoreCreateBinary(); 
      if ( ( xSerialSemaphorePower ) != NULL ) xSemaphoreGive( ( xSerialSemaphorePower ) ); 
    }

    if ( xBufferMutex == NULL )  // Check to confirm that the Serial Semaphore has not already been created.
    {
      xBufferMutex = xSemaphoreCreateMutex(); 
      if ( ( xBufferMutex ) != NULL ) xSemaphoreGive( ( xBufferMutex ) ); 
    }
    
    xTaskCreate(
      TaskReadAcc1
      ,  (const portCHAR *) "AnalogRead"
      ,  2000 // This stack size can be checked & adjusted by reading Highwater
      ,  NULL
      ,  3  // priority
      ,  NULL );
    xTaskCreate(
      TaskReadPower
      ,  (const portCHAR *) "AnalogRead"
      ,  400 // This stack size can be checked & adjusted by reading Highwater
      ,  NULL
      ,  2  // priority
      ,  NULL );
    xTaskCreate(
      TaskSendData
      ,  (const portCHAR *) "AnalogRead"
      ,  2000 // This stack size can be checked & adjusted by reading Highwater
      ,  NULL
      ,  1  // priority
      ,  NULL );
   

}



float format_accel(int16_t a) {
    return (float) (a * ACCELRANGE / 32767.0);
}

float format_g(int16_t a) {
    return (float) (a * GYRORANGE / 32767.0);
}

int32_t format_current(int16_t a) {
    float currentScaled;
    currentScaled = (a * VOLTAGEREF / 1023.0) / (10 * RESISTSHUNT);
    return (int32_t) (currentScaled * NUMDIGITS);
}

int32_t format_voltage(int16_t a) {
    return (int32_t) (a * VOLTAGEREF * 2 * NUMDIGITS / 1023.0);
}


char intToChar (int32_t num, char* array) {
    //return dtostrf(num/NUMDIGITS, 3, 2, array);
}



void handshakeOperation() {
  int flag = 0;
  while(flag == 0) {
    if (Serial.available()) {
      if (Serial.read() == 'H') {
        flag = 1;
        handshakeCount = 0;
        Serial.write('A');
      }
    }
  }
}

char* getHash(char input[]) {
  uint32_t Hash = 0;
  for (int i=0; i<strlen(input); i++) {
    Hash ^= input[i];
  }

  char checksum_c[5]; 
  return itoa(Hash, checksum_c, 10);
}

void loop()
{
  // Empty. Things are done in Tasks.
}


void TaskReadAcc1(void *pvParameters)  // This is a task.

{
  (void) pvParameters;
  int i = 0;
  TickType_t xLastWakeTime;
  const TickType_t xPeriod = pdMS_TO_TICKS( 1 );
  
  for (;;)
  {
    if ( xSemaphoreTake( xSerialSemaphoreSensor1, ( TickType_t ) 1 ) == pdTRUE ) {
       
      // We were able to obtain or "Take" the semaphore and can now access the shared resource.

      digitalWrite(SENSOR_1,LOW);
      digitalWrite(SENSOR_2,HIGH);
      digitalWrite(SENSOR_3,HIGH);
  
      //Serial.print("1: ");
      accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
      if (ax == 0 && ay == 0 && az == 0) {
        accelgyro.initialize();
      }

      digitalWrite(SENSOR_1,HIGH);
      digitalWrite(SENSOR_2,LOW);
      digitalWrite(SENSOR_3,HIGH);


       //Serial.print("1: ");
      accelgyro.getMotion6(&ax2, &ay2, &az2, &gx2, &gy2, &gz2);
      if (ax2 == 0 && ay2 == 0 && az2 == 0) {
        accelgyro.initialize();
      }

      digitalWrite(SENSOR_1,HIGH);
      digitalWrite(SENSOR_2,HIGH);
      digitalWrite(SENSOR_3,LOW);

      accelgyro.getMotion6(&ax3, &ay3, &az3, &gx3, &gy3, &gz3);
      if (ax3 == 0 && ay3 == 0 && az3 == 0) {
        accelgyro.initialize();
      }


              
     if ( xSemaphoreTake( xBufferMutex, ( TickType_t ) 1 ) == pdTRUE ) {    
        ax_f = format_accel(ax); // scale value to g and shrink to 8bits, data as NUMINTEGERS
        ay_f = format_accel(ay);
        az_f = format_accel(az);
        gx_f = format_g(gx-ogx); // scale value to d/s and shrink to 8bits, data as NUMINTEGERS
        gy_f = format_g(gy-ogy);
        gz_f = format_g(gz-ogz);
    
        sensorReadings1[0] = (char) 0;
        dtostrf(ax_f, 3, 3, ax_c);
        dtostrf(ay_f, 3, 3, ay_c);
        dtostrf(az_f, 3, 3, az_c);
        dtostrf(gx_f, 3, 2, gx_c);
        dtostrf(gy_f, 3, 2, gy_c);
        dtostrf(gz_f, 3, 2, gz_c);
        sprintf(sensorReadings1,"|1,%s,%s,%s,%s,%s,%s", ax_c, ay_c, az_c, gx_c, gy_c, gz_c);

        ax2_f = format_accel(ax2); // scale value to g and shrink to 8bits, data as NUMINTEGERS
        ay2_f = format_accel(ay2);
        az2_f = format_accel(az2);
        gx2_f = format_g(gx2-ogx2); // scale value to d/s and shrink to 8bits, data as NUMINTEGERS
        gy2_f = format_g(gy2-ogy2);
        gz2_f = format_g(gz2-ogz2);
  
  
        sensorReadings2[0] = (char) 0;
  
        dtostrf(ax2_f, 3, 3, ax2_c);
        dtostrf(ay2_f, 3, 3, ay2_c);
        dtostrf(az2_f, 3, 3, az2_c);
        dtostrf(gx2_f, 3, 2, gx2_c);
        dtostrf(gy2_f, 3, 2, gy2_c);
        dtostrf(gz2_f, 3, 2, gz2_c);


        
        sprintf(sensorReadings2,"|2,%s,%s,%s,%s,%s,%s", ax2_c, ay2_c, az2_c, gx2_c, gy2_c, gz2_c);
        // sensor 1


        ax3_f = format_accel(ax3); // scale value to g and shrink to 8bits, data as NUMINTEGERS
        ay3_f = format_accel(ay3);
        az3_f = format_accel(az3);
        gx3_f = format_g(gx2-ogx3); // scale value to d/s and shrink to 8bits, data as NUMINTEGERS
        gy3_f = format_g(gy2-ogy3);
        gz3_f = format_g(gz2-ogz3);
  
        dtostrf(ax3_f, 3, 3, ax3_c);
        dtostrf(ay3_f, 3, 3, ay3_c);
        dtostrf(az3_f, 3, 3, az3_c);
        dtostrf(gx3_f, 3, 2, gx3_c);
        dtostrf(gy3_f, 3, 2, gy3_c);
        dtostrf(gz3_f, 3, 2, gz3_c);

        sensorReadings3[0] = (char) 0;
      
        sprintf(sensorReadings3,"|3,%s,%s,%s,%s,%s,%s", ax3_c, ay3_c, az3_c, gx3_c, gy3_c, gz3_c);
        xSemaphoreGive( xBufferMutex );
        
      }
    }
  }
}

void TaskReadPower(void *pvParameters)  // This is a task.
{
  (void) pvParameters;
  TickType_t xLastWakeTime;
  const TickType_t xFrequency = 4;
  int i = 0;

  xLastWakeTime = xTaskGetTickCount();

  for (;;)
  {
    if ( xSemaphoreTake( xSerialSemaphorePower, ( TickType_t ) 1 ) == pdTRUE )
    {
      if ( xSemaphoreTake( xBufferMutex, ( TickType_t ) 1 ) == pdTRUE ) {

        currentSensor = analogRead(CURRENT); // get raw reading
        currentValue = format_current(currentSensor)/NUMDIGITS; // scale value to A and convert to int
        
        voltageSensor = analogRead(VOLTAGE); // get raw reading
        voltageValue = format_voltage(voltageSensor)/NUMDIGITS; // scale value to V and convert to int
        
        dtostrf(currentValue, 3, 4, current_c);
        dtostrf(voltageValue, 3, 4, voltage_c);

        powerReadings[0] = (char) 0;
        sprintf(powerReadings,"|%s,%s", current_c, voltage_c);
        xSemaphoreGive( xBufferMutex );
      }
    }
     vTaskDelayUntil( &xLastWakeTime, xFrequency );
  }
}

int ackWait(char fullMessage [], int msgIndex) {
  int flag = 0;
  int failFlag = 0;
  int initialTime = xTaskGetTickCount();
  
  while(flag == 0) {
    int currTime = xTaskGetTickCount();

    if ( (currTime - initialTime) > 100) return 0;
    if (Serial.available()) {
      char result = Serial.read();
      if (result == 'A') {
        return 1;
      } else if (result == 'N'){
        //initialTime = currTime;
        //Serial.println("\n\n\n");
        failFlag++;
        initialTime = currTime;
        TransmitMessage(fullMessage, msgIndex);
        if (failFlag == 10 ) return 2;
      }
    }
  }
}



void TransmitMessage(char message[], int msgLength) {
    for (int i=0; i<msgLength; i++) {
      Serial.write(message[i]);
    }
    Serial.write('\n');
}


void TaskSendData(void *pvParameters)  // This is a task.
{
  (void) pvParameters;
  TickType_t xLastWakeTime;
  const TickType_t xPeriod = pdMS_TO_TICKS( 20 );
  xLastWakeTime = xTaskGetTickCount();

  for (;;)
  {
    vTaskDelayUntil( &xLastWakeTime, xPeriod ); 
    if ( xSemaphoreTake( xBufferMutex, ( TickType_t ) 2 ) == pdTRUE ) {
      //if Buffer Queue not empty, send all from buffer first

      if (handshakeCount == 4) {
        handshakeOperation();
      }

      sprintf(fullMessage,"%d", msgID++);
      
     
      int len = strlen(sensorReadings1);
      int msgIndex = strlen(fullMessage);
   
      strcat(fullMessage,sensorReadings1);
      msgIndex+=len;

      len = strlen(sensorReadings2);
      
      strcat(fullMessage,sensorReadings2);
      msgIndex+=len;

      len = strlen(sensorReadings3);

      strcat(fullMessage,sensorReadings3);
      msgIndex+=len;
      
      len = strlen(powerReadings);

      strcat(fullMessage,powerReadings);
      msgIndex+=len;

      char* checksum_c = getHash(fullMessage);
       
      len = strlen(checksum_c);
      
      fullMessage[msgIndex]='|';
      msgIndex++;
        
      strcat(fullMessage,checksum_c);
      msgIndex+=len;

      
      for (int i=0; i<msgIndex; i++) {
        Serial.write(fullMessage[i]);
      }
      
      Serial.write('\n');

      int ackResult = ackWait(fullMessage, msgIndex); //Waiting for acknowledge signal

      // if no ack, add to buffer
      if (ackResult == 1) {
        
      } else if (ackResult == 0) {
        handshakeCount++;
      } 
      

      memset(fullMessage, 0, sizeof(fullMessage));
     // if no ack, add to buffer
      
      xSemaphoreGive( xBufferMutex );
      xSemaphoreGive( xSerialSemaphoreSensor1 );
      xSemaphoreGive( xSerialSemaphorePower );
     }
  }
}
