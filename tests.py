import unittest, random, os, tempfile
from lib.configurator import Configurator
from lib.paper import Paper, paper_units, paper_sizes, paper_orientation
from lib.receipt_printer import ReceiptFont, ReceiptPrinter, ReceiptPaper
from lib.settings_group import CfgSetting, SettingsGroup
from lib.font import FontConfigurator, Font, gui_components
from lib.cli import WfCfgParser
from lib.os import get_property_files, LOCKFILE

dummy_files = set([ 'testA.txt', 'testB.txt' ])
default_settings = [('menu.burger.cheese', 'Y'),
                    ('menu.burger.pickles', '2')]

def makeDummyFiles():
    # create temporary config files with dummy values
    lines = ['='.join(kv) for kv in default_settings]
    for f in dummy_files:
        if os.path.exists(f + LOCKFILE):
            os.remove(f + LOCKFILE)
        with open(f, 'w') as fo:
            fo.write('\n'.join(lines) + '\n')

def deleteDummyFiles():
    # delete temporary config files
    for f in dummy_files:
        os.remove(f)

def fileDict(Configurator_obj, filepath):
    with open(filepath, 'r') as fo:
        text = [_ for _ in fo.read().split('\n') if _.strip()]
    configs = [Configurator_obj.config_line_processor(line) for line in text]
    page_dict = {key:val for key, val in configs}
    return page_dict
        
def checkFiles(TestCase_obj, Configurator_obj, keypath, expected_value,
               cfgValParser = None):
    for f in Configurator_obj.config_files:
        cfg = fileDict(Configurator_obj, f) # read files
        TestCase_obj.assertTrue(keypath in cfg,
                                "Keypath not found in file!\n"
                                "File contents: %s\n" % str(cfg) +\
                                "Keypath: %s\n" % keypath +\
                                "Filepath: %s" % f)
        cfgVal = cfg[keypath]
        if cfgValParser is not None:
            cfgVal = cfgValParser(cfgVal)
        TestCase_obj.assertEqual(expected_value, cfgVal,
                                 "Expected value not found at keypath!\n"
                                 "Keypath: %s\nFilepath: %s" % (keypath, f))
    

class TestCfgSettingClass(unittest.TestCase):
    def test_value(self):
        # validate strings; mixed case values pass against lower case
        # validation set
        v = {'hello', 'goodbye'}
        cs = CfgSetting(str, value='Hello', valids=v)
        self.assertIsInstance(cs.value, str)
        self.assertEqual('Hello', cs.value)
        cs.value = 'GoodBye'
        self.assertIsInstance(cs.value, str)
        self.assertEqual('GoodBye', cs.value)

        # passing an int to str setting fails
        with self.assertRaises(TypeError):
            cs.value = 23

        # passing an invalid str fails
        with self.assertRaises(ValueError):
            cs.value = 'fail'

        # float settings accept floats or ints
        cs = CfgSetting(float)
        cs.value = 1
        self.assertIsInstance(cs.value, float)
        self.assertEqual(cs.value, 1.0)
        cs.value = 0.5
        self.assertIsInstance(cs.value, float)
        self.assertEqual(cs.value, 0.5)

        # int settings accept ints
        cs = CfgSetting(int)
        cs.value = 3
        self.assertIsInstance(cs.value, int)
        self.assertEqual(cs.value, 3)

        # passing a str to a float fails
        with self.assertRaises(TypeError):
            cs.value = 'fail'

        # including the wrong type in validation set fails
        with self.assertRaises(TypeError):
            cs = CfgSetting(int, valids={1, 2, 'c'})
        with self.assertRaises(TypeError):
            cs = CfgSetting(str, valids={'a', 'b', 3})

        # passing an invalid int fails
        cs = CfgSetting(int, valids={1, 2, 3})
        with self.assertRaises(ValueError):
            cs.value = 4

    def test_value_getter(self):
        g = lambda x: x.upper()
        cs = CfgSetting(str, value='hello', getter=g)
        self.assertEqual('HELLO', cs.value)

        g = lambda x: x[::-1]
        cs = CfgSetting(str, value='hello', getter=g)
        self.assertEqual('olleh', cs.value)

        g = lambda x: 5
        cs = CfgSetting(str, value='hello', getter=g)
        self.assertEqual(5, cs.value)

        g = lambda x: 2**x
        cs = CfgSetting(int, value=4, getter=g)
        self.assertEqual(16, cs.value)

    def test_modified(self):
        cs = CfgSetting(int)
        self.assertFalse(cs.modified)
        cs.value = 0
        self.assertTrue(cs.modified)

        cs = CfgSetting(int, value=0)
        self.assertTrue(cs.modified)
        
        
