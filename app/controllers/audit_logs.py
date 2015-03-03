from ferris import Controller, route_with, messages
from app.models.calendar import Calendar as calendar_model
import StringIO
import csv
import datetime


class AuditLogs(Controller):
    class Meta:
        prefixes = ('api',)
        components = (messages.Messaging, )
        Model = calendar_model

    @route_with(template='/api/audit_logs/downloads', methods=['GET'])
    def api_generate_report(self):
        fields2 = 'Timestamp    The action performed    How the action was invoked    What App User invoked the action    Targetted user or resource    Target event altered    Comment\n'
        out = StringIO.StringIO()
        logs = calendar_model.query().fetch()
        out.write(fields2)
        for log in logs:
            data = '%s    %s    %s    %s    %s    %s    %s\n' % (datetime.datetime.strftime(log.created, '%m/%d/%Y %I:%M:%S %p'), log.action, log.how_the_action_invoked, log.app_user_invoked_action, log.target_resource, log.target_event_altered, log.comment)

            out.write(data)

        self.response.headers['Content-Type'] = 'application/ms-excel;charset=UTF-8'
        self.response.headers['Content-Transfer-Encoding'] = 'Binary'
        self.response.headers['Content-disposition'] = 'attachment; filename="arista-calendar-log-%s.log"' % datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        self.response.out.write(out.getvalue())
        out.close()
        return self.response


    @route_with(template='/api/audit_logs/downloads/csv', methods=['GET'])
    def api_generate_report_csv(self):
        fields = ['Timestamp','The action performed', 'How the action was invoked',
        'What App User invoked the action', 'Targetted user or resource', 'Target event altered', 'Comment']

        out = StringIO.StringIO()
        # fromdate = datetime.datetime.strptime(self.request.params['fromdate'], "%Y-%m-%d")
        # todate = datetime.datetime.strptime(self.request.params['todate'], "%Y-%m-%d")

        #now = datetime.datetime.now().strftime("%Y-%m-%d")
        #calendar_model.created >= now, calendar_model.created <= now
        logs = calendar_model.query().fetch()
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()

        for log in logs:
            data = {
                'Timestamp': datetime.datetime.strftime(log.created, '%m/%d/%Y %I:%M:%S %p'),
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
        self.response.headers['Content-disposition'] = 'attachment; filename="arista-calendar-log-%s.csv"' % datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        self.response.out.write(out.getvalue())
        out.close()
        return self.response
