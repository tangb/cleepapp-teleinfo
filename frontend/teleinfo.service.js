/**
 * Teleinfo service
 * Handle teleinfo module requests
 */
var teleinfoService = function($rootScope, rpcService, raspiotService) {
    var self = this;
    
    /**
     * Get teleinfo data
     */
    self.getTeleinfo = function() {
        return rpcService.sendCommand('get_teleinfo', 'teleinfo');
    };

    /**
     * Catch power update event
     */
    $rootScope.$on('teleinfo.power.update', function(event, uuid, params) {
        for( var i=0; i<raspiotService.devices.length; i++ ) {   
            if( raspiotService.devices[i].uuid===uuid ) {
                raspiotService.devices[i].lastupdate = params.lastupdate;
                raspiotService.devices[i].power = params.power;
                raspiotService.devices[i].currentmode = params.currentmode;
                raspiotService.devices[i].nextmode = params.nextmode;
                raspiotService.devices[i].heurescreuses = params.heurescreuses;
                raspiotService.devices[i].heurespleines = params.heurespleines;
                raspiotService.devices[i].subscription = params.subscription;
                break;
            }   
        }   
    });

};
    
var RaspIot = angular.module('RaspIot');
RaspIot.service('teleinfoService', ['$rootScope', 'rpcService', 'raspiotService', teleinfoService]);

