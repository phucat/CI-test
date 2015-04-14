
angular.module('app.controllers').controller('MainCtrl', function($log, $window, $scope, $rootScope,aristaFactory, aristaREST, pubsub, loading){
    "use_strict";
    $scope.tz_offset = new Date().getTimezoneOffset()/60*-1;
    $scope.calendar_resources = [];

    $scope.load_identity = function(reload_route) {
        $scope.identity_loading = loading.new();
    };
    $scope.load_identity();

    $scope.users = [];
    var users_search = [];

    var users = function (){
        $scope.loader = true;
        aristaREST.get_all_users()
        .success(function(data, status, headers, config){
            users_search = data.slice(0);
            //$log.info('success users',data);
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

    var previous_start = '';
    var previous_list = []
    $scope.cal_resources = function(feed){
        $scope.identity_loading = loading.new();
        $scope.calendar_resources = [];
        $scope.previous_page = '';
        $scope.next_page = '';
        aristaREST.get_all_resources(feed)
        .success(function(data, status, headers, config){

            if (data.items) $scope.calendar_resources = data.items;
            else $scope.calendar_resources = [];
            console.log(feed);
            if(previous_list.indexOf(data.page)==-1) previous_list.push(data.page);


            if (feed != undefined){

                current_page = previous_list.indexOf(data.page)-1;
                console.log('current_page:',current_page);
                console.log(typeof previous_list[current_page]);
                if(previous_list.indexOf(data.page)==-1) previous_list.push(data.page);
                else previous_start = previous_list[current_page];

                console.log('previous_list:',previous_list);
                console.log('previous_start:',previous_start);
                if (previous_start)
                {
                    $scope.previous_page = previous_start;
                }
            }
            else{
                // if (data.previous) $scope.previous_page = data.previous;
                $scope.previous_page = '';
            }

            if (data.next) $scope.next_page = data.next;
            else $scope.next_page = '';

            console.log('previous',data.previous);
            console.log('Next',data.next);
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
                            $window.alert("There is an existing Resource with that ID. Please try again.");
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
                    $scope.cal_resources();
                    $log.info('success', d);
                    $window.alert(d.message);
                }).error(function(d){
                    $log.error('failed', d);
                    if(d.code == 500)
                    {
                        $window.alert("There was an error when attempting to connect to the Resource API. Please wait a few moments and try again.");
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
                    $log.info(d);
                    $window.alert('There was an error when attempting to connect to the server. Please wait a few moments and try again.');
                });
            });
        }
        else
        {
            alert('Please select a user to be removed.');
        }
    }


}).controller('TzCtrl', function($scope){
    "use strict";
    $scope.tz_offset = new Date().getTimezoneOffset()/60;

}).controller('ResourceModal', function($scope, $rootScope, $log){
    "use strict";

    // this has to be $scope.model, else it won't work
    $scope.model = {};
    $scope.on_show = function(){
        $scope.model.title = $rootScope.model.action || '';
        $scope.model.resourceId = $rootScope.model.resourceId || '';
        $scope.model.resourceCommonName = $scope.model.resourceCommonName || $rootScope.model.resourceCommonName;
        $scope.model.old_resourceCommonName = $rootScope.model.resourceCommonName || '';
        $scope.model.old_resourceType = $rootScope.model.resourceType || '';
        $scope.model.old_resourceDescription = $rootScope.model.resourceDescription || '';
        $scope.model.resourceType = $scope.model.resourceType || $rootScope.model.resourceType;
        $scope.model.resourceDescription = $scope.model.resourceDescription || $rootScope.model.resourceDescription;
        $scope.model.resourceEmail = $scope.model.resourceEmail || $rootScope.model.resourceEmail;
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
}).controller('ResourceTableCtrl', function($log, $window, $scope, $rootScope,aristaFactory, aristaREST, pubsub, loading){
    "use_strict";

    $scope.itemsPerPage = 50;
    $scope.currentPage = 0;

    $scope.range = function() {
        var rangeSize = ($scope.pageCount() >= 10) ? 10 : $scope.pageCount();
        var ret = [];
        var start;

        start = $scope.currentPage;
        if ( start > $scope.pageCount()-rangeSize ) {
          start = $scope.pageCount()-rangeSize;
        }

        for (var i=start; i<start+rangeSize; i++) {
          ret.push(i);
        }
        return ret;
    };


    $scope.prevPage = function() {
        $scope.identity_loading = loading.new();
        if ($scope.currentPage > 0) {
          $scope.currentPage--;
        }
    };

    $scope.prevPageDisabled = function() {
        return $scope.currentPage === 0 ? "disabled" : "";
    };

    $scope.nextPage = function() {
        $scope.identity_loading = loading.new();
        if ($scope.currentPage < $scope.pageCount() - 1) {
          $scope.currentPage++;
        }
    };

    $scope.nextPageDisabled = function() {
        return $scope.currentPage === $scope.pageCount() - 1 ? "disabled" : "";
    };

    $scope.pageCount = function() {
        return Math.ceil($scope.total/$scope.itemsPerPage);
    };

    $scope.setPage = function(n) {
        if (n > 0 && n < $scope.pageCount()) {
          $scope.currentPage = n;
        }
    };

    var promise = aristaFactory.resource_list('feed');
        promise.then(
        function(payload) {
            $scope.pagedItems = aristaFactory.get($scope.itemsPerPage, $scope.itemsPerPage);
            $scope.total = aristaFactory.total();
        },
        function(errorPayload) {

            $log.error(errorPayload.status);
            $log.error('failed', errorPayload);

        });

    $scope.$watch("currentPage", function(newValue, oldValue) {
        if ($scope.pagedItems){
            $scope.pagedItems = aristaFactory.get(newValue*$scope.itemsPerPage, $scope.itemsPerPage);
            $scope.total = aristaFactory.total();

            console.log('page items',$scope.pagedItems);
            console.log('page count',$scope.pageCount);
            console.log('next_page',$scope.nextPage);
            console.log('previous_page',$scope.previousPage);
            console.log('current_page',$scope.currentPage);
        }

    });


});