class TestSettingsGroup(unittest.TestCase):
    def setUp(self):
        self.keypath = 'some.path.'
        self.sg = SettingsGroup(self.keypath)
    
    def test_path(self):
        # contains the right keypath
        self.assertEqual(self.keypath, self.sg.keypath)
    
    def test_key_operations(self):
        # no keys added; not modified
        self.assertFalse(self.sg.modified)

        # key added, but no value set; not modified
        key, val = 'some_key', 1
        self.sg.add_setting(key, int)        
        self.assertFalse(self.sg.modified)

        # key value added; modified is true
        self.sg.get_setting(key).value = val
        self.assertEqual(val, self.sg.get_setting(key).value)
        self.assertTrue(self.sg.modified)

        # make sure settings is delivering key/value in proper fashion
        self.assertEqual(val, len(self.sg.settings))
        k, v = self.sg.settings[0]
        self.assertEqual(str(val), v)
        self.assertEqual(self.keypath + key, k)

        # test override key with new value
        new_key = 'new_key'
        self.sg.override_key(key, new_key)
        k, v = self.sg.settings[0]
        self.assertEqual(str(val), v)
        self.assertEqual(self.keypath + new_key, k)

        # deleting the only key should make modified be false
        self.sg.delete_setting(key)
        self.assertFalse(self.sg.modified)

class TestConfiguratorClass(unittest.TestCase):
    def setUp(self):
        makeDummyFiles()
        self.c = Configurator(dummy_files)

    def tearDown(self):
        deleteDummyFiles()

    def checkFiles(self, keypath, value, cfgValParser = None):
        # make sure files are updated correctly
        return checkFiles(self, self.c, keypath, value, cfgValParser)

    def fileToDict(self, filepath):
        return fileDict(self.c, filepath)
            
    def reset(self):
        # reset default keys to default values
        for key, value in default_settings:
            self.c.update(key, value)
        self.c.run()
        self.assertFalse(self.c.changes_staged)
        # make sure files are updated correctly
        for key, value in default_settings:
            self.c.update(key, value)
            
    def test_config_line_processor(self):
        line = 'peripherals.receipt.dot_matrix=N'
        key, value = 'peripherals.receipt.dot_matrix', 'N'
        self.assertEqual(self.c.config_line_processor(line), [key, value])

    def test_config_line_formatter(self):
        line = 'peripherals.receipt.dot_matrix=N'
        key, value = 'peripherals.receipt.dot_matrix', 'N'
        self.assertEqual(self.c.config_line_formatter(key, value), line)
        
    def test_no_changes(self):
        """Make sure Configurator does not change files when run with
        no changes staged."""
        old = list() # file contents pre-run
        for f in sorted(self.c.config_files):
            with open(f, 'r') as fo:
                old.append(fo.read())
        self.assertFalse(self.c.changes_staged)
        self.c.run() # run without any changes
        self.assertFalse(self.c.changes_staged)
        new = list() # file contents post-run
        for f in sorted(self.c.config_files):
            with open(f, 'r') as fo:
                new.append(fo.read())
        # make sure files have not changed
        for old, new in zip(old, new):
            self.assertEqual(old, new)        
                
    def test_update(self):
        updates = [('menu.burger.cheese', 'N'),
                   ('menu.burger.onion', 'Y'),
                   ('menu.burger.side.fries', '15')]
        
        # write some updates to files
        self.assertFalse(self.c.changes_staged)
        for key, value in updates:
            self.c.update(key, value)
        self.assertTrue(self.c.changes_staged)
        self.c.run() # write changes to files
        self.assertFalse(self.c.changes_staged)
        # make sure files updated correctly
        for key, value in updates:
            self.checkFiles(key, value)
        # reset files to default values
        self.reset()

    def test_batch_update(self):
        # write some updates to files
        self.assertFalse(self.c.changes_staged)
        updates = [('menu.salad.lettuce', 'Y'),
                   ('menu.salad.dressing', 'RANCH'),
                   ('menu.salad.onion', 'N')]
        self.c.batch_update(updates)
        self.assertTrue(self.c.changes_staged)
        self.c.run() # write changes to files
        self.assertFalse(self.c.changes_staged)
        # make sure files updated correctly and default settings were
        # correctly preserved
        for key, value in updates + default_settings:
            self.checkFiles(key, value)

    def test_delete(self):
        for key, value in default_settings:
            # delete key
            self.assertFalse(self.c.changes_staged)
            self.c.delete(key)
            self.assertTrue(self.c.changes_staged)
            self.c.run()
            self.assertFalse(self.c.changes_staged)
            # check files
            for f in self.c.config_files:
                cfg = self.fileToDict(f)
                self.assertFalse(key in cfg)
        # reset files to default values
        self.reset()


