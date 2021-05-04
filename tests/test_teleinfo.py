import unittest
import logging
import sys
sys.path.append('../')
from backend import cteleinfo
from cleep.exception import InvalidParameter, MissingParameter, CommandError, Unauthorized
from cleep.libs.tests import session
import os, io
import time
from mock import Mock



class MockedParser():
    def __init__(self, get_frame_output):
        self.get_frame_output = get_frame_output

    def set_get_frame_output(self, get_frame_output):
        self.get_frame_output = get_frame_output

    def get_frame(self, *args, **kwargs):
        return self.get_frame_output





class TestTeleinfoConfigureHardware(unittest.TestCase):

    DATA = {
        'DATA': 'dummy'
    }

    def setUp(self):
        logging.basicConfig(level=logging.FATAL, format=u'%(asctime)s %(name)s:%(lineno)d %(levelname)s : %(message)s')
        self.session = session.TestSession(self)

        self.path = os.path.join(os.getcwd(), 'DUMMY_DONGLE_TINFO_USB')
        cteleinfo.Parser = Mock(return_value=MockedParser(self.DATA))
        cteleinfo.UTInfo2 = Mock()

    def tearDown(self):
        self.session.clean()

    def init(self, mock_teleinfo_task=Mock()):
        Teleinfo_ = self.session.clone_class(cteleinfo.Cteleinfo)
        Teleinfo_.USB_PATH = os.path.abspath('./') + '/'
        if mock_teleinfo_task:
            Teleinfo_._teleinfo_task = mock_teleinfo_task
        self.module = self.session.setup(Teleinfo_)
        self.session.start_module(self.module)

    def test_configure_hardware_dongle_found(self):
        try:
            with io.open(self.path, 'w') as f:
                f.write(u'')
            self.init()
        
            self.assertNotEqual(self.module._get_config_field('port'), None)
            self.assertIsNotNone(self.module.teleinfo_task)

        finally:
            if os.path.exists(self.path):
                os.remove(self.path)

    def test_configure_hardware_dongle_not_found(self):
        self.init()
        
        self.assertEqual(self.module._get_config_field('port'), None)
        self.assertIsNotNone(self.module.teleinfo_task)
        self.assertEqual(self.module._get_teleinfo_raw_data(), {})

    def test_configure_hardware_exception(self):
        try:
            with io.open(self.path, 'w') as f:
                f.write(u'')
            cteleinfo.Parser.side_effect = Exception('test')
            self.init()

            self.assertFalse(self.module._configure_hardware())

        finally:
            if os.path.exists(self.path):
                os.remove(self.path)

    def test_teleinfo_task_with_dongle(self):
        # execute test here because dongle is needed
        try:
            with io.open(self.path, 'w') as f:
                f.write(u'')
            self.init(None)

            self.module._teleinfo_task()
            logging.debug('RAW=%s' % self.module.last_raw)
            self.assertEqual(len(self.module.last_raw), len(self.DATA))
            self.assertEqual(list(self.module.last_raw.keys())[0], list(self.DATA.keys())[0])

        finally:
            if os.path.exists(self.path):
                os.remove(self.path)

    def test_teleinfo_task_with_dongle_no_raw(self):
        try:
            with io.open(self.path, 'w') as f:
                f.write(u'')
            self.init(None)

            # mock
            self.module._get_teleinfo_raw_data = Mock(return_value={})

            self.module._teleinfo_task()
            logging.debug('RAW=%s' % self.module.last_raw)
            # should return last valid raw data (read during startup)
            self.assertEqual(self.module.last_raw, self.DATA)

        finally:
            if os.path.exists(self.path):
                os.remove(self.path)

    def test_teleinfo_task_without_dongle(self):
        self.init(None)
        self.module._teleinfo_task()
        logging.debug('RAW=%s' % self.module.last_raw)
        self.assertEqual(len(self.module.last_raw), 0)





