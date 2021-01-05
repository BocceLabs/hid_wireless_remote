# Working with Remotes

I had an ATI Remote Wonder Plus laying around in the closet from approximately 2003.  

![](ati_remote_wonder_plus.JPG?raw=true)

The goal was to get it to work with Python so I can use it for controlling a PyQT app.

Step 1 was to get it to communicate.

# Poking around online

I investigated the following:

* lirc
* pylirc

Neither worked for me after trying and banging my head on the desk.

# Getting it to work at the USB.core level

I then came across a good writeup on Pimoroni:

[Controlling Your Robot: USB HID/Wireless Keyboards](https://learn.pimoroni.com/tutorial/robots/controlling-your-robot-wireless-keyboard) - Pimoroni.com

While the title is misleading, my USB RF remote is an "HID" device meaning that it "acts" like a keyboard.

Following the instructions there:

```
# install libusb
sudo apt-get install libusb-dev

# clone PyUSB
git clone https://github.com/walac/pyusb
cd pyusb
sudo python setup.py install

# find your HID device
sudo lsusb

# my device is 0bc7:0004 X10 Wireless Technology, Inc. X10 Receiver
```

I then used their exact example script but with a `1` second delay instead of `0.01` second delay:

```
# imports
import usb.core
import usb.util
import time

# set constants
USB_IF      = 0 # Interface
USB_TIMEOUT = 5 # Timeout in MS

# set device info
USB_VENDOR  = 0x0bc7 # Replace with info from `lsusb` command
USB_PRODUCT = 0x0004 # Replace with info from `lsusb` command

# initialize the device
dev = usb.core.find(idVendor=USB_VENDOR, idProduct=USB_PRODUCT)

# set an endpoint
endpoint = dev[0][(0,0)][0]

# detach from the kernel driver so we
# can use the device directly
if dev.is_kernel_driver_active(USB_IF) is True:
  dev.detach_kernel_driver(USB_IF)

# claim the device here for our example
usb.util.claim_interface(dev, USB_IF)

# infinitely loop
while True:
    # set the control back to `None`
    control = None

    # try to read a value from the HID device and print the result
    try:
        control = dev.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize, USB_TIMEOUT)
        print(control)
    # don't worry if there's a failure (pass without handling the exception)
    except:
        pass

    # wait 1 second before trying again
    time.sleep(1) # Let CTRL+C actually exit
```


# Setting a udev rule

You may wish to set a udev rule.

[Hardware Hump Day: USB Device Rules on Raspberry Pi](https://www.sparkfun.com/news/2332) - Sparkfun.com
	
	
Plug/unplug your HID wireless receiver from USB and then check the device messages:

```
dmesg
```

You can also get similar information from:

```
lsusb
```

I extracted enough information from both of the above to build the following rule:

```
ACTION=="add", ATTRS{product}=="USB Receiver", ATTRS{idVendor}=="0bc7", ATTRS{idProduct}=="0004", SYMLINK+="ATI_Remote"
```

Paste that in a rules file such as follows on a Raspberry Pi:

```
nano /etc/udev/rules.d/10-ati-remote.rules
```

Reboot your Raspberry Pi (might not be necessary, but I recommend it).

Now when I plug/unplug my device and list devices:

```
ls /dev
```

It is listed as `ATI_Remote`.  

You can use this information to create a USB rule so you don't need to use the sudo command to run the Python script.

# Creating a device rule for your user

List the long information for your device:

```
ls -l /dev/ATI_Remote
```

Mine indicates that the remote is part of the `root` group.  This might be risky from a security standpoint (suggestions are welcome), but I'm adding the username to the `root` group.

```
# add pi user to the root group
usermod -a -G root pi
```

Another option (haven't tried) is to add another (or change the) rule for our device to change its permissions (you should recognize the format of this rule from above):

```
SUBSYSTEM=="block", ATTRS{product}=="USB Receiver", ATTRS{idVendor}=="0bc7", ATTRS{idProduct}=="0004", ACTION=="add", RUN+="/bin/setfacl -m u:pi:rw- /dev/$name"
```

# Keymap

You can build a keymap based on the data you receive in the test program.  Keep a pen and paper handy as you map your remote.  Or better yet, take a picture of the remote and mark it up with a drawing app on your computer.

There might be an existing keymap available for your device. Poke around online.

# Conclusion

Be persistent and you should be able to get your HID device added/working/tested. 