class TestReceiptFont(unittest.TestCase):
    def test_name(self):
        rf = ReceiptFont()
        rf.name = 'Arbitrary Sans'
        self.assertTrue(rf.modified)
        self.assertIsInstance(rf.name, str)
        self.assertEqual('Arbitrary Sans', rf.name)

    def test_size(self):
        rf = ReceiptFont()
        rf.size = 18
        self.assertTrue(rf.modified)
        self.assertEqual(18, rf.size)

    def test_style(self):
        self.assertEqual(0, ReceiptFont.REGULAR)
        self.assertEqual(1, ReceiptFont.BOLD)
        self.assertEqual(2, ReceiptFont.ITALIC)
        
        rf = ReceiptFont()
        rf.style = 'regular'
        self.assertTrue(rf.modified)
        self.assertEqual(ReceiptFont.REGULAR, rf.style)
        rf.style = 'bold'
        self.assertEqual(ReceiptFont.BOLD, rf.style)
        rf.style = 'italic'
        self.assertEqual(ReceiptFont.ITALIC, rf.style)

        with self.assertRaises(ValueError):
            rf.style = 'fail'
            
    def test_make_regular(self):
        rf = ReceiptFont()
        rf.make_regular()
        self.assertTrue(rf.modified)
        self.assertEqual(ReceiptFont.REGULAR, rf.style)

    def test_make_regular(self):
        rf = ReceiptFont()
        rf.make_bold()
        self.assertTrue(rf.modified)
        rf.make_regular() # change from default bold
        rf.make_bold() # change back to bold        
        self.assertEqual(ReceiptFont.BOLD, rf.style)

    def test_make_italic(self):
        rf = ReceiptFont()
        rf.make_italic()
        self.assertTrue(rf.modified)
        self.assertEqual(ReceiptFont.ITALIC, rf.style)


