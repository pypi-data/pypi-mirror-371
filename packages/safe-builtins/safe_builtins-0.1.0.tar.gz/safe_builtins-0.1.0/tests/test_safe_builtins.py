from result import Ok, Err

# Import all safe built-ins
from safe_builtins import (
    safe_abs, safe_all, safe_any, safe_ascii, safe_bin,
    safe_bytearray, safe_bytes, safe_chr, safe_compile,
    safe_complex, safe_dict, safe_divmod, safe_float, safe_int,
    safe_len, safe_list, safe_max, safe_min, safe_open, safe_ord, safe_pow, safe_range, safe_round,
    safe_set, safe_str,
    safe_sum, safe_tuple, safe_type, safe_zip, safe_bool
)

def test_safe_abs():
    # Test successful case
    result = safe_abs(-5)
    assert isinstance(result, Ok)
    assert result.unwrap() == 5
    
    # Test error case
    # Using a built-in type that doesn't support __abs__ to trigger TypeError
    result = safe_abs(None)
    assert isinstance(result, Err)

def test_safe_all():
    # Test successful case
    result = safe_all([True, True, False])
    assert isinstance(result, Ok)
    assert not result.unwrap()
    
    result = safe_all([True, True, True])
    assert isinstance(result, Ok)
    assert result.unwrap()
    
    # Test error case with a non-iterable object
    result = safe_all(123)  # integers are not iterable
    assert isinstance(result, Err)

def test_safe_any():
    # Test successful case
    result = safe_any([False, False, True])
    assert isinstance(result, Ok)
    assert result.unwrap()
    
    result = safe_any([False, False, False])
    assert isinstance(result, Ok)
    assert not result.unwrap()
    
    # Test error case with a non-iterable object
    result = safe_any(123)  # integers are not iterable
    assert isinstance(result, Err)

def test_safe_ascii():
    # Test successful case
    result = safe_ascii("Hello")
    assert isinstance(result, Ok)
    assert result.unwrap() == "'Hello'"
    
    # Test error case
    # Using a custom object that raises TypeError in __repr__
    class NotStringable:
        def __repr__(self):
            raise TypeError("Cannot convert to string")
    
    result = safe_ascii(NotStringable())
    assert isinstance(result, Err)

def test_safe_bin():
    # Test successful case
    result = safe_bin(10)
    assert isinstance(result, Ok)
    assert result.unwrap() == '0b1010'
    
    # Test error case
    result = safe_bin("not a number")
    assert isinstance(result, Err)

def test_safe_bool():
    # Test successful cases
    result = safe_bool(1)
    assert isinstance(result, Ok)
    assert result.unwrap()
    
    result = safe_bool(0)
    assert isinstance(result, Ok)
    assert not result.unwrap()
    
    result = safe_bool("")
    assert isinstance(result, Ok)
    assert not result.unwrap()
    
    # Test error case
    # Using a custom object that raises TypeError in __bool__
    class NotConvertible:
        def __bool__(self):
            raise TypeError("Cannot convert to bool")
    
    result = safe_bool(NotConvertible())
    assert isinstance(result, Err)

def test_safe_bytearray():
    # Test successful case
    result = safe_bytearray([1, 2, 3])
    assert isinstance(result, Ok)
    assert isinstance(result.unwrap(), bytearray)
    
    # Test error case
    result = safe_bytearray(-1)  # Negative size
    assert isinstance(result, Err)

def test_safe_bytes():
    # Test successful case
    result = safe_bytes([1, 2, 3])
    assert isinstance(result, Ok)
    assert isinstance(result.unwrap(), bytes)
    
    # Test error case
    result = safe_bytes(-1)  # Negative size
    assert isinstance(result, Err)

def test_safe_chr():
    # Test successful case
    result = safe_chr(65)
    assert isinstance(result, Ok)
    assert result.unwrap() == 'A'
    
    # Test error case
    # Using a negative number to trigger ValueError
    result = safe_chr(-1)  # Invalid Unicode code point
    assert isinstance(result, Err)

def test_safe_compile():
    # Test successful case
    result = safe_compile("1 + 1", "<string>", "eval")
    assert isinstance(result, Ok)
    # Check that we can evaluate the compiled code
    compiled_code = result.unwrap()
    assert eval(compiled_code) == 2
    
    # Test error case
    result = safe_compile("invalid syntax", "<string>", "eval")
    assert isinstance(result, Err)

def test_safe_complex():
    # Test successful cases
    result = safe_complex(1)
    assert isinstance(result, Ok)
    assert result.unwrap() == (1+0j)
    
    result = safe_complex("1+2j")
    assert isinstance(result, Ok)
    assert result.unwrap() == (1+2j)
    
    # Test error case
    result = safe_complex("invalid")
    assert isinstance(result, Err)

def test_safe_dict():
    # Test successful cases
    result = safe_dict()
    assert isinstance(result, Ok)
    assert result.unwrap() == {}
    
    result = safe_dict(a=1, b=2)
    assert isinstance(result, Ok)
    assert result.unwrap() == {'a': 1, 'b': 2}
    
    # Test error case
    result = safe_dict({1, 2, 3})  # Set is not a valid argument
    assert isinstance(result, Err)

def test_safe_divmod():
    # Test successful case
    result = safe_divmod(10, 3)
    assert isinstance(result, Ok)
    assert result.unwrap() == (3, 1)
    
    # Test error case - division by zero
    result = safe_divmod(10, 0)
    assert isinstance(result, Err)

