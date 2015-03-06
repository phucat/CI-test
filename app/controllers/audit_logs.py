from ferris import Controller, route_with, messages, settings
from app.models.audit_log import AuditLog as AuditLogModel
import StringIO
import csv
import logging
from datetime import date, timedelta, datetime
config = settings.get('admin_account')


class AuditLogs(Controller):
    class Meta:
        prefixes = ('api',)
        components = (messages.Messaging, )
        Model = AuditLogModel

    @route_with(template='/api/audit_logs/downloads', methods=['GET'])
    def api_generate_report(self):
        fields2 = 'Timestamp    The action performed    How the action was invoked    What App User invoked the action    Targetted user or resource    Target event altered    Comment\n'
        out = StringIO.StringIO()
        logs = AuditLogModel.list_all()
        out.write(fields2)
        for log in logs:
            data = '%s    %s    %s    %s    %s    %s    %s\n' % (datetime.strftime(log.created, '%m/%d/%Y %I:%M:%S %p'), log.action, log.how_the_action_invoked, log.app_user_invoked_action, log.target_resource, log.target_event_altered, log.comment)

            out.write(data)

        self.response.headers['Content-Type'] = 'application/ms-excel;charset=UTF-8'
        self.response.headers['Content-Transfer-Encoding'] = 'Binary'
        self.response.headers['Content-disposition'] = 'attachment; filename="arista-calendar-log-%s.log"' % datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        self.response.out.write(out.getvalue())
        out.close()
        return self.response


    @route_with(template='/api/auditlogs/generate/report/csv/<key>')
    def api_generate_report_csv(self, key):
        fields = ['Timestamp','The action performed', 'How the action was invoked',
        'What App User invoked the action', 'Targetted user or resource', 'Target event altered', 'Comment']

        now = datetime.now()

        if key == 'daily':
            one_day = timedelta(days=1)
            fromdate = now - one_day
            todate = now
        elif key == 'weekly':
            one_week = timedelta(weeks=1)
            fromdate = now - one_week
            todate = now

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

        # self.response.headers['Content-Type'] = 'application/ms-excel;charset=UTF-8'
        # self.response.headers['Content-Transfer-Encoding'] = 'Binary'
        # self.response.headers['Content-disposition'] = 'attachment; filename="arista-calendar-log-%s.csv"' % datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        # self.response.out.write(out.getvalue())

        filename = "arista-calendar-log-%s.csv" % datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        email = config['email']
        if key == 'daily':
            AuditLogModel.daily_notification_on_major_actions(email, filename, out.getvalue())
        elif key == 'weekly':
            AuditLogModel.weekly_notification_on_major_actions(email, filename, out.getvalue())

        out.close()

        return 'Email Sent'
