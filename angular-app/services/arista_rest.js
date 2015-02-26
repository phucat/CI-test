angular.module('app.services').
factory('aristaREST', function($http) {

    var service = {};

    service.get_all_users = function (){
        return $http.get('/api/calendar/users');
    };

    service.get_all_resources = function (){
        return $http.get('/api/calendar/resource');
    };

    service.get_all_events = function (){
        return $http.get('/api/calendar/events');
    };

    service.remove_user_from_events = function (email, comment){
        return $http.post('/api/calendar/remove_user/events/' + email , {'comment':comment});
    };

    service.create_resource = function(resource) {
        return $http.post('/api/calendar/resource/create', resource);
    }
    service.update_resource = function(resource) {
        return $http.post('/api/calendar/update' , resource);
    };

    return service;
});
