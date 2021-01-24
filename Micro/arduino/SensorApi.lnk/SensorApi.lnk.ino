int fsrreading; //Variable to store FSR value
int fsrreading2; //Variable to store FSR value

#define fsrpin A0
#define fsrpin2 A4

#include <Arduino_JSON.h>

void setup() {
  // put your setup code here, to run once:
Serial.begin(115200);

}

void loop() {
  // put your main code here, to run repeatedly:
fsrreading = analogRead(fsrpin);
fsrreading2 = analogRead(fsrpin2);


//int inputValues [10];

//for(i=0; i<10; i++){
//  
//inputValues[i] = analogRead(fsrpin);
//delay(1);
//}

  // Print the fsrreading in the serial monitor:
  // Print the string "Analog reading = ".
//  Serial.print("Analog reading = ");
  // Print the fsrreading:
//  Serial.print(fsrreading);
  // We can set some threshholds to display how much pressure is roughly applied:
if (fsrreading > 800) {
  JSONVar myObject;
  myObject["step"] = 1;
  myObject["val"] = 1;
  String jsonString = JSON.stringify(myObject);
  Serial.println(jsonString);
  while(analogRead(fsrpin)>400){
    
    }
    myObject["val"] = 0;
    jsonString = JSON.stringify(myObject);
    Serial.println(jsonString);
  }
if (fsrreading2 > 800) {
  JSONVar myObject;
  myObject["step"] = 2;
  myObject["val"] = 1;
  String jsonString = JSON.stringify(myObject);
  Serial.println(jsonString);
  while(analogRead(fsrpin2)>400){
    
    }
    myObject["val"] = 0;
    jsonString = JSON.stringify(myObject);
    Serial.println(jsonString);
  }
    

//  delay(500); //Delay 500 ms.
}
