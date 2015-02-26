
angular.module('app.controllers').controller('MainCtrl', function($log, $scope, $rootScope,aristaFactory, aristaREST, pubsub){
    "use_strict";

    $scope.calendar_resources = [];
    $scope.counter = 0;

    var users = function (){
        $log.info('loading users...');
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

    var cal_resources = function(){
        aristaREST.get_all_resources()
        .success(function(data, status, headers, config){
            $scope.calendar_resources = data.items;
        }).error(function(data, status, headers, config){
            $scope.calendar_resources = {};
        });
    };
    users();
    cal_resources();

    $scope.show_resourceModal = function(resource,action) {
        $rootScope.model = resource;
        $rootScope.model.action = action;
        $log.info(action);
        pubsub.publish('modal:resourceModal:show', {}, function(r){
            $log.info('shown resourceModal.', r);
            if(action == 'Create new resource'){
                aristaFactory.create_resource(r);
            }
            else if (action == 'Update resource')
            {
                aristaFactory.update_resource(r);
            }
        });
    };

    $scope.show_login = function(email){
        pubsub.publish('modal:loginModal:show', {email: email || ''}, function(r){

        });
    };

    $scope.selectedUser = function (item, model){
        $scope.counter++;
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
