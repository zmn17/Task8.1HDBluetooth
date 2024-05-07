import struct
import RPi.GPIO as GPIO
from bluepy.btle import Peripheral, Scanner, DefaultDelegate
import time

led_pin = 17
buzzer_pin = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(buzzer_pin, GPIO.OUT)

lux = None

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

try:
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(10.0)

    nano_address = None
    for dev in devices:
        for (adtype, desc, value) in dev.getScanData():
            if value == 'Arduino Nano 33 IoT':
                nano_address = dev.addr
                break
        if nano_address:
            break

    if nano_address:
        print("Found Arduino Nano 33 IoT at address", nano_address)
        nano = Peripheral(nano_address)
        try:
            service = nano.getServiceByUUID("19B10010-E8F2-537E-4F6C-D104768A1214")
            luxCharacteristic = service.getCharacteristics("19B10011-E8F2-537E-4F6C-D104768A1214")[0]

            while True:
                lux_bytes = luxCharacteristic.read()
                lux = struct.unpack('f', lux_bytes)[0]
                print(f"Light Intensity: {lux:.2f} lux")

                if lux <= 5:
                    GPIO.output(buzzer_pin, GPIO.HIGH)
                    time.sleep(0.2)
                    GPIO.output(buzzer_pin, GPIO.LOW)
                    GPIO.output(led_pin, GPIO.HIGH)
                    time.sleep(0.2)
                    GPIO.output(led_pin, GPIO.LOW)

                elif lux <= 10:
                    GPIO.output(led_pin, GPIO.HIGH)
                    time.sleep(0.5)
                    GPIO.output(led_pin, GPIO.LOW)

                time.sleep(1)

        finally:
            nano.disconnect()
            print("Disconnected")
    else:
        print("Arduino Nano 33 IoT not found")
except Exception as e:
    print("An error occurred:", e)
finally:
    GPIO.cleanup()

