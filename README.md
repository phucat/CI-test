Google Calendar Development Networks
===========================================

The purpose of this engagement is to deliver an application for the IT staff to push updates to Customer’s Google Calendar environment. The following Google Calendar elements will be updated within this application:

Resource Information
Event Participants

The application will be made available as a web application to specific users within the domain. Authentication and access will be controlled by a Google Group. The primary objectives of this application are to ensure Calendar Resource information updates are pushed to existing Calendar entries and to remove event participants from a Calendar entry once the corresponding user is removed from the Google Environment.

Quick Start Guide
=================

1. In Google Admin settings, include API's scopes

        https://www.googleapis.com/auth/calendar,
        https://www.googleapis.com/auth/admin.directory.user,
        https://apps-apis.google.com/a/feeds/calendar/resource/#readonly,
        https://www.googleapis.com/auth/admin.directory.group.readonly,
        https://www.googleapis.com/auth/admin.directory.orgunit.readonly


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

3. In plugins/service_account/settings.py update the ff:
        domain = ndb.StringProperty(indexed=False, verbose_name="DOMAIN")
        default_user = ndb.StringProperty(indexed=False, verbose_name="ADMIN_USER")
        client_email = ndb.StringProperty(indexed=False, verbose_name="***@developer.gserviceaccount.com")

4. Since were using google_directory plugin: run **/api/google/directory/prime** to cache users.

5. Endpoint for schedule removal run **/api/schedule/remove/user/<email>**

6. Endpoint for system settings **/admin** to add email group for daily notifications


Live Deployment Checklist
-------------------------

 1. Include API scope
 2. Service Account / Server Key / Domain Admin


Warnings and Gotchas
---------------------------
 * Please add to this list any weirdness, hacks,
 * installs, or other oddities needed for this Project.


How to run Unit Tests
-----------------------
1.


Further Documentation
----------------------
/
