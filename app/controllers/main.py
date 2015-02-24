from ferris import Controller, route_with


class Main(Controller):

    @route_with(template='/')
    def show(self):
        self.meta.view.template_name = 'angular/index.html'
