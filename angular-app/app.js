/*jshint browser:true, globalstrict:true, eqnull:true */
/*global angular:true*/

'use strict';

angular.module('cs.utilities', ['cs.pubsub', 'cs.passive-messenger', 'cs.loading', 'cs.modal']);
angular.module('app.services', ['cs.utilities',]);
angular.module('app.controllers', ['app.services',]);
angular.module('app.directives', ['cs.utilities']);


/* Main Application Module */
var App = angular.module('app', ['app.services', 'app.directives', 'app.controllers', 'ngRoute', 'ngSanitize','ui.select']).run(function($log, passive_messenger, $timeout){
    $log.info('Angular App Loaded');
    $timeout(function(){ passive_messenger.success('Loaded'); });
});
