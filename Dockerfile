FROM python:3.10-slim

WORKDIR /app
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y python3-dev

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run setup script
RUN python setup.py

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