class TestPaperClass(unittest.TestCase):  
    def setUp(self):
        self.p = Paper()
    
    def test_margin_top(self):
        self.p.margin_top = 1
        self.assertEqual(1.0, self.p.margin_top)
        self.assertIsInstance(self.p.margin_top, float)
        self.p.margin_top = 0.75
        self.assertEqual(0.75, self.p.margin_top)
        with self.assertRaises(TypeError):
            self.p.margin_top = 'fail'

    def test_margin_right(self):
        self.p.margin_right = 1
        self.assertEqual(1.0, self.p.margin_right)
        self.assertIsInstance(self.p.margin_right, float)
        self.p.margin_right = 0.75
        self.assertEqual(0.75, self.p.margin_right)
        with self.assertRaises(TypeError):
            self.p.margin_right = 'fail'

    def test_margin_bottom(self):
        self.p.margin_bottom = 1
        self.assertEqual(1.0, self.p.margin_bottom)
        self.assertIsInstance(self.p.margin_bottom, float)
        self.p.margin_bottom = 0.75
        self.assertEqual(0.75, self.p.margin_bottom)
        with self.assertRaises(TypeError):
            self.p.margin_bottom = 'fail'

    def test_margin_left(self):
        self.p.margin_left = 1
        self.assertEqual(1.0, self.p.margin_left)
        self.assertIsInstance(self.p.margin_left, float)
        self.p.margin_left = 0.75
        self.assertEqual(0.75, self.p.margin_left)
        with self.assertRaises(TypeError):
            self.p.margin_left = 'fail'

    def test_margins(self):
        self.p.margins = [1,2,3,4]
        self.assertEqual([1,2,3,4], self.p.margins)
        self.assertIsInstance(self.p.margins, list)
        self.assertEqual(1, self.p.margin_top)
        self.assertEqual(2, self.p.margin_right)
        self.assertEqual(3, self.p.margin_bottom)
        self.assertEqual(4, self.p.margin_left)
        self.p.margins = (2,3,4,5)
        self.assertEqual([2,3,4,5], self.p.margins)
        self.assertIsInstance(self.p.margins, list)
        self.assertEqual(2, self.p.margin_top)
        self.assertEqual(3, self.p.margin_right)
        self.assertEqual(4, self.p.margin_bottom)
        self.assertEqual(5, self.p.margin_left)
        self.p.margins = 3,4,5,6
        self.assertEqual([3,4,5,6], self.p.margins)
        self.assertIsInstance(self.p.margins, list)
        self.assertEqual(3, self.p.margin_top)
        self.assertEqual(4, self.p.margin_right)
        self.assertEqual(5, self.p.margin_bottom)
        self.assertEqual(6, self.p.margin_left)
        self.p.margins = 0.75
        self.assertEqual([0.75, 0.75, 0.75, 0.75], self.p.margins)
        self.assertIsInstance(self.p.margins, list)
        self.assertEqual(0.75, self.p.margin_top)
        self.assertEqual(0.75, self.p.margin_right)
        self.assertEqual(0.75, self.p.margin_bottom)
        self.assertEqual(0.75, self.p.margin_left)

        with self.assertRaises(TypeError):
            self.p.margins = 1, 2, 'fail', 3

        with self.assertRaises(TypeError):
            self.p.margins = 'fail'

    def test_size(self):
        self.p.size = 'a4'
        self.assertEqual('A4', self.p.size)
        self.p.size = 'lEGaL'
        self.assertEqual('LEGAL', self.p.size)
        self.p.size = 'LetTer'
        self.assertEqual('LETTER', self.p.size)
        self.p.size = 'receipt'
        self.assertEqual('RECEIPT', self.p.size)
        self.p.size = 'CUSTOM'
        self.assertEqual('CUSTOM', self.p.size)
        self.assertIsInstance(self.p.size, str)

        with self.assertRaises(TypeError):
            self.p.size = 8.5

        with self.assertRaises(TypeError):
            self.p.size = 1

        with self.assertRaises(ValueError):
            self.p.size = 'fail'

    def test_units(self):
        self.p.units = 'inch'
        self.assertEqual('INCH', self.p.units)
        self.p.units = 'CeNTi'
        self.assertEqual('CENTI', self.p.units)
        self.assertIsInstance(self.p.units, str)
        
        with self.assertRaises(TypeError):
            self.p.units = 8.5

        with self.assertRaises(TypeError):
            self.p.units = 1

        with self.assertRaises(ValueError):
            self.p.units = 'fail'

    def test_orientation(self):
        self.p.orientation = 'portrait'
        self.assertEqual('PORTRAIT', self.p.orientation)
        self.p.orientation = 'LaNdSCapE'
        self.assertEqual('LANDSCAPE', self.p.orientation)
        self.assertIsInstance(self.p.orientation, str)
        
        with self.assertRaises(TypeError):
            self.p.orientation = 8.5

        with self.assertRaises(TypeError):
            self.p.orientation = 1

        with self.assertRaises(ValueError):
            self.p.orientation = 'fail'

    def test_settings(self):
        self.p.margins = 0.5
        self.p.units = 'inch'
        self.p.size = 'letter'
        self.p.orientation = 'portrait'

        kp = self.p.keypath
        self.assertTrue((kp + 'margin_top', '0.5') in self.p.settings)
        self.assertTrue((kp + 'margin_right', '0.5') in self.p.settings)
        self.assertTrue((kp + 'margin_bottom', '0.5') in self.p.settings)
        self.assertTrue((kp + 'margin_left', '0.5') in self.p.settings)
        self.assertTrue((kp + 'margin_unit', 'INCH') in self.p.settings)
        self.assertTrue((kp + 'orientation', 'PORTRAIT') in self.p.settings)
        self.assertTrue((kp + 'paper_size', 'LETTER') in self.p.settings)


