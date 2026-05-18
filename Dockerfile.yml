FROM python:3.11-slim

LABEL description="Dockerized Streamlit celebrity quiz"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1 curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY generate_dataset.py .

RUN mkdir -p dataset/images temp

RUN mkdir -p /root/.streamlit && printf "\
[general]\nemail = \"\"\n\n\
[server]\nheadless = true\nenableCORS = false\nenableXsrfProtection = false\n\n\
[theme]\nbase = \"dark\"\nbackgroundColor = \"#0d0d0d\"\nsecondaryBackgroundColor = \"#111111\"\ntextColor = \"#e8e0d0\"\nprimaryColor = \"#c8b89a\"\n\
" > /root/.streamlit/config.toml

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.address=0.0.0.0", \
            "--server.port=8501"]
