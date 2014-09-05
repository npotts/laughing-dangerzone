Socat Virtual Serial Port Pair 
==============================

This helpful script creates effectively a virtual serial port (VSP) under Linux.  It uses socat to create two ptys and imbue them with serial port qualities.  They are not exactly serial ports, but are close enough for serial port development.

Functionally it just creates 2 pairs via commands similar to 


``` sh
socat PTY,link=/tmp/in,raw,echo=0  PTY,link=/tmp/out,raw,echo=0 &
```
