# -*- coding: utf-8 -*-

# Cotinga helps maths teachers creating worksheets
# and managing pupils' progression.
# Copyright 2018-2022 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Cotinga.

# Cotinga is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Cotinga is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Cotinga; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gi
try:
    gi.require_version('Gtk', '3.0')
except ValueError:
    raise
else:
    from gi.repository import Gtk


__all__ = ['ComboDialog']


# LATER: factorize code with PresetsComboDialog (only the source changes; take
# care of on_choice_changed too, and keep this version for the message)

class ComboDialog(Gtk.Dialog):

    def __init__(self, title, message, source, parentw):
        Gtk.Dialog.__init__(self, title, parentw, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_modal(True)

        self.set_size_request(450, 100)
        self.box = self.get_content_area()
        self.main_grid = Gtk.Grid()
        self.main_grid.set_border_width(5)
        self.main_grid.set_hexpand(True)
        # As Gtk.Box will get deprecated, one can expect that
        # get_content_area() will later return something else than a Box.
        # Note that then, box can be replaced by self.main_grid

        central_grid = Gtk.Grid()
        central_grid.set_hexpand(False)

        if message not in [None, '']:
            message_label = Gtk.Label(message)
        else:
            message_label = Gtk.Grid()
        central_grid.attach(message_label, 0, 0, 1, 1)

        store = Gtk.ListStore(str)
        for entry in source:
            store.append([entry])

        self.source = source

        combo = Gtk.ComboBox.new_with_model(store)

        renderer = Gtk.CellRendererText()
        combo.pack_start(renderer, False)
        combo.add_attribute(renderer, 'text', 0)

        combo.set_active(0)
        combo.connect('changed', self.on_choice_changed)

        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        self.choice = model[tree_iter][0]

        central_grid.attach_next_to(combo, message_label,
                                    Gtk.PositionType.BOTTOM, 1, 1)
        void1 = Gtk.Grid()
        void1.set_hexpand(True)
        void2 = Gtk.Grid()
        void2.set_hexpand(True)
        self.main_grid.attach(void1, 0, 0, 1, 1)
        self.main_grid.attach_next_to(central_grid, void1,
                                      Gtk.PositionType.RIGHT, 1, 1)
        self.main_grid.attach_next_to(void2, central_grid,
                                      Gtk.PositionType.RIGHT, 1, 1)
        self.box.add(self.main_grid)
        self.show_all()

    def on_choice_changed(self, combo):
        # TODO: simplify such callback functions: couldn't tree_iter be
        # returned by a property?
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            self.choice = model[tree_iter][0]
        else:
            entry = combo.get_child()
            print('Entered: %s' % entry.get_text())
