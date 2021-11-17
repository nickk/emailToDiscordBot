#!/usr/bin/env python
# coding: utf-8


# importing os and pickle module in program  
import os
import pickle
# Creating utils for Gmail APIs  
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# Importing libraries for encoding/decoding messages in base64  
from base64 import urlsafe_b64decode, urlsafe_b64encode
# Importing libraries for dealing with the attachment of MIME types in Gmail  
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

# Import the email modules we'll need
from email import policy
from email.parser import BytesParser
import mimetypes

from mimetypes import guess_type as guess_mime_type
import base64
import email
from pprint import pprint
import pandas as pd
from bs4 import BeautifulSoup
from tabulate import tabulate
import time
import redis
import pickle
import zlib
import numpy as np


r = redis.Redis()
p = r.pubsub()


SCOPES = ['https://mail.google.com/'] 
OurEmailID = 'xxxxxxx@gmail.com'  ################ ENTER YOUR EMAIL ADDRESS HERE


def authenticateGmailAPIs():
    creds = None    
    if os.path.exists("token.pickle"): 
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'xxxxxx.apps.googleusercontent.com.json', ################ ENTER YOUR JSON CREDENTIALS FILE LOCATION HERE
                SCOPES)
            creds = flow.run_local_server(port=0)         
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


# Get the Gmail API service by calling the function
ServicesGA = authenticateGmailAPIs()


