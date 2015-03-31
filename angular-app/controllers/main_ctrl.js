
angular.module('app.controllers').controller('MainCtrl', function($log, $window, $scope, $rootScope,aristaFactory, aristaREST, pubsub, loading){
    "use_strict";

    $scope.calendar_resources = [];

    $scope.load_identity = function(reload_route) {
        $scope.identity_loading = loading.new();
    };
    $scope.load_identity();

    $scope.users = [];
    var users_search = []

    var users = function (){
        $scope.loader = true;
        aristaREST.get_all_users()
        .success(function(data, status, headers, config){
            users_search = data.slice(0);
            $log.info('success users',data);
            $scope.loader = false;
        }).error(function(data, status, headers, config){
            $scope.users = {};
            $log.info('errors users', data);
            $scope.loader = false;
        });
    };

    $scope.refreshUsers = function (query) {
        if (query.length >= 3){
            $scope.users = [];
            regexp = new RegExp(query, 'i');

            for (var i = 0; i < users_search.length; i++) {
                var node = users_search[i];
                if (node.primaryEmail.search(regexp) > -1 || node.name.fullName.search(regexp) > -1) {
                    $scope.users.push(node);
                }
            }
        }
    };

    $scope.cal_resources = function(feed){
        $scope.identity_loading = loading.new();
        $scope.calendar_resources = []
        aristaREST.get_all_resources(feed)
        .success(function(data, status, headers, config){

            if (data.items) $scope.calendar_resources = data.items;
            else $scope.calendar_resources = [];

            if (data.previous) $scope.previous_page = data.previous;
            else $scope.previous_page = '';

            if (data.next) $scope.next_page = data.next;
            else $scope.next_page = '';

        }).error(function(data, status, headers, config){
            $scope.calendar_resources = [];
        });
    };

    users();
    $scope.cal_resources();

    $scope.show_resourceModal = function(resource,action) {
        $rootScope.model = resource;
        $rootScope.model.action = action;
        var old_resource = [];
        pubsub.publish('modal:resourceModal:show', {}, function(r){
            old_resource = $scope.calendar_resources;
            $scope.calendar_resources = [];
            if(action == 'Create new resource'){
                var promise = aristaREST.create_resource(r);
                    $scope.cal_resources();
                    promise.then(
                    function(payload) {
                        $window.alert(payload.data.message);
                        $log.info(payload.status);
                        $log.info('success',payload.data);
                    },
                    function(errorPayload) {
                        if (errorPayload.status == 406)
                        {
                            $window.alert("There is an existing Resource with that ID");
                        }
                        else if (errorPayload.status == 402)
                        {
                            $window.alert("There is an existing Resource with that Name");
                        }
                        else{
                            $window.alert('Server Error.');
                        }

                        $scope.show_resourceModal(r,'Create new resource');
                        $log.error(errorPayload.status);
                        $log.error('failed', errorPayload);

                    });
            }
            else if (action == 'Update resource')
            {
                aristaREST.update_resource(r)
                .success(function(d){
                    for (var i = old_resource.length - 1; i >= 0; i--) {
                        if (old_resource[i].resourceId == d.items[0].resourceId){
                            old_resource[i].resourceCommonName = d.items[0].resourceCommonName;
                            old_resource[i].resourceDescription = d.items[0].resourceDescription;
                            old_resource[i].resourceType = d.items[0].resourceType;
                        }
                    }
                    $scope.calendar_resources = old_resource;
                    $log.info('success', d);
                    $window.alert(d.message);
                }).error(function(d){
                    $log.error('failed', d);
                    if(d.code == 500)
                    {
                        $window.alert('You are not authorized to use this Calendar Resource API.');
                    }
                    else{
                        $window.alert(d.error);
                    }

                });
            }
        });
    };

    $scope.selectedUser = function (item, model){
        $scope.eventResult = {item: item, model: model};
    };

    $scope.remove_user = function(){
        if ($scope.eventResult != undefined){
            pubsub.publish('modal:removerModal:show', {}, function(r){
                $log.info('shown removerModal.',r.comment);
                $scope.loader = true;
                aristaREST.remove_user_from_events($scope.eventResult.item.primaryEmail,r.comment)
                .success(function(d){
                    $scope.loader = false;
                    $window.alert(d.message);
                }).error(function(d){
                    $window.alert(d);
                });
            });
        }
        else
        {
            alert('Please select a user to be removed.');
        }
    }

}).controller('ResourceModal', function($scope, $rootScope, $log){
    "use strict";

    // this has to be $scope.model, else it won't work
    $scope.model = {};
    $scope.on_show = function(){
        $scope.model.title = $rootScope.model.action || '';
        $scope.model.resourceId = $rootScope.model.resourceId || '';
        $scope.model.resourceCommonName = $scope.model.resourceCommonName || $rootScope.model.resourceCommonName;
        $scope.model.old_resourceCommonName = $rootScope.model.resourceCommonName || '';
        $scope.model.resourceType = $scope.model.resourceType || $rootScope.model.resourceType;
        $scope.model.resourceDescription = $scope.model.resourceDescription || $rootScope.model.resourceDescription;
    };

    $scope.save = function(){
       $scope.callback($scope.model);
    };

}).controller('RemoverModal', function($scope){
    "use_strict";
    $scope.model = {};

    $scope.on_show = function(){
        $scope.model.comment = $scope.model.comment || '';
    };

    $scope.save = function(){
       $scope.callback($scope.model);
    };
});
