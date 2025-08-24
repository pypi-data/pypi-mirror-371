#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Comprehensive tests for fx_lib.func module."""

import unittest
from typing import Any, List
import sys
import os
import importlib.util

# Add the fx_lib package to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import modules directly to avoid package-level imports that require yaml
def load_module_from_file(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load modules directly
base_dir = os.path.join(os.path.dirname(__file__), '..', 'fx_lib')
func_module = load_module_from_file('func', os.path.join(base_dir, 'func.py'))
math_module = load_module_from_file('math', os.path.join(base_dir, 'math.py'))

# Extract functions we need to test
range1 = func_module.range1
enumerate1 = func_module.enumerate1
p = func_module.p
convert_size = func_module.convert_size
chunks = func_module.chunks
modable = math_module.modable


class TestRange1(unittest.TestCase):
    """Tests for range1() function - 1-indexed range."""
    
    def test_range1_positive_integer(self):
        """Test range1 with positive integer."""
        result = list(range1(5))
        self.assertEqual(result, [1, 2, 3, 4, 5])
    
    def test_range1_one(self):
        """Test range1 with n=1."""
        result = list(range1(1))
        self.assertEqual(result, [1])
    
    def test_range1_zero(self):
        """Test range1 with n=0."""
        result = list(range1(0))
        self.assertEqual(result, [])
    
    def test_range1_negative(self):
        """Test range1 with negative integer."""
        result = list(range1(-1))
        self.assertEqual(result, [])
    
    def test_range1_large_number(self):
        """Test range1 with large number."""
        result = list(range1(1000))
        self.assertEqual(len(result), 1000)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[-1], 1000)


class TestEnumerate1(unittest.TestCase):
    """Tests for enumerate1() function - 1-indexed enumerate."""
    
    def test_enumerate1_list(self):
        """Test enumerate1 with a list."""
        result = list(enumerate1(['a', 'b', 'c']))
        self.assertEqual(result, [(1, 'a'), (2, 'b'), (3, 'c')])
    
    def test_enumerate1_tuple(self):
        """Test enumerate1 with a tuple."""
        result = list(enumerate1(('x', 'y', 'z')))
        self.assertEqual(result, [(1, 'x'), (2, 'y'), (3, 'z')])
    
    def test_enumerate1_string(self):
        """Test enumerate1 with a string."""
        result = list(enumerate1('abc'))
        self.assertEqual(result, [(1, 'a'), (2, 'b'), (3, 'c')])
    
    def test_enumerate1_empty_list(self):
        """Test enumerate1 with empty list."""
        result = list(enumerate1([]))
        self.assertEqual(result, [])
    
    def test_enumerate1_single_item(self):
        """Test enumerate1 with single item."""
        result = list(enumerate1(['only']))
        self.assertEqual(result, [(1, 'only')])
    
    def test_enumerate1_generator(self):
        """Test enumerate1 with a generator."""
        def gen():
            yield 'first'
            yield 'second'
        
        result = list(enumerate1(gen()))
        self.assertEqual(result, [(1, 'first'), (2, 'second')])


class TestFunctionComposition(unittest.TestCase):
    """Tests for p() function - function composition utility."""
    
    def test_p_single_function(self):
        """Test p with single function."""
        result = p(5, lambda x: x * 2)
        self.assertEqual(result, 10)
    
    def test_p_multiple_functions(self):
        """Test p with multiple functions."""
        result = p(5, lambda x: x * 2, lambda x: x + 3, lambda x: x / 2)
        # 5 * 2 = 10, 10 + 3 = 13, 13 / 2 = 6.5
        self.assertEqual(result, 6.5)
    
    def test_p_no_functions(self):
        """Test p with no functions (should return original value)."""
        result = p(42)
        self.assertEqual(result, 42)
    
    def test_p_string_operations(self):
        """Test p with string operations."""
        result = p('hello', str.upper, lambda x: x + ' WORLD', str.lower)
        self.assertEqual(result, 'hello world')
    
    def test_p_list_operations(self):
        """Test p with list operations."""
        result = p([1, 2, 3], lambda x: x + [4], lambda x: x * 2)
        self.assertEqual(result, [1, 2, 3, 4, 1, 2, 3, 4])
    
    def test_p_type_conversion(self):
        """Test p with type conversion functions."""
        result = p('123', int, lambda x: x * 2, str)
        self.assertEqual(result, '246')
    
    def test_p_with_none(self):
        """Test p with None value."""
        result = p(None, lambda x: x or 'default', str.upper)
        self.assertEqual(result, 'DEFAULT')