class TestTeleinfoConfigureDevices(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.FATAL, format=u'%(asctime)s %(name)s:%(lineno)d %(levelname)s : %(message)s')
        self.session = session.TestSession(self)

        self.path = os.path.join(os.getcwd(), 'DUMMY_DONGLE_TINFO_USB')
        cteleinfo.Parser = Mock()
        cteleinfo.UTInfo2 = Mock()

    def tearDown(self):
        self.session.clean()

    def init(self):
        Teleinfo_ = self.session.clone_class(cteleinfo.Cteleinfo)
        Teleinfo_.USB_PATH = os.path.abspath('./') + '/'
        Teleinfo_._teleinfo_task = Mock()
        self.module = self.session.setup(Teleinfo_)
        self.session.start_module(self.module)

    """
    def test_configure_devices_with_existing_config(self):
        # create Teleinfo instance to create config file
        self.init()
        
        # get devices
        old_devices = self.module._get_devices()
        logging.debug('Old devices: %s' % old_devices)

        # then create new Teleinfo instance to use existing devices
        module = self.session.respawn_module()
        devices = module._get_devices()
        logging.debug('Devices: %s' % devices)

        # check if devices uuid are the same
        self.assertEqual(len(old_devices), len(devices), 'Number of devices should be the same')
        for device_uuid in old_devices:
            self.assertTrue(device_uuid in devices, 'Device should be correctly reloaded')
    """




class TestTeleinfo(unittest.TestCase):

    DATA = {
        'MOTDETAT': '000000',
        'ADCO': '041529016009',
        'OPTARIF': 'HC..',
        'ISOUSC': '45',
        'HCHC': '000643083',
        'HCHP': '000825429',
        'PTEC': 'HP..',
        'IINST': '003',
        'IMAX': '029',
        'PAPP': '00620',
        'HHPHC': 'A',
    }

    def setUp(self):
        logging.basicConfig(level=logging.CRITICAL, format=u'%(asctime)s %(name)s:%(lineno)d %(levelname)s : %(message)s')
        self.session = session.TestSession(self)

        cteleinfo.UTInfo2 = Mock()
        cteleinfo.Parser = Mock(return_value=MockedParser(self.DATA))
        self.path = os.path.join(os.getcwd(), 'DUMMY_DONGLE_TINFO_USB')
        with io.open(self.path, 'w') as f:
            f.write(u'')
        Teleinfo_ = self.session.clone_class(cteleinfo.Cteleinfo)
        Teleinfo_.USB_PATH = os.path.abspath('./') + '/'
        Teleinfo_._teleinfo_task = Mock()
        self.module = self.session.setup(Teleinfo_)
        self.session.start_module(self.module)

    def tearDown(self):
        self.session.clean()

    def test_stop_teleinfo_task(self):
        self.assertIsNotNone(self.module.teleinfo_task)
        self.module._stop_teleinfo_task()
        self.assertIsNone(self.module.teleinfo_task)

    def test_restart_teleinfo_task(self):
        id_task = id(self.module.teleinfo_task)
        self.module._restart_teleinfo_task()
        self.assertNotEqual(id_task, id(self.module.teleinfo_task))

    def test_get_teleinfo(self):
        self.module.last_raw = self.DATA
        values = self.module.get_teleinfo()
        self.assertEqual(len(values), len(self.DATA.keys()))
        for value in values:
            self.assertTrue(value['key'] in self.DATA.keys())
            self.assertEqual(self.DATA[value['key']], value['value'])

    def test_get_teleinfo_last_raw_empty(self):
        values = self.module.get_teleinfo()
        self.assertEqual(len(values), 0)

    def test_get_teleinfo_raw_data(self):
        raw = self.module._get_teleinfo_raw_data()
        logging.debug('RAW=%s' % raw)
        self.assertEqual(len(raw), len(self.DATA))
        for key,value in raw.items():
            self.assertTrue(key in self.DATA)
            self.assertEqual(value, self.DATA[key])


        



class TestTeleinfoHistoBase(unittest.TestCase):

    TI_HISTO_BASE = {
        'IINST': '002',
        'MOTDETAT': '000000',
        'OPTARIF': 'BASE',
        'ADCO': '061662394908',
        'ISOUSC': '30',
        'BASE': '018048633',
        'IMAX': '090',
        'PTEC': 'TH..',
        'PAPP': '00510',
        'HHPHC': 'A',
    }

    def setUp(self):
        logging.basicConfig(level=logging.CRITICAL, format=u'%(asctime)s %(name)s:%(lineno)d %(levelname)s : %(message)s')
        self.session = session.TestSession(self)

        cteleinfo.UTInfo2 = Mock()
        self.mocked_parser = MockedParser({})
        cteleinfo.Parser = Mock(return_value=self.mocked_parser)
        self.path = os.path.join(os.getcwd(), 'DUMMY_DONGLE_TINFO_USB')
        with io.open(self.path, 'w') as f:
            f.write(u'')

    def tearDown(self):
        self.session.clean()
        if os.path.exists(self.path):
            os.remove(self.path)

    def init(self):
        Teleinfo_ = self.session.clone_class(cteleinfo.Cteleinfo)
        Teleinfo_.USB_PATH = os.path.abspath('./') + '/'
        self.module = self.session.setup(Teleinfo_)
        self.session.start_module(self.module)

    def test_teleinfo_task(self):
        self.init()
        self.mocked_parser.set_get_frame_output(self.TI_HISTO_BASE)
        self.module._teleinfo_task()
        
        self.assertEqual(self.session.event_call_count('teleinfo.power.update'), 1)
        self.assertEqual(self.session.event_call_count('teleinfo.consumption.update'), 0)
        event_params = self.session.get_last_event_params('teleinfo.power.update')
        logging.debug('Event params: %s' % event_params)
        self.assertEqual(event_params['power'], int(self.TI_HISTO_BASE['IINST']) * self.module.VA_FACTOR)
        self.assertEqual(event_params['currentmode'], self.TI_HISTO_BASE['PTEC'])
        self.assertEqual(event_params['subscription'], self.TI_HISTO_BASE['ISOUSC'])
        self.assertEqual(event_params['heurescreuses'], int(self.TI_HISTO_BASE['BASE']))
        self.assertEqual(event_params['heurespleines'], 0)





