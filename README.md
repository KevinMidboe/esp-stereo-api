# esp-stereo-api
Using micropython on a esp8266 to create an api endpoint for controlling my stereo


# Setup
> Setup is done on MacOS 10.14.3

### Flashing the chip with micropython
We need to start by flashing micropython to our esp8266. Download micropython from [http://micropython.org/download#esp8266](http://micropython.org/download#esp8266).  

Next we need to install esptool from espressif. This is a python-based, platform independent, utility to communicate with the ORM bootloader in the Espressif ESP8266 & ESP32 chips. There might be other great tools for flashing these chips out there aswell. Check out their [github page](https://github.com/espressif/esptool) for updated installation instructions.  

Now we can flash our chip with the downloaded binary file. First find your esp chip:  
```
$ ls /dev/tty.usb*
```

I run esp8266 tool from the source files in a virtualenv, your command might veary slightly:  
```
$ env/bin/python3 esptool.py -p /dev/tty.usbserial-1460 write_flash -z 0x0000 ~/firmware-combined.bin
```

Note the *tty.usbserial-1460* device name and the path *../firmware-combined.bin* for the micropython binary.


### Install

Requirements:
 - ampy [https://github.com/pycampers/ampy](https://github.com/pycampers/ampy) / `pip install adafruit-ampy`

Transfer boot script:  
```
$ ampy -p /dev/tty.usbserial-1460 put boot.py
```

Again note the *tty.usbeserial-1460* device name.

### Configure

Temperary requirement - set PSID and password for network to connect to. Fill in the empty strings `sta_if.connect('', '')` on line 44 in boot.py.
