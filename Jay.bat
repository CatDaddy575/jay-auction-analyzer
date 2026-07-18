@echo off
start http://localhost:8501
cd /d "D:\Claude\bringatrailer-agent"
streamlit run app.py