def test_safe_float():
    # Test successful cases
    result = safe_float("3.14")
    assert isinstance(result, Ok)
    assert result.unwrap() == 3.14
    
    result = safe_float(42)
    assert isinstance(result, Ok)
    assert result.unwrap() == 42.0
    
    # Test error case
    result = safe_float("not a number")
    assert isinstance(result, Err)

def test_safe_int():
    # Test successful cases
    result = safe_int("42")
    assert isinstance(result, Ok)
    assert result.unwrap() == 42
    
    result = safe_int(3.14)
    assert isinstance(result, Ok)
    assert result.unwrap() == 3
    
    result = safe_int("42", 16)  # Base 16
    assert isinstance(result, Ok)
    assert result.unwrap() == 66
    
    # Test error case
    result = safe_int("not a number")
    assert isinstance(result, Err)

def test_safe_len():
    # Test successful case
    result = safe_len([1, 2, 3])
    assert isinstance(result, Ok)
    assert result.unwrap() == 3
    
    # Test error case
    # Using an integer, which doesn't have a length
    result = safe_len(123)
    assert isinstance(result, Err)

def test_safe_list():
    # Test successful case
    result = safe_list((1, 2, 3))
    assert isinstance(result, Ok)
    assert result.unwrap() == [1, 2, 3]
    
    # Test error case with a non-iterable object
    result = safe_list(123)  # integers are not iterable
    assert isinstance(result, Err)

def test_safe_max():
    # Test successful case
    result = safe_max([1, 2, 3])
    assert isinstance(result, Ok)
    assert result.unwrap() == 3
    
    # Test error case - empty sequence without default
    result = safe_max([])
    assert isinstance(result, Err)

def test_safe_min():
    # Test successful case
    result = safe_min([1, 2, 3])
    assert isinstance(result, Ok)
    assert result.unwrap() == 1
    
    # Test error case - empty sequence without default
    result = safe_min([])
    assert isinstance(result, Err)

def test_safe_open():
    # Test error case - file doesn't exist
    result = safe_open("non_existent_file.txt")
    assert isinstance(result, Err)
    
    # We won't test successful case as it would require creating temporary files

def test_safe_ord():
    # Test successful case
    result = safe_ord('A')
    assert isinstance(result, Ok)
    assert result.unwrap() == 65
    
    # Test error case
    result = safe_ord('AB')  # More than one character
    assert isinstance(result, Err)

def test_safe_pow():
    # Test successful case
    result = safe_pow(2, 3)
    assert isinstance(result, Ok)
    assert result.unwrap() == 8
    
    # Test error case
    result = safe_pow(2, -3, 0)  # Third argument is zero
    assert isinstance(result, Err)

def test_safe_range():
    # Test successful case
    result = safe_range(5)
    assert isinstance(result, Ok)
    assert list(result.unwrap()) == [0, 1, 2, 3, 4]
    
    # Test error case
    result = safe_range("not a number")
    assert isinstance(result, Err)

def test_safe_round():
    # Test successful case
    result = safe_round(3.14159, 2)
    assert isinstance(result, Ok)
    assert result.unwrap() == 3.14
    
    # Test error case
    result = safe_round("not a number")
    assert isinstance(result, Err)

def test_safe_set():
    # Test successful case
    result = safe_set([1, 2, 2, 3])
    assert isinstance(result, Ok)
    assert result.unwrap() == {1, 2, 3}
    
    # Test error case with a non-iterable object
    result = safe_set(123)  # integers are not iterable
    assert isinstance(result, Err)

def test_safe_str():
    # Test successful case
    result = safe_str(123)
    assert isinstance(result, Ok)
    assert result.unwrap() == "123"
    
    # Test error case
    # Using a custom object that raises TypeError in __str__
    class NotStringable:
        def __str__(self):
            raise TypeError("Cannot convert to string")
    
    result = safe_str(NotStringable())
    assert isinstance(result, Err)

def test_safe_sum():
    # Test successful case
    result = safe_sum([1, 2, 3])
    assert isinstance(result, Ok)
    assert result.unwrap() == 6
    
    # Test error case
    result = safe_sum([1, 2, "not a number"])
    assert isinstance(result, Err)

def test_safe_tuple():
    # Test successful case
    result = safe_tuple([1, 2, 3])
    assert isinstance(result, Ok)
    assert result.unwrap() == (1, 2, 3)
    
    # Test error case with a non-iterable object
    result = safe_tuple(123)  # integers are not iterable
    assert isinstance(result, Err)

def test_safe_type():
    # Test successful case
    result = safe_type("Hello")
    assert isinstance(result, Ok)
    assert result.unwrap() is str
    
    # Test error case with 3 arguments (name, bases, dict)
    result = safe_type("NewClass", (), {})
    assert isinstance(result, Ok)
    
    # Test error case
    result = safe_type("NewClass", "not a tuple", {})
    assert isinstance(result, Err)

def test_safe_zip():
    # Test successful case
    result = safe_zip([1, 2], ['a', 'b'])
    assert isinstance(result, Ok)
    assert list(result.unwrap()) == [(1, 'a'), (2, 'b')]
    
    # Test error case with a non-iterable object
    result = safe_zip(123)  # integers are not iterable
    assert isinstance(result, Err)
