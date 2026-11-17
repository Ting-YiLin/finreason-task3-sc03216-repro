import unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from score_practice import normalize_id,decimalize,pair_eq
class Tests(unittest.TestCase):
 def test_id(self):
  self.assertEqual(normalize_id(48),'DEV_000048')
  self.assertEqual(normalize_id('000048'),'DEV_000048')
 def test_decimal(self):
  self.assertEqual(decimalize('(1,284)'),decimalize('-1284'))
  self.assertEqual(decimalize('1284.00'),decimalize('1,284'))
 def test_joint(self):
  self.assertFalse(pair_eq({'extracted_value':'-1','calculated_value':'0'},{'extracted_value':'-1','calculated_value':'1'}))
if __name__=='__main__':unittest.main()
