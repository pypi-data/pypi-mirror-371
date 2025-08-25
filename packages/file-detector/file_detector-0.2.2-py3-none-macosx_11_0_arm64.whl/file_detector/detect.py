import os
import sys
import ctypes
from ctypes import c_char_p, c_size_t, c_uint8, c_uint16, Structure
from typing import NamedTuple
from enum import IntEnum

PathLike = str | os.PathLike[str]

# Resolve shared library name
if sys.platform.startswith("win"):
    _LIB_NAME = "_file_detect.dll"
elif sys.platform == "darwin":
    _LIB_NAME = "_file_detect.dylib"
else:
    _LIB_NAME = "_file_detect.so"

_DIR = os.path.dirname(__file__)

# Load the library beside this package or from current working dir
_lib_path = os.path.join(_DIR, _LIB_NAME)
_db_path = os.path.join(_DIR, "magic.mgc")

if not os.path.exists(_lib_path):
    # Fall back to letting the linker search path resolve it
    _lib_path = _LIB_NAME

_lib = ctypes.CDLL(_lib_path)

class _fd_kind_t(Structure):
    _fields_ = [("category", c_uint8),
                ("_align", c_uint8),
                ("subtype", c_uint16)]

# Prototypes
_lib.fd_detect_file_kind.argtypes = [c_char_p]
_lib.fd_detect_file_kind.restype = _fd_kind_t

_lib.fd_detect_buffer_kind.argtypes = [ctypes.c_void_p, c_size_t]
_lib.fd_detect_buffer_kind.restype = _fd_kind_t

_lib.fd_set_magic_db_path.argtypes = [c_char_p]
_lib.fd_set_magic_db_path.restype = None

# the library should handle closing on thread shutdown
# _lib.fd_close_for_thread.argtypes = []
# _lib.fd_close_for_thread.restype = None

_lib.fd_set_magic_db_path(os.fsencode(_db_path))

# Public API

class FileCategory(IntEnum):
    UNKNOWN    = 0
    TEXT       = 1
    DOCUMENT   = 2
    IMAGE      = 3
    ARCHIVE    = 4
    EXECUTABLE = 5
    DATABASE   = 6
    AUDIO      = 7
    VIDEO      = 8
    FONT       = 9


class FileSubtype(IntEnum):
    GENERIC       = 0

    TXT_MARKDOWN  = 1
    TXT_HTML      = 2
    TXT_SVG       = 3
    TXT_PYTHON    = 4
    TXT_C         = 5
    TXT_CPP       = 6
    TXT_JS        = 7
    TXT_TS        = 8
    TXT_SHELL     = 9
    TXT_JSON      = 10
    TXT_YAML      = 11
    TXT_TOML      = 12
    TXT_XML       = 13
    TXT_CSV       = 14
    TXT_PERL      = 38
    TXT_INI       = 45
    TXT_JAVA      = 46
    TXT_PO        = 50
    TXT_PEM       = 59
    TXT_SSH_KEY   = 60
    TXT_TROFF     = 62
    TXT_ALGOL     = 63
    TXT_RUBY      = 67
    TXT_TEX       = 68
    TXT_ASM       = 69
    TXT_FORTRAN    = 71
    TXT_OBJECTIVE_C = 72
    TXT_MAKEFILE   = 74

    DOC_PDF       = 15
    DOC_EPUB      = 61
    DOC_CHM       = 66
    DOC_XLSX       = 76

    IMG_PNG       = 16
    IMG_JPEG      = 17
    IMG_GIF       = 18
    IMG_BMP       = 19
    IMG_WEBP      = 20
    IMG_TIFF      = 21
    IMG_ACO       = 47
    IMG_ICO       = 52
    IMG_ANI       = 55
    IMG_PCX       = 58

    AR_ZIP        = 22
    AR_TAR        = 23
    AR_GZIP       = 24
    AR_BZIP2      = 25
    AR_XZ         = 26
    AR_7Z         = 27
    AR_RAR        = 28
    AR_ZLIB       = 39
    AR_COMPRESS   = 48

    EXE_ELF       = 29
    EXE_PE        = 30
    EXE_MACHO     = 31
    EXE_OBJ       = 42
    EXE_COFF      = 43

    DB_SQLITE     = 32
    DB_PCAP       = 33
    DB_WASM       = 34
    DB_JAVA_CLASS = 35
    DB_JAR        = 36
    DB_PYC        = 37
    DB_GIT        = 40
    DB_OLE        = 41
    DB_CDF        = 44
    DB_SIMH       = 49
    DB_MO         = 51
    DB_MAT        = 56
    DB_NETCDF     = 57
    DB_MBOX       = 64
    DB_NPY        = 65
    DB_FITS       = 70
    DB_MS_PDB      = 73

    FONT_EOT      = 53
    FONT_OTF      = 54
    FONT_TEX_TFM   = 75

    # Add any others if missed


class Kind(NamedTuple):
    category: FileCategory
    subtype: FileSubtype


def detect_file(path: PathLike) -> Kind:
    """
    Detect file kind by path. Returns (category, subtype).
    """
    p = os.fsencode(os.fspath(path))
    res = _lib.fd_detect_file_kind(p)

    try:
        cat_e = FileCategory(int(res.category))
    except ValueError:
        cat_e = FileCategory.UNKNOWN

    try:
        sub_e = FileSubtype(int(res.subtype))
    except ValueError:
        sub_e = FileSubtype.GENERIC

    return Kind(cat_e, sub_e)


def detect_buffer(buf: bytes | bytearray | memoryview) -> Kind:
    """
    Detect buffer kind. Returns (category, subtype).
    """
    mv = memoryview(buf)

    # Ensure 1-D C-contiguous
    if mv.ndim != 1 or not mv.c_contiguous:
        mv = memoryview(mv.tobytes())  # copy to contiguous

    n = mv.nbytes
    if mv.readonly:
        baff = (ctypes.c_char * n).from_buffer_copy(mv) # copy
    else:
        baff = (ctypes.c_char * n).from_buffer(mv) # zero-copy

    ptr = ctypes.c_void_p(ctypes.addressof(baff))
    res = _lib.fd_detect_buffer_kind(ptr, c_size_t(n))

    try:
        cat_e = FileCategory(int(res.category))
    except ValueError:
        cat_e = FileCategory.UNKNOWN

    try:
        sub_e = FileSubtype(int(res.subtype))
    except ValueError:
        sub_e = FileSubtype.GENERIC

    return Kind(cat_e, sub_e)


def is_text(kind: Kind):
    return kind.category == FileCategory.TEXT
