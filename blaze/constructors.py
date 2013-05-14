from __future__ import absolute_import

# This are the constructors for the blaze array objects.  Having them
# as external functions allows to more flexibility and helps keeping
# the blaze array object compact, just showing the interface of the
# array itself.
#
# The blaze array __init__ method should be considered private and for
# advanced users only. It will provide the tools supporting the rest
# of the constructors, and will use low-level parameters, like
# ByteProviders, that an end user may not even need to know about.

from .array import Array
from .datadescriptor import (IDataDescriptor,
                NumPyDataDescriptor, BLZDataDescriptor)
from .datashape import dshape as _dshape_builder, to_numpy, to_dtype

import numpy as np
import inspect
from . import blz

try:
    basestring
    # if basestring exists... use it (fails on python 3)
    def _is_str(s):
        return isinstance(s, basestring)
except NameError:
    # python 3 version
    def _is_str(s):
        return isinstance(s, str)

# note that this is rather naive. In fact, a proper way to implement
# the array from a numpy is creating a ByteProvider based on "obj"
# and infer the indexer from the apropriate information in the numpy
# array.
def array(obj, dshape=None, caps={'efficient-write': True}):
    """Create an in-memory Blaze array.

    Parameters
    ----------
    obj : array_like
        Initial contents for the array.

    dshape : datashape
        The datashape for the resulting array. By default the
        datashape will be inferred from data. If an explicit dshape is
        provided, the input data will be coerced into the provided
        dshape.

        caps : capabilities dictionary
        A dictionary containing the desired capabilities of the array.

    Returns
    -------
    out : a concrete, in-memory blaze array.

    Bugs
    ----
    Right now the explicit dshape is ignored. This needs to be
    corrected. When the data cannot be coerced to an explicit dshape
    an exception should be raised.

    """
    dshape = dshape if not _is_str(dshape) else _dshape_builder(dshape)

    if isinstance(obj, IDataDescriptor):
        # TODO: Validate the 'caps', convert to another kind
        #       of data descriptor if necessary
        dd = obj
    elif isinstance(obj, np.ndarray):
        dd = NumPyDataDescriptor(obj)
    elif isinstance(obj, blz.barray):
        dd = BLZDataDescriptor(obj)
    elif inspect.isgenerator(obj):
        return _fromiter(obj, dshape, caps)
    elif 'efficient-write' in caps:
        dt = None if dshape is None else to_dtype(dshape)
        # NumPy provides efficient writes
        dd = NumPyDataDescriptor(np.array(obj, dtype=dt))
    elif 'compress' in caps:
        dt = None if dshape is None else to_dtype(dshape)
        # BLZ provides compression
        dd = BLZDataDescriptor(blz.barray(obj, dtype=dt))
    else:
        raise TypeError(('Failed to construct blaze array from '
                        'object of type %r') % type(obj))
    return Array(dd)


# XXX This should probably be made public because the `count` param
# for BLZ is very important for getting good performance.
def _fromiter(gen, dshape, caps):
    """Create an array out of an iterator."""
    dshape = dshape if not _is_str(dshape) else _dshape_builder(dshape)

    if 'efficient-write' in caps:
        dt = None if dshape is None else to_dtype(dshape)
        # NumPy provides efficient writes
        dd = NumPyDataDescriptor(np.fromiter(gen, dtype=dt))
    elif 'compress' in caps:
        dt = None if dshape is None else to_dtype(dshape)
        # BLZ provides compression
        dd = BLZDataDescriptor(blz.fromiter(gen, dtype=dt, count=-1))
    return Array(dd)


def zeros(dshape, caps={'efficient-write': True}):
    """Create an array and fill it with zeros.

    Parameters
    ----------
    dshape : datashape
        The datashape for the resulting array.

    caps : capabilities dictionary
        A dictionary containing the desired capabilities of the array.

    Returns
    -------
    out : a concrete, in-memory blaze array.

    """
    dshape = dshape if not _is_str(dshape) else _dshape_builder(dshape)
    if 'efficient-write' in caps:
        shape, dt = (None,None) if dshape is None else to_numpy(dshape)
        # NumPy provides efficient writes
        dd = NumPyDataDescriptor(np.zeros(shape, dtype=dt))
    elif 'compress' in caps:
        shape, dt = (None,None) if dshape is None else to_numpy(dshape)
        # BLZ provides compression
        dd = BLZDataDescriptor(blz.zeros(shape, dtype=dt))
    return Array(dd)


def ones(dshape, caps={'efficient-write': True}):
    """Create an array and fill it with ones.

    Parameters
    ----------
    dshape : datashape
        The datashape for the resulting array.

    caps : capabilities dictionary
        A dictionary containing the desired capabilities of the array.

    Returns
    -------
    out: a concrete blaze array

    """
    dshape = dshape if not _is_str(dshape) else _dshape_builder(dshape)

    if 'efficient-write' in caps:
        shape, dt = (None,None) if dshape is None else to_numpy(dshape)
        # NumPy provides efficient writes
        dd = NumPyDataDescriptor(np.ones(shape, dtype=dt))
    elif 'compress' in caps:
        shape, dt = (None,None) if dshape is None else to_numpy(dshape)
        # BLZ provides compression
        dd = BLZDataDescriptor(blz.ones(shape, dtype=dt))
    return Array(dd)


# for a temptative open function:
def open(uri):
    raise NotImplementedError
