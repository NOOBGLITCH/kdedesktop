import os
import subprocess

subprocess.run(['pip', 'install', '-q', 'colab-xterm'])

CRD_SSH_Code = input("Google CRD SSH Code: ")
username = "user"  # Change username if needed
password = "root"  # Change password if needed
Pin = 123456       # Set default PIN or modify it

# Write the inputs to environment variables
%env CRD_SSH_Code=$CRD_SSH_Code
%env username=$username
%env password=$password
%env Pin=$Pin
