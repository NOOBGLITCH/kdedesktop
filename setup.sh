#!/bin/bash

# -------------------- User inputs / config --------------------
echo -n "Google CRD SSH Code: "
read CRD_SSH_Code
CRD_SSH_Code=$(echo "$CRD_SSH_Code" | tr -d '[:space:]')
username="user"       # change if you want a different default
password="root"       # change default password here
Pin=123456            # must be >= 6 digits
Autostart=true        # create autostart .desktop entry
KeepAlive=true        # if true, script will block at end (to keep session alive)
# --------------------------------------------------------------

# Function to run commands with error checking
run() {
    echo "> $*"
    if ! "$@"; then
        echo "❌ Command failed: $*"
        exit 1
    fi
}

# Function to run shell commands
run_shell() {
    echo "> $1"
    if ! eval "$1"; then
        echo "❌ Shell command failed: $1"
        exit 1
    fi
}

# Install apt packages with retry for broken dependencies
install_with_retry() {
    if ! apt install -y "$@"; then
        echo "⚠️ Fixing broken dependencies and retrying..."
        apt install -y --fix-broken
        apt install -y "$@"
    fi
}

ensure_user() {
    if id "$1" &>/dev/null; then
        echo "User '$1' already exists."
    else
        echo "Creating user '$1'..."
        useradd -m "$1"
    fi
    usermod -aG sudo "$1"
    echo "$1:$password" | chpasswd
    sed -i "s:/bin/sh:/bin/bash:g" /etc/passwd
}

installCRD() {
    echo "Installing Chrome Remote Desktop .deb and dependencies..."
    wget -q "https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb" -O "/tmp/chrome-remote-desktop_current_amd64.deb"
    
    if ! dpkg --install "/tmp/chrome-remote-desktop_current_amd64.deb"; then
        apt install -y --fix-broken
        dpkg --install "/tmp/chrome-remote-desktop_current_amd64.deb"
    fi
    echo "✅ Chrome Remote Desktop package installed."
}

installDesktopEnvironment() {
    echo "Installing KDE (kde-standard)... This can take a while."
    export DEBIAN_FRONTEND=noninteractive
    apt update -y
    install_with_retry kde-standard -y
    echo "exec /usr/bin/startplasma-x11" > /etc/chrome-remote-desktop-session
    
    # Try to remove optional packages (ignore errors if they don't exist)
    apt remove --assume-yes gnome-terminal light-locker 2>/dev/null || echo "Note: some optional packages could not be removed."
    
    # Try to disable sddm service
    systemctl disable sddm.service 2>/dev/null || echo "sddm.service not found or could not be disabled."
    
    echo "✅ KDE Plasma installed and configured for Chrome Remote Desktop."
}

installGoogleChrome() {
    echo "Downloading and running browser setup..."
    
    # Download the setup script from GitHub
    wget -q "https://raw.githubusercontent.com/NOOBGLITCH/kdedesktop/refs/heads/main/setup.sh" -O "/tmp/setup.sh"
    
    # Make it executable and run with bash
    chmod +x "/tmp/setup.sh"
    bash "/tmp/setup.sh"
    
    echo "✅ Browser setup completed."
}

finish() {
    # Create autostart entry if enabled
    if [ "$Autostart" = "true" ]; then
        autostart_dir="/home/$1/.config/autostart"
        mkdir -p "$autostart_dir"
        link="https://github.com/NOOBGLITCH/kdedesktop"
        
        cat > "$autostart_dir/colab.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Colab
Exec=sh -c "sensible-browser $link"
Icon=
Comment=Open a predefined notebook at session signin.
X-GNOME-Autostart-enabled=true
EOF
        
        chmod +x "$autostart_dir/colab.desktop"
        chown -R "$1:$1" "/home/$1/.config"
        echo "✅ Autostart .desktop created."
    fi

    # Add user to chrome-remote-desktop group
    usermod -aG chrome-remote-desktop "$1" 2>/dev/null || echo "⚠️ Could not add user to chrome-remote-desktop group"

    # Run CRD registration if code provided
    if [ -n "$CRD_SSH_Code" ]; then
        command="$CRD_SSH_Code --pin=$Pin"
        su - "$1" -c "$command" || echo "⚠️ Running CRD registration command failed"
    else
        echo "⚠️ No CRD SSH code provided; skipping registration step."
    fi

    # Start chrome-remote-desktop service
    service chrome-remote-desktop start 2>/dev/null || echo "⚠️ Could not start chrome-remote-desktop service"

    echo ""
    echo ".........................................................."
    echo ".....Brought By The Disala................................"
    echo ".........................................................."
    echo "Log in PIN : $Pin"
    echo "User Name : $1"
    echo "User Pass : $password"
    echo ".........................................................."
    echo ""

    # Keep alive if enabled
    if [ "$KeepAlive" = "true" ]; then
        echo "Keeping script alive (press Ctrl+C to exit)."
        while true; do
            sleep 1
        done
    fi
}

# --------------------- Main execution ---------------------
main() {
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        echo "Error: This script must be run as root. Please run with sudo or as root."
        exit 1
    fi

    # Validate inputs
    if [ -z "$CRD_SSH_Code" ]; then
        echo "Please enter authcode from the given link and run again."
        exit 1
    fi

    if [ ${#Pin} -lt 6 ]; then
        echo "Enter a pin of 6 or more digits."
        exit 1
    fi

    # Run the setup
    apt update -y
    ensure_user "$username"
    installCRD
    installDesktopEnvironment
    installGoogleChrome
    finish "$username"
}

# Run main function
main "$@"a