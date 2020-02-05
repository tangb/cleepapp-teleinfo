#!/usr/bin/env python
# -*- coding: utf-8 -*-

from raspiot.libs.internals.event import Event

class TeleinfoConsumptionUpdateEvent(Event):
    """
    Teleinfo.consumption.update event
    """

    EVENT_NAME = u'teleinfo.consumption.update'
    EVENT_SYSTEM = False
    EVENT_PARAMS = [u'heurescreuses', u'heurespleines']
    EVENT_CHARTABLE = True

    def __init__(self, bus, formatters_broker, events_broker):
        """ 
        Constructor

        Args:
            bus (MessageBus): message bus instance
            formatters_broker (FormattersBroker): formatters broker instance
            events_broker (EventsBroker): events broker instance
        """
        Event.__init__(self, bus, formatters_broker, events_broker)

