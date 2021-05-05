#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teleinfo cleep application

Named Cteleinfo because of used teleinfo library that have the same name
"""

import time
import glob
from cleep.libs.internals.task import Task
from cleep.core import CleepModule
from cleep.common import CATEGORIES
from teleinfo import Parser
from teleinfo.hw_vendors import UTInfo2

__all__ = ['Cteleinfo']

class Cteleinfo(CleepModule):
    """
    Teleinfo application.
    Returns current France Enedis electricity provider.
    This application uses MicroTeleinfo dongle built by Charles Hallard (http://hallard.me/utinfo/)

    Note:
        python library: https://github.com/demikl/python-teleinfo
        Teleinfo protocol description: https://www.planete-domotique.com/blog/2010/03/30/la-teleinformation-edf/
    """
    MODULE_AUTHOR = 'Cleep'
    MODULE_VERSION = '1.1.1'
    MODULE_DEPS = []
    MODULE_CATEGORY = CATEGORIES.SERVICE
    MODULE_DESCRIPTION = 'Gets house power consumption infos from Enedis electric power meter'
    MODULE_LONGDESCRIPTION = 'This application reads data from Enedis Linky (or older compatible version) house \
                             power meter and make<br>possible to monitor your house power consumption usage and \
                             build charts on some useful indicators.'
    MODULE_TAGS = ['electricity', 'power', 'teleinfo', 'enedis', 'edf', 'erdf', 'engie']
    MODULE_COUNTRY = 'fr'
    MODULE_URLINFO = 'https://github.com/tangb/cleepmod-teleinfo'
    MODULE_URLHELP = 'https://github.com/tangb/cleepmod-teleinfo/wiki'
    MODULE_URLSITE = 'https://www.enedis.fr/'
    MODULE_URLBUGS = 'https://github.com/tangb/cleepmod-teleinfo/issues'
    MODULE_LABEL = 'Teleinfo'

    MODULE_CONFIG_FILE = 'teleinfo.conf'
    DEFAULT_CONFIG = {
        'port': None,
        'previousconsoheurespleines': None,
        'previousconsoheurescreuses': None,
    }

    TELEINFO_TASK_DELAY = 60 # seconds
    USB_PATH = '/dev/serial/by-id/'
    VA_FACTOR = 220

    def __init__(self, bootstrap, debug_enabled):
        """
        Constructor

        Args:
            bootstrap (dict): bootstrap objects
            debug_enabled (bool): flag to set debug level to logger
        """
        # init
        CleepModule.__init__(self, bootstrap, debug_enabled)

        # members
        self.teleinfo_task = None
        self.instant_power_device_uuid = None
        self.power_consumption_device_uuid = None
        self.last_raw = {}
        self.__teleinfo_parser = None
        self.__last_conso_heures_creuses = 0
        self.__last_conso_heures_pleines = 0

        # events
        self.power_update_event = self._get_event('teleinfo.power.update')
        self.consumption_update_event = self._get_event('teleinfo.consumption.update')

    def _configure(self):
        """
        Configure module
        """
        # configure devices
        self._configure_devices()

        # configure hardware
        if self._configure_hardware():
            #update values at startup
            self.logger.debug('Update data at startup')
            self._teleinfo_task()

        # start teleinfo task
        self._start_teleinfo_task()

    def _configure_devices(self):
        """
        Configure teleinfo devices
        """
        instant_power_default_device = {
            'type': 'teleinfoinstantpower',
            'name': 'Instant power',
            'lastupdate': None,
            'power': 0,
            'currentmode': None,
            'nextmode': None,
        }
        power_consumption_default_device = {
            'type': 'teleinfopowerconsumption',
            'name': 'Power consumption',
            'lastupdate': None,
            'heurescreuses': 0,
            'heurespleines': 0,
        }

        # get devices
        for uuid, device in self._get_devices().items():
            if device['type']=='teleinfoinstantpower':
                self.instant_power_device_uuid = uuid
            elif device['type']=='teleinfopowerconsumption':
                self.power_consumption_device_uuid = uuid

        # add missing devices
        if not self.instant_power_device_uuid:
            self.logger.debug('Adding new instant power device')
            device = self._add_device(instant_power_default_device)
            if not device: # pragma: no cover
                raise Exception('Unable to add new device')
            self.instant_power_device_uuid = device['uuid']
        if not self.power_consumption_device_uuid:
            self.logger.debug('Adding new power consumption device')
            device = self._add_device(power_consumption_default_device)
            if not device: # pragma: no cover
                raise Exception('Unable to add new device')
            self.power_consumption_device_uuid = device['uuid']

        self.logger.debug('Found instant power device "%s"' % self.instant_power_device_uuid)
        self.logger.debug('Found power consumption device "%s"' % self.power_consumption_device_uuid)

    def _configure_hardware(self):
        """
        Configure hardware
        Search device (device path) and initialize parser

        Returns:
            bool: True if hardware configured successfully, False otherwise
        """
        # scan dongle port
        self.logger.trace('Scanning "%s" for devices' % self.USB_PATH)
        devices = [path for path in glob.glob(self.USB_PATH + '*') if path.find('TINFO')>0]
        self.logger.debug('Found devices: %s' % devices)
        if len(devices)==0:
            self.logger.warning('No Teleinfo hardware found, teleinfo disabled')
            return False

        # get only one device
        port = devices[0]
        self._set_config_field('port', port)
        self.logger.info('Using device "%s" as teleinfo port' % port)

        # init parser
        try:
            self.__teleinfo_parser = Parser(UTInfo2(port=port))
            return True

        except Exception:
            self.logger.exception('Fatal error initializing teleinfo parser. Are you using MicroTeleinfo dongle?')
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
        self.logger.trace('Event received %s' % event)
        # compute and send consumption event once a day at midnight
        # previous day consumption is stored in configuration file to take care of device reboot
        if event['event']=='parameters.time.now' and event['params']['hour']==0 and event['params']['minute']==0:
            config = self._get_config()
            if config['previousconsoheurescreuses'] is not None and config['previousconsoheurespleines'] is not None:
                params = {
                    'lastupdate': int(time.time()),
                    'heurescreuses': (self.__last_conso_heures_creuses - config['previousconsoheurescreuses']),
                    'heurespleines': (self.__last_conso_heures_pleines - config['previousconsoheurespleines']),
                }

                # send consumption event and update device
                self.logger.trace('Send consumption update event with params: %s' % params)
                self._update_device(self.instant_power_device_uuid, params)
                self.consumption_update_event.send(params=params, device_id=self.power_consumption_device_uuid)

            # save last power consumption in config file
            self.logger.info('Save last power consumption of the day')
            self._update_config({
                'previousconsoheurescreuses': self.__last_conso_heures_creuses,
                'previousconsoheurespleines': self.__last_conso_heures_pleines,
            })

    def _teleinfo_task(self):
        """
        Teleinfo task reads data from dongle and store current consumption.
        It also emit power event.
        """
        try:
            if not self._get_config_field('port'):
                return

            self.logger.trace('Update teleinfo')

            # read teleinfo data
            raw = self._get_teleinfo_raw_data()
            self.logger.debug('Raw teleinfo: %s' % raw)

            # compute some values
            if not raw:
                return

            # save as soon as possible some data
            if not self.last_raw:
                self.last_raw = raw

            keys = set(raw.keys())
            # power consumption
            if set(['HCHC', 'HCHP']).issubset(keys):
                # handle heures creuses/pleines
                self.logger.trace('Handle heures creuses/pleines')
                ints = Cteleinfo.to_int(raw, ['HCHC', 'HCHP'])
                if ints:
                    self.__last_conso_heures_creuses = ints['HCHC']
                    self.__last_conso_heures_pleines = ints['HCHP']
            elif set(['EJPHN', 'EJPHPM']).issubset(keys):
                # handle EJP
                self.logger.trace('Handle EJP')
                ints = Cteleinfo.to_int(raw, ['EJPHN', 'EJPHPM'])
                if ints:
                    self.__last_conso_heures_creuses = ints['EJPHN']
                    self.__last_conso_heures_pleines = ints['EJPHPM']
            elif set(['BBRHCJB', 'BBRHPJB', 'BBRHCJW', 'BBRHPJW', 'BBRHCJR', 'BBRHPJR']).issubset(keys):
                # handle Tempo
                self.logger.trace('Handle Tempo')
                ints = Cteleinfo.to_int(raw, ['BBRHCJB', 'BBRHPJB', 'BBRHCJW', 'BBRHPJW', 'BBRHCJR', 'BBRHPJR'])
                if ints:
                    self.__last_conso_heures_creuses = ints['BBRHCJB'] + ints['BBRHCJW'] + ints['BBRHCJR']
                    self.__last_conso_heures_pleines = ints['BBRHPJB'] + ints['BBRHPJW'] + ints['BBRHPJR']
            elif set(['BASE']).issubset(keys):
                # handle Base
                self.logger.trace('Handle Base')
                ints = Cteleinfo.to_int(raw, ['BASE'])
                if ints:
                    self.__last_conso_heures_creuses = ints['BASE']
                    self.__last_conso_heures_pleines = 0
            else:
                self.logger.debug('No consumption value in raw data %s' % raw)

            # instant power
            if set(['IINST']).issubset(keys):
                ints = Cteleinfo.to_int(raw, ['IINST'])
            elif set(['IINST1', 'IINST2', 'IINST3']).issubset(keys):
                ints = Cteleinfo.to_int(raw, ['IINST1', 'IINST2', 'IINST3'])
                ints['IINST'] = ints['IINST1'] + ints['IINST2'] + ints['IINST3']
            else:
                ints = None
            if ints:
                # handle next mode
                next_mode = None
                if set(['DEMAIN']).issubset(keys):
                    next_mode = raw['DEMAIN']
                elif set(['PEJP']).issubset(keys):
                    next_mode = 'EJP in %s mins' % raw['PEJP']

                params = {
                    'lastupdate': int(time.time()),
                    'power': ints['IINST'] * self.VA_FACTOR,
                    'currentmode': raw['PTEC'] if 'PTEC' in raw else None,
                    'nextmode': next_mode,
                    'heurescreuses': self.__last_conso_heures_creuses,
                    'heurespleines': self.__last_conso_heures_pleines,
                    'subscription': raw['ISOUSC'] if 'ISOUSC' in raw else None,
                }

                # and emit events
                self.logger.trace('Send power update event with params: %s' % params)
                self._update_device(self.instant_power_device_uuid, params)
                self.power_update_event.send(params=params, device_id=self.instant_power_device_uuid)

            # save last raw
            self.last_raw = raw

        except Exception: # pragma: no cover
            self.logger.exception('Exception during teleinfo task:')

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
        return [{'key':k, 'value':v} for k,v in self.last_raw.items()]

    @staticmethod
    def to_int(raw, keys):
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
        except Exception: # pragma: no cover
            return None

