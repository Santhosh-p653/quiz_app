FROM python:3.11-slim

LABEL description="Streamlit Celebrity Quiz App"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1 curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# IMPORTANT: we DO NOT generate dataset in Docker
# dataset is mounted from host

RUN mkdir -p /root/.streamlit && printf "\
[general]\nemail = \"\"\n\n\
[server]\nheadless = true\nenableCORS = false\nenableXsrfProtection = false\n\n\
[theme]\nbase = \"dark\"\nbackgroundColor = \"#0d0d0d\"\nsecondaryBackgroundColor = \"#111111\"\ntextColor = \"#e8e0d0\"\nprimaryColor = \"#c8b89a\"\n\
" > /root/.streamlit/config.toml

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.address=0.0.0.0", \
            "--server.port=8501"]