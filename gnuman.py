import base64
import json
import os
import pickle

from email.mime.text import MIMEText

from lxml import html
import pause
import requests
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import errors
from googleapiclient.discovery import build

STORE_URL = 'https://garynuman.tmstor.es/index.php?page=products&section=all&lf=454634a53a858c8c610454594289f92a'
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def send_mail(config):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(STORE_URL)
    message['to'] = config['to_addr']
    message['from'] = config['from_addr']
    message['subject'] = 'Cambios en la tienda de Gary Numan!!!'
    message = {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    try:
        message = (service.users().messages().send(userId='me', body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def check_site(config):
    response = requests.get(STORE_URL)
    while True:
        last = ''.join(response.text.split())
        response = requests.get(STORE_URL)
        if ''.join(response.text.split()) != last:
            send_mail(config)
        pause.days(1)


def main():
    with open('config.json') as file:
        check_site(json.load(file))


if __name__ == '__main__':
    main()
