# Use a lightweight Python image
FROM python:3.10-slim-bookworm



LABEL org.opencontainers.image.title="CipherElite"
LABEL org.opencontainers.image.description="Advanced Telegram Userbot"
LABEL org.opencontainers.image.authors="Rishabh"
LABEL org.opencontainers.image.source="https://github.com/rishabhops/CipherElite"


RUN echo "====================================" && \
    echo "  ____ _       _                  " && \
    echo " / ___(_)_ __ | |__   ___ _ __    " && \
    echo "| |   | | '_ \| '_ \ / _ \ '__|   " && \
    echo "| |___| | |_) | | | |  __/ |      " && \
    echo " \____|_| .__/|_| |_|\___|_|      " && \
    echo "        |_|                       " && \
    echo " _____ _ _ _                      " && \
    echo "| ____| (_) |_ ___                " && \
    echo "|  _| | | | __/ _ \               " && \
    echo "| |___| | | ||  __/               " && \
    echo "|_____|_|_|\__\___|               " && \
    echo "====================================" && \
    echo "   🚀 C I P H E R  E L I T E 🚀     " && \
    echo "       By: Rishabh | Thanos Pro     " && \
    echo "===================================="

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN echo "⚙️ Preparing System Dependencies..."
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python modules
COPY requirements.txt .
RUN echo "📦 Installing Python Modules..."
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of your bot's code into the container
COPY . .

# Final success message before starting
RUN echo "✅ Build Complete! Ready to launch."

# Command to start the bot
CMD ["python3", "main.py"]
