#!/usr/bin/python
# Ubuntu Tweak - PyGTK based desktop configure tool
#
# Copyright (C) 2007-2008 TualatriX <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import pygtk
pygtk.require("2.0")
import gtk
import os
import gobject
import gconf
import gettext

try:
    from common.package import PackageWorker, AptCheckButton, update_apt_cache
    DISABLE = False
except ImportError:
    DISABLE = True

from common.factory import Factory
from common.widgets import ListPack, TablePack, TweakPage
from common.widgets.dialogs import InfoDialog
from common.utils import set_label_for_stock_button

(
    COLUMN_ICON,
    COLUMN_TITLE,
) = range(2)

class EmblemsView(gtk.IconView):
    def __init__(self):
        gtk.IconView.__init__()

        model = self.__create_model()
        self.set_model(model)

    def __create_model(self):
        model = gtk.ListStore(
                gtk.gdk.Pixbuf,
                gobject.TYPE_STRING)

        return model

    def __add_colums(self):
        renderer = gtk.CellRendererPixbuf()
        self.pack_start(renderer, False)
        self.set_attributes(renderer, pixbuf = COLUMN_ICON)

        renderer = gtk.CellRendererText()
        self.pack_start(renderer, True)
        self.set_attributes(renderer, text = COLUMN_TITLE)

    def update_model(self):
        pass

class Nautilus(TweakPage):
    """Nautilus Settings"""
    def __init__(self):
        TweakPage.__init__(self)

        button = Factory.create("gconfcheckbutton", _("Show advanced permissions on Permissions tab of File Property"), "show_advanced_permissions")

        box = ListPack(_("File Browser"), (button, )) 
        self.pack_start(box, False, False, 0)

        box = ListPack(_("CD Burner"), (
            Factory.create("gconfcheckbutton", _("Enable BurnProof technology"), "burnproof"),
            Factory.create("gconfcheckbutton", _("Enable OverBurn"), "overburn"),
        ))
        self.pack_start(box, False, False, 0)


        boxes = []
        hbox1 = gtk.HBox(False, 5)
        label = gtk.Label(_('Default thumbnail icon size'))
        hbox1.pack_start(label, False, False, 0)
        boxes.append(hbox1)

        button = Factory.create('gconfspinbutton', 
                            'thumbnail_size',
                            16, 512, 16)
        hbox1.pack_end(button, False, False, 0)

        button = Factory.create('gconfspinbutton', 
                            'maximum_size',
                            -1, 512, 1)
        if button:
            hbox2 = gtk.HBox(False, 5)
            label = gtk.Label(_('Maximum size of the thumbnail cache (MB)'))

            hbox2.pack_start(label, False, False, 0)
            hbox2.pack_end(button, False, False, 0)
            boxes.append(hbox2)

        if button:
            button = Factory.create('gconfspinbutton', 
                                'maximum_age',
                                -1, 180, 1)

            hbox3 = gtk.HBox(False, 5)
            label = gtk.Label(_('Maximum age for the thumbnail in the cache (Day)'))
            hbox3.pack_start(label, False, False, 0)
            hbox3.pack_end(button, False, False, 0)
            boxes.append(hbox3)

        hbox4 = gtk.HBox(False, 5)
        button = gtk.Button(stock = gtk.STOCK_CLEAR)
        set_label_for_stock_button(button, _('Clean up the cache'))
        hbox4.pack_end(button, False, False, 0)
        boxes.append(hbox4)

        box = ListPack(_('Thumbnails Settings'), boxes)
        self.pack_start(box, False, False, 0)


        if not DISABLE:
            update_apt_cache(True)
            self.packageWorker = PackageWorker()

            self.nautilus_terminal = AptCheckButton(_('Nautilus with Open Terminal'), 'nautilus-open-terminal')
            self.nautilus_terminal.connect('toggled', self.colleague_changed)
            self.nautilus_root = AptCheckButton(_('Nautilus with Root Privileges'), 'nautilus-gksu')
            self.nautilus_root.connect('toggled', self.colleague_changed)
            self.nautilus_wallpaper = AptCheckButton(_('Nautilus with Wallpaper'), 'nautilus-wallpaper')
            self.nautilus_wallpaper.connect('toggled', self.colleague_changed)
            box = ListPack(_("Nautilus Extensions"), (
                self.nautilus_terminal,
                self.nautilus_root,
                self.nautilus_wallpaper,
            ))

            self.button = gtk.Button(stock = gtk.STOCK_APPLY)
            self.button.connect("clicked", self.on_apply_clicked, box)
            self.button.set_sensitive(False)
            hbox = gtk.HBox(False, 0)
            hbox.pack_end(self.button, False, False, 0)

            box.vbox.pack_start(hbox, False, False, 0)

            self.pack_start(box, False, False, 0)

    def spinbutton_value_changed_cb(self, widget, data = None):
        client = gconf.client_get_default()
        client.set_int("/apps/nautilus/icon_view/thumbnail_size", int(widget.get_value()))

    def on_apply_clicked(self, widget, box):
        to_add = []
        to_rm = []

        for widget in box.items:
            if widget.get_active():
                to_add.append(widget.pkgname)
            else:
                to_rm.append(widget.pkgname)

        state = self.packageWorker.perform_action(widget.get_toplevel(), to_add, to_rm)

        if state == 0:
            self.button.set_sensitive(False)
            InfoDialog(_("Update Successfully!")).launch()
        else:
            InfoDialog(_("Update Failed!")).launch()

        update_apt_cache()

    def colleague_changed(self, widget):
        if self.nautilus_terminal.get_state() != self.nautilus_terminal.get_active() or\
                self.nautilus_root.get_state() != self.nautilus_root.get_active() or\
                self.nautilus_wallpaper.get_state() != self.nautilus_wallpaper.get_active():
                    self.button.set_sensitive(True)
        else:
            self.button.set_sensitive(False)

if __name__ == "__main__":
    from utility import Test
    Test(Nautilus)
