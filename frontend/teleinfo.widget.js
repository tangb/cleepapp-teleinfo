/**
 * Teleinfo widget
 * Display teleinfo dashboard widget
 */
var widgetTeleinfoDirective = function(raspiotService, teleinfoService) {

    var widgetTeleinfoController = ['$scope', function($scope) {
        var self = this;
        self.device = $scope.device;
        self.hasCharts = raspiotService.isAppInstalled('charts');
        self.chartOptions = {
            'type': 'line',
            'fields': ['timestamp', 'power'],
            'color': '#FF6600',
            'label': 'Instant power (W)'
        };
        self.hasDatabase = raspiotService.isAppInstalled('database');
    }];

    return {
        restrict: 'EA',
        templateUrl: 'teleinfo.widget.html',
        replace: true,
        scope: {
            'device': '='
        },
        controller: widgetTeleinfoController,
        controllerAs: 'widgetCtl'
    };
};

var RaspIot = angular.module('RaspIot');
RaspIot.directive('widgetTeleinfoDirective', ['raspiotService', 'teleinfoService', widgetTeleinfoDirective]);

