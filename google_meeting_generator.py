from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import date
from datetime import timedelta
from calendar import TUESDAY
# from pagerduty_user_picker import *

# To start this script, 
# cd /Users/zachsimon/Documents/code/Oncall Meeting Scheduler
# Then run 
# `source "/Users/zachsimon/Documents/code/Oncall Meeting Scheduler/.venv/bin/activate"`
# Then run
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# Then run
# python3 google_meeting_generator.py

# If you need help, check out this Google article that was the basis for this script:
# https://developers.google.com/calendar/api/quickstart/python

# If modifying these scopes, delete the file credentials.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Details about the event
# Date/Time format is RFC3339: https://datatracker.ietf.org/doc/html/rfc3339#section-5.8
# Time zone is not needed in the format if it is provided separately (and it is below)
EVENT = {
    'summary': 'Oncall Handoff',
    'description': 'Last week\'s pager notes can be found here: ',
    'start': {
        'dateTime': 'start_time',
        'timeZone': 'America/Los_Angeles',
    },
    'end': {
        'dateTime': 'end_time',
        'timeZone': 'America/Los_Angeles',
    },
    'attendees': [
        {'email': 'oike@sapanetwork.com'},
        {'email': 'eke.ikenna71@gmail.com'},
    ],
    'reminders': {
        'useDefault': True
    },
}


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file credentials.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('credentials.json'):
        creds = Credentials.from_authorized_user_file('credentials.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save the refreshed credentials back to credentials.json
            with open('credentials.json', 'w') as token:
                token.write(creds.to_json())
        else:
            # In Jenkins, we should always have valid credentials from AWS Secrets Manager
            raise Exception("Invalid credentials in credentials.json. Please check AWS Secrets Manager.")

    update_event_with_correct_date_and_time()

    urls = create_urls()
    responses = get_responses(urls)
    user_emails = get_user_emails(responses)
    # print(user_emails)

    update_event_attendees(user_emails)

    try:
        # print(EVENT)
        service = build('calendar', 'v3', credentials=creds)
        event = service.events().insert(calendarId='primary', body=EVENT).execute()
        print('Event created: %s' % (event.get('htmlLink')))

        # # Call the Calendar API
        # now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        # print('Getting the upcoming 10 events')
        # events_result = service.events().list(calendarId='primary', timeMin=now,
        #                                       maxResults=10, singleEvents=True,
        #                                       orderBy='startTime').execute()
        # events = events_result.get('items', [])

        # if not events:
        #     print('No upcoming events found.')
        #     return

        # # Prints the start and name of the next 10 events
        # for event in events:
        #     start = event['start'].get('dateTime', event['start'].get('date'))
        #     print(start, event['summary'])

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

def update_event_attendees(user_emails):
    user_emails_as_list_of_dicts = []
    for email in user_emails:
        user_emails_as_list_of_dicts.append({'email': email})
    EVENT['attendees'] = EVENT['attendees'] + user_emails_as_list_of_dicts

if __name__ == '__main__':
    main()