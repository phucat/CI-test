Google Calendar Development
Arista Networks
===========================

The purpose of this engagement is to deliver an application for the IT staff to push updates to Customer’s Google Calendar environment. The following Google Calendar elements will be updated within this application:

Resource Information
Event Participants

The application will be made available as a web application to specific users within the Arista domain. Authentication and access will be controlled by a Google Group. The primary objectives of this application are to ensure Calendar Resource information updates are pushed to existing Calendar entries and to remove event participants from a Calendar entry once the corresponding user is removed from the Google Environment.

Quick Start Guide
=================

1. In Google Admin settings, include API's scopes

        https://www.googleapis.com/auth/calendar,
        https://www.googleapis.com/auth/calendar.readonly,
        https://apps-apis.google.com/a/feeds/calendar/resource/#readonly,
        https://www.googleapis.com/auth/admin.directory.group.readonly,
        https://www.googleapis.com/auth/admin.directory.orgunit.readonly,
        https://www.googleapis.com/auth/admin.directory.user.readonly

2. In Settings.py update the ff:

        settings['oauth2_service_account'] = {
            'client_email' : 'gserviceaccount.com'
            'private_key': 'key' #must be in pem file
            'developer_key': server_key in public api access
            'domain' : 'clientdomain.com'
            'default_user': 'admin acount'
        }

        settings['google_directory'] = {
            'domain': 'clientdomain.com'
        }

        settings['admin_account'] = {
            'email': 'admin acount',
            'domain': 'clientdomain.com',
            'password': 'admin password'
        }


3. Since were using google_directory plugin: run /api/google/directory/prime to cache users.

4. Endpoint for schedule removal run '/api/schedule/remove/user/<email>'




Live Deployment Checklist
-------------------------

 1. Include API scope
 2. steps to deploy this project
 3. live, including build processes,
 4. incidentals, etc.


Warnings and Gotchas
---------------------------
 * Please add to this list any weirdness, hacks,
 * installs, or other oddities needed for this Project.


How to run Unit Tests
-----------------------
1. Please replace this text with
2. a short guide for any future developer
3. to follow to test any Unit Tests
4. your code has.


Further Documentation
----------------------
Place any other documentation you may create as you develop.
