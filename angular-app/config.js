App.config(
    function($routeProvider, $locationProvider) {
        $routeProvider.
            when('/main', {
                templateUrl: '/ng-view/partials/list-calendar-resources-form.html',
                controller: 'MainCtrl'
            }).

            // admin routes
            /*when('/admin', {
                templateUrl: '/ng-view/partials/admin.html',
                controller: 'AdminCtrl'
            }).
*/
            otherwise({
                redirectTo: '/main'
            });

        // $route, $routeParams, $location

        $locationProvider.html5Mode(false);
    }
);
