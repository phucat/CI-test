
angular.module('app.controllers').controller('MainCtrl', function($log, $window, $scope, $rootScope,aristaFactory, aristaREST, pubsub, loading){
    "use_strict";

    $scope.calendar_resources = [];

    var users = function (){
        $scope.loader = true;
        aristaREST.get_all_users()
        .success(function(data, status, headers, config){
            $scope.users = data;
            $log.info('success users',data);
            $scope.loader = false;
        }).error(function(data, status, headers, config){
            $scope.users = {};
            $log.info('errors users', data);
            $scope.loader = false;
        });
    };

    $scope.cal_resources = function(){
        aristaREST.get_all_resources()
        .success(function(data, status, headers, config){

            $scope.calendar_resources = data.items;

        }).error(function(data, status, headers, config){
            $scope.calendar_resources = {};
        });

        //$scope.resource_loading = loading.new();
        /*aristaREST.get_all_resources().success(function(d){
            if (d.items) $scope.calendar_resources = d.items;
            else $scope.calendar_resources = [];
            if (d.items.previous_page) $scope.previous_page = d.items.previous_page;
            else $scope.previous_page = '';
            if (d.items.next_page) $scope.next_page = d.items.next_page;
            else $scope.next_page = '';
        });*/
    };
    users();
    $scope.cal_resources();

    $scope.show_resourceModal = function(resource,action) {
        $rootScope.model = resource;
        $rootScope.model.action = action;
        var old_resource = [];
        pubsub.publish('modal:resourceModal:show', {}, function(r){
            $log.info('shown resourceModal.', r);
            if(action == 'Create new resource'){
                aristaFactory.create_resource(r);
            }
            else if (action == 'Update resource')
            {
                old_resource = $scope.calendar_resources;
                $scope.calendar_resources = [];
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
                    $window.alert(d.message);
                }).error(function(d){
                    $window.alert(d);
                });
            }
        });
    };

    $scope.show_login = function(email){
        pubsub.publish('modal:loginModal:show', {email: email || ''}, function(r){

        });
    };

    $scope.selectedUser = function (item, model){
        $scope.eventResult = {item: item, model: model};
    };

    $scope.remove_user = function(){
        pubsub.publish('modal:removerModal:show', {}, function(r){
            $log.info('shown removerModal.',r.comment);
            $scope.loader = true;
            aristaFactory.remove_user_from_events($scope.eventResult.item.primaryEmail,r.comment);
            $scope.loader = false;
        });
    }

}).controller('LoginModal', function($scope){
    "use strict";

    // this has to be $scope.model, else it won't work
    $scope.model = {};

    $scope.on_show = function(){
        $scope.model.email = $scope.model.email || '';
        $scope.model.password = $scope.model.password || '';
    };

    $scope.save = function(){
        $scope.callback($scope.model);
    };

    $scope.form_shown = 'login';
    $scope.show_forgot = function(){ $scope.form_shown = 'forgot'; };
    $scope.show_login = function(){ $scope.form_shown = 'login'; };

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
