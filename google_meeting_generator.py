import os
from datetime import date, timedelta
from calendar import TUESDAY
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuration
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
WORKSPACE_EMAIL = 'oike@sapanetwork.com'

def get_next_tuesday():
    """Calculate the date of the next Tuesday."""
    today = date.today()
    days_ahead = TUESDAY - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days_ahead)

def create_event():
    """Creates a calendar event for the next Tuesday."""
    
    # Check if credentials file exists
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Credentials file not found: {SERVICE_ACCOUNT_FILE}")
    
    # Get next Tuesday's date
    meeting_day = get_next_tuesday()
    
    # Event details
    event = {
        'summary': 'Oncall Handoff',
        'description': 'Weekly oncall handoff meeting',
        'start': {
            'dateTime': f'{meeting_day}T10:00:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': f'{meeting_day}T10:30:00',
            'timeZone': 'America/Los_Angeles',
        },
        'attendees': [
            {'email': WORKSPACE_EMAIL},
            {'email': 'eke.ikenna71@gmail.com'},
        ],
        'reminders': {
            'useDefault': True
        },
    }
    
    try:
        # Load and configure credentials
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=SCOPES
        )
        creds = creds.with_subject(WORKSPACE_EMAIL)
        
        # Create calendar service
        service = build('calendar', 'v3', credentials=creds)
        
        # Log event details
        print("Creating event:")
        print(f"  Summary: {event['summary']}")
        print(f"  Date: {meeting_day}")
        print(f"  Time: 10:00 AM - 10:30 AM PST")
        print(f"  Attendees: {', '.join([a['email'] for a in event['attendees']])}")
        
        # Create the event
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"\n✓ Event created successfully!")
        print(f"  Link: {created_event.get('htmlLink')}")
        
    except HttpError as error:
        print(f'✗ API Error: {error}')
        raise
    except Exception as error:
        print(f'✗ Error: {error}')
        raise

if __name__ == '__main__':
    create_event()