class TestTeleinfoHistoHCHP(unittest.TestCase):

    TI_HISTO_HCHP = {
        'MOTDETAT': '000000',
        'ADCO': '041529016009',
        'OPTARIF': 'HC..',
        'ISOUSC': '45',
        'HCHC': '000643083',
        'HCHP': '000825429',
        'PTEC': 'HP..',
        'IINST': '003',
        'IMAX': '029',
        'PAPP': '00620',
        'HHPHC': 'A',
    }

    def setUp(self):
        logging.basicConfig(level=logging.CRITICAL, format=u'%(asctime)s %(name)s:%(lineno)d %(levelname)s : %(message)s')
        self.session = session.TestSession(self)

        cteleinfo.UTInfo2 = Mock()
        self.mocked_parser = MockedParser({})
        cteleinfo.Parser = Mock(return_value=self.mocked_parser)
        self.path = os.path.join(os.getcwd(), 'DUMMY_DONGLE_TINFO_USB')
        with io.open(self.path, 'w') as f:
            f.write(u'')

    def tearDown(self):
        self.session.clean()
        if os.path.exists(self.path):
            os.remove(self.path)

    def init(self):
        Teleinfo_ = self.session.clone_class(cteleinfo.Cteleinfo)
        Teleinfo_.USB_PATH = os.path.abspath('./') + '/'
        self.module = self.session.setup(Teleinfo_)
        self.session.start_module(self.module)

    def test_teleinfo_task(self):
        self.init()
        self.mocked_parser.set_get_frame_output(self.TI_HISTO_HCHP)
        self.module._teleinfo_task()
        
        self.assertEqual(self.session.event_call_count('teleinfo.power.update'), 1)
        self.assertEqual(self.session.event_call_count('teleinfo.consumption.update'), 0)
        event_params = self.session.get_last_event_params('teleinfo.power.update')
        logging.debug('Event params: %s' % event_params)
        self.assertEqual(event_params['power'], int(self.TI_HISTO_HCHP['IINST']) * self.module.VA_FACTOR)
        self.assertEqual(event_params['currentmode'], self.TI_HISTO_HCHP['PTEC'])
        self.assertEqual(event_params['subscription'], self.TI_HISTO_HCHP['ISOUSC'])
        self.assertEqual(event_params['heurescreuses'], int(self.TI_HISTO_HCHP['HCHC']))
        self.assertEqual(event_params['heurespleines'], int(self.TI_HISTO_HCHP['HCHP']))

    def test_event_received(self):
        event = {
            'event': 'parameters.time.now',
            'params': {
                'hour': 0,
                'minute': 0,
            }
        }

        self.init()
        self.mocked_parser.set_get_frame_output(self.TI_HISTO_HCHP)
        self.module._teleinfo_task()
        
        self.module.event_received(event)
        self.assertEqual(self.session.event_call_count('teleinfo.consumption.update'), 0)

        self.module.event_received(event)
        self.assertEqual(self.session.event_call_count('teleinfo.consumption.update'), 1)
        event_params = self.session.get_last_event_params('teleinfo.consumption.update')
        logging.debug('Event params: %s' % event_params)
        # should be equal to 0 because no consumption between 2 measures
        self.assertEqual(event_params['heurescreuses'], 0)
        self.assertEqual(event_params['heurespleines'], 0)
        logging.debug('Config: %s' % self.module._get_config())

        # force different consumption
        self.module._update_config({
            'previousconsoheurescreuses': int(self.TI_HISTO_HCHP['HCHC']) - 666,
            'previousconsoheurespleines': int(self.TI_HISTO_HCHP['HCHP']) - 999,
        })
        self.module.event_received(event)
        self.assertEqual(self.session.event_call_count('teleinfo.consumption.update'), 2)
        event_params = self.session.get_last_event_params('teleinfo.consumption.update')
        logging.debug('Event params: %s' % event_params)
        self.assertEqual(event_params['heurescreuses'], 666)
        self.assertEqual(event_params['heurespleines'], 999)





