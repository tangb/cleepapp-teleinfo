#!/usr/bin/env python
# -*- coding: utf-8 -*-

from raspiot.libs.internals.event import Event

class TeleinfoPowerUpdateEvent(Event):
    """
    Teleinfo.power.update event
    """

    EVENT_NAME = u'teleinfo.power.update'
    EVENT_SYSTEM = False
    EVENT_PARAMS = [
        u'lastupdate',
        u'power', # puissance instantanée
        u'currentmode', # mode courant
        u'nextmode' # prochain mode
    ]
    EVENT_CHARTABLE = True
    EVENT_CHART_PARAMS = [u'power']

    def __init__(self, bus, formatters_broker, events_broker):
        """ 
        Constructor

        Args:
            bus (MessageBus): message bus instance
            formatters_broker (FormattersBroker): formatters broker instance
            events_broker (EventsBroker): events broker instance
        """
        Event.__init__(self, bus, formatters_broker, events_broker)

