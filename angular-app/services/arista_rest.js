angular.module('app.services').
factory('aristaREST', function($http) {

    var service = {};

    service.get_all_users = function (){
        return $http.get('/api/calendar/users');
    };

    service.get_all_resources = function (feed){
        if(!feed){
            feed = 'feed';
        }
        return $http.get('/api/calendar/resource/' + feed);
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
        return $http.post('/api/calendar/resource/update' , resource);
    };

    service.get_scheduled_pending_users = function(url) {
        return $http.get(url || '/api/schedule/list/pending');
    };

    service.update_schedule_user = function(email,status){
        return $http.post('/api/schedule/update/user', {'email':email, 'status': status});
    };

    service.remove_schedule_user = function(email,status){
        return $http.post('/api/schedule/cancel/user', {'email':email, 'status': status});
    };



    return service;
});
