import usb.core
import usb.util
import time

USB_IF = 0
USB_TIMEOUT = 5

# read output from `sudo lsusb` and find your USB remote
# mine is X10 Wireless Technology, Inc. X10 Receiver
USB_VENDOR = 0x0bc7
USB_PRODUCT = 0x0004

dev = usb.core.find(idVendor=USB_VENDOR, idProduct=USB_PRODUCT)
#print(dev)
endpoint = dev[0][(0,0)][0]

if dev.is_kernel_driver_active(USB_IF) is True:
    dev.detach_kernel_driver(USB_IF)

usb.util.claim_interface(dev, USB_IF)

while True:
    control = None

    try:
        control = dev.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize, USB_TIMEOUT)
        print(control)
    except Exception as e:
        print("waiting on Cartman again!")

    time.sleep(1)
