# Docker Environment Setup Guide

This repository contains a Dockerfile for building a Docker image with Python environment based on Ubuntu 24.04 LTS.

## Requirements

- Docker installed on your system

## Building the Docker Image

Run the following command in the directory containing the Dockerfile to build the image:

```bash
docker build -t scandata-py .
```

## Running the Container

To start a new container from the built image:

```bash
docker run --name scandata-container -it scandata-py
```

## Restarting the Container

To restart the container after stopping it:

```bash
docker start -i scandata-container
```

## Installed Packages

This Docker image comes with the following packages installed:

- Ubuntu 24.04 LTS (Noble Numbat)
- vim
- Python 3
- Python virtual environment (in /opt/venv)
- X11/XCB libraries for GUI support (e.g., libx11-xcb1, libxcb-xinerama0)
- Python packages installed in the virtual environment:
  - numpy
  - pandas
  - matplotlib
  - torch
  - torchvision
  - pyqt6

> Note: Due to PEP 668 in Ubuntu 24.04, Python packages are installed in a virtual environment rather than system-wide.

## Running GUI Applications (e.g., PyQt6)

To run GUI applications from within the container that require an X server (like those built with PyQt6), you need to ensure the container can connect to your host's X server.

1.  **X Server on Host:** Make sure you have an X server running on your host machine.
    *   **Windows:** Use WSLg (Windows Subsystem for Linux GUI) if you are running Docker Desktop with the WSL 2 backend (recommended), or install a third-party X server like VcXsrv or Xming.
    *   **Linux:** X server is typically available by default.
    *   **macOS:** XQuartz is a common X server.

2.  **DISPLAY Environment Variable:** The `Dockerfile` already sets `ENV DISPLAY=:0.0`. This usually works for WSLg and Linux hosts. For other X servers, you might need to adjust this or pass the `DISPLAY` variable when running the container. For example:
    ```bash
    # For Linux/macOS, find your IP (e.g., using ifconfig or ip addr)
    # and replace YOUR_HOST_IP.
    # For some setups, 'host.docker.internal:0.0' might work.
    docker run --name scandata-container -it -e DISPLAY=YOUR_HOST_IP:0.0 -v /tmp/.X11-unix:/tmp/.X11-unix scandata-py
    ```
    For WSLg, usually no extra `DISPLAY` configuration is needed in the `docker run` command if `ENV DISPLAY=:0.0` is set in the Dockerfile.

3.  **X Server Access Control:** Ensure your X server allows connections from the Docker container. For VcXsrv on Windows, you might need to disable access control (e.g., by unchecking "Disable access control" in XLaunch).

## Sharing Files with the Host

To mount a host directory to the container for file sharing:

```bash
docker run --name scandata -v /host/path:/app -it scandata-py
```

For Windows:

```bash
docker run --name scandata -v C:\host\path:/app -it scandata-py
``` 