class TestReceiptPaper(TestPaperClass):
    def setUp(self):
        self.p = ReceiptPaper()

    def test_orientation(self):
        self.skipTest("orientation setting is not part of "
                      "ReceiptPaper subclass")

    def test_size(self):
        self.skipTest("paper size setting is not part of "
                      "ReceiptPaper subclass")

    def test_width(self):
        self.p.width = 1
        self.assertEqual(1.0, self.p.width)
        self.assertIsInstance(self.p.width, float)
        self.p.width = 0.75
        self.assertEqual(0.75, self.p.width)
        with self.assertRaises(TypeError):
            self.p.width = 'fail'
        
    def test_settings(self):       
        self.p.margins = 0.25
        self.p.units = 'inch'
        self.p.width = 3
        
        self.assertEqual(self.p.margin_top, 0.25)
        self.assertEqual(self.p.margin_right, 0.25)
        self.assertEqual(self.p.margin_bottom, 0.25)
        self.assertEqual(self.p.margin_left, 0.25)
        self.assertEqual(self.p.units, 'INCH')
        self.assertEqual(self.p.width, 3.0)

        kp = self.p.keypath
        margin = kp + 'margin.%s'        
        self.assertTrue((margin % 'top', '0.25') in self.p.settings)
        self.assertTrue((margin % 'right', '0.25') in self.p.settings)
        self.assertTrue((margin % 'bottom', '0.25') in self.p.settings)
        self.assertTrue((margin % 'left', '0.25') in self.p.settings)
        self.assertTrue((kp + 'unit', 'INCH') in self.p.settings)
        self.assertTrue((kp + 'width', '3.0') in self.p.settings)


class TestReceiptPrinter(TestConfiguratorClass, TestSettingsGroup):
    def setUp(self):
        self.rp = ReceiptPrinter(dummy_files)
        # run SettingsGroup class tests
        TestSettingsGroup.setUp(self)
        self.sg = self.rp
        self.keypath = self.rp.keypath
        # run Configurator class tests
        TestConfiguratorClass.setUp(self)
        self.c = self.rp

    def untouched_ReceiptPrinter(self):
        rp = ReceiptPrinter(dummy_files)
        self.assertFalse(rp.changes_staged)
        self.assertFalse(rp.modified)
        return rp
        
    def test_modified(self):
        # adding a new receipt printer flags modified
        rp = self.untouched_ReceiptPrinter()
        rp.add('Some Receipt Printer')
        self.assertTrue(rp.changes_staged)
        self.assertTrue(rp.modified)

        # changing the font flags modified
        rp = self.untouched_ReceiptPrinter()
        rp.font.size = 18
        self.assertTrue(rp.changes_staged)
        self.assertTrue(rp.modified)

        # changing the paper flags modified
        rp = self.untouched_ReceiptPrinter()
        rp.paper.margins = 0.25
        self.assertTrue(rp.changes_staged)
        self.assertTrue(rp.modified)
        
        # enabling flags modified
        rp = self.untouched_ReceiptPrinter()
        rp.enable()
        self.assertTrue(rp.changes_staged)
        self.assertTrue(rp.modified)

        # disabling flags modified
        rp = self.untouched_ReceiptPrinter()
        rp.disable()
        self.assertTrue(rp.changes_staged)
        self.assertTrue(rp.modified)
        
    def test_font(self):
        # ensure fresh files
        makeDummyFiles()
        # prepare font settings
        name, size, style = 'Arbitrary Sans', 18, 'regular'        
        self.rp.font.name = name
        self.assertEqual(name, self.rp.font.name)
        self.rp.font.size = size
        self.assertEqual(size, self.rp.font.size)
        self.rp.font.style = style
        self.assertEqual(ReceiptFont.REGULAR, self.rp.font.style)
        # ensure font string is correctly formatted
        font_str = '|'.join([name, str(ReceiptFont.REGULAR), str(size)])
        self.assertEqual(font_str, str(self.rp.font))
        k, v = self.rp.settings[0]
        font_keypath = self.rp.keypath + 'font'
        self.assertEqual(font_keypath, k)
        self.assertEqual(font_str, v)
        # update files
        self.rp.run()
        # make sure files are updated correctly
        self.checkFiles(font_keypath, font_str)

    def test_paper(self):
        # ensure fresh files
        makeDummyFiles()
        # update files
        key, value = self.rp.paper.keypath + 'width', 3.5
        self.rp.paper.width = value
        self.rp.run()
        # make sure files are updated correctly
        self.checkFiles(key, value, float)

    def test_add(self):
        # ensure fresh files
        makeDummyFiles()
        # update files
        printer_name = 'Some Receipt Printer'               
        self.rp.add(printer_name)
        self.rp.run()
        # make sure files are updated correctly
        key, value = self.rp.keypath + 'name', printer_name
        self.checkFiles(key, value)
        key, value = self.rp.keypath + 'dot_matrix', 'N'
        self.checkFiles(key, value)
        key, value = self.rp.keypath + 'enabled', 'Y'
        self.checkFiles(key, value)

    def test_disable(self):
        # make sure it's enabled
        self.rp.enable()
        self.rp.run()
        # now disable it
        self.rp.disable()
        self.rp.run()
        # make sure files are right
        key, value = self.rp.keypath + 'enabled', 'N'
        self.checkFiles(key, value)

    def test_enable(self):
        # make sure it's disabled
        self.rp.disable()
        self.rp.run()
        # now enable it
        self.rp.enable()
        self.rp.run()
        # make sure files are right
        key, value = self.rp.keypath + 'enabled', 'Y'
        self.checkFiles(key, value)
        

