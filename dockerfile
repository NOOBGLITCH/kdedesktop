FROM ubuntu:latest

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV USER=user
ENV PASSWORD=root
ENV VNC_PASSWORD=password
ENV DISPLAY=:1
ENV RESOLUTION=1280x720

# Set working directory
WORKDIR /app

# Install system dependencies and KDE Plasma
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --fix-broken && \
    apt-get install -y \
    wget \
    curl \
    sudo \
    x11vnc \
    xvfb \
    supervisor \
    net-tools \
    procps \
    firefox \
    git \
    nano \
    dbus-x11 \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Install KDE Standard strictly
RUN apt-get update && apt-get install -y \
    kde-standard \
    && rm -rf /var/lib/apt/lists/*

# Install noVNC and websockify
RUN wget -q https://github.com/novnc/noVNC/archive/refs/heads/main.tar.gz -O /tmp/novnc.tar.gz \
    && tar -xzf /tmp/novnc.tar.gz -C /opt/ \
    && mv /opt/noVNC-main /opt/novnc \
    && wget -q https://github.com/novnc/websockify/archive/refs/heads/main.tar.gz -O /tmp/websockify.tar.gz \
    && tar -xzf /tmp/websockify.tar.gz -C /opt/ \
    && mv /opt/websockify-main /opt/websockify \
    && rm -f /tmp/novnc.tar.gz /tmp/websockify.tar.gz

# Create user and set password
RUN useradd -m -s /bin/bash $USER \
    && echo "$USER:$PASSWORD" | chpasswd \
    && usermod -aG sudo $USER \
    && echo "$USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb \
    && apt-get install -y /tmp/chrome.deb \
    && rm -f /tmp/chrome.deb

# Configure VNC
RUN mkdir -p /home/$USER/.vnc \
    && echo "$VNC_PASSWORD" | x11vnc -storepasswd - \
    && chown -R $USER:$USER /home/$USER/.vnc

# Set KDE defaults
RUN mkdir -p /home/$USER/.config \
    && chown -R $USER:$USER /home/$USER/.config

# Create supervisord.conf
RUN cat > /etc/supervisor/conf.d/supervisord.conf << 'EOF'
[supervisord]
nodaemon=true
logfile=/var/log/supervisord.log
pidfile=/var/run/supervisord.pid
childlogdir=/var/log/

[program:xvfb]
command=Xvfb :1 -screen 0 1280x720x24
autorestart=true
user=user

[program:x11vnc]
command=x11vnc -display :1 -xkb -forever -shared -repeat -listen localhost -rfbauth /home/user/.vnc/passwd
autorestart=true
user=user

[program:kde]
command=/usr/bin/startplasma-x11
environment=DISPLAY=:1
autorestart=true
user=user

[program:dbus]
command=/usr/bin/dbus-run-session -- /usr/bin/startplasma-x11
environment=DISPLAY=:1
autorestart=true
user=user

[program:novnc]
command=/opt/websockify/run --web /opt/novnc 6080 localhost:5900
autorestart=true
user=user

[program:web]
command=python3 -m http.server 8080 --directory /opt/novnc
autorestart=true
user=user
EOF

# Create start.sh
RUN cat > /app/start.sh << 'EOF'
#!/bin/bash

# Start DBus
sudo service dbus start

# Start supervisord
sudo /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf &

# Wait for services to start
sleep 10

# Get container IP
IP=$(hostname -i)

echo "================================================"
echo "🎯 KDE Plasma Desktop Environment"
echo "🌐 noVNC Access URLs:"
echo "   Web Interface: http://$IP:8080/vnc.html"
echo "   Direct VNC:    $IP:5900"
echo ""
echo "🔧 Connection Details:"
echo "   VNC Password: $VNC_PASSWORD"
echo "   User: $USER"
echo "   Password: $PASSWORD"
echo ""
echo "🚀 Ready to use!"
echo "================================================"

# Keep container running
wait
EOF

RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 8080  # noVNC web interface
EXPOSE 5900  # VNC server
EXPOSE 6080  # noVNC alternative port

# Set up health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD netstat -an | grep 8080 > /dev/null || exit 1

# Set the user
USER $USER

# Start services
CMD ["/app/start.sh"]