FROM python:3.10-slim-buster

# Switch to bash as the default shell
SHELL ["/bin/bash", "-c"]

# Set the working directory
WORKDIR /app

# Install Java, wget and other dependencies (required for Tika)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    default-jre \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create Tika directory and download Tika Server
RUN mkdir -p /opt/tika
WORKDIR /opt/tika
RUN wget https://archive.apache.org/dist/tika/2.8.0/tika-server-standard-2.8.0.jar
RUN ln -s tika-server-standard-2.8.0.jar tika-server.jar

# Start Tika server in the background at container startup
RUN echo '#!/bin/bash' > /opt/tika/start-tika.sh
RUN echo 'java -jar /opt/tika/tika-server.jar --host=0.0.0.0 --port=9998 &' >> /opt/tika/start-tika.sh
RUN chmod +x /opt/tika/start-tika.sh

# Update package lists and install unzip
RUN apt-get update && apt-get install -y ffmpeg

# Return to app directory
WORKDIR /app

# Install UV for faster dependency management.
RUN pip install --no-cache-dir uv

# Set the working directory for the application.
WORKDIR /app

# Copy project files.
COPY backend ./backend
COPY backend/pyproject.toml ./pyproject.toml

# Create and activate a virtual environment using UV.
RUN uv venv .venv
RUN . /app/.venv/bin/activate && uv pip install -e .

# Expose the port
EXPOSE 8005

# Set environment variables for Tika
ENV TIKA_SERVER_ENDPOINT=http://localhost:9998

# Command to run the FastAPI application with the activated venv
ENTRYPOINT ["/bin/bash", "-c", "/opt/tika/start-tika.sh && source /app/.venv/bin/activate && exec \"$@\"", "-s"]
CMD ["uvicorn", "backend.doc_api:app", "--host", "0.0.0.0", "--port", "8005"]