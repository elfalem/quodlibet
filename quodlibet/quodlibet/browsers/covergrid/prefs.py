# -*- coding: utf-8 -*-
# Copyright 2004-2007 Joe Wreschnig, Michael Urman, Iñigo Serna
#           2009-2010 Steven Robertson
#      2012,2013,2016 Nick Boultbee
#           2009-2013 Christoph Reiter
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

from gi.repository import Gtk

from quodlibet import config
from quodlibet import qltk
from quodlibet import util
from quodlibet import _
from quodlibet.browsers._base import FakeDisplayItem, EditDisplayPatternMixin
from quodlibet.formats import PEOPLE
from quodlibet.qltk import Button, Icons
from quodlibet.qltk.ccb import ConfigCheckButton
from quodlibet.util import format_rating
from quodlibet.util.i18n import numeric_phrase

PEOPLE
_SOME_PEOPLE = "\n".join([util.tag("artist"), util.tag("performer"),
                         util.tag("composer"), util.tag("arranger"), ])

_EMPTY = _("Songs not in an album")
DEFAULT_PATTERN_TEXT = """[b]<album|<album>|%s>[/b]<date| (<date>)>
[small]<~discs|<~discs> - ><~tracks> - <~long-length>[/small]
<~people>""" % _EMPTY


class Preferences(qltk.UniqueWindow, EditDisplayPatternMixin):
    _DEFAULT_PATTERN = DEFAULT_PATTERN_TEXT

    _PREVIEW_ITEM = FakeDisplayItem({
        "date": "2010-10-31",
        "~length": util.format_time_display(6319),
        "~long-length": util.format_time_long(6319),
        "~tracks": numeric_phrase("%d track", "%d tracks", 5),
        "~discs": numeric_phrase("%d disc", "%d discs", 2),
        "~#rating": 0.75,
        "album": _("An Example Album"),
        "~people": _SOME_PEOPLE + "..."})

    def __init__(self, browser):
        if self.is_not_unique():
            return
        super(Preferences, self).__init__()
        self.set_border_width(12)
        self.set_title(_("Cover Grid Preferences") + " - Quod Libet")
        self.set_default_size(420, 380)
        self.set_transient_for(qltk.get_top_parent(browser))
        # Do this config-driven setup at instance-time
        self._PREVIEW_ITEM["~rating"] = format_rating(0.75)

        box = Gtk.VBox(spacing=6)
        vbox = Gtk.VBox(spacing=6)
        cb = ConfigCheckButton(
            _("Show album _text"), "browsers", "album_text")
        cb.set_active(config.getboolean("browsers", "album_text"))
        cb.connect('toggled',
                   lambda s: browser.toggle_text())
        vbox.pack_start(cb, False, True, 0)

        cb2 = ConfigCheckButton(
            _("Show \"All Albums\" Item"), "browsers", "covergrid_all")
        cb2.set_active(config.getboolean("browsers", "covergrid_all", False))
        cb2.connect('toggled',
                   lambda s: browser.view.get_model().refilter())
        vbox.pack_start(cb2, False, True, 0)

        cb3 = ConfigCheckButton(
            _("Vertical Split"), "browsers", "covergrid_vertical")
        cb3.set_active(config.getboolean("browsers",
            "covergrid_vertical", True))
        cb3.connect('toggled',
                   lambda s: browser.toggle_vert())
        vbox.pack_start(cb3, False, True, 0)

        def mag_changed(mag):
            config.set("browsers", "covergrid_magnification", mag.get_value())

        # Only redraws the covers when the user releases the slider
        def mag_button_release(*_):
            browser.update_mag()

        mag_scale = Gtk.HScale(
            adjustment=Gtk.Adjustment.new(config.getfloat("browsers",
                "covergrid_magnification", 3), 0., 10., .5, 5, 0))
        mag_scale.set_tooltip_text(_("Cover Magnification"))
        l = Gtk.Label(label=_("Cover Magnification"))
        mag_scale.set_value_pos(Gtk.PositionType.RIGHT)
        mag_scale.connect('value-changed', mag_changed)
        mag_scale.connect('button-release-event', mag_button_release)

        vbox.pack_start(l, False, True, 0)
        vbox.pack_start(mag_scale, False, True, 0)

        f = qltk.Frame(_("Options"), child=vbox)
        box.pack_start(f, False, True, 12)

        display_frame = self.edit_display_pane(browser, _("Album Display"))
        box.pack_start(display_frame, True, True, 0)

        main_box = Gtk.VBox(spacing=12)
        close = Button(_("_Close"), Icons.WINDOW_CLOSE)
        close.connect('clicked', lambda *x: self.destroy())
        b = Gtk.HButtonBox()
        b.set_layout(Gtk.ButtonBoxStyle.END)
        b.pack_start(close, True, True, 0)

        main_box.pack_start(box, True, True, 0)
        self.use_header_bar()

        if not self.has_close_button():
            main_box.pack_start(b, False, True, 0)
        self.add(main_box)

        close.grab_focus()
        self.show_all()