class TestTeleinfoHistoEJP(unittest.TestCase):

    TI_HISTO_EJP = {
        'ADCO': '041529016009',
        'OPTARIF': 'EJP.',
        'ISOUSC': '20',
        'EJPHPM': '000476413',
        'EJPHN': '004669447',
        'IMAX': '039',
        'PTEC': 'HN..',
        'PAPP': '02070',
        'PEJP': '30',
        'IINST': '009',
    }

    def setUp(self):
        logging.basicConfig(level=logging.CRITICAL, format=u'%(asctime)s %(name)s:%(lineno)d %(levelname)s : %(message)s')
        self.session = session.TestSession(self)

        cteleinfo.UTInfo2 = Mock()
        self.mocked_parser = MockedParser({})
        cteleinfo.Parser = Mock(return_value=self.mocked_parser)
        self.path = os.path.join(os.getcwd(), 'DUMMY_DONGLE_TINFO_USB')
        with io.open(self.path, 'w') as f:
            f.write(u'')

    def tearDown(self):
        self.session.clean()
        if os.path.exists(self.path):
            os.remove(self.path)

    def init(self):
        Teleinfo_ = self.session.clone_class(cteleinfo.Cteleinfo)
        Teleinfo_.USB_PATH = os.path.abspath('./') + '/'
        self.module = self.session.setup(Teleinfo_)
        self.session.start_module(self.module)

    def test_teleinfo_task(self):
        self.init()
        self.mocked_parser.set_get_frame_output(self.TI_HISTO_EJP)
        self.module._teleinfo_task()
        
        self.assertEqual(self.session.event_call_count('teleinfo.power.update'), 1)
        self.assertEqual(self.session.event_call_count('teleinfo.consumption.update'), 0)
        event_params = self.session.get_last_event_params('teleinfo.power.update')
        logging.debug('Event params: %s' % event_params)
        self.assertEqual(event_params['power'], int(self.TI_HISTO_EJP['IINST']) * self.module.VA_FACTOR)
        self.assertEqual(event_params['currentmode'], self.TI_HISTO_EJP['PTEC'])
        self.assertEqual(event_params['subscription'], self.TI_HISTO_EJP['ISOUSC'])
        self.assertEqual(event_params['heurescreuses'], int(self.TI_HISTO_EJP['EJPHN']))
        self.assertEqual(event_params['heurespleines'], int(self.TI_HISTO_EJP['EJPHPM']))





