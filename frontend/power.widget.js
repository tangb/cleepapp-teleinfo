/**
 * Power widget
 * Display power dashboard widget
 */
var widgetPowerDirective = function(raspiotService, teleinfoService) {

    var widgetPowerController = ['$scope', function($scope) {
        var self = this;
        self.device = $scope.device;
        self.graphOptions = {
            'type': 'bar',
            'fields': ['timestamp', 'power'],
            'color': '#FF6600',
            'label': 'Power (W)'
        };
        self.hasDatabase = raspiotService.isAppInstalled('database');
    }];

    return {
        restrict: 'EA',
        templateUrl: 'power.widget.html',
        replace: true,
        scope: {
            'device': '='
        },
        controller: widgetPowerController,
        controllerAs: 'widgetCtl'
    };
};

var RaspIot = angular.module('RaspIot');
RaspIot.directive('widgetPowerDirective', ['raspiotService', 'teleinfoService', widgetPowerDirective]);

