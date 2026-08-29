# -*- coding: utf-8 -*-
import numpy as np

def _shift_indices(dx, dy, sizex, sizey):
    absdx = np.abs(dx)
    absdy = np.abs(dy)
    xc1 = int((dx + absdx) / 2.)
    xc2 = int(sizex + (dx - absdx) / 2.)
    yc1 = int((dy + absdy) / 2.)
    yc2 = int(sizey + (dy - absdy) / 2.)
    xp1 = int(-((dx - absdx) / 2.))
    xp2 = int(sizex - (dx + absdx) / 2.)
    yp1 = int(-((dy - absdy) / 2.))
    yp2 = int(sizey - (dy + absdy) / 2.)
    return xc1, xc2, yc1, yc2, xp1, xp2, yp1, yp2


def _layer_state(layer, sizex, sizey):
    top = layer['top']
    bottom = layer['bottom']
    psi = layer['psi']

    bush = np.where((top > 0.) & (bottom == 0.), top, 0.)
    bushplant = bush > 1.

    vegsh = np.zeros((sizex, sizey))
    vegsh[bushplant] = 1.

    T = np.ones((sizex, sizey))
    T[bushplant] = psi[bushplant]

    return {
        'top': top, 'bottom': bottom, 'psi': psi,
        'vegsh': vegsh, 'T': T,
        'temptop': np.zeros((sizex, sizey)),
        'tempbot': np.zeros((sizex, sizey)),
        'temppsi': np.ones((sizex, sizey)),
        'lasttop': np.zeros((sizex, sizey)),
        'lastbot': np.zeros((sizex, sizey)),
    }


def _step_layer(st, a, xc1, xc2, yc1, yc2, xp1, xp2, yp1, yp2, dz, dzprev):
    st['temptop'][:] = 0.
    st['tempbot'][:] = 0.
    st['temppsi'][:] = 1.
    st['lasttop'][:] = 0.
    st['lastbot'][:] = 0.

    st['temptop'][xp1:xp2, yp1:yp2] = st['top'][xc1:xc2, yc1:yc2] - dz
    st['tempbot'][xp1:xp2, yp1:yp2] = st['bottom'][xc1:xc2, yc1:yc2] - dz
    st['temppsi'][xp1:xp2, yp1:yp2] = st['psi'][xc1:xc2, yc1:yc2]
    st['lasttop'][xp1:xp2, yp1:yp2] = st['top'][xc1:xc2, yc1:yc2] - dzprev
    st['lastbot'][xp1:xp2, yp1:yp2] = st['bottom'][xc1:xc2, yc1:yc2] - dzprev

    fabovea = st['temptop'] > a
    gabovea = st['tempbot'] > a
    lastfabovea = st['lasttop'] > a
    lastgabovea = st['lastbot'] > a

    vegsh2 = (fabovea.astype(float) + gabovea.astype(float)
              + lastfabovea.astype(float) + lastgabovea.astype(float))
    vegsh2[vegsh2 == 4] = 0.
    vegsh2[vegsh2 > 0] = 1.

    newsh = (vegsh2 == 1.) & (st['vegsh'] == 0.)
    st['T'][newsh] = st['temppsi'][newsh]

    st['vegsh'] = np.fmax(st['vegsh'], vegsh2)
    return vegsh2


def shadowingfunction_ground_transparency(a, layers, azimuth, altitude, scale,
                                          amaxvalue, feedback=None):
    degrees = np.pi / 180.
    az = azimuth * degrees
    alt = altitude * degrees

    sizex = a.shape[0]
    sizey = a.shape[1]

    f = np.copy(a)
    temp = np.zeros((sizex, sizey))
    sh = np.zeros((sizex, sizey))

    states = [_layer_state(L, sizex, sizey) for L in layers]

    pibyfour = np.pi / 4.
    three = 3. * pibyfour
    five = 5. * pibyfour
    seven = 7. * pibyfour
    sinaz = np.sin(az)
    cosaz = np.cos(az)
    tanaz = np.tan(az)
    ssin = np.sign(sinaz)
    scos = np.sign(cosaz)
    dssin = np.abs(1. / sinaz)
    dscos = np.abs(1. / cosaz)
    tanaltbyscale = np.tan(alt) / scale

    index = 0
    dx = dy = dz = 0.
    dzprev = 0.

    while (amaxvalue >= dz) and (np.abs(dx) < sizex) and (np.abs(dy) < sizey):
        if feedback is not None and feedback.isCanceled():
            break

        if ((pibyfour <= az) and (az < three)) or ((five <= az) and (az < seven)):
            dy = ssin * index
            dx = -1. * scos * np.abs(np.round(index / tanaz))
            ds = dssin
        else:
            dy = ssin * np.abs(np.round(index * tanaz))
            dx = -1. * scos * index
            ds = dscos

        dz = (ds * index) * tanaltbyscale
        xc1, xc2, yc1, yc2, xp1, xp2, yp1, yp2 = _shift_indices(dx, dy, sizex, sizey)

        temp[:] = 0.
        temp[xp1:xp2, yp1:yp2] = a[xc1:xc2, yc1:yc2] - dz
        f = np.fmax(f, temp)
        sh[:] = 0.
        sh[f > a] = 1.

        for st in states:
            _step_layer(st, a, xc1, xc2, yc1, yc2, xp1, xp2, yp1, yp2, dz, dzprev)

        dzprev = dz
        index += 1.

    sh = 1. - sh

    shground = np.copy(sh)
    Tlist = []
    vegsh_comb = np.zeros((sizex, sizey))
    for st in states:
        Tlist.append(st['T'])
        shground = shground * st['T']
        vegsh_comb = np.fmax(vegsh_comb, st['vegsh'])

    vegsh_comb[vegsh_comb > 0] = 1.
    vegsh_out = 1. - vegsh_comb

    return {'sh': sh, 'shground': shground, 'T': Tlist, 'vegsh': vegsh_out}


