# NTRIP Line Client
The NTRIP line client packet reads NMEA data from the serial port and receives RTCM data from the NTRIP server with this NMEA data. It then writes this RTCM data to the serial port.  

<br />

## NTRIP Client Usage
### 1. Bash Script
Configure the `start_ntripclient.sh` and run below command on terminal:
```
./start_ntripclient.sh
```

<br />

### 2. Line Arguments
Call the program with following arguments:  
```
python3 ntripclient -p serial_port -b serial_baudrate -S ntrip_server ...
```
**Serial Communication Arguments**
```
-p  --serial_port      Serial port name  
-b  --serial_baudrate  Serial baudrate  
-t  --serial_timeout   Serial timeout
```
**NTRIP Client Arguments**
```
-S  --ntrip_server     NTRIP server name or address  
-P  --ntrip_port       NTRIP server port number  
-V  --ntrip_version    NTRIP version  
    Valid versions:
        0: No specified version
        1: Ntrip/1.0  
        2: Ntrip/2.0  

-M  --mountpoint       Mount point  
-U  --username         Username  
-W  --password         Password  
```

<br />  

### Contact
[![LinkedIn Badge](https://img.shields.io/badge/LinkedIn-Profile-informational?style=flat&logo=linkedin&logoColor=white&color=0D76A8)](https://www.linkedin.com/in/abdullahdangac/)  
