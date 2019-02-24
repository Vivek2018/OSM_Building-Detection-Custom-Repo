# Taken from https://medium.com/@annissouames99/how-to-upload-files-automatically-to-drive-with-python-ee19bb13dda

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
g_login = GoogleAuth()
g_login.LocalWebserverAuth()
drive = GoogleDrive(g_login)

with open("path_to_your_file","r") as file:
    #do something here with file
    file_drive = drive.CreateFile({'title': os.path.basename(file.name)})
    file_drive.SetContentString(file.read())
    file1_drive.Upload()

file = open('path/to/file.txt')
print(file.name)
# Print path/to/file.txt
print(os.path.basename(file.name))
# Print file.txt only