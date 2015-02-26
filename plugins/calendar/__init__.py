import httplib2, logging, urllib2
from apiclient.discovery import build
from apiclient import errors
from plugins import service_account
from ferris.core import settings

scopes = (
    'https://www.googleapis.com/auth/calendar'
    )

DEVELOPER_KEY = settings.get('oauth2_service_account')['developer_key']


def build_client(user):
    logging.info('calendar: build_client')
    try:
        http = httplib2.Http()
        credentials = service_account.build_credentials(scopes, user)
        credentials.authorize(http)
        calendar = build('calendar', 'v3', http=http, developerKey=DEVELOPER_KEY)
        return calendar
    except urllib2.HTTPError, err:
        logging.info('build_client HTTPError!')
        logging.info(str(err))
        return build_client(user)


def get_all_events(email):
    logging.info('calendar: get_all_events')
    response = None
    page_token = None

    while True:
        try:
            calendar = build_client(email)
            param = {'calendarId': email, 'timeZone': 'GMT', 'singleEvents': True, 'showDeleted': True, 'pageToken': page_token}

            events = calendar.events().list(**param).execute()

            if not page_token:
                response = events
            else:
                response['items'].extend(events['items'])

            logging.info("google event response ==> %s" % response)

            page_token = events.get('nextPageToken')
            if not page_token:
                break

        except urllib2.HTTPError, err:
            logging.error(err)
            continue

    return response


def get_all_modified_events(email, updatedMin):
    logging.info('calendar: get_all_modified_events')
    response = None
    page_token = None
    while True:
        calendar = build_client(email)
        param = {'calendarId': email, 'timeZone': 'GMT', 'singleEvents': True, 'showDeleted': True, 'updatedMin': updatedMin, 'pageToken': page_token}
        events = calendar.events().list(**param).execute()

        if not page_token:
            response = events
        else:
            response['items'].extend(events['items'])

        page_token = events.get('nextPageToken')
        if not page_token:
            break
    return response


def get_all_events_by_date(email, start_date, end_date, showDeleted=True, query=None):
    logging.info('calendar: get_all_events_by_date')
    response = None
    page_token = None
    while True:
        calendar = build_client(email)
        param = {
            'calendarId': email,
            'timeMax': end_date,
            'timeMin': start_date,
            'singleEvents': True,
            'timeZone': 'GMT',
            'showDeleted': showDeleted,
            'pageToken': page_token
        }

        if query:
            param['q'] = query

        events = calendar.events().list(**param).execute()

        if not page_token:
            response = events
        else:
            response['items'].extend(events['items'])

        page_token = events.get('nextPageToken')
        if not page_token:
            break

    return response


def get_event_by_id(email, id):
    logging.info('calendar: get_event_by_id')
    calendar = build_client(email)
    param = {'calendarId': email, 'eventId': id}
    event = calendar.events().get(**param).execute()
    return event


def create_event(email, post):
    logging.info('calendar: create_event')
    try:
        calendar = build_client(email)
        logging.info('calendar client created successfully!')
        response = calendar.events().insert(calendarId=email, body=post).execute()
        return response
    except errors.HttpError, e:
        logging.info('create_event HTTPError!')
        logging.info(str(e))
        return create_event(email, post)
    # except:
    #     logging.info('create_event: unexpected error!')
    #     return create_event(email, post)


def update_event(event_id, email, post):
    logging.info('calendar: update_event')
    logging.info('Updating Google event: [' + event_id + '].')
    try:
        calendar = build_client(email)
        response = calendar.events().patch(calendarId=email, eventId=event_id, body=post).execute()
        logging.info('CALENDAR Update EVENT RESPONSE =================')
        logging.info(response)
        logging.info('CALENDAR Update EVENT RESPONSE =================')
        return response
    except Exception, e:
        logging.error('Error on Update EVENT:')
        logging.error(e)
        logging.error('Error on Update EVENT:')




def move_event(event_id, owner_email, new_owner_email):
    logging.info('calendar: move_event')
    logging.info('Moving calendar event from [' + owner_email + '] to [' + new_owner_email + '] with event id (' + event_id + ').')
    calendar = build_client(owner_email)
    # rule = calendar.acl().get(calendarId=owner_email, ruleId='user:' + new_owner_email).execute()
    # rule['role'] = 'writer'
    # updated_rule = calendar.acl().update(calendarId=owner_email, ruleId=rule['id'], body=rule).execute()
    # response = None
    # if updated_rule:
    #     response = calendar.events().move(calendarId=owner_email, eventId=event_id, destination=new_owner_email)
    response = calendar.events().move(calendarId=owner_email, eventId=event_id, destination=new_owner_email)
    return response


def delete_event(id, email):
    logging.info('calendar: delete_event')
    logging.info('Deleting event: [' + id + '] of ' + email + '.')
    calendar = build_client(email)
    response = calendar.events().delete(calendarId=email, eventId=id).execute()
    return response


def make_watch_request(email, post):
    logging.info('calendar: make_watch_request')
    calendar = build_client(email)
    response = calendar.events().watch(calendarId=email, body=post).execute()
    return response


def stop_watch_request(email, post):
    logging.info('calendar: stop_watch_request')
    calendar = build_client(email)
    response = calendar.channels().stop(body=post).execute()
    return response


def get_token(email):
    logging.info('calendar: get_token')
    credentials = service_account.build_credentials(scopes, email)
    token = service_account.credentials_to_token(credentials)
    return token
