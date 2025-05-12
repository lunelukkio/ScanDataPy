FROM ubuntu:24.04

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install required packages
RUN apt-get update && \
    apt-get install -y vim python3 python3-pip python3-venv python3-full libx11-xcb1 libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxkbcommon-x11-0 libgl1 libxcb-cursor0 && \
    apt-get clean && \
    apt -y update && \
    apt -y apt -y install libopencv-dev
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV DISPLAY=:0.0

# Install Python packages in the virtual environment
RUN pip3 install --no-cache-dir numpy pandas matplotlib torch torchvision pyqt6 psutil scipy pyqtgraph

# Command to keep container running
CMD ["/bin/bash"] 