@echo off
cd /d "D:\Claude\bringatrailer-agent"
start http://localhost:8501
start "" streamlit run app.py
exit