class TestFontConfigurator(TestConfiguratorClass):
    def setUp(self):
        super().setUp()
        self.fc = FontConfigurator(dummy_files)
        self.c = self.fc

    def test_config_line_processor(self):
        line = 'VerifyfieldFont|Arbitrary Sans|bold|18|'
        key, value = 'VerifyfieldFont', 'Arbitrary Sans|bold|18'
        self.assertEqual(self.fc.config_line_processor(line), [key, value])

    def test_config_line_formatter(self):
        line = 'VerifyfieldFont|Arbitrary Sans|bold|18|'
        key, value = 'VerifyfieldFont', 'Arbitrary Sans|bold|18'
        self.assertEqual(self.fc.config_line_formatter(key, value), line)
    
    def test_update(self):
        makeDummyFiles()
        font = ('Arbitrary Sans', 'plain', '23')
        self.fc.update('all', font[0], font[1], int(font[2]))
        self.fc.run()

        value = '|'.join(font)
        for key in gui_components:
            self.checkFiles(key, value)

    def test_batch_update(self):
        updates = [(str(), str())]
        with self.assertRaises(NotImplementedError):
            self.fc.batch_update(updates)

    def test_delete(self):
        key = 'key'
        with self.assertRaises(NotImplementedError):
            self.fc.delete(key)
        

