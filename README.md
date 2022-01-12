This is WIP and under test use only if you want to contribute its not a complete working set


# mavlink_experiments
Simple Qt app for experiments with MAVLink protocol and testing

## Dependencies
* C++11 compatible compiler
* Qt5 development modules: Core Network SerialPort
* CMake 2.8.11 or greater
  
### Ubuntu users can use apt:
```bash
sudo apt update
sudo apt install libqt5positioning5
sudo apt-get install g++ cmake qtbase5-dev libqt5serialport5-dev qtpositioning5-dev libqt5svg5-dev
```
### Fedora/CentOS/RHEL users can use dnf:
```bash
sudo dnf install g++ cmake qt5-devel qt5-qtserialbus-devel qt5-qtlocation qtpositioning5-dev libqt5svg5-dev
```
## Cloning
```bash
git clone --recurse-submodules https://github.com/mark-nick-o/mavlink_experiments
```
Don't forget submodules

## Building
```bash
mkdir build
cd build
cmake ..
make
```
I have added the camera protocol for testing.. WIP (becasuse I might be preferning to use the driver as python due to the requests library being more suitable for the micasense camera, this will at sometime be checked when i have spare time)
https://mavlink.io/en/services/camera.html

At present I have added a class for control of the micaSense camera RedEye/RedEdge/Altim This is working via http over Wifi 
and some mavlink communication scripts for testing using pymavlink and mavlink-routerd as well as scripts to run them via crontab to keep mavlink-routerd running all the time even when it is killed.

This is for use at present on raspberry Pi 