# Using a default funnction to add attachments in Mail
def AddAttachment(mail, NameofFile):
    content_type, encoding = guess_mime_type(NameofFile)
    if content_type is None or encoding is not None:  # defining none file type attachment
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':  # defining text file type attachment
        fp = open(NameofFile, 'rb')  # opening file
        msg = MIMEText(fp.read().decode(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':  # defining image file type attachment
        fp = open(NameofFile, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':  # defining audio file type attachment
        fp = open(NameofFile, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)  # reading file
        fp.close()
    else:
        fp = open(NameofFile, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()  # closing file
    NameofFile = os.path.basename(NameofFile)
    msg.add_header('Content-Disposition', 'attachment', NameofFile=NameofFile)
    mail.attach(msg)  # composing the mail with given attachment


# Creating mail with a default function
def CreateMail(RecieverMail, SubofMail, BodyofMail,
               attachments=[]):  # various import content of mail as function's parameter
    # Using if else to check if there is any attachment in mail or not  
    if not attachments:  # no attachment is given in the mail
        mail = MIMEText(BodyofMail)  # Body of Mail
        mail['to'] = RecieverMail  # mail ID of Reciever
        mail['from'] = OurEmailID  # our mail ID
        mail['subject'] = SubofMail  # Subject of Mail
    else:  # attachment is given in the mail
        mail = MIMEMultipart()
        mail['to'] = RecieverMail
        mail['from'] = OurEmailID
        mail['subject'] = SubofMail
        mail.attach(MIMEText(BodyofMail))
        for NameofFile in attachments:
            AddAttachment(mail, NameofFile)
    return {'raw': urlsafe_b64encode(mail.as_bytes()).decode()}


# Creating a default function to send a mail
def SendMail(ServicesGA, RecieverMail, SubofMail, BodyofMail, attachments=[]):
    return ServicesGA.users().messages().send(
        userId="me",
        body=CreateMail(RecieverMail, SubofMail, BodyofMail, attachments)
    ).execute()  # Body of the mail with execute() function


def get_messages(service, user_id):
    try:
        #msgs = service.users().messages().list(userId='me',q='in:inbox is:unread').execute()
        return service.users().messages().list(userId=user_id, q='in:inbox is:unread').execute()
    except Exception as error:
        print('An error occurred: %s' % error)


def get_message(service, user_id, msg_id):
    try:
        return service.users().messages().get(userId=user_id, id=msg_id, format='metadata').execute()
    except Exception as error:
        print('An error occurred: %s' % error)


def get_mime_message(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id,
                                             format='raw').execute()
        #print('Message snippet: %s' % message['snippet'])
        msg_str = base64.urlsafe_b64decode(message['raw'].encode("utf-8")).decode("utf-8")
        mime_msg = email.message_from_string(msg_str)

        ret_email = mime_msg.get_payload(decode=True).decode()#''
        #print(ret_email)
        return ret_email

    except Exception as error:
        print('An error occurred: %s' % error)


def process_emails(msg_html_bodies):
    for i in range(len(msg_html_bodies)):
        html_table = msg_html_bodies[i]
        # fix HTML
        soup = BeautifulSoup(html_table, "html.parser")
        
        
        for table in soup.findChildren(attrs={'style': 'bordercolor="#cccccc"'}): 
            print(table.contents)
            for c in table.children:
                for z in c.findChildren(attrs={'style': 'background-color:whitesmoke'}):
                    z.unrwap()
                #if c.name in ['tbody', 'thead']:
                #    c.unwrap()
        df = pd.read_html(str(soup), flavor="bs4")
        
        df = df[0]

        start_end = []
        in_table = False
        for i in range(len(df)):    
            isN = pd.isnull(df.iloc[[i], 0]).values[0]    
            curr_t = df.iloc[[i], 0].values[0]

            if (curr_t == 'BLOCK TRADES'):       
                current_start = i+1
                current_header = df.iloc[i-1,0]        
                in_table = True
            if (isN) & (in_table == True):        
                start_end.append([current_header, [current_start, i]])
                in_table = False
        tble_dfs = []        
        
        for x in start_end:
            tit = x[0]
            j = x[1]
            #tble_dfs.append([x[0],df.iloc[j[0]:j[1],:].copy()])
            dfff = df.iloc[j[0]:j[1],:].copy()
            dfff.rename(columns={0:'TIME (CT)', 1: '1', 2: 'PRODUCT', 3: 'SYM', 4: 'B/S', 5: 'QTY', 6: 'STRIKE', 7: 'TYPE', 8: 'PRICE'}, inplace=True)
            sm_table_cleaned = dfff.iloc[1:, [0,2,3,4,5,6,7,8]].copy()
            sm_table_cleaned.reset_index(drop=True, inplace=True)
            sm_table_cleaned.iloc[:,3] = sm_table_cleaned.iloc[:,3].apply(str)
            sm_table_cleaned.iloc[:,3] = sm_table_cleaned.iloc[:,3].str.replace('nan', '-')

            #sm_table_cleaned.iloc[:,7] = sm_table_cleaned.iloc[:,7].apply(float)
            #sm_table_cleaned.iloc[:,7] = np.round(sm_table_cleaned.iloc[:,7],3)

            sm_table_cleaned.iloc[:,5] = sm_table_cleaned.iloc[:,5].apply(str)
            sm_table_cleaned.iloc[:,5] = sm_table_cleaned.iloc[:,5].str.replace('nan', '-')
            sm_table_cleaned.loc[-1] = [tit, '', '', '', '', '', '', '']  # adding a row (7x)
            sm_table_cleaned.index = sm_table_cleaned.index + 1  # shifting index
            sm_table_cleaned.sort_index(inplace=True)        
            yield(sm_table_cleaned)



if __name__ == '__main__':
    while True:
        messages = get_messages(ServicesGA, OurEmailID)
        msg_html_bodies = []
        if len(messages) > 1: #if unread emails
            for m in messages['messages']:
                msg_html_bodies.append(get_mime_message(ServicesGA, OurEmailID, m['id']))
                # mark as read
                ServicesGA.users().messages().modify(userId=OurEmailID, id=m['id'], body={
                    'removeLabelIds': ['UNREAD']
                }).execute()    

        #else:
        #    print('no new unreads')

        gen = process_emails(msg_html_bodies)
        
        #print(msg_html_bodies)
        
        
        for i in gen:                        
            r.publish('tradingview', zlib.compress(pickle.dumps(i)))
            print((tabulate(i, headers='keys', tablefmt='psql', showindex=False, numalign="right")))
        time.sleep(10)
