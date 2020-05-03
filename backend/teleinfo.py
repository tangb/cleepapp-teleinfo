#!/usr/bin/env python
# -*- coding: utf-8 -*-

#fix teleinfo import. If not specified import local one that does not contain Parser and other stuff
#this is fixed in python3.X
from __future__ import absolute_import
import logging
import time
from raspiot.exception import CommandError, MissingParameter, InvalidParameter
from raspiot.libs.internals.task import Task
from raspiot.core import RaspIotModule
from raspiot.common import CATEGORIES
import glob
from teleinfo import Parser
from teleinfo.hw_vendors import UTInfo2

__all__ = [u'Teleinfo']

class Teleinfo(RaspIotModule):
    """
    Teleinfo application.
    Returns current France Enedis electricity provider.
    This application uses MicroTeleinfo dongle built by Charles Hallard (http://hallard.me/utinfo/)

    Note:
        python library: https://github.com/demikl/python-teleinfo
        Teleinfo protocol description: https://www.planete-domotique.com/blog/2010/03/30/la-teleinformation-edf/
    """
    MODULE_AUTHOR = u'Cleep'
    MODULE_VERSION = u'1.0.0'
    MODULE_PRICE = 0
    MODULE_DEPS = []
    MODULE_CATEGORY = CATEGORIES.SERVICE
    MODULE_DESCRIPTION = u'Gets house power consumption infos from Enedis electric power meter'
    MODULE_LONGDESCRIPTION = u'This application reads data from Enedis Linky (or older compatible version) house power meter and make<br>\
                             possible to monitor your house power consumption usage and build charts on some useful indicators.'
    MODULE_TAGS = [u'electricity', u'power', u'teleinfo', u'enedis', u'edf', u'erdf', u'engie']
    MODULE_COUNTRY = u'fr'
    MODULE_URLINFO = u'https://github.com/tangb/cleepmod-teleinfo'
    MODULE_URLHELP = u'https://github.com/tangb/cleepmod-teleinfo/wiki'
    MODULE_URLSITE = u'https://www.enedis.fr/'
    MODULE_URLBUGS = u'https://github.com/tangb/cleepmod-teleinfo/issues'

    MODULE_CONFIG_FILE = u'teleinfo.conf'
    DEFAULT_CONFIG = {
        u'port': None,
        u'previousconsoheurespleines': None,
        u'previousconsoheurescreuses': None,
    }

    TELEINFO_TASK_DELAY = 60 # seconds
    USB_PATH = u'/dev/serial/by-id/'
    VA_FACTOR = 220

    def __init__(self, bootstrap, debug_enabled):
        """
        Constructor

        Args:
            bootstrap (dict): bootstrap objects
            debug_enabled (bool): flag to set debug level to logger
        """
        #init
        RaspIotModule.__init__(self, bootstrap, debug_enabled)

        #members
        self.teleinfo_task = None
        self.instant_power_device_uuid = None
        self.power_consumption_device_uuid = None
        self.last_raw = {}
        self.__teleinfo_parser = None
        self.__last_conso_heures_creuses = 0
        self.__last_conso_heures_pleines = 0

        #events
        self.power_update_event = self._get_event('teleinfo.power.update')
        self.consumption_update_event = self._get_event('teleinfo.consumption.update')
        
    def _configure(self):
        """
        Configure module
        """
        #configure devices
        self._configure_devices()

        #configure hardware
        if self._configure_hardware():
            #update values at startup
            self.logger.debug(u'Update data at startup')
            self._teleinfo_task()

        #start teleinfo task
        self._start_teleinfo_task()

    def _configure_devices(self):
        """
        Configure teleinfo devices
        """
        instant_power_default_device = {
            u'type': u'teleinfoinstantpower',
            u'name': u'Instant power',
            u'lastupdate': None,
            u'power': 0,
            u'currentmode': None,
            u'nextmode': None,
        }
        power_consumption_default_device = {
            u'type': u'teleinfopowerconsumption',
            u'name': u'Power consumption',
            u'lastupdate': None,
            u'heurescreuses': 0,
            u'heurespleines': 0,
        }

        #get devices
        for uuid, device in self._get_devices().iteritems():
            if device[u'type']==u'teleinfoinstantpower':
                self.instant_power_device_uuid = uuid
            elif device[u'type']==u'teleinfopowerconsumption':
                self.power_consumption_device_uuid = uuid

        #add missing devices
        if not self.instant_power_device_uuid:
            self.logger.debug(u'Adding new instant power device')
            device = self._add_device(instant_power_default_device)
            if not device: # pragma: no cover
                raise Exception(u'Unable to add new device')
            self.instant_power_device_uuid = device[u'uuid']
        if not self.power_consumption_device_uuid:
            self.logger.debug(u'Adding new power consumption device')
            device = self._add_device(power_consumption_default_device)
            if not device: # pragma: no cover
                raise Exception(u'Unable to add new device')
            self.power_consumption_device_uuid = device[u'uuid']

        self.logger.debug(u'Found instant power device "%s"' % self.instant_power_device_uuid)
        self.logger.debug(u'Found power consumption device "%s"' % self.power_consumption_device_uuid)

    def _configure_hardware(self):
        """
        Configure hardware
        Search device (device path) and initialize parser

        Returns:
            bool: True if hardware configured successfully, False otherwise
        """
        #scan dongle port
        self.logger.trace(u'Scanning "%s" for devices' % self.USB_PATH)
        devices = [path for path in [f for f in glob.glob(self.USB_PATH + u'*')] if path.find(u'TINFO')>0]
        self.logger.debug('Found devices: %s' % devices)
        if len(devices)==0:
            self.logger.warn(u'No Teleinfo hardware found, teleinfo disabled')
            return False

        #get only one device
        port = devices[0]
        self._set_config_field(u'port', port)
        self.logger.info(u'Using device "%s" as teleinfo port' % port)

        #init parser
        try:
            self.__teleinfo_parser = Parser(UTInfo2(port=port))
            return True

        except:
            self.logger.exception(u'Fatal error initializing teleinfo parser. Are you using MicroTeleinfo dongle?')
            return False

    def _stop(self):
        """
        Stop module
        """
        self._stop_teleinfo_task()

    def _start_teleinfo_task(self):
        """
        Start teleinfo task
        """
        if self.teleinfo_task is None:
            self.teleinfo_task = Task(self.TELEINFO_TASK_DELAY, self._teleinfo_task, self.logger)
            self.teleinfo_task.start()

    def _stop_teleinfo_task(self):
        """
        Stop weather task
        """
        if self.teleinfo_task is not None:
            self.teleinfo_task.stop()
            self.teleinfo_task = None

    def _restart_teleinfo_task(self):
        """
        Restart teleinfo task
        """
        self._stop_teleinfo_task()
        self._start_teleinfo_task()

    def event_received(self, event):
        """ 
        Event received from bus

        Params:
            event (MessageRequest): event data
        """
        self.logger.trace(u'Event received %s' % event)
        #compute and send consumption event once a day at midnight
        #previous day consumption is stored in configuration file to take care of device reboot
        if event[u'event']==u'parameters.time.now' and event[u'params'][u'hour']==0 and event[u'params'][u'minute']==0:
            config = self._get_config()
            if config[u'previousconsoheurescreuses'] is not None and config[u'previousconsoheurespleines'] is not None:
                params = {
                    u'lastupdate': int(time.time()),
                    u'heurescreuses': (self.__last_conso_heures_creuses - config[u'previousconsoheurescreuses']),
                    u'heurespleines': (self.__last_conso_heures_pleines - config[u'previousconsoheurespleines']),
                }

                #send consumption event and update device
                self.logger.trace(u'Send consumption update event with params: %s' % params)
                self._update_device(self.instant_power_device_uuid, params)
                self.consumption_update_event.send(params=params, device_id=self.power_consumption_device_uuid)

            #save last power consumption in config file
            self.logger.info(u'Save last power consumption of the day')
            self._update_config({
                u'previousconsoheurescreuses': self.__last_conso_heures_creuses,
                u'previousconsoheurespleines': self.__last_conso_heures_pleines,
            })

    def _teleinfo_task(self):
        """
        Teleinfo task reads data from dongle and store current consumption.
        It also emit power event.
        """
        try:
            if not self._get_config_field(u'port'):
                return

            self.logger.trace(u'Update teleinfo')

            #read teleinfo data
            raw = self._get_teleinfo_raw_data()
            self.logger.debug(u'Raw teleinfo: %s' % raw)

            #compute some values
            if not raw:
                return

            # save as soon as possible some data
            if not self.last_raw:
                self.last_raw = raw

            keys = set(raw.keys())
            #power consumption
            if set([u'HCHC', u'HCHP']).issubset(keys):
                #handle heures creuses/pleines
                self.logger.trace(u'Handle heures creuses/pleines')
                ints = self.to_int(raw, [u'HCHC', u'HCHP'])
                if ints:
                    self.__last_conso_heures_creuses = ints[u'HCHC']
                    self.__last_conso_heures_pleines = ints[u'HCHP']
            elif set([u'EJPHN', u'EJPHPM']).issubset(keys):
                #handle EJP
                self.logger.trace(u'Handle EJP')
                ints = self.to_int(raw, [u'EJPHN', u'EJPHPM'])
                if ints:
                    self.__last_conso_heures_creuses = ints[u'EJPHN']
                    self.__last_conso_heures_pleines = ints[u'EJPHPM']
            elif set([u'BBRHCJB', u'BBRHPJB', u'BBRHCJW', u'BBRHPJW', u'BBRHCJR', u'BBRHPJR']).issubset(keys):
                #handle Tempo
                self.logger.trace(u'Handle Tempo')
                ints = self.to_int(raw, [u'BBRHCJB', u'BBRHPJB', u'BBRHCJW', u'BBRHPJW', u'BBRHCJR', u'BBRHPJR'])
                if ints:
                    self.__last_conso_heures_creuses = ints[u'BBRHCJB'] + ints[u'BBRHCJW'] + ints[u'BBRHCJR']
                    self.__last_conso_heures_pleines = ints[u'BBRHPJB'] + ints[u'BBRHPJW'] + ints[u'BBRHPJR']
            elif set([u'BASE']).issubset(keys):
                #handle Base
                self.logger.trace(u'Handle Base')
                ints = self.to_int(raw, [u'BASE'])
                if ints:
                    self.__last_conso_heures_creuses = ints[u'BASE']
                    self.__last_conso_heures_pleines = 0
            else:
                self.logger.debug(u'No consumption value in raw data %s' % raw)

            #instant power
            if set([u'IINST']).issubset(keys):
                ints = self.to_int(raw, [u'IINST'])
            elif set([u'IINST1', u'IINST2', u'IINST3']).issubset(keys):
                ints = self.to_int(raw, [u'IINST1', u'IINST2', u'IINST3'])
                ints[u'IINST'] = ints[u'IINST1'] + ints[u'IINST2'] + ints[u'IINST3']
            else:
                ints = None
            if ints:
                #handle next mode
                next_mode = None
                if set([u'DEMAIN']).issubset(keys):
                    next_mode = raw[u'DEMAIN']
                elif set([u'PEJP']).issubset(keys):
                    next_mode = u'EJP in %s mins' % raw[u'PEJP']

                params = {
                    u'lastupdate': int(time.time()),
                    u'power': ints[u'IINST'] * self.VA_FACTOR,
                    u'currentmode': raw[u'PTEC'] if u'PTEC' in raw else None,
                    u'nextmode': next_mode,
                    u'heurescreuses': self.__last_conso_heures_creuses,
                    u'heurespleines': self.__last_conso_heures_pleines,
                    u'subscription': raw[u'ISOUSC'] if u'ISOUSC' in raw else None,
                }
                    
                #and emit events
                self.logger.trace(u'Send power update event with params: %s' % params)
                self._update_device(self.instant_power_device_uuid, params)
                self.power_update_event.send(params=params, device_id=self.instant_power_device_uuid)

            # save last raw
            self.last_raw = raw

        except Exception as e: # pragma: no cover
            self.logger.exception(u'Exception during teleinfo task:')

    def _get_teleinfo_raw_data(self):
        """
        Get teleinfo raw data from power meter

        Returns:
            dict: raw teleinfo data or empty if no dongle connected
        """
        self.logger.trace('Parser= %s' % self.__teleinfo_parser)
        if self.__teleinfo_parser:
            return self.__teleinfo_parser.get_frame()

        return {}

    def get_teleinfo(self):
        """
        Return latest teleinfo data

        Returns:
            dict: dict of teleinfo data according to user subscription (can be empty if no dongle configured)::

                [
                    {
                        key (string): key of teleinfo item (IINST, DEMAIN, HCHC...),
                        value (string): value of teleinfo item
                    },
                    ...
                ]

        """
        return [{'key':k, 'value':v} for k,v in self.last_raw.iteritems()]

    def to_int(self, raw, keys):
        """
        Convert all values from raw to integer
        This function is useful to check values are valid

        Args:
            raw (dict): raw data from teleinfo
            keys (list): list of keys available in raw to convert
        Returns:
            dict: dict of key-int or None if error occured
        """
        try:
            out = {}
            for key in keys:
                out[key] = int(raw[key])
            return out
        except: # pragma: no cover
            return None

