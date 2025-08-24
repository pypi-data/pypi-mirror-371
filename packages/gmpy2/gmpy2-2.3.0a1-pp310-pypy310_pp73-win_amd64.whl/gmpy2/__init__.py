"""""" # start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'gmpy2.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

from .gmpy2 import *
from .gmpy2 import __version__
# Internal variables/functions are not imported by * above.
# These are used by some python level functions and are needed
# at the top level.
# Use try...except to for static builds were _C_API is not available.
try:
    from .gmpy2 import _C_API, _mpmath_normalize, _mpmath_create
except ImportError:
    from .gmpy2 import _mpmath_normalize, _mpmath_create
