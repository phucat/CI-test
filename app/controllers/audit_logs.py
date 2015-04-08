from ferris import Controller, route_with, messages, settings
from ferris.core import time_util
from app.models.audit_log import AuditLog as AuditLogModel
from app.models.email_recipient import EmailRecipient
import StringIO
import csv
import logging
from time import sleep
from datetime import date, timedelta, datetime
import dateutil.tz
config = settings.get('admin_account')


class AuditLogs(Controller):
    class Meta:
        prefixes = ('api',)
        components = (messages.Messaging, )
        Model = AuditLogModel

    @route_with(template='/api/audit_logs/downloads/<tz_offset>', methods=['GET'])
    @route_with(template='/api/audit_logs/downloads', methods=['GET'])
    def api_generate_report(self, tz_offset=None):
        tz_offset = float(tz_offset) if tz_offset else 0
        # for x in xrange(1, 201):
        #     AuditLogModel.email_fluff(config['email'])

        fields = ['Timestamp','The action performed', 'How the action was invoked',
        'What App User invoked the action', 'Targetted user or resource', 'Target event altered', 'Comment']

        now = datetime.now()
        local_now = time_util.localize(now, tz=dateutil.tz.tzoffset(None, tz_offset*60*60))
        tomorrow = local_now + timedelta(days=1)
        fromdate = time_util.localize(datetime(now.year, now.month, now.day, 0, 0, 0), tz=dateutil.tz.tzoffset(None, 0))
        todate = time_util.localize(datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0), tz=dateutil.tz.tzoffset(None, 0))
        logging.info("RANGE: %s %s " % (fromdate, todate))
        out = StringIO.StringIO()
        logs = AuditLogModel.fetch_date_range(fromdate, todate)
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()

        for log in logs.iter():
            data = {
                'Timestamp': datetime.strftime(log.created, '%m/%d/%Y %I:%M:%S %p'),
                'The action performed': log.action,
                'How the action was invoked': log.how_the_action_invoked,
                'What App User invoked the action': log.app_user_invoked_action,
                'Targetted user or resource': log.target_resource,
                'Target event altered': log.target_event_altered,
                'Comment': log.comment
            }

            writer.writerow(data)

        self.response.headers['Content-Type'] = 'application/ms-excel;charset=UTF-8'
        self.response.headers['Content-Transfer-Encoding'] = 'Binary'
        self.response.headers['Content-disposition'] = 'attachment; filename="arista-calendar-log-%s.csv"' % datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        self.response.out.write(out.getvalue())
        out.close()
        return self.response

    @route_with(template='/api/auditlogs/generate/report/csv/<key>')
    def api_generate_report_csv(self, key):
        fields = ['Timestamp','The action performed', 'How the action was invoked',
        'What App User invoked the action', 'Targetted user or resource', 'Target event altered', 'Comment']

        now = datetime.now()

        # localize

        if key == 'daily':
            tomorrow = now + timedelta(days=1)
            fromdate = datetime(now.year, now.month, now.day, 0, 0, 0)
            todate = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)
        elif key == 'weekly':
            one_week = timedelta(weeks=1)
            fromdate1 = now - one_week
            fromdate = datetime(fromdate1.year, fromdate1.month, fromdate1.day, 0, 0, 0)
            todate = datetime(now.year, now.month, now.day, 23, 59, 59)

        out = StringIO.StringIO()
        logs = AuditLogModel.fetch_date_range(fromdate, todate)
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()

        for log in logs:
            data = {
                'Timestamp': datetime.strftime(log.created, '%m/%d/%Y %I:%M:%S %p'),
                'The action performed': log.action,
                'How the action was invoked': log.how_the_action_invoked,
                'What App User invoked the action': log.app_user_invoked_action,
                'Targetted user or resource': log.target_resource,
                'Target event altered': log.target_event_altered,
                'Comment': log.comment
            }

            writer.writerow(data)

        filename = "arista-calendar-log-%s.csv" % datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        settings = EmailRecipient.list_all()
        emails = [setting.email for setting in settings]

        if key == 'daily':
            AuditLogModel.daily_notification_on_major_actions(emails, filename, out.getvalue())
        elif key == 'weekly':
            AuditLogModel.weekly_notification_on_major_actions(emails, filename, out.getvalue())

        out.close()

        return 'Email Sent'


def get_midnight(offset):
    midnight = 24 + offset
    if midnight > 24:
        midnight -= 24
    return midnight