class TestCliParser(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.gettempdir()
        self.font_files = get_property_files('font', {self.tempdir}, True)
        self.pref_files = get_property_files('preference', {self.tempdir}, True)
        self.paper = Paper()
        self.parser = WfCfgParser(self.pref_files, self.font_files)

    def checkFiles(self, Configurator_obj, keypath, value, cfgValParser = None):
        # make sure files are updated correctly
        return checkFiles(self, Configurator_obj, keypath, value, cfgValParser)

    def marginTester(self, configurator, keypath, margins, margin_args):
        # uniform margins from single value
        args = margin_args + ['0.25']
        self.parser.run(args)
        for margin in margins:
            key = keypath + margin
            self.checkFiles(configurator, key, '0.25')

        # values assigned in order to correct margin
        values = ['0.35', '0.45', '0.55', '0.65']
        args = margin_args + values
        self.parser.run(args)
        for margin, value in zip(margins, values):
            key = keypath + margin
            self.checkFiles(configurator, key, value)

        # fail with 3 margin values provided
        args = margin_args + values[1:]
        with self.assertRaises(ValueError):
            self.parser.run(args)

        # fail with 2 margin values provided
        args = margin_args + values[2:]
        with self.assertRaises(ValueError):
            self.parser.run(args)

        # fail with 5 margin values provided
        args = margin_args + values + ['0.75']
        with self.assertRaises(ValueError):
            self.parser.run(args)

    def test_attributes(self):
        # make sure we have the right classes
        self.assertIsInstance(self.parser.main_cfg, Configurator)
        self.assertIsInstance(self.parser.font_cfg, FontConfigurator)
        self.assertIsInstance(self.parser.receipt, ReceiptPrinter)
        # make sure we have the right config files
        self.assertEqual(self.parser.main_cfg.config_files, self.pref_files)
        self.assertEqual(self.parser.font_cfg.config_files, self.font_files)
        self.assertEqual(self.parser.receipt.config_files, self.pref_files)        

    def test_main_crud_parser(self):
        # add two new keys
        args = ['main', '--update', 'foo=bar', 'bar=baz']
        self.parser.run(args)
        self.checkFiles(self.parser.main_cfg, 'foo', 'bar')
        self.checkFiles(self.parser.main_cfg, 'bar', 'baz')
        # update existing keys
        args = ['main', '--update', 'foo=baz', 'bar=foo']
        self.parser.run(args)
        self.checkFiles(self.parser.main_cfg, 'foo', 'baz')
        self.checkFiles(self.parser.main_cfg, 'bar', 'foo')
        # delete one key
        args = ['main', '--delete', 'foo']
        self.parser.run(args)
        for f in self.parser.main_cfg.config_files:
            cfg = fileDict(self.parser.main_cfg, f)
            self.assertFalse('foo' in cfg)
        # delete another key
        args = ['main', '--delete', 'bar']
        self.parser.run(args)
        for f in self.parser.main_cfg.config_files:
            cfg = fileDict(self.parser.main_cfg, f)
            self.assertFalse('bar' in cfg)

    def test_paper_parser_units(self):
        # test paper units setting        
        key = self.paper.keypath + 'margin_unit'
        for value in paper_units:
            args = ['paper', '--units', value]
            self.parser.run(args)
            self.checkFiles(self.parser.main_cfg, key, value.upper())

    def test_paper_parser_size(self):
        # test paper size setting
        key = self.paper.keypath + 'paper_size'
        for value in paper_sizes:            
            args = ['paper', '--size', value]
            self.parser.run(args)
            self.checkFiles(self.parser.main_cfg, key, value.upper())

    def test_paper_parser_orientation(self):
        # test paper orientation setting
        key = self.paper.keypath + 'orientation'
        for value in paper_orientation:            
            args = ['paper', '--orientation', value]
            self.parser.run(args)
            self.checkFiles(self.parser.main_cfg, key, value.upper())

    def test_paper_parser_margins(self):
        keypath = self.paper.keypath
        margins = ['margin_' + m for m in ['top','right','bottom','left']]
        configurator = self.parser.main_cfg
        margin_args = ['paper', '--margins']
        self.marginTester(configurator, keypath, margins, margin_args)
        
    def test_font_parser(self):
        # test updating ALL gui components
        args = ['font', 'ALL', '"Arbitrary Sans"', '23', 'bold']
        font = Font(args[2], args[4], args[3])
        make_uniform = lambda: self.parser.run(args)
        make_uniform()
        for gc in gui_components:
            self.checkFiles(self.parser.font_cfg, gc, str(font))

        # test updating targeted gui components
        for target_gc in gui_components:
            make_uniform() # reset to original values of old font
            new_args = ['font', target_gc, 'Another Font', '42', 'italic']
            new_font = Font(new_args[2], new_args[4], new_args[3])
            self.parser.run(new_args) # target single gui component with new font
            for gc in gui_components:
                if gc == target_gc:
                    expected_value = str(new_font)
                else:
                    expected_value = str(font)
                self.checkFiles(self.parser.font_cfg, gc, expected_value)

    def test_receipt_parser_paper(self):
        keypath = self.parser.receipt.paper.keypath
        margins = ['margin.' + m for m in ['top','right','bottom','left']]
        configurator = self.parser.receipt
        margin_args = ['receipt-printer', '--paper-margins']
        self.marginTester(configurator, keypath, margins, margin_args)

        args = ['receipt-printer', '--paper-width', '5.50']
        self.parser.run(args)
        key = keypath + 'width'
        self.checkFiles(self.parser.receipt, key, 5.5, float)

        for p_unit in paper_units:
            args = ['receipt-printer', '--paper-units', p_unit]
            self.parser.run(args)
            key = keypath + 'unit'
            self.checkFiles(self.parser.receipt, key, p_unit.upper())
        
    def __receipt_printer_remove(self):
        args = ['receipt-printer', '--remove']
        self.parser.run(args)
        key = self.parser.receipt.keypath + 'enabled'
        self.checkFiles(self.parser.receipt, key, 'N')

    def __receipt_printer_add(self):
        printer_name = 'ReceiptBoss 5000'
        args = ['receipt-printer', '--add', printer_name]
        self.parser.run(args)
        key = self.parser.receipt.keypath + 'enabled'
        self.checkFiles(self.parser.receipt, key, 'Y')
        key = self.parser.receipt.keypath + 'name'
        self.checkFiles(self.parser.receipt, key, printer_name)

    def test_receipt_parser_add_remove(self):
        self.__receipt_printer_remove()
        self.__receipt_printer_add()
        self.__receipt_printer_remove()

        
if __name__ == '__main__':
    unittest.main()
