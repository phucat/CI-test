from apiclient.discovery import build
import logging


def init_client(client):
    try:
        calendar = build('calendar', 'v3', http=client)
    except Exception as e:
        calendar = None
        logging.error('Could not init calendar!')
        logging.error(e)

    return calendar