class TestConvertSize(unittest.TestCase):
    """Tests for convert_size() function - human-readable file size formatting."""
    
    def test_convert_size_zero(self):
        """Test convert_size with zero bytes."""
        result = convert_size(0)
        self.assertEqual(result, '0B')
    
    def test_convert_size_bytes(self):
        """Test convert_size with bytes."""
        self.assertEqual(convert_size(500), '500.0B')
        self.assertEqual(convert_size(1023), '1023.0B')
    
    def test_convert_size_kilobytes(self):
        """Test convert_size with kilobytes."""
        self.assertEqual(convert_size(1024), '1.0KB')
        self.assertEqual(convert_size(1536), '1.5KB')  # 1024 + 512
        self.assertEqual(convert_size(2048), '2.0KB')
    
    def test_convert_size_megabytes(self):
        """Test convert_size with megabytes."""
        self.assertEqual(convert_size(1024 * 1024), '1.0MB')
        self.assertEqual(convert_size(1536 * 1024), '1.5MB')
    
    def test_convert_size_gigabytes(self):
        """Test convert_size with gigabytes."""
        self.assertEqual(convert_size(1024 * 1024 * 1024), '1.0GB')
        self.assertEqual(convert_size(int(2.5 * 1024 * 1024 * 1024)), '2.5GB')
    
    def test_convert_size_large_values(self):
        """Test convert_size with very large values."""
        # Test TB
        tb_size = 1024 ** 4
        self.assertEqual(convert_size(tb_size), '1.0TB')
        
        # Test PB
        pb_size = 1024 ** 5
        self.assertEqual(convert_size(pb_size), '1.0PB')
    
    def test_convert_size_string_input(self):
        """Test convert_size with string input that can be converted to int."""
        result = convert_size('1024')
        self.assertEqual(result, '1.0KB')
    
    def test_convert_size_float_input(self):
        """Test convert_size with float input."""
        result = convert_size(1536.7)
        self.assertEqual(result, '1.5KB')
    
    def test_convert_size_invalid_input(self):
        """Test convert_size with invalid input."""
        with self.assertRaises(ValueError):
            convert_size('not_a_number')
    
    def test_convert_size_negative_input(self):
        """Test convert_size with negative input."""
        # This should raise an error since negative file sizes don't make sense
        with self.assertRaises(ValueError):
            convert_size(-1024)


class TestChunks(unittest.TestCase):
    """Tests for chunks() function - split lists into evenly sized chunks."""
    
    def test_chunks_even_division(self):
        """Test chunks with list that divides evenly."""
        result = list(chunks([1, 2, 3, 4, 5, 6], 2))
        self.assertEqual(result, [[1, 2], [3, 4], [5, 6]])
    
    def test_chunks_uneven_division(self):
        """Test chunks with list that doesn't divide evenly."""
        result = list(chunks([1, 2, 3, 4, 5], 2))
        self.assertEqual(result, [[1, 2], [3, 4], [5]])
    
    def test_chunks_single_chunk(self):
        """Test chunks where chunk size equals list length."""
        result = list(chunks([1, 2, 3], 3))
        self.assertEqual(result, [[1, 2, 3]])
    
    def test_chunks_chunk_size_larger_than_list(self):
        """Test chunks where chunk size is larger than list."""
        result = list(chunks([1, 2], 5))
        self.assertEqual(result, [[1, 2]])
    
    def test_chunks_empty_list(self):
        """Test chunks with empty list."""
        result = list(chunks([], 2))
        self.assertEqual(result, [])
    
    def test_chunks_single_element(self):
        """Test chunks with single element list."""
        result = list(chunks(['only'], 1))
        self.assertEqual(result, [['only']])
    
    def test_chunks_chunk_size_one(self):
        """Test chunks with chunk size of 1."""
        result = list(chunks([1, 2, 3], 1))
        self.assertEqual(result, [[1], [2], [3]])
    
    def test_chunks_string_list(self):
        """Test chunks with list of strings."""
        result = list(chunks(['a', 'b', 'c', 'd', 'e'], 3))
        self.assertEqual(result, [['a', 'b', 'c'], ['d', 'e']])
    
    def test_chunks_mixed_types(self):
        """Test chunks with mixed data types."""
        result = list(chunks([1, 'two', 3.0, True, None], 2))
        self.assertEqual(result, [[1, 'two'], [3.0, True], [None]])
    
    def test_chunks_zero_chunk_size(self):
        """Test chunks with zero chunk size."""
        with self.assertRaises(ValueError):
            list(chunks([1, 2, 3], 0))
    
    def test_chunks_negative_chunk_size(self):
        """Test chunks with negative chunk size."""
        with self.assertRaises(ValueError):
            list(chunks([1, 2, 3], -1))


class TestModable(unittest.TestCase):
    """Tests for modable() function from math module - divisibility check."""
    
    def test_modable_divisible(self):
        """Test modable with numbers that are divisible."""
        self.assertTrue(modable(10, 2))
        self.assertTrue(modable(15, 3))
        self.assertTrue(modable(100, 10))
        self.assertTrue(modable(0, 5))  # 0 is divisible by any non-zero number
    
    def test_modable_not_divisible(self):
        """Test modable with numbers that are not divisible."""
        self.assertFalse(modable(10, 3))
        self.assertFalse(modable(7, 2))
        self.assertFalse(modable(100, 7))
    
    def test_modable_negative_numbers(self):
        """Test modable with negative numbers."""
        self.assertTrue(modable(-10, 2))
        self.assertTrue(modable(10, -2))
        self.assertTrue(modable(-10, -2))
        self.assertFalse(modable(-10, 3))
    
    def test_modable_same_numbers(self):
        """Test modable with same numbers."""
        self.assertTrue(modable(5, 5))
        self.assertTrue(modable(-5, -5))
    
    def test_modable_division_by_zero(self):
        """Test modable with division by zero."""
        with self.assertRaises(ZeroDivisionError):
            modable(10, 0)
    
    def test_modable_large_numbers(self):
        """Test modable with large numbers."""
        self.assertTrue(modable(1000000, 1000))
        self.assertFalse(modable(1000001, 1000))


if __name__ == '__main__':
    unittest.main()