#!/bin/bash

# Load the values from the user_input.txt file
source user_input.txt

# Autostart is set to true
Autostart=true

# Function to install Chrome Remote Desktop
installCRD() {
  wget https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb
  dpkg --install chrome-remote-desktop_current_amd64.deb
  apt install --assume-yes --fix-broken
  echo "Chrome Remote Desktop Installed"
}

# Function to install Desktop Environment
installDesktopEnvironment() {
  export DEBIAN_FRONTEND=noninteractive
  apt install --assume-yes xfce4 desktop-base xfce4-terminal
  echo "exec /etc/X11/Xsession /usr/bin/xfce4-session" > /etc/chrome-remote-desktop-session
  apt remove --assume-yes gnome-terminal
  apt install --assume-yes xscreensaver
  sudo apt purge light-locker
  sudo apt install --reinstall xfce4-screensaver
  systemctl disable lightdm.service
  echo "XFCE4 Desktop Environment Installed"
}

# Function to install Google Chrome
installGoogleChrome() {
  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg --install google-chrome-stable_current_amd64.deb
  apt install --assume-yes --fix-broken
  echo "Google Chrome Installed"
}

# Function to install Telegram
installTelegram() {
  apt install --assume-yes telegram-desktop
  echo "Telegram Installed"
}

# Function to change wallpaper
changeWallpaper() {
  curl -s -L -k -o xfce-verticals.png https://gitlab.com/chamod12/changewallpaper-win10/-/raw/main/CachedImage_1024_768_POS4.jpg
  mv xfce-verticals.png /usr/share/backgrounds/xfce/
  echo "Wallpaper Changed"
}

# Function to install Qbittorrent
installQbittorrent() {
  sudo apt update
  sudo apt install -y qbittorrent
  echo "Qbittorrent Installed"
}

# Create new user
useradd -m $username
adduser $username sudo
echo "$username:$password" | sudo chpasswd
sed -i 's/\/bin\/sh/\/bin\/bash/g' /etc/passwd

# Install CRD, Desktop Environment, Google Chrome, Telegram, Wallpaper, and Qbittorrent
apt update
installCRD
installDesktopEnvironment
changeWallpaper
installGoogleChrome
installTelegram
installQbittorrent

# Autostart configuration
if $Autostart ; then
  mkdir -p /home/$username/.config/autostart
  link="www.youtube.com/@The_Disala"
  echo "[Desktop Entry]
Type=Application
Name=Colab
Exec=sh -c \"sensible-browser $link\"
Icon=
Comment=Open a predefined notebook at session signin.
X-GNOME-Autostart-enabled=true" > /home/$username/.config/autostart/colab.desktop
  chmod +x /home/$username/.config/autostart/colab.desktop
  chown $username:$username /home/$username/.config
fi

# Add user to chrome-remote-desktop group and start the service
adduser $username chrome-remote-desktop
su - $username -c "$CRD_SSH_Code --pin=$Pin"
service chrome-remote-desktop start

# Display final information
echo "..................................................................."
echo "Brought By The Disala"
echo "..................................................................."
echo "Log in PIN : $Pin"
echo "User Name : $username"
echo "User Pass : $password"
echo "..................................................................."
echo "Youtube Video Tutorial - https://youtu.be/xqpCQCJXKxU"
echo "..................................................................."

# Keep script running
while true; do sleep 1000; done