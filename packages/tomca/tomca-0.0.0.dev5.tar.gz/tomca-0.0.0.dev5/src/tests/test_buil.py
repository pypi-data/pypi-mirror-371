import unittest
from tmcx.buil import calc_vol_depth
from pathlib import Path
from Software import tmcx

jcfg = tmcx.impo.jcfg_json(Path(r"C:\dev\mcx\Software\tests\test_modal.json"))


class TestBuil(unittest.TestCase):

    def test_vol_equality(self):
        self.assertEqual(calc_vol_depth(jcfg), 4.93)

    def test_vol_positive(self):
        self.assertTrue(calc_vol_depth(jcfg) > 0)


if __name__ == "__main__":
    unittest.main()
