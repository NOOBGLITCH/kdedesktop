import os
import subprocess

subprocess.run(['pip', 'install', '-q', 'colab-xterm'])

# Python code to capture user input
CRD_SSH_Code = input("Google CRD SSH Code: ")
username = "user"  # Default username, can be modified
password = "root"  # Default password, can be modified
Pin = 123456       # Default PIN

# Save the inputs to a temporary file
with open("user_input.txt", "w") as f:
    f.write(f"CRD_SSH_Code={CRD_SSH_Code}\n")
    f.write(f"username={username}\n")
    f.write(f"password={password}\n")
    f.write(f"Pin={Pin}\n")
