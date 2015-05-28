import csv
from ferris import Controller, route_with, messages
from ferris.core import time_util
from app.models.audit_log import AuditLog as AuditLogModel
from plugins.unicode_writer import UnicodeDictWriter
import StringIO
import logging
from datetime import timedelta, datetime
import dateutil.tz


class AuditLogs(Controller):
    class Meta:
        prefixes = ('api',)
        components = (messages.Messaging, )
        Model = AuditLogModel

    @route_with(template='/api/audit_logs/downloads/<tz_offset>', methods=['GET'])
    @route_with(template='/api/audit_logs/downloads', methods=['GET'])
    def api_generate_report(self, tz_offset=None):
        tz_offset = float(tz_offset) if tz_offset else 0

        fields = ['Timestamp',
        'The action performed',
        'How the action was invoked',
        'What App User invoked the action',
        'Targetted user or resource',
        'Target event altered',
        'Comment']

        now = datetime.now()
        local_now = time_util.localize(now, tz=dateutil.tz.tzoffset(None, tz_offset*60*60))
        tomorrow = local_now + timedelta(days=1)
        weeks = now - timedelta(weeks=2)
        fromdate = time_util.localize(datetime(weeks.year, weeks.month, weeks.day, 0, 0, 0), tz=dateutil.tz.tzoffset(None, 0))
        todate = time_util.localize(datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0), tz=dateutil.tz.tzoffset(None, 0))

        logging.info("RANGE: %s %s " % (fromdate, todate))
        out = StringIO.StringIO()
        logs = AuditLogModel.fetch_date_range(fromdate, todate)
        # writer = UnicodeDictWriter(out, fields)
        writer = csv.DictWriter(out, fieldnames=fields)

        writer.writeheader()

        for log in logs.iter():
            if type(log.action) is not 'NoneType':
                log.action.encode('utf-8').strip()

            if type(log.how_the_action_invoked) is unicode:
                log.how_the_action_invoked.encode('utf-8').strip()

            if type(log.app_user_invoked_action) is unicode:
                log.app_user_invoked_action.encode('utf-8').strip()

            if type(log.target_resource) is unicode:
                log.target_resource.encode('utf-8').strip()

            if type(log.target_event_altered) is unicode:
                log.target_event_altered.encode('utf-8').strip()

            if type(log.comment) is not 'NoneType':
                log.comment.encode('utf-8').strip()
                logging.info('COMMENT: %s' % log.comment)

            data = {
                "Timestamp": datetime.strftime(log.created, '%m/%d/%Y %I:%M:%S %p'),
                "The action performed": log.action,
                "How the action was invoked": log.how_the_action_invoked,
                "What App User invoked the action": log.app_user_invoked_action,
                "Targetted user or resource": log.target_resource,
                "Target event altered": log.target_event_altered,
                "Comment": log.comment
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
        fields = ['Timestamp', 'The action performed', 'How the action was invoked',
                  'What App User invoked the action', 'Targetted user or resource', 'Target event altered', 'Comment']

        now = datetime.now()

        # localize

        if key == 'daily':
            yesterday = now - timedelta(days=1)
            fromdate = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
            todate = datetime(now.year, now.month, now.day, 0, 0, 0)
        elif key == 'weekly':
            one_week = timedelta(weeks=1)
            fromdate1 = now - one_week
            fromdate = datetime(fromdate1.year, fromdate1.month, fromdate1.day, 0, 0, 0)
            todate = datetime(now.year, now.month, now.day, 23, 59, 59)

        out = StringIO.StringIO()
        logs = AuditLogModel.fetch_date_range(fromdate, todate)
        writer = UnicodeDictWriter(out, fields)
        writer.writeheader()

        for log in logs:
            if type(log.action) is not 'NoneType':
                log.action.encode('utf-8').strip()

            if type(log.how_the_action_invoked) is unicode:
                log.how_the_action_invoked.encode('utf-8').strip()

            if type(log.app_user_invoked_action) is unicode:
                log.app_user_invoked_action.encode('utf-8').strip()

            if type(log.target_resource) is unicode:
                log.target_resource.encode('utf-8').strip()

            if type(log.target_event_altered) is unicode:
                log.target_event_altered.encode('utf-8').strip()

            if type(log.comment) is not 'NoneType':
                log.comment.encode('utf-8').strip()

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

        if key == 'daily':
            AuditLogModel.daily_notification_on_major_actions(filename, out.getvalue())
        elif key == 'weekly':
            AuditLogModel.weekly_notification_on_major_actions(filename, out.getvalue())

        out.close()

        return 'Email Sent'


def get_midnight(offset):
    midnight = 24 + offset
    if midnight > 24:
        midnight -= 24
    return midnight
