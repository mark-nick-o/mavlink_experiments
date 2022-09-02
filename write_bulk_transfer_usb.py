with open("/sys/module/usbcore/parameters/usbfs_memory_mb", "w") as f:
    print("150", file=f)
f.close()
