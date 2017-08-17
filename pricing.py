from __future__ import print_function
import httplib2
import os
import subprocess
import tkinter
from tkinter import filedialog, messagebox, StringVar
from subprocess import PIPE
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Alpha Pricing tool using slic3r and sheets apis'
TOP = tkinter.Tk()
RET_PRICE = StringVar()
FILE_NAME = StringVar()
FILE = tkinter.Label(TOP, textvariable = FILE_NAME)
COST = tkinter.Label(TOP, textvariable = RET_PRICE)
FILE_NAME.set("Please choose a part")

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def price(inFile):
    exe = './Slic3r.app/contents/MacOS/slic3r'
    config = './config.ini'
    args = [
        exe, 
        '--load', 
        config, 
        '--post-process',
        './gcoder.py',
        inFile]
    print(args)
    slic3r = subprocess.Popen(args, stdout = subprocess.PIPE)
    x=0
    output = []
    for line in slic3r.stdout:
        if "=>" in line.decode():
            pass
        elif "Done" in line.decode():
            pass
        elif "Filament" in line.decode():
            pass
        else:
            output.append(line.decode())
            x+=1
    slic3r.wait()
    print(output)
    timelist = (output[0].rstrip()).split(':')
    print(timelist)
    ept = float(timelist[0]) + (float(timelist[1])/60)
    ept = round(ept,2)
    print(ept)
    volume = (output[1].rstrip()).split('c')[0]
    print(volume)
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    spreadsheetId = '1HRzMV4tARMrlR33rqCBW89Z4azpLqMnPFVWNfAX3sMQ'
    rangeName = 'A2'
    bodyobj = {'range':'A2',
               'values':[[volume]]}
    result = service.spreadsheets().values().update(spreadsheetId=spreadsheetId, 
                                                    range=rangeName, 
                                                    valueInputOption='USER_ENTERED', 
                                                    body=bodyobj).execute()

    rangeName = 'A4'
    bodyobj = {'range':'A4',
               'values':[[ept]]}
    result = service.spreadsheets().values().update(spreadsheetId=spreadsheetId, 
                                                    range=rangeName, 
                                                    valueInputOption='USER_ENTERED', 
                                                    body=bodyobj).execute()
                                                    
    rangeName = 'D14'
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    print(values[0][0])
    return values[0][0]

def main():
    RET_PRICE = StringVar()
    TOP.title('Pricing Tool')
    values = 0
    Price = tkinter.Label(text=values)
    B1 = tkinter.Button(TOP, text='Browse', command=openfile)
    B1.pack()
    B2 = tkinter.Button(TOP, text='Calculate Price', command=priceback)
    B2.pack()
    FILE.pack()
    COST.pack()
    TOP.mainloop()

def openfile():
    global NAME
    NAME = tkinter.filedialog.askopenfilename(
        initialdir = './examples', 
        title='Select GCode File')
    FILE_NAME.set(NAME)

def priceback():
    RET_PRICE.set(price(NAME))

if __name__ == '__main__':
    main()
