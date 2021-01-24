#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
//
//#include <Filters.h>
//#include <Filters/Butterworth.hpp>
//#include <Filters/Notch.hpp>
//#include <Filters/SMA.hpp>

// Sampling Parameters
const double sampling_f = 500; // Hz
const int sampling_d = min(1, 1000/sampling_f);

//// Notch Filter
//const double notch_f = 50; // Hz
//const double norm_notch = 2 * notch_f / sampling_f;
//auto filter2 = simpleNotchFIR(norm_notch);
//auto filter3 = simpleNotchFIR(2 * norm_notch);


// Base Signal Filtering
//const double H_f = 60; // Hz
//const double L_f = 0.5; // Hz
//const double norm_H = 2 * H_f / sampling_f;
//const double norm_L = 2 * L_f / sampling_f;
//auto filter0 = butter<3>(norm_L);
//auto filter1 = butter<3>(norm_H);

// Timer
unsigned long t0 = millis();

// Differentiation
float delta;

// Last ECG read
float last = 0;

int IN_MESSAGE = 128;
String incoming;
int fanss[] = {2,3,4,5};
int fan1, fan2, fan3, fan4;
Adafruit_BNO055 bno = Adafruit_BNO055(55);
DynamicJsonDocument doc(1024);
DynamicJsonDocument out_doc(1024);

void set_fan(int pin_int, int on) {
  if (on == 1){
    digitalWrite(pin_int, HIGH);
  } else {
    digitalWrite(pin_int, LOW);
  }
}

void setup() {
    // fans
    pinMode(2, OUTPUT);
    pinMode(3, OUTPUT);
    pinMode(4, OUTPUT);
    pinMode(5, OUTPUT);

    // ECG lom lop for signal control
    pinMode(39, INPUT);
    pinMode(38, INPUT);
    
    Serial.begin(115200);
    
    if (!bno.begin()) {
      Serial.print("NO BNO055 Detected!");
      while(1);
    }
    bno.setExtCrystalUse(true);
    while (!Serial){}
    

}

void loop() {
  // Serial Reading
  if (Serial.available() > 0) {
    deserializeJson(doc, Serial);
    if (!doc["fan"].isNull()){
      for(int i = 0;i<4;i++){
//        int temp[5] = doc["fan"];
//        Serial.println(i);
        
        if (doc["fan"][i] == 1){
          
            digitalWrite(fanss[i], HIGH);
          } else {
            digitalWrite(fanss[i], LOW);
                  }
        
        }
//      set_fan(doc["fan"][0], doc["fan"][1]);
    }
  }

  // Serial Write
  if (millis() - t0 > sampling_d){
    t0 = millis();
//    auto ECG_read = analogRead(A0);
//    auto lower = filter0(ECG_read);
//    auto f_ECG_read = filter3(filter2(filter1(ECG_read - lower)));
//    delta = (f_ECG_read - last)/sampling_d;
    
    sensors_event_t event; 
    bno.getEvent(&event);
    out_doc["time"] = millis();
//    out_doc["ECG"] = f_ECG_read;
//    out_doc["lom"] = digitalRead(39);
//    out_doc["lop"] = digitalRead(38);
//    out_doc["delta"] = delta;
    out_doc["pressure1"] = 1023 - analogRead(A1);
    out_doc["pressure2"] = 1023 - analogRead(A2);
    out_doc["x"] = event.orientation.x;
    out_doc["y"] = event.orientation.y;
    out_doc["z"] = event.orientation.z;

    serializeJson(out_doc, Serial);
    Serial.write("\n");
//    last = f_ECG_read;
  }
}
