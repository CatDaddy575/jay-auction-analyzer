#!/usr/bin/env python
import subprocess
import webbrowser
import time
import os

os.chdir(r"D:\Claude\bringatrailer-agent")

# Open browser
webbrowser.open("http://localhost:8501")

# Wait a moment
time.sleep(2)

# Start Streamlit
subprocess.run(["streamlit", "run", "app.py"])
