#
#       Copyright (C) 2014
#       Sean Poyser (seanpoyser@gmail.com)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#


import xbmcaddon
import xbmc
import xbmcgui
import os
import stat
import shutil

import download
import extract

ADDONID   = 'plugin.program.vpnicity'
ADDON     =  xbmcaddon.Addon(ADDONID)
HOME      =  ADDON.getAddonInfo('path')
PROFILE   =  xbmc.translatePath(ADDON.getAddonInfo('profile'))
ICON      =  os.path.join(HOME, 'icon.png')
ICON      =  xbmc.translatePath(ICON)
RESOURCES =  os.path.join(HOME, 'resources')
TITLE     =  ADDON.getAddonInfo('name')
VERSION   =  ADDON.getAddonInfo('version')
KEYMAP    = 'vpnicity_menu.xml'
GETTEXT   =  ADDON.getLocalizedString
LOGINURL  = 'https://www.vpnicity.com/wp-login.php'
DEBUG     =  False


def GetXBMCVersion():
    version = xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')
    version = version.split('.')
    return int(version[0]), int(version[1]) #major, minor eg, 13.9.902


MAJOR, MINOR = GetXBMCVersion()
FRODO        = (MAJOR == 12) and (MINOR < 9)
GOTHAM       = (MAJOR == 13) or (MAJOR == 12 and MINOR == 9)
HELIX        = (MAJOR == 14) or (MAJOR == 13 and MINOR == 9)



def log(text):
    try:
        output = '%s V%s : %s' % (TITLE, VERSION, str(text))
        
        if DEBUG:
            xbmc.log(output)
        else:
            xbmc.log(output, xbmc.LOGDEBUG)
    except:
        pass



def notify(message, length=10000):
    cmd = 'XBMC.notification(%s,%s,%d,%s)' % (TITLE, message, length, ICON)
    xbmc.executebuiltin(cmd)


def checkAutoStart():
    try:
        import vpn

        abrv   = ADDON.getSetting('ABRV')
        label  = ADDON.getSetting('LABEL')
        server = ADDON.getSetting('SERVER')

        if len(abrv) == 0:
            return

        if len(label) == 0:
            best   = vpn.GetBest(abrv)
            label  = vpn.COUNTRIES[abrv.upper()] #best[0]
            server = best[3]

        notify('Starting %s VPNicity' % label, 15000)
        return vpn.VPN(label, abrv, server)

    except Exception, e:
        log('Error in autoStart %s' % str(e))



def showBusy():
    busy = None
    try:
        import xbmcgui
        busy = xbmcgui.WindowXMLDialog('DialogBusy.xml', '')
        busy.show()

        try:    busy.getControl(10).setVisible(False)
        except: pass
    except:
        busy = None

    return busy


def triggerChangelog():
    #call showChangeLog like this to workaround bug in openElec
    script = os.path.join(HOME, 'showChangelog.py')
    cmd    = 'AlarmClock(%s,RunScript(%s),%d,True)' % ('changelog', script, 0)
    xbmc.executebuiltin(cmd)


def showVideo():
    
    import yt    
    yt.PlayVideo('-DpU4yOJO_I', forcePlayer=True)
    xbmc.sleep(500)
    while xbmc.Player().isPlaying():
        xbmc.sleep(500)


def checkVersion():
    prev = GetSetting('VERSION')
    curr = VERSION
    log('******** VPNicity Launched ********')

    if prev == curr:
        return

    SetSetting('VERSION', curr)

    if GetSetting('VIDEO').lower() != 'true':
        showVideo()

    d = xbmcgui.Dialog()
    d.ok(TITLE + ' - ' + VERSION, 'Changed Dialog boxes to Notifications.')
    triggerChangelog()
    


def dialogOK(line1, line2='', line3=''):
    d = xbmcgui.Dialog()
    d.ok(TITLE, line1, line2 , line3)


def yesno(line1, line2 = '', line3 = '', no = 'No', yes = 'Yes'):
    dlg = xbmcgui.Dialog()
    return dlg.yesno(TITLE, line1, line2, line3, no, yes) == 1


def progress(line1, line2 = '', line3 = '', hide = True):
    dp = xbmcgui.DialogProgress()
    dp.create(TITLE, line1, line2, line3)
    if hide:
        hideCancelButton()
    return dp


def hideCancelButton():
    tries = 10
    while tries > 0:
        tries -=1

        try:
            xbmc.sleep(250)
            WINDOW_PROGRESS = xbmcgui.Window(10101)
            CANCEL_BUTTON   = WINDOW_PROGRESS.getControl(10)
            CANCEL_BUTTON.setVisible(False)
            return
        except:
            pass


def verifyPluginsFile():
    file = os.path.join(PROFILE, 'plugins', 'plugins.ini')

    if os.path.exists(file):
        return file

    src = os.path.join(HOME, 'resources', 'plugins', 'plugins.ini')

    try:    os.mkdir(os.path.join(PROFILE))
    except: pass

    try:    os.mkdir(os.path.join(PROFILE, 'plugins'))
    except: pass

    import shutil
    shutil.copyfile(src, file)
    return file


def getSudo():
    if GetSetting('OS') == 'Windows':
        return ''

    if GetSetting('OS') == 'OpenELEC':
        return ''

    sudo = GetSetting('SUDO') == 'true'    

    if not sudo:
        return ''

    sudopwd = GetSetting('SUDOPASS')

    if sudopwd:
        return 'echo \'%s\' | sudo -S ' % sudopwd

    return 'sudo '


def showText(heading, text):
    id = 10147

    xbmc.executebuiltin('ActivateWindow(%d)' % id)
    xbmc.sleep(100)

    win = xbmcgui.Window(id)

    retry = 50
    while (retry > 0):
        try:
            xbmc.sleep(10)
            retry -= 1
            win.getControl(1).setLabel(heading)
            win.getControl(5).setText(text)
            return
        except:
            pass


def showChangelog(addonID=None):
    try:
        if addonID:
            ADDON = xbmcaddon.Addon(addonID)
        else: 
            ADDON = xbmcaddon.Addon(ADDONID)

        f     = open(ADDON.getAddonInfo('changelog'))
        text  = f.read()
        title = '%s - %s' % (xbmc.getLocalizedString(24054), ADDON.getAddonInfo('name'))

        showText(title, text)

    except:
        pass


def GetSetting(param):
    return ADDON.getSetting(param)


def SetSetting(param, value):
    ADDON.setSetting(param, value)


def platform():
    if xbmc.getCondVisibility('system.platform.android'):
        return 'android'
    elif xbmc.getCondVisibility('system.platform.linux'):
        return 'linux'
    elif xbmc.getCondVisibility('system.platform.windows'):
        return 'windows'
    elif xbmc.getCondVisibility('system.platform.osx'):
        return 'osx'
    elif xbmc.getCondVisibility('system.platform.atv2'):
        return 'atv2'
    elif xbmc.getCondVisibility('system.platform.ios'):
        return 'ios'