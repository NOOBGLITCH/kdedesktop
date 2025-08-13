FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Build arguments from GitLab CI/CD variables
ARG CRD_USERNAME
ARG CRD_PASSWORD
ARG CRD_PIN
ARG CRD_SSH_CODE

# Install base dependencies
RUN apt update && apt install -y \
    sudo wget curl gnupg ca-certificates systemd coreutils \
    xfce4 desktop-base xfce4-terminal xscreensaver \
    qbittorrent telegram-desktop \
    && apt clean && rm -rf /var/lib/apt/lists/*

# Install Chrome Remote Desktop
RUN wget https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb && \
    dpkg --install chrome-remote-desktop_current_amd64.deb || true && \
    apt install --assume-yes --fix-broken && \
    rm chrome-remote-desktop_current_amd64.deb

# Install Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg --install google-chrome-stable_current_amd64.deb || true && \
    apt install --assume-yes --fix-broken && \
    rm google-chrome-stable_current_amd64.deb

# Change wallpaper (non-fatal if URL fails)
RUN curl -s -L -o /usr/share/backgrounds/xfce/custom_wall.jpg \
    https://gitlab.com/chamod12/changewallpaper-win10/-/raw/main/CachedImage_1024_768_POS4.jpg || true

# Create user & set password
RUN useradd -m ${CRD_USERNAME} && \
    echo "${CRD_USERNAME}:${CRD_PASSWORD}" | chpasswd && \
    adduser ${CRD_USERNAME} sudo && \
    chsh -s /bin/bash ${CRD_USERNAME} && \
    \
    # Encode credentials
    USER_B64=$(echo -n "${CRD_USERNAME}" | base64) && \
    PASS_B64=$(echo -n "${CRD_PASSWORD}" | base64) && \
    USER_SHA=$(echo -n "${CRD_USERNAME}" | sha256sum | cut -d ' ' -f1) && \
    PASS_SHA=$(echo -n "${CRD_PASSWORD}" | sha256sum | cut -d ' ' -f1) && \
    \
    # Save encoded credentials to a file
    echo "PIN: ${CRD_PIN}" > /root/crd_login.txt && \
    echo "USER_B64: ${USER_B64}" >> /root/crd_login.txt && \
    echo "PASS_B64: ${PASS_B64}" >> /root/crd_login.txt && \
    echo "USER_SHA256: ${USER_SHA}" >> /root/crd_login.txt && \
    echo "PASS_SHA256: ${PASS_SHA}" >> /root/crd_login.txt

# Configure CRD session
RUN bash -c 'echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > /etc/chrome-remote-desktop-session' && \
    systemctl disable lightdm.service || true

# Add user to CRD group and run setup command
RUN adduser ${CRD_USERNAME} chrome-remote-desktop && \
    su - ${CRD_USERNAME} -c "${CRD_SSH_CODE} --pin=${CRD_PIN}" || true

# Expose CRD web port
EXPOSE 443

# Start CRD on container boot
CMD service chrome-remote-desktop start && tail -f /dev/null
