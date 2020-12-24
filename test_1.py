import unittest
from decimal import Decimal
from backend import task


class TaskTest(unittest.TestCase):
    
    # Correctness tests
    def test_empty(self):
        data_list = []
        self.assertEqual(task(data_list), 0)

    def test_one_num(self):
        data_list = [1]
        self.assertEqual(task(data_list), 1)

    def test_all_positives(self):
        data_list = [1, 0.7, 11, 4, 2]
        self.assertAlmostEqual(task(data_list), 1.529294935451837, places = 8)

    def test_all_negatives(self):
        data_list = [-1, -0.7, -11, -4, -2]
        self.assertEqual(task(data_list), 0)

    def test_all_zeros(self):
        data_list = [0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(task(data_list), 0)

    def test_positives_negatives_zero(self):
        data_list = [0.3, -2, 0, 12, 1.111, 0.023, -1]
        self.assertAlmostEqual(task(data_list), 0.08369073190975263, places = 8)
    
    # Errors tests
    def test_only_incorrect_values(self):
        data_lists = [['0', 'ad', ' '], ['', [], int]]
        for data_list in data_lists:
            self.assertRaises(TypeError, task, data_list)

    def test_numeric_incorrect_values(self):
        data_lists = [[1, 0, 'aaacs a', '-1', -0.1, 7], [float, 1.1111, -2.9, ';']]
        for data_list in data_lists:
            self.assertRaises(TypeError, task, data_list)

    # Additional
    def test_decimal_module(self):
        data_list = [Decimal("11.1"), Decimal("0.0"), Decimal("-1.2"), Decimal("7.1"), Decimal("-2"), Decimal("2.2222"), Decimal("12.3")]
        self.assertEqual(task(data_list).quantize(Decimal("1.00000000")), Decimal('5.24768776'))
    
    def test_small_number(self):
        data_lists = [[1e-20], [1e-17, -2, 1, 0.3]]
        answers = [1e-20, 3e-17]
        for data_list, answer in zip(data_lists, answers):
            self.assertEqual(task(data_list), answer)

    def test_big_number(self):
        data_lists = [[1e+20], [0, 2e+18, -1.123, 0.1, 3, -2, 1]]
        answers = [1e+20, 0.3529411764705882]
        for data_list, answer in zip(data_lists, answers):
            self.assertAlmostEqual(task(data_list), answer, places = 8)
    
    def test_big_small_numbers(self):
        data_lists = [[1e+19, 1e-18], [0, 2e+18, 1e-19, -0.1, -3, 2, 0.001, 11]]
        answers = [2e-18, 4.999999999999999e-19]
        for data_list, answer in zip(data_lists, answers):
            self.assertAlmostEqual(task(data_list), answer, places = 8)


if __name__ == "__main__":
    unittest.main()