def shadowingfunction_20_transparency(a, tree_top, tree_bottom, tree_psi,
                                      block_top, block_bottom, block_psi,
                                      azimuth, altitude, scale, amaxvalue,
                                      feedback=None, usetree=1, useblock=1):
    layers = []
    if usetree:
        layers.append({'top': tree_top, 'bottom': tree_bottom, 'psi': tree_psi})
    if useblock:
        layers.append({'top': block_top, 'bottom': block_bottom, 'psi': block_psi})
    res = shadowingfunction_ground_transparency(a, layers, azimuth, altitude,
                                                scale, amaxvalue, feedback)
    T = res['T']
    res['Ttree'] = T[0] if usetree else np.ones_like(a)
    res['Tblock'] = T[-1] if useblock else np.ones_like(a)
    return res


def shadowingfunction_wallheight_23_transparency(a, layers, azimuth, altitude,
                                                 scale, amaxvalue, walls, aspect,
                                                 feedback=None):
    degrees = np.pi / 180.
    az = azimuth * degrees
    alt = altitude * degrees

    sizex = np.shape(a)[0]
    sizey = np.shape(a)[1]

    f = np.copy(a)
    temp = np.zeros((sizex, sizey))
    sh = np.zeros((sizex, sizey))
    wallbol = (walls > 0).astype(float)

    shvoveg = np.zeros((sizex, sizey))
    for L in layers:
        shvoveg = np.fmax(shvoveg, L['top'])

    states = [_layer_state(L, sizex, sizey) for L in layers]

    pibyfour = np.pi / 4.
    three = 3. * pibyfour
    five = 5. * pibyfour
    seven = 7. * pibyfour
    sinaz = np.sin(az)
    cosaz = np.cos(az)
    tanaz = np.tan(az)
    ssin = np.sign(sinaz)
    scos = np.sign(cosaz)
    dssin = np.abs(1. / sinaz)
    dscos = np.abs(1. / cosaz)
    tanaltbyscale = np.tan(alt) / scale

    index = 0
    dx = dy = dz = 0.
    dzprev = 0.

    while (amaxvalue >= dz) and (np.abs(dx) < sizex) and (np.abs(dy) < sizey):
        if feedback is not None and feedback.isCanceled():
            break

        if ((pibyfour <= az) and (az < three)) or ((five <= az) and (az < seven)):
            dy = ssin * index
            dx = -1. * scos * np.abs(np.round(index / tanaz))
            ds = dssin
        else:
            dy = ssin * np.abs(np.round(index * tanaz))
            dx = -1. * scos * index
            ds = dscos

        dz = (ds * index) * tanaltbyscale
        xc1, xc2, yc1, yc2, xp1, xp2, yp1, yp2 = _shift_indices(dx, dy, sizex, sizey)

        temp[:] = 0.
        temp[xp1:xp2, yp1:yp2] = a[xc1:xc2, yc1:yc2] - dz
        f = np.fmax(f, temp)
        sh[:] = 0.
        sh[f > a] = 1.

        for st in states:
            _step_layer(st, a, xc1, xc2, yc1, yc2, xp1, xp2, yp1, yp2, dz, dzprev)
            shvoveg = np.fmax(shvoveg, st['temptop'])

        dzprev = dz
        index += 1.

    azilow = az - np.pi / 2.
    azihigh = az + np.pi / 2.
    if azilow >= 0 and azihigh < 2 * np.pi:
        facesh = np.logical_or(aspect < azilow, aspect >= azihigh).astype(float) - wallbol + 1
    elif azilow < 0 and azihigh <= 2 * np.pi:
        azilow = azilow + 2 * np.pi
        facesh = np.logical_or(aspect > azilow, aspect <= azihigh) * -1 + 1
    elif azilow > 0 and azihigh >= 2 * np.pi:
        azihigh = azihigh - 2 * np.pi
        facesh = np.logical_or(aspect > azilow, aspect <= azihigh) * -1 + 1

    sh = 1. - sh

    vegsh_comb = np.zeros((sizex, sizey))
    for st in states:
        vegsh_comb = np.fmax(vegsh_comb, st['vegsh'])
    vegsh_comb[vegsh_comb > 0] = 1.
    shvoveg = (shvoveg - a) * vegsh_comb
    vegsh_out = 1. - vegsh_comb

    shvo = f - a
    facesun = np.logical_and(facesh + (walls > 0).astype(float) == 1, walls > 0).astype(float)
    wallsun = np.copy(walls - shvo)
    wallsun[wallsun < 0] = 0
    wallsun[facesh == 1] = 0
    wallsh = np.copy(walls - wallsun)

    wallshve = shvoveg * wallbol
    wallshve = wallshve - wallsh
    wallshve[wallshve < 0] = 0
    idw = np.where(wallshve > walls)
    wallshve[idw] = walls[idw]
    wallsun = wallsun - wallshve
    idw = np.where(wallsun < 0)
    wallshve[idw] = 0
    wallsun[idw] = 0

    shground = np.copy(sh)
    Tlist = []
    for st in states:
        Tlist.append(st['T'])
        shground = shground * st['T']

    return {'sh': sh, 'shground': shground, 'vegsh': vegsh_out, 'T': Tlist,
            'wallsh': wallsh, 'wallsun': wallsun, 'wallshve': wallshve,
            'facesh': facesh, 'facesun': facesun}
