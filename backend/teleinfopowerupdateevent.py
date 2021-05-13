#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teleinfo power update event
"""

from cleep.libs.internals.event import Event

class TeleinfoPowerUpdateEvent(Event):
    """
    Teleinfo.power.update event
    """

    EVENT_NAME = 'teleinfo.power.update'
    EVENT_PARAMS = [
        'lastupdate',
        'power', # puissance instantanée
        'currentmode', # mode courant
        'nextmode', # prochain mode
        'heurescreuses', #index HC ou BASE
        'heurespleines', #index HP
        'subscription', #abonnement
    ]
    EVENT_CHARTABLE = True
    EVENT_CHART_PARAMS = ['power']
    EVENT_PROPAGATE = True

    def __init__(self, params):
        """
        Constructor

        Args:
            params (dict): event parameters
        """
        Event.__init__(self, params)

