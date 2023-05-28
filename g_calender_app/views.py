import os
import requests
import datetime
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.urls import reverse
from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from urllib.parse import urlencode
from urllib.parse import parse_qs
from googleapiclient.errors import HttpError
from .models import calender_event_model

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "credentials/client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
API_SERVICE_NAME = 'calender'
API_VERSION = 'v2'

def home_page(request):
    return render(request, 'templates/index.html', {'fact': 'Yo !'});

def events_page(request):
    return render(request, 'templates/events_page.html', {'fact': 'Yo !'});

def oauth2callback(request):
    # Specify the state when creating the flow in the callback so that it can
    # be verified in the authorization server response.
    state = request.session['state']

    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback'))

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    creds = flow.credentials
    # print('Credentials obtained: ')
    # print(creds)
    request.session['credentials'] = credentials_to_dict(creds)
    # print(request.session['credentials'])

    data = request.session['credentials']

     # Serialize the data dictionary into a query string
    serialized_data = urlencode(data)
    # print('Serialized Data:')
    # print(serialized_data)

    token = data['token']
    client_secret = data['client_secret']
    client_id = data['client_id']
    refresh_token = data['refresh_token']

    # Pass the serialized data as a URL parameter in the redirect URL
    redirect_url = reverse('GoogleCalendarRedirectView')
    redirect_url += f'?client_secret={client_secret}'+ f'&client_id={client_id}' + f'&token={token}' + f'&refresh_token={refresh_token}'

    return redirect(redirect_url)

def GoogleCalendarInitView(request):
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback'))

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true',
        prompt="consent"
    )

    # Store the state so the callback can verify the auth server response.
    request.session['state'] = state

    return redirect(authorization_url)



def GoogleCalendarRedirectView(request):

    # Access the values from the data dictionary as needed
    token = request.GET.get('token', '')
    refresh_token = request.GET.get('refresh_token', '')
    # token_uri = request.GET.get('token_uri', '')
    client_id = request.GET.get('client_id', '')
    client_secret = request.GET.get('client_secret')

    data = {
       'token': token,
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }

    creds = credentials.Credentials.from_authorized_user_info(data, SCOPES)

    eventsList = []
    events = {}

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        eventsList = events_result.get('items', [])

        print('eventsList size:')
        print(len(eventsList))

        if not eventsList:
            print('No upcoming events found.')
            return render(request, 'templates/events_page.html', {'events': {}});

        # Prints the start and name of the next 10 events
        for event in eventsList:
            
            start = event['start'].get('dateTime', event['start'].get('date'))[:10]
            current_event = calender_event_model.CalendarEventModel.from_dict(event)
            print(current_event.start_time)
            print('\n')
            if start not in events:
                events[start] = []
            events[start].append(current_event)

        print('\n Events dict: ')
        for k, vals in events.items():
            print(k)
            for val in vals:
                print(val)
        

    except HttpError as error:
        print('An error occurred: %s' % error)

    google_colors = ["#4285F4", "#DB4437", "#0F9D58", "#F4B400", "#AB47BC"]


    return render(request, 'templates/events_page.html', {'events': events, 'google_colors': google_colors});

def credentials_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes,
    }