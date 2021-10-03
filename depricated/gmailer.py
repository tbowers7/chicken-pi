# -*- coding: utf-8 -*-

"""
  FILE: gmailer.py

Contains a class for sending email using the GMAIL SMTP server

"""

# Futures
# […]

# Built-in/Generic Imports
import os,sys
# […]

# Libs
import smtplib
from cryptography.fernet import Fernet
# […]

# Own modules
#from {path} import {class}

## Boilerplate variables
__author__ = 'Timothy P. Ellsworth Bowers'
__copyright__ = 'Copyright 2019-2020, chicken-pi'
__credits__ = ['Stephen Bowers']
__license__ = 'LGPL-3.0'
__version__ = '0.1.0'
__email__ = 'chickenpi.flag@gmail.com'
__status__ = 'Development Status :: 1 - Planning'



### Read in the decryption key and encrypted username/passwd
ABSPATH = os.path.abspath(os.path.dirname(sys.argv[0]))
with open(ABSPATH+'/.key.bin','rb') as fileobj:
    for line in fileobj:
        key = line
with open(ABSPATH+'/.gmailuname.bin','rb') as fileobj:
    for line in fileobj:
        cryptuname = line
with open(ABSPATH+'/.gmailpasswd.bin','rb') as fileobj:
    for line in fileobj:
        cryptpasswd = line
ciphering = Fernet(key)

### Set Email Variables
SMTP_SERVER    = 'smtp.gmail.com'   # Email Server
SMTP_PORT      = 587
GMAIL_USERNAME = str(ciphering.decrypt(cryptuname),'utf-8')
GMAIL_PASSWORD = str(ciphering.decrypt(cryptpasswd), 'utf-8')


### Emailer is the class for interfacing with GMAIL
class Emailer:
    def sendmail(self, recipient, subject, content):

        # Create Headers
        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject,
                   "To: " + recipient, "MIME-Version: 1.0",
                   "Content-Type: text/html"]
        headers = "\r\n".join(headers)

        # Connect to the Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()

        # Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

        # Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, headers +
                         "\r\n\r\n" + content)
        session.quit()
