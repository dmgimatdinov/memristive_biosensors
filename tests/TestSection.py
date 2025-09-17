
import unittest
from DB_6 import Section, BiosensorGUI

class TestSection(unittest.TestCase):
    
    def test_GUI_pagination(self):
        biosensorGUI = BiosensorGUI()
        self.assertEqual(biosensorGUI.page_size, 50)
        
if __name__ == '__main__':
    unittest.main()