import datetime as dt
from builtins import range

from ..Utilities import shadowingfunctions as shadow
from ..Utilities.SEBESOLWEIGCommonFiles import shadowingfunction_wallheight_13
from ..Utilities import shadowingfunction_transparency as shtr
from ..Utilities.misc import *
from ..Utilities.SEBESOLWEIGCommonFiles import sun_position as sp


class _PBShim(object):
    class _PB(object):
        def setRange(self, *a):
            pass

        def setValue(self, *a):
            pass

    def __init__(self):
        self.progressBar = _PBShim._PB()


def dailyshading(dsm, scale, lon, lat, sizex, sizey, tv, UTC, timeInterval, onetime,
                 feedback, folder, gdal_data, dst, wallshadow, wheight, waspect,
                 usetree, tree_top, tree_bottom, tree_psi,
                 useblock, block_top, block_bottom, block_psi):

    year = tv[0]
    month = tv[1]
    day = tv[2]

    altmed = np.median(dsm)
    location = {'longitude': lon, 'latitude': lat, 'altitude': altmed}

    layers = []
    if usetree == 1:
        tree_psi = np.where(tree_top > 0., tree_psi, 1.0)
        layers.append({'top': tree_top, 'bottom': tree_bottom, 'psi': tree_psi})
    if useblock == 1:
        block_psi = np.where(block_top > 0., block_psi, 1.0)
        layers.append({'top': block_top, 'bottom': block_bottom, 'psi': block_psi})

    usefloating = len(layers) > 0

    amaxvalue = dsm.max() - dsm.min()
    for L in layers:
        reach = np.max(np.maximum(L['top'] - dsm, 0.))
        amaxvalue = np.maximum(amaxvalue, reach)

    pbshim = _PBShim()

    shtot = np.zeros((sizex, sizey))

    if onetime == 1:
        itera = 1
    else:
        itera = int(np.round(1440 / timeInterval))

    alt = np.zeros(itera)
    azi = np.zeros(itera)
    hour = int(0)
    index = 0
    time = dict()
    time['UTC'] = UTC

    if wallshadow == 1:
        walls = wheight
        dirwalls = waspect
    else:
        walls = np.zeros((sizex, sizey))
        dirwalls = np.zeros((sizex, sizey))

    for i in range(0, itera):
        if feedback is not None:
            if feedback.isCanceled():
                break
            feedback.setProgress(int(100 * i / itera))

        if onetime == 0:
            minu = int(timeInterval * i)
            if minu >= 60:
                hour = int(np.floor(minu / 60))
                minu = int(minu - hour * 60)
        else:
            minu = tv[4]
            hour = tv[3]

        doy = day_of_year(year, month, day)

        ut_time = doy - 1. + ((hour - dst) / 24.0) + (minu / (60. * 24.0)) + (0. / (60. * 60. * 24.0))

        if ut_time < 0:
            year = year - 1
            month = 12
            day = 31
            doy = day_of_year(year, month, day)
            ut_time = ut_time + doy - 1

        HHMMSS = dectime_to_timevec(ut_time)

        time['year'] = year
        time['month'] = month
        time['day'] = day
        time['hour'] = HHMMSS[0]
        time['min'] = HHMMSS[1]
        time['sec'] = HHMMSS[2]

        sun = sp.sun_position(time, location)
        alt[i] = 90. - sun['zenith']
        azi[i] = sun['azimuth']

        if time['sec'] == 59:
            time['sec'] = 0
            time['min'] = time['min'] + 1
            if time['min'] == 60:
                time['min'] = 0
                time['hour'] = time['hour'] + 1
                if time['hour'] == 24:
                    time['hour'] = 0

        time_vector = dt.datetime(year, month, day, time['hour'], time['min'], time['sec'])
        timestr = time_vector.strftime("%Y%m%d_%H%M")

        if alt[i] > 0:

            if wallshadow == 1:
                if usefloating:
                    res = shtr.shadowingfunction_wallheight_23_transparency(
                        dsm, layers, azi[i], alt[i], scale, amaxvalue,
                        walls, dirwalls * np.pi / 180., feedback)
                    sh = res['shground']
                    wallsh = res['wallsh']
                    wallshve = res['wallshve']

                    if onetime == 0:
                        saveraster(gdal_data, folder + '/Facadeshadow_fromvegetation_' + timestr + '_LST.tif', wallshve)
                else:
                    sh, wallsh, _, _, _ = shadowingfunction_wallheight_13(
                        dsm, azi[i], alt[i], scale, walls, dirwalls * np.pi / 180.)

                if onetime == 0:
                    saveraster(gdal_data, folder + '/Shadow_ground_' + timestr + '_LST.tif', sh)
                    saveraster(gdal_data, folder + '/Facadeshadow_frombuilding_' + timestr + '_LST.tif', wallsh)

            else:
                if usefloating:
                    res = shtr.shadowingfunction_ground_transparency(
                        dsm, layers, azi[i], alt[i], scale, amaxvalue, feedback)
                    sh = res['shground']
                else:
                    sh = shadow.shadowingfunctionglobalradiation(dsm, azi[i], alt[i], scale, pbshim, 0)

                if onetime == 0:
                    saveraster(gdal_data, folder + '/Shadow_' + timestr + '_LST.tif', sh)

            shtot = shtot + sh
            index += 1

    shfinal = shtot / index

    if wallshadow == 1:
        if onetime == 1:
            saveraster(gdal_data, folder + '/Facadeshadow_frombuilding_' + timestr + '_LST.tif', wallsh)
            if usefloating:
                saveraster(gdal_data, folder + '/Facadeshadow_fromvegetation_' + timestr + '_LST.tif', wallshve)

    if feedback is not None:
        feedback.setProgress(0)

    return {'shfinal': shfinal, 'time_vector': time_vector}


def day_of_year(yy, month, day):
    if (yy % 4) == 0:
        if (yy % 100) == 0:
            if (yy % 400) == 0:
                leapyear = 1
            else:
                leapyear = 0
        else:
            leapyear = 1
    else:
        leapyear = 0

    if leapyear == 1:
        dayspermonth = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        dayspermonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    doy = np.sum(dayspermonth[0:month - 1]) + day
    return doy


def dectime_to_timevec(dectime):
    doy = np.floor(dectime)
    DH = dectime - doy
    HOURS = int(24 * DH)
    DM = 24 * DH - HOURS
    MINS = int(60 * DM)
    DS = 60 * DM - MINS
    SECS = int(60 * DS)
    return (HOURS, MINS, SECS)
