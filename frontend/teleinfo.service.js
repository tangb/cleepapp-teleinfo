/**
 * Teleinfo service
 * Handle teleinfo module requests
 */
var teleinfoService = function($q, $rootScope, rpcService, raspiotService) {
    var self = this;
    
    /**
     * Init module devices
     */
    self.initDevices = function(devices) {   
        return devices;
    };

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
        for( var i=0; i<raspiotService.devices.length; i++ )
        {   
            if( raspiotService.devices[i].uuid===uuid )
            {   
                raspiotService.devices[i].lastupdate = params.lastupdate;
                raspiotService.devices[i].power = params.power;
                raspiotService.devices[i].currentmode = params.currentmode;
                raspiotService.devices[i].nextmode = params.nextmode;
                break;
            }   
        }   
    });

};
    
var RaspIot = angular.module('RaspIot');
RaspIot.service('sensorsService', ['$q', '$rootScope', 'rpcService', 'raspiotService', sensorsService]);