class TestTeleinfoHistoTempo(unittest.TestCase):

    TI_HISTO_TEMPO = {
        'ADCO': '041529016009',
        'OPTARIF': 'BBR.',
        'ISOUSC': '45',
        'BBRHCJB': '002697099',
        'BBRHPJB': '003494559',
        'BBRHCJW': '000041241',
        'BBRHPJW': '000194168',
        'BBRHCJR': '000000000',
        'BBRHPJR': '000089736',
        'PTEC': 'HPJB',
        'DEMAIN': '--',
        'IINST': '002',
        'IMAX': '030',
        'PAPP': '00430',
        'HHPHC': 'Y',
        'MOTDETAT': '000000',
    }

    def setUp(self):
        logging.basicConfig(level=logging.CRITICAL, format=u'%(asctime)s %(name)s:%(lineno)d %(levelname)s : %(message)s')
        self.session = session.TestSession(self)

        cteleinfo.UTInfo2 = Mock()
        self.mocked_parser = MockedParser({})
        cteleinfo.Parser = Mock(return_value=self.mocked_parser)
        self.path = os.path.join(os.getcwd(), 'DUMMY_DONGLE_TINFO_USB')
        with io.open(self.path, 'w') as f:
            f.write(u'')

    def tearDown(self):
        self.session.clean()
        if os.path.exists(self.path):
            os.remove(self.path)

    def init(self):
        Teleinfo_ = self.session.clone_class(cteleinfo.Cteleinfo)
        Teleinfo_.USB_PATH = os.path.abspath('./') + '/'
        self.module = self.session.setup(Teleinfo_)
        self.session.start_module(self.module)

    def test_teleinfo_task(self):
        self.init()
        self.mocked_parser.set_get_frame_output(self.TI_HISTO_TEMPO)
        self.module._teleinfo_task()
        
        self.assertEqual(self.session.event_call_count('teleinfo.power.update'), 1)
        self.assertEqual(self.session.event_call_count('teleinfo.consumption.update'), 0)
        event_params = self.session.get_last_event_params('teleinfo.power.update')
        logging.debug('Event params: %s' % event_params)
        self.assertEqual(event_params['power'], int(self.TI_HISTO_TEMPO['IINST']) * self.module.VA_FACTOR)
        self.assertEqual(event_params['currentmode'], self.TI_HISTO_TEMPO['PTEC'])
        self.assertEqual(event_params['subscription'], self.TI_HISTO_TEMPO['ISOUSC'])
        self.assertEqual(event_params['heurescreuses'], int(self.TI_HISTO_TEMPO['BBRHCJB'])+int(self.TI_HISTO_TEMPO['BBRHCJW'])+int(self.TI_HISTO_TEMPO['BBRHCJR']))
        self.assertEqual(event_params['heurespleines'], int(self.TI_HISTO_TEMPO['BBRHPJB'])+int(self.TI_HISTO_TEMPO['BBRHPJW'])+int(self.TI_HISTO_TEMPO['BBRHPJR']))





class TestTeleinfoHistoEJPTriphase(unittest.TestCase):

    TI_HISTO_EJP_TRI = {
        'ADCO': '041529016009',
        'OPTARIF': 'EJP.',
        'ISOUSC': '20',
        'EJPHN': '174297706',
        'EJPHPM': '002113651',
        'PTEC': 'HN..',
        'IINST1': '001',
        'IINST2': '002',
        'IINST3': '004',
        'IMAX1': '034',
        'IMAX2':'032',
        'IMAX3': '035',
        'PMAX': '16160',
        'PAPP': '00370',
        'MOTDETAT': '000000',
        'PPOT': '00',
    }

    def setUp(self):
        logging.basicConfig(level=logging.CRITICAL, format=u'%(asctime)s %(name)s:%(lineno)d %(levelname)s : %(message)s')
        self.session = session.TestSession(self)

        cteleinfo.UTInfo2 = Mock()
        self.mocked_parser = MockedParser({})
        cteleinfo.Parser = Mock(return_value=self.mocked_parser)
        self.path = os.path.join(os.getcwd(), 'DUMMY_DONGLE_TINFO_USB')
        with io.open(self.path, 'w') as f:
            f.write(u'')

    def tearDown(self):
        self.session.clean()
        if os.path.exists(self.path):
            os.remove(self.path)

    def init(self):
        Teleinfo_ = self.session.clone_class(cteleinfo.Cteleinfo)
        Teleinfo_.USB_PATH = os.path.abspath('./') + '/'
        self.module = self.session.setup(Teleinfo_)
        self.session.start_module(self.module)

    def test_teleinfo_task(self):
        self.init()
        self.mocked_parser.set_get_frame_output(self.TI_HISTO_EJP_TRI)
        self.module._teleinfo_task()
        
        self.assertEqual(self.session.event_call_count('teleinfo.power.update'), 1)
        self.assertEqual(self.session.event_call_count('teleinfo.consumption.update'), 0)
        event_params = self.session.get_last_event_params('teleinfo.power.update')
        logging.debug('Event params: %s' % event_params)
        self.assertEqual(event_params['power'], (int(self.TI_HISTO_EJP_TRI['IINST1'])+int(self.TI_HISTO_EJP_TRI['IINST2'])+int(self.TI_HISTO_EJP_TRI['IINST3'])) * self.module.VA_FACTOR)
        self.assertEqual(event_params['currentmode'], self.TI_HISTO_EJP_TRI['PTEC'])
        self.assertEqual(event_params['subscription'], self.TI_HISTO_EJP_TRI['ISOUSC'])
        self.assertEqual(event_params['heurescreuses'], int(self.TI_HISTO_EJP_TRI['EJPHN']))
        self.assertEqual(event_params['heurespleines'], int(self.TI_HISTO_EJP_TRI['EJPHPM']))


if __name__ == "__main__":
    # coverage run --omit="*/lib/python*/*","test_*" --concurrency=thread test_teleinfo.py; coverage report -m -i
    unittest.main()
    
