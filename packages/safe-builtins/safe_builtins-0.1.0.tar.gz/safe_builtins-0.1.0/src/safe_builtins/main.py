from result import (
    as_result
)

safe_abs = as_result(ValueError, TypeError)(abs)
safe_aiter = as_result(TypeError)(aiter)
safe_all = as_result(TypeError)(all)
safe_any = as_result(TypeError)(any)
safe_anext = as_result(TypeError, StopAsyncIteration)(anext)
safe_ascii = as_result(TypeError)(ascii)
safe_bin = as_result(TypeError)(bin)
safe_breakpoint = as_result(RuntimeError)(breakpoint)
safe_bytearray = as_result(TypeError, ValueError)(bytearray)
safe_bytes = as_result(TypeError, ValueError)(bytes)
safe_chr = as_result(TypeError, ValueError)(chr)
safe_compile = as_result(SyntaxError, ValueError, TypeError)(compile)
safe_complex = as_result(TypeError, ValueError)(complex)
safe_delattr = as_result(TypeError, AttributeError)(delattr)
safe_dict = as_result(TypeError, ValueError)(dict)
safe_dir = as_result(TypeError)(dir)
safe_divmod = as_result(TypeError, ZeroDivisionError)(divmod)
safe_enumerate = as_result(TypeError)(enumerate)
safe_eval = as_result(SyntaxError, NameError, TypeError)(eval)
safe_exec = as_result(SyntaxError, TypeError)(exec)
safe_filter = as_result(TypeError)(filter)
safe_float = as_result(TypeError, ValueError)(float)
safe_format = as_result(TypeError, ValueError)(format)
safe_frozenset = as_result(TypeError)(frozenset)
safe_getattr = as_result(TypeError, AttributeError)(getattr)
safe_hash = as_result(TypeError)(hash)
safe_hex = as_result(TypeError)(hex)
safe_id = as_result(TypeError)(id)
safe_input = as_result(EOFError, KeyboardInterrupt, TypeError)(input)
safe_int = as_result(TypeError, ValueError)(int)
safe_isinstance = as_result(TypeError)(isinstance)
safe_issubclass = as_result(TypeError)(issubclass)
safe_iter = as_result(TypeError)(iter)
safe_len = as_result(TypeError, OverflowError)(len)
safe_list = as_result(TypeError)(list)
safe_map = as_result(TypeError)(map)
safe_max = as_result(TypeError, ValueError)(max)
safe_memoryview = as_result(TypeError, ValueError)(memoryview)
safe_min = as_result(TypeError, ValueError)(min)
safe_next = as_result(TypeError, StopIteration)(next)
safe_object = as_result(TypeError)(object)
safe_oct = as_result(TypeError)(oct)

safe_open = as_result(
        FileNotFoundError,
        IsADirectoryError,
        NotADirectoryError,
        PermissionError,
        FileExistsError,
        OSError,
        ValueError,
        TypeError,
    )(open)

safe_ord = as_result(TypeError, ValueError)(ord)
safe_bool = as_result(TypeError)(bool)
safe_pow = as_result(TypeError, ValueError)(pow)
safe_range = as_result(TypeError, ValueError)(range)
safe_reversed = as_result(TypeError)(reversed)
safe_round = as_result(TypeError)(round)
safe_set = as_result(TypeError)(set)
safe_setattr = as_result(TypeError, AttributeError)(setattr)
safe_slice = as_result(TypeError)(slice)
safe_sorted = as_result(TypeError)(sorted)
safe_staticmethod = as_result(TypeError)(staticmethod)
safe_str = as_result(TypeError, UnicodeError)(str)
safe_sum = as_result(TypeError)(sum)
safe_super = as_result(TypeError)(super)
safe_tuple = as_result(TypeError)(tuple)
safe_type = as_result(TypeError)(type)
safe_vars = as_result(TypeError)(vars)
safe_zip = as_result(TypeError)(zip)
safe_import = as_result(ImportError, ModuleNotFoundError)(__import__)

