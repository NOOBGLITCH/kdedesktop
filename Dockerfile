FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ARG CRD_USERNAME
ARG CRD_PASSWORD
ARG CRD_PIN

ENV CRD_AUTOSTART=true

# Core deps
RUN apt update && apt install -y \
    sudo wget curl gnupg ca-certificates systemd \
    xfce4 desktop-base xfce4-terminal xscreensaver \
    qbittorrent telegram-desktop \
    && apt clean && rm -rf /var/lib/apt/lists/*

# Chrome Remote Desktop
RUN wget https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb && \
    dpkg -i chrome-remote-desktop_current_amd64.deb || apt -y -f install && \
    rm chrome-remote-desktop_current_amd64.deb

# Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt -y -f install && \
    rm google-chrome-stable_current_amd64.deb

# Create user, sudo, bash shell
RUN useradd -m ${CRD_USERNAME} && \
    echo "${CRD_USERNAME}:${CRD_PASSWORD}" | chpasswd && \
    adduser ${CRD_USERNAME} sudo && \
    sed -i 's/\/bin\/sh/\/bin\/bash/g' /etc/passwd

# Add user to CRD group
RUN adduser ${CRD_USERNAME} chrome-remote-desktop

# XFCE as CRD session
RUN bash -lc 'echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > /etc/chrome-remote-desktop-session' && \
    systemctl disable lightdm.service || true

# Nice wallpaper
RUN curl -s -L -o /usr/share/backgrounds/xfce/custom_wall.jpg \
    https://gitlab.com/chamod12/changewallpaper-win10/-/raw/main/CachedImage_1024_768_POS4.jpg || true

# Save encoded creds (Base64 + SHA256) for later retrieval
RUN USER_B64=$(echo -n "${CRD_USERNAME}" | base64) && \
    PASS_B64=$(echo -n "${CRD_PASSWORD}" | base64) && \
    USER_SHA=$(echo -n "${CRD_USERNAME}" | sha256sum | cut -d ' ' -f1) && \
    PASS_SHA=$(echo -n "${CRD_PASSWORD}" | sha256sum | cut -d ' ' -f1) && \
    echo "PIN: ${CRD_PIN}" > /root/crd_login.txt && \
    echo "USER_B64: ${USER_B64}" >> /root/crd_login.txt && \
    echo "PASS_B64: ${PASS_B64}" >> /root/crd_login.txt && \
    echo "USER_SHA256: ${USER_SHA}" >> /root/crd_login.txt && \
    echo "PASS_SHA256: ${PASS_SHA}" >> /root/crd_login.txt

# Copy entrypoint
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# No ports required for CRD
# CRD auth code is provided at runtime via env: CRD_SSH_CODE

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
