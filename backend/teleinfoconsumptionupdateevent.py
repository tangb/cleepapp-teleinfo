#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teleinfo consumption update event
"""

from cleep.libs.internals.event import Event

class TeleinfoConsumptionUpdateEvent(Event):
    """
    Teleinfo.consumption.update event
    """

    EVENT_NAME = 'teleinfo.consumption.update'
    EVENT_SYSTEM = False
    EVENT_PARAMS = ['lastupdate', 'heurescreuses', 'heurespleines']
    EVENT_CHARTABLE = True
    EVENT_CHART_PARAMS = ['heurescreuses', 'heurespleines']

    def __init__(self, params):
        """
        Constructor

        Args:
            params (dict): event parameters
        """
        Event.__init__(self, params)

