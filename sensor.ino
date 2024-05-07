#include <ArduinoBLE.h>
#include <Wire.h>
#include <BH1750.h>

// Initialize the BH1750 object
BH1750 lightMeter;

// BLE Service and Characteristic
BLEService lightService("19B10010-E8F2-537E-4F6C-D104768A1214");
BLEFloatCharacteristic lightIntensityCharacteristic("19B10011-E8F2-537E-4F6C-D104768A1214", BLERead | BLENotify);

void setup() {
  Serial.begin(9600);
  Wire.begin();

  if (!lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println("Failed to initialize the BH1750 sensor!");
    while (1);
  }

  if (!BLE.begin()) {
    Serial.println("Starting BLE failed!");
    while (1);
  }

  BLE.setLocalName("Arduino Nano 33 IoT");
  BLE.setAdvertisedService(lightService);
  lightService.addCharacteristic(lightIntensityCharacteristic);
  BLE.addService(lightService);
  lightIntensityCharacteristic.writeValue(0.0);

  BLE.advertise();
  Serial.println("Bluetooth device is ready to go!");
}

void loop() {
  BLEDevice central = BLE.central();

  if (central) {
    Serial.print("Connected to Raspberry Pi: ");
    Serial.println(central.address());

    while (central.connected()) {
      float lux = lightMeter.readLightLevel();
      
      Serial.print("Light Intensity: ");
      Serial.print(lux);
      Serial.println(" lx");

      lightIntensityCharacteristic.writeValue(lux);

      delay(1000);
    }

    Serial.println("Disconnected from Raspberry Pi");
  }
}
