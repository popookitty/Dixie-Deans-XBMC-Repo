#
#      Copyright (C) 2014 Richard Dean
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

import xbmc
import xbmcaddon
import os
import dixie

try:
    import requests2 as requests
except:
    import requests

import cookielib
import urllib
import urllib2
from urllib2 import HTTPError



ADDON      = xbmcaddon.Addon(id = 'script.tvguidedixie')
DIXIEURL   = ADDON.getSetting('dixie.url').upper()
username   = ADDON.getSetting('username')
password   = ADDON.getSetting('password')
baseurl    = dixie.GetLoginUrl()
datapath   = xbmc.translatePath(ADDON.getAddonInfo('profile'))
cookiepath = os.path.join(datapath, 'cookies')
cookiefile = os.path.join(cookiepath, 'on-tapp.lwp')
account    = { 'log' : username, 'pwd' : password, 'wp-submit' : 'Log In' }


urlopen = urllib2.urlopen
Request = urllib2.Request
cj      = cookielib.LWPCookieJar()
payload = urllib.urlencode(account)
opener  = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

if not os.path.exists(cookiepath):
    try:
        os.makedirs(cookiepath)
    except: pass

if os.path.isfile(cookiefile):
    cj.load(cookiefile)


def resetCookie():
    try:
        if os.path.isfile(cookiefile):
            os.remove(cookiefile)
    except: pass


def doLogin():
    try:
        req    = Request(baseurl, payload)
        handle = opener.open(req)
        code   = handle.getcode()

        for index, cookie in enumerate(cj):
            cj.save(cookiefile)
            print cookie
            return code

    except urllib2.HTTPError, error:
        if hasattr(error, 'code'):
            code = error.code
            
            return code


def checkFiles(url):
    url      = dixie.GetDixieUrl(DIXIEURL) + 'update.txt'
    request  = requests.get(url, allow_redirects=False, auth=(username, password))
    response = request.text
    code     = request.status_code
    reason   = request.reason
    
    print '----- Check OnTapp.TV Files -----'
    print '---------- status code ----------'
    print code

    return code


def getFiles(url):
    url      = dixie.GetDixieUrl(DIXIEURL) + 'update.txt'
    request  = requests.get(url, allow_redirects=False, auth=(username, password))
    response = request.text

    return response
