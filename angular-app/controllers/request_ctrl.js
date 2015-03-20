angular.module('app.controllers').controller('RequestCtrl', function($log, $window, $scope, $rootScope, aristaREST, pubsub, loading){
    "use_strict";

    $scope.get_scheduled_pending_users = function(url)
    {
        $scope.loader = true;
        $scope.identity_loading = loading.new();
        $scope.identity_loading.watch(aristaREST.get_scheduled_pending_users(url))
        .success(function(data, status, headers, config){
            $scope.loader = false;
            if (data.items) $scope.pending_users = data.items;
            else $scope.pending_users = [];

            if (data.previous_page) $scope.previous_page = data.previous_page;
            else $scope.previous_page = '';

            if (data.next_page) $scope.next_page = data.next_page;
            else $scope.next_page = '';
        }).error(function(data, status, headers, config){
            $scope.users = {};
            $log.info('errors users', data);
            $scope.loader = false;
        });
    }

    $scope.get_scheduled_pending_users();

    $scope.remove_user = function(email){
        pubsub.publish('modal:userDeleteModal:show', {}, function(r){
            $scope.loader = true;
            $scope.identity_loading = loading.new();
            $scope.identity_loading.watch(aristaREST.update_schedule_user(email,'Approve'))
            .success(function(d){
                $scope.loader = false;
                $scope.get_scheduled_pending_users();
                $window.alert('The request has been ' + d);
            }).error(function(d){
                $scope.loader = false;
                $scope.get_scheduled_pending_users();
                $window.alert(d.error);
            });

        });
    }

    $scope.cancel_user = function(email){
        $scope.identity_loading = loading.new();
        $scope.loader = true;
        aristaREST.update_schedule_user(email,'Cancel')
        .success(function(d){
            $scope.loader = false;
            $scope.get_scheduled_pending_users();
            $window.alert('The request has been cancelled.');
        }).error(function(d){
            $scope.loader = false;
            $scope.get_scheduled_pending_users();
            $window.alert('The removal request for '+ email +' has been processed.');
        });
    };

}).controller('UserDeleteModal', function($scope){
    "use_strict";
    $scope.model = {};

    $scope.on_show = function(){

    };

    $scope.confirm = function(){
       $scope.callback($scope.model);
    };
});
