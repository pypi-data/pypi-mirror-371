#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018-2025 Institute of Computer Science of the Czech Academy of
# Sciences, Prague, Czech Republic. Authors: Pavel Krc, Martin Bures, Jaroslav
# Resler.
#
# This file is part of PALM-METEO.
#
# PALM-METEO is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# PALM-METEO is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# PALM-METEO. If not, see <https://www.gnu.org/licenses/>.

"""Functions for vertical interpolation"""

import numpy as np
from .config import cfg, ConfigError
from .utils import ax_

interpolators = {}

def interpolator(name):
    """Decorator for list of interpolators"""

    def saver(fn):
        interpolators[name] = fn
        return fn
    return saver

def lpad(var):
    """Pad variable in first dimension by repeating lowest layer twice"""
    return np.r_[var[0:1], var]

def get_vinterp(ztarget, zsource, linear=True, wind=True):
    """
    Return configured vertical interpolators for given target and source level
    heights. Returns linear interpolator and/or configured wind profile
    interpolator.
    """
    try:
        ipol = interpolators[cfg.vinterp.interpolator]
    except KeyError:
        raise ConfigError('Unknown interpolator', cfg.vinterp, 'interpolator')

    res = []

    if linear:
        res.append(ipol(ztarget, zsource))

    if wind:
        alpha = cfg.vinterp.wind_power_law
        if alpha is False:
            if linear:
                #same as linear, repeat
                res.append(res[0])
            else:
                res.append(ipol(ztarget, zsource))
        else:
            # do not overwrite in-place
            ztarget = ztarget**alpha
            zsource = zsource**alpha
            res.append(ipol(ztarget, zsource))

    return res

@interpolator('prepared')
def get_vinterp_prepared(ztarget, zsource):
    """
    Creates Python-based vertical interpolator with prepared weights.
    Accepts 1D or 3D ztarget and zsource (at least 1 must be 3D).
    Extrapolates below zsource, but not above.
    """

    # Broadcast source and target arrays
    if len(ztarget.shape) == 1:
        nzt = ztarget.shape[0]
        zs = zsource
        nzs, ny, nx = zs.shape
        zt = np.broadcast_to(ztarget[:,ax_,ax_], (nzt, ny, nx))
    elif len(zsource.shape) == 1:
        nzs = zsource.shape[0]
        zt = ztarget
        nzt, ny, nx = zt.shape
        zs = np.broadcast_to(zsource[:,ax_,ax_], (nzs, ny, nx))
    else:
        zs = zsource
        zt = ztarget
        nzs, ny, nx = zsource.shape
        nzt = ztarget.shape[0]
        assert (ny, nx) == ztarget.shape[1:]

    # Find indices of target z-levels within source
    idx1 = np.zeros((nzt, ny, nx), dtype='i4')
    for j in range(ny):
        for i in range(nx):
            idx1[:,j,i] = np.searchsorted(zs[:,j,i], zt[:,j,i], 'left')
    below = (idx1 == 0) # extrapolation below
    idx0 = idx1 - 1
    idx0[below] = 0

    # Find weights for interpolation
    ogz, ogy, ogx = np.ogrid[0:nzt, 0:ny, 0:nx]
    zs0 = zs[idx0,ogy,ogx]
    zsd = zs[idx1,ogy,ogx] - zs0
    zsd[below] = 1.
    w = (zt - zs0) / zsd
    w[below] = 0.

    # Vertical interpolation routine. Argument: 3D variable data
    def vinterp(*variables):
        for var in variables:
            v0 = var[idx0,ogy,ogx]
            yield v0 + w*(var[idx1,ogy,ogx]-v0)

    return vinterp

@interpolator('metpy')
def get_vinterp_metpy(ztarget, zsource):
    """Returns a wrapper for the MetPy interpolator"""
    from metpy.interpolate import interpolate_1d

    # Because we often require levels below the lowest level from zsource, we
    # will always add one layer at negative level with repeated values from the
    # lowest level, therefore we extrapolate.
    zs = np.zeros((zsource.shape[0]+1,) + zsource.shape[1:], dtype=zsource.dtype)
    zs[0,:,:] = -999999. #always below terrain
    zs[1:,:,:] = zsource

    def vinterp(*variables):
        return interpolate_1d(ztarget, zs, *map(lpad, variables),
                              return_list_always=True)
    return vinterp

@interpolator('fortran')
def get_vinterp_fortran(ztarget, zsource):
    """Returns a wrapper for the native Fortran interpolator"""
    from .vinterp_native import zinterp
    linear = zinterp.linear
    dtype_f = 'f%d' % zinterp.wp

    def vinterp(*variables):
        s = variables[0].shape
        ain = np.empty((len(variables), s[0], s[1], s[2]), dtype=dtype_f, order='F')
        for i,v in enumerate(variables):
            ain[i,:,:,:] = v[:,:,:]
        aout, err = linear(ain, zsource, ztarget)
        if err:
            raise ValueError(('Error {4}: requested heights ({0}, {1}) lie outside '
                'provided heights ({2}, {3}).').format(ztarget[0],
                    ztarget[-1], zsource[0].max(), zsource[-1].min(), err))
        return aout
    return vinterp
