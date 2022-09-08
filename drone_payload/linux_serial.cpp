#ifndef __linux_serial_
#define __linux_serial_

#include <sys/ioctl.h>
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>

#define SERIAL_PORT "/dev/ttyACM1"

int serial_gimbal_open(int fd)
{

    struct termios tio; // serial communication setting
    int baudrate = B57600;
    int i;
    int len;
    int ret;
    int size;

    fd = open(SERIAL_PORT, O_RDWR); // open the device
    if (fd < 0) {
        printf("open error\n");
        return -1;
    }

    tio.c_cflag += CREAD;            // Receive enabled
    tio.c_cflag += CLOCAL;           // local line (no modem control)
    tio.c_cflag += CS8;              // data bit: 8bit
    tio.c_cflag += 0;                // stop bit: 1bit
    tio.c_cflag += 0;                // parity:None

    cfsetispeed(&tio, baudrate);
    cfsetospeed(&tio, baudrate);

    cfmakeraw(&tio); // RAW mode

    tcsetattr(fd, TCSANOW, &tio); // configure device

    ioctl(fd, TCSETS, &tio); // enable port settings

    return fd;

}

void serial_gimbal_close(int fd)
{
    close(fd);
}

#endif
