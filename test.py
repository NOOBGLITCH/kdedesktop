import os
import subprocess
import shutil

CRD_SSH_Code = input("Google CRD SSH Code :")
username = "user"  # Change this to your desired username.
password = "root"  # Change this to your desired password.

Pin = 123456  # Ensure this is at least 6 digits.
Autostart = True  # Change to False if you don't need autostart.

class CRDSetup:
    def __init__(self, user):
        # Instead of 'apt', use pip or direct downloads to install packages
        self.installCRD()
        self.installDesktopEnvironment()
        self.installGoogleChrome()
        self.installTelegram()
        self.installQbit()
        self.finish(user)

    @staticmethod
    def installCRD():
        subprocess.run(['wget', 'https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb', '-P', '/home/{}/'.format(username)])
        print("Chrome Remoted Desktop package downloaded.")
        # Directly download CRD package and provide instructions for manual installation

    @staticmethod
    def installDesktopEnvironment():
        # Provide instructions for a desktop environment that doesn't require root access.
        print("Unable to install XFCE4 Desktop Environment without root access.")

    @staticmethod
    def installGoogleChrome():
        subprocess.run(['wget', 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb', '-P', '/home/{}/'.format(username)])
        print("Google Chrome package downloaded.")

    @staticmethod
    def installTelegram():
        subprocess.run(['wget', 'https://telegram.org/dl/desktop/linux', '-P', '/home/{}/'.format(username)])
        print("Telegram package downloaded.")

    @staticmethod
    def installQbit():
        print("Unable to install Qbittorrent without root access.")

    @staticmethod
    def finish(user):
        print("Setup completed. Please manually install packages if necessary.")

try:
    if CRD_SSH_Code == "":
        print("Please enter authcode from the given link")
    elif len(str(Pin)) < 6:
        print("Enter a pin more or equal to 6 digits")
    else:
        CRDSetup(username)
except NameError as e:
    print("'username' variable not found, create a user first.")
