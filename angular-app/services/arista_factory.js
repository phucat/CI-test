angular.module('app.services').
factory('aristaFactory', function($window, $log, $http, aristaREST){
    var service = {};
    var count = 0;
    var list = [];
    var promise;

    service.fetch_all_users = function(){
        return aristaREST.get_all_users()
            .success(function(d){
                count = (d !== undefined) ? d.length : 0;
                if (count > 0) list = d;
            });
    };

    service.fetch_all_resources = function(){
        return aristaREST.get_all_resources()
            .success(function(d){
                count = (d.items !== undefined) ? d.items.length : 0;
                if (count > 0) list = d.items;
            });
    };

    service.create_resource = function(resource) {
        return aristaREST.create_resource(resource)
            .success(function(res){
                $log.info('success create resource', res);
            }).error(function(res){
                $log.info('error create resource', res);
            })
    };

    service.list = function(){
        return list;
    };

    service.count = function(){
        return count;
    };

    service.resource_list = function(feed){
        return aristaREST.get_all_resources(feed)
        .success(function(d, status, headers, config){
            count = (d.items !== undefined) ? d.items.length : 0;
            if (count > 0) list = d.items;

        }).error(function(d, status, headers, config){
            list = [];
        });
    }

    service.get = function(offset, limit){
        console.log('get', list );
        return list.slice(offset, offset+limit);
    }

    service.total= function() {
        return count;
    }

    return service;
});
