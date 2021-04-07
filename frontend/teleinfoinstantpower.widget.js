/**
 * Teleinfo widget
 * Display teleinfo dashboard widget
 */
angular
.module('Cleep')
.directive('widgetTeleinfoinstantpowerDirective', ['$mdDialog', 'cleepService',
function($mdDialog, cleepService) {

    var widgetTeleinfoController = ['$scope', function($scope) {
        var self = this;
        self.tabIndex = 'instant';
        self.instantPowerDevice = $scope.device;
        self.powerConsumptionDevice = null;
        self.hasCharts = cleepService.isAppInstalled('charts');
        self.chartInstantPowerOptions = {
            'type': 'line',
            'fields': ['timestamp', 'power'],
            'color': '#FF5722',
            'label': 'Power (W)'
        };
        self.chartPowerConsumptionOptions = {
            'type': 'multibar',
            'fields': ['timestamp', 'heurescreuses', 'heurespleines'],
            'color': ['#2196F3', '#FF0000'],
            'label': 'Power (W)',
            'timerange': {
                'predefined': 604800,
            },
        };
        self.hasDatabase = cleepService.isAppInstalled('database');
        self.nextModes = {
            '----': { 'label': 'Couleur de demain inconnue', 'icon': 'help-circle-outline', 'style': '' },
            'BLEU': { 'label': 'Couleur bleu', 'icon': 'circle', 'style': 'color: blue;' },
            'BLAN': { 'label': 'Couleur blanc', 'icon': 'circle', 'style': 'color: white;' },
            'ROUG': { 'label': 'Couleur rouge', 'icon': 'circle', 'style': 'color: red;' },
        };
        self.currentModes = {
            'TH..': { 'label': 'Toutes les heures', 'icon': 'circle-outline', 'style': '' },
            'HC..': { 'label': 'Heures creuses', 'icon': 'circle-outline', 'style': '' },
            'HP..': { 'label': 'Heures pleines', 'icon': 'currency-usd-circle', 'style': '' },
            'HN..': { 'label': 'Heures normales', 'icon': 'circle-outline', 'style': '' },
            'PM..': { 'label': 'Heures de pointe', 'icon': 'currency-usd-circle', 'style': '' },
            'HCJB': { 'label': 'Heures creuses jours bleus', 'icon': 'circle-outline', 'style': 'color: blue;' },
            'HCJW': { 'label': 'Heures creuses jours blancs', 'icon': 'circle-outline', 'style': 'color: white;' },
            'HCJR': { 'label': 'Heures creuses jours rouges', 'icon': 'circle-outline', 'style': 'color: red;' },
            'HPJB': { 'label': 'Heures pleines jours bleus', 'icon': 'circle-outline', 'style': 'color: blue;' },
            'HPJW': { 'label': 'Heures pleines jours blancs', 'icon': 'currency-usd-circle-outline', 'style': 'color: white;' },
            'HPJR': { 'label': 'Heures pleines jours rouges', 'icon': 'currency-usd-circle', 'style': 'color: red;' },
        };

        /** 
         * Open dialog
         */
        self.openDialog = function(ev) {
            $mdDialog.show({
                controller: function() { return self; },
                controllerAs: 'teleinfoCtl',
                templateUrl: 'teleinfoDialog.widget.html',
                parent: angular.element(document.body),
                clickOutsideToClose: true,
                targetEvent: ev,
                fullscreen: true,
            }); 
        };

        /**
         * Cancel dialog
         */
        self.cancelDialog = function() {
            $mdDialog.cancel();
        };

        /**
         * Init controller
         */
        self.$onInit = function()
        {
            // get teleinfo devices
            for( var i=0; i<cleepService.devices.length; i++ ) {
                if( cleepService.devices[i].type==='teleinfopowerconsumption' ) {
                    self.powerConsumptionDevice = cleepService.devices[i];
                    break;
                }
            }
        };

    }];

    return {
        restrict: 'EA',
        templateUrl: 'teleinfoinstantpower.widget.html',
        replace: true,
        scope: {
            'device': '='
        },
        controller: widgetTeleinfoController,
        controllerAs: 'widgetCtl',
    };
}]);

