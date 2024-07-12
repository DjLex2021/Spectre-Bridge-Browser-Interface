# Spectre Bridge Browser Interface (original by HNP Hotfix)

Modified version of "HNP Hotfix Spectre Bridge Browser Interface"
- Web server port is 8088
- Automatic page reload disabled
- Table view of devices
- Additional list of inactive devices
- Record date and time of last block found
- Record date and time of last block seen
- Split device name and IP
- Display number of active & inactive devices
- Display overall hashrate
- Display device hashrate
- Display device uptime


![Spectre Bridge Browser Interface](https://github.com/user-attachments/assets/1f074ad0-e0db-4d05-a2b3-683275d237e9)


Need Python:
[Windows](https://www.python.org/downloads/windows/)
[Linux](https://www.python.org/downloads/source/)


## Installation
Install Python and extract the downloaded ZIP file

## Run spr_brigde and output to file
Screen
```bash
screen -S spr_bridge -L -Logfile /path/to/spr_bridge_output_txtfile -d -m /path/to/spr_bridge
```

CLI
```bash
/path/to/spr_bridge >> /path/to/spr_bridge_output_txtfile 2>&1 &
```

## Usage of Browser Interface Script
Run the script:
```bash
python3 fetch_metrics.py /path/to/spr_bridge_output_txtfile
```


You can create a startup script and run it via crontabs:
```bash
#!/bin/bash
if ps aux | grep 'python3 fetch_metrics.py' | grep -v grep; then
    exit 1
else
    cd /path/to/fetch_metrics_script
    /usr/bin/python3 fetch_metrics.py
fi
```

Open the Browser and type in the address: localhost:8088

If you want to open it from other devices in the network: <IP>:8088
