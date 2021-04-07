/**
 * Teleinfo service
 * Handle teleinfo module requests
 */
angular
.module('Cleep')
.service('teleinfoService', ['$rootScope', 'rpcService', 'cleepService',
function($rootScope, rpcService, cleepService) {
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
        for( var i=0; i<cleepService.devices.length; i++ ) {   
            if( cleepService.devices[i].uuid===uuid ) {
                cleepService.devices[i].lastupdate = params.lastupdate;
                cleepService.devices[i].power = params.power;
                cleepService.devices[i].currentmode = params.currentmode;
                cleepService.devices[i].nextmode = params.nextmode;
                cleepService.devices[i].heurescreuses = params.heurescreuses;
                cleepService.devices[i].heurespleines = params.heurespleines;
                cleepService.devices[i].subscription = params.subscription;
                break;
            }   
        }   
    });

}]);

