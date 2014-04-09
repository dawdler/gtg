# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Getting Things GNOME! - a personal organizer for the GNOME desktop
# Copyright (c) 2008-2013 - Lionel Dricot & Bertrand Rousseau
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

""" General class for representing time and periodic time intervals in GTG """

import datetime
import dbus

from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop


class Timer(GObject.GObject):
    __signal_type__ = (GObject.SignalFlags.RUN_FIRST,
                       None,
                       ())

    __gsignals__ = {'refresh': __signal_type__,}

    def __init__(self, config, vmanager):
        self.vmanager = vmanager
        self.config = config
        GObject.GObject.__init__(self)
        bus = dbus.SystemBus()
        bus.add_signal_receiver(self.emit_refresh,
                                'Resuming',
                                'org.freedesktop.UPower',
                                'org.freedesktop.UPower')
        self.__init__signals()
        
    def __init__signals(self):
        """initializes the signals to refresh the workview when GTG starts"""
        refresh_hour = self.config.get('hour')
        refresh_min = self.config.get('min')
        now = datetime.datetime.now()
        refresh_time = datetime.datetime(now.year, now.month, now.day,
                                         0, 0, 0)
        secs_to_refresh = self.seconds_before(refresh_time)
        self.add_gobject_timeout(secs_to_refresh, self.emit_refresh)
        self.add_gobject_timeout(86400, self.day_starts)
        refresh_time = datetime.datetime(now.year, now.month, now.day,
                                         int(refresh_hour),
                                         int(refresh_min), 0)
        secs_to_refresh = self.seconds_before(refresh_time)
        self.add_gobject_timeout(secs_to_refresh, self.emit_refresh)
                
    def seconds_before(self, time):
        """Returns number of seconds remaining before next refresh"""
        now = datetime.datetime.now()
        secs_to_refresh = (time-now)
        if secs_to_refresh.total_seconds() < 0:
            secs_to_refresh += datetime.timedelta(days=1)
        return secs_to_refresh.total_seconds()

    def interval_to_time(self, interval):
        """Convert user given periodic interval to time"""
        now = datetime.datetime.now()
        now += datetime.timedelta(hours=int(interval))
        return now

    def add_gobject_timeout(self, time, callback):
        return GObject.timeout_add_seconds(time, callback)

    def emit_refresh(self):
        """Emit Signal for workview to refresh"""
        self.emit("refresh")
        return False
 
    def day_starts(self):
        """Emit signal when day starts""" 
        self.emit("refresh")
        return True

    def time_changed(self):
        self.browser = self.vmanager.get_browser()
        refresh_hour = self.config.get('hour')
        refresh_min = self.config.get('min')
        now = datetime.datetime.now()
        refresh_time = datetime.datetime(now.year, now.month, now.day,
                                         int(refresh_hour),
                                         int(refresh_min), 0)
        secs_to_refresh = self.seconds_before(refresh_time)
        print(secs_to_refresh)
        self.add_gobject_timeout(secs_to_refresh,
                                 self.browser.refresh_workview)

    def set_configuration(self, refresh_hour, refresh_min):
        now = datetime.datetime.now()
        try: 
            d = datetime.datetime(now.year, now.month, now.day,
                                  int(refresh_hour),
                                  int(refresh_min), 00)
            self.config.set('hour', refresh_hour)
            self.config.set('min', refresh_min)
        except (ValueError, TypeError):
            self.config.set('hour', "00")
            self.config.set('min', "00")
            raise ValueError
