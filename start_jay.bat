@ECHO OFF
cd /d "D:\Claude\bringatrailer-agent"
start http://localhost:8501
python -m streamlit run app.py --server.port=8501
