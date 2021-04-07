/**
 * Teleinfo config directive
 * Handle teleinfo module configuration
 */
angular
.module('Cleep')
.directive('teleinfoConfigComponent', ['teleinfoService', 'cleepService',
function(teleinfoService, cleepService) {

    var teleinfoController = function() {
        var self = this;
        self.tabIndex = 'teleinfo';
        self.port = '';
        self.teleinfo = [];
        self.extra = {
            'ADCO':     {'label': 'Adresse du concentrateur de téléreport', 'unit': ''},
            'OPTARIF':  {'label': 'Option tarifaire choisie', 'unit': ''},
            'BASE':     {'label': 'Index option base', 'unit': 'Wh'},
            'HCHC':     {'label': 'Index option heures creuses', 'unit': 'Wh'},
            'HCHP':     {'label': 'Index option heures pleines', 'unit': 'Wh'},
            'EJPHN':    {'label': 'Index option EJP heures normales', 'unit': 'Wh'},
            'EJPHPN':   {'label': 'Index option EJP heures de pointe mobile', 'unit': 'Wh'},
            'PTEC':     {'label': 'Période tarifaire en cours', 'unit': ''},
            'MOTDETAT': {'label': 'Mot d\'état du compteur', 'unit': ''},
            'ISOUSC':   {'label': 'Intensité souscrite', 'unit': 'A'},
            'BBRHCJB':  {'label': 'Index option tempo heures creuses jours bleus', 'unit': 'Wh'},
            'BBRHPJB':  {'label': 'Index option tempo heures pleines jours bleus', 'unit': 'Wh'},
            'BBRHCJW':  {'label': 'Index option tempo heures creuses jours blancs', 'unit': 'Wh'},
            'BBRHPJW':  {'label': 'Index option tempo heures pleines jours blancs', 'unit': 'Wh'},
            'BBRHCJR':  {'label': 'Index option tempo heures creuses jours rouges', 'unit': 'Wh'},
            'BBRHPJR':  {'label': 'Index option tempo heures pleines jours rouges', 'unit': 'Wh'},
            'PEJP':     {'label': 'Préavis début EJP (30min)', 'unit': 'min'},
            'DEMAIN':   {'label': 'Couleur du lendemain', 'unit': ''},
            'IINST':    {'label': 'Intensité instantanée', 'unit': 'A'},
            'ADPS':     {'label': 'Avertissement de dépassement de puissance souscrite', 'unit': 'A'},
            'IMAX':     {'label': 'Intensité maximale appelée', 'unit': 'A'},
            'HHPHC':    {'label': 'Horaires heures pleines heures creuses', 'unit': ''},
            'PAPP':     {'label': 'Puissance apparente', 'unit': 'VA'},
        };

        /**
         * Init controller
         */
        self.$onInit = function() {
            console.log('init teleingfo')
            cleepService.getModuleConfig('teleinfo')
                .then(function(config) {
                    self.port = config.port
                    if( !self.port ) {
                        // switch to install tab if port not specified
                        self.tabIndex = 'install';
                    }
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
                .then(function(resp) {
                    for(var index in resp.data) {
                        self.teleinfo.push({
                            'key': resp.data[index].key,
                            'value': resp.data[index].value,
                            'unit': self.extra[resp.data[index].key].unit,
                            'label': self.extra[resp.data[index].key].label,
                        });
                    }
                });
        };

    };

    return {
        templateUrl: 'teleinfo.config.html',
        replace: true,
        scope: true,
        controller: teleinfoController,
        controllerAs: 'teleinfoCtl',
    };
}]);

