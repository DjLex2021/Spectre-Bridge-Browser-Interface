#!/bin/bash

# Change directory to the web folder
cd /path/to/web

# Open the web browser to the specified URL
xdg-open http://localhost:80 &

# Execute the Python script
python3 /path/to/fetch_metrics.py

# Pause the script (Optional)
read -p "Press Enter to continue..."