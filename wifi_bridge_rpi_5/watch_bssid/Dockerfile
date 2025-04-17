FROM arm64v8/python:3.10-bullseye

# Set working directory
WORKDIR /app
COPY . .

# Install system packages
RUN apt-get update && apt-get install -y \
    iw \
    gcc \
    python3-dev \
    libcap2-bin \
    wget \
    && apt-get clean

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install gpiozero

# Install lgpio manually from Gadgetoid release (working on ARM64)
RUN wget https://github.com/Gadgetoid/PY_LGPIO/releases/download/0.2.2.0/lgpio-0.2.2.0.tar.gz && \
    tar -xvzf lgpio-0.2.2.0.tar.gz && \
    cd lgpio-0.2.2.0 && \
    python3 setup.py install && \
    cd .. && rm -rf lgpio-0.2.2.0*

# add to gpio group
RUN groupadd -g 997 gpio 2>/dev/null || true

# Run your app
CMD ["python3", "main.py"]
