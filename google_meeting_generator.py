from __future__ import print_function

import datetime
import os.path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import date, timedelta
from calendar import TUESDAY

# Use your service account credentials file
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Test event details - modified for your testing
EVENT = {
    'summary': 'TEST - Oncall Handoff',
    'description': 'This is a test event created by the script.',
    'start': {
        'dateTime': 'start_time',
        'timeZone': 'America/Los_Angeles',
    },
    'end': {
        'dateTime': 'end_time',
        'timeZone': 'America/Los_Angeles',
    },
    'attendees': [
        {'email': 'oike@sapanetwork.com'},  # Your Workspace email
        {'email': 'eke.ikenna71@gmail.com'},  # Your personal email
    ],
    'reminders': {
        'useDefault': True
    },
}

def main():
    """Creates calendar events using service account authentication."""
    
    # Load service account credentials from credentials.json
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, 
        scopes=SCOPES
    )
    
    # Impersonate your Workspace email
    creds = creds.with_subject('oike@sapanetwork.com')

    update_event_with_correct_date_and_time()

    try:
        print("Event details:")
        print(f"Summary: {EVENT['summary']}")
        print(f"Start: {EVENT['start']['dateTime']}")
        print(f"End: {EVENT['end']['dateTime']}")
        print(f"Attendees: {[attendee['email'] for attendee in EVENT['attendees']]}")
        
        service = build('calendar', 'v3', credentials=creds)
        event = service.events().insert(calendarId='primary', body=EVENT).execute()
        print('\nEvent created: %s' % (event.get('htmlLink')))

    except HttpError as error:
        print('An error occurred: %s' % error)

def update_event_with_correct_date_and_time():
    today = date.today()
    days_ahead_tuesday = TUESDAY - today.weekday()
    if days_ahead_tuesday <= 0:
        days_ahead_tuesday += 7
    meeting_day = today + timedelta(days_ahead_tuesday)
    EVENT['start']['dateTime'] = f'{meeting_day}T10:00:00'
    EVENT['end']['dateTime'] = f'{meeting_day}T10:30:00'

if __name__ == '__main__':
    main()