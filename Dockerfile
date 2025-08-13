FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt update && apt install -y \
    sudo curl wget gnupg2 ca-certificates python3 python3-pip systemd \
    xfce4 desktop-base xfce4-terminal xscreensaver \
    qbittorrent telegram-desktop \
    && apt clean && rm -rf /var/lib/apt/lists/*

# Add Chrome Remote Desktop and Google Chrome
RUN wget https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb && \
    dpkg -i chrome-remote-desktop_current_amd64.deb || apt install -f -y && \
    rm chrome-remote-desktop_current_amd64.deb && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt install -f -y && \
    rm google-chrome-stable_current_amd64.deb

# Copy setup script
COPY setup_crd.py /setup_crd.py
RUN chmod +x /setup_crd.py

CMD ["python3", "/setup_crd.py"]
