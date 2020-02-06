/**
 * Teleinfo config directive
 * Handle teleinfo module configuration
 */
var teleinfoConfigDirective = function(teleinfoService, raspiotService) {

    var teleinfoController = function()
    {
        var self = this;
        self.port = '';
        self.teleinfo = {};

        /**
         * Init controller
         */
        self.init = function()
        {
            raspiotService.getModuleConfig('teleinfo')
                .then(function(config) {
                    self.port = config.port
                })
                .then(function() {
                    // load current teleinfo data
                    self.getTeleinfo();
                });
        };

        /**
         * Get teleinfo data
         */
        self.getTeleinfo = function() {
            teleinfoService.getTeleinfo()
                .then(function(data) {
                    self.teleinfo = data.toArray();
                });
        };

    };

    var teleinfoLink = function(scope, element, attrs, controller) {
        controller.init();
    };

    return {
        templateUrl: 'teleinfo.config.html',
        replace: true,
        scope: true,
        controller: teleinfoController,
        controllerAs: 'teleinfoCtl',
        link: teleinfoLink
    };
};

var RaspIot = angular.module('RaspIot');
RaspIot.directive('teleinfoConfigDirective', ['teleinfoService', teleinfoConfigDirective])

