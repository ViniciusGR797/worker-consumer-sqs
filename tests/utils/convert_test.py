import unittest
from decimal import Decimal
from utils.convert import convert_floats_to_decimal

class TestConvertFloatsToDecimal(unittest.TestCase):

    def test_float_conversion(self):
        result = convert_floats_to_decimal(12.34)
        self.assertIsInstance(result, Decimal)
        self.assertEqual(result, Decimal("12.34"))

    def test_int_remains_int(self):
        result = convert_floats_to_decimal(42)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 42)

    def test_str_remains_str(self):
        result = convert_floats_to_decimal("hello")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "hello")

    def test_bool_remains_bool(self):
        result = convert_floats_to_decimal(True)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_none_remains_none(self):
        result = convert_floats_to_decimal(None)
        self.assertIsNone(result)

    def test_list_with_floats(self):
        data = [1, 2.5, "abc", 3.75]
        result = convert_floats_to_decimal(data)
        self.assertEqual(result, [1, Decimal("2.5"), "abc", Decimal("3.75")])
        for i, val in enumerate(result):
            if isinstance(val, Decimal):
                self.assertIsInstance(val, Decimal)

    def test_dict_with_floats(self):
        data = {"a": 1, "b": 2.5, "c": {"d": 3.75}}
        result = convert_floats_to_decimal(data)
        self.assertEqual(result["a"], 1)
        self.assertIsInstance(result["b"], Decimal)
        self.assertEqual(result["b"], Decimal("2.5"))
        self.assertIsInstance(result["c"]["d"], Decimal)
        self.assertEqual(result["c"]["d"], Decimal("3.75"))

    def test_nested_structures(self):
        data = {"x": [1, 2.5, {"y": 3.75}], "z": 4.0}
        result = convert_floats_to_decimal(data)
        self.assertIsInstance(result["z"], Decimal)
        self.assertIsInstance(result["x"][1], Decimal)
        self.assertIsInstance(result["x"][2]["y"], Decimal)
        self.assertEqual(result["z"], Decimal("4.0"))
        self.assertEqual(result["x"][1], Decimal("2.5"))
        self.assertEqual(result["x"][2]["y"], Decimal("3.75"))
