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

import re
import json
import shutil
from pathlib import Path
from gettext import translation

from pikepdf import Pdf

from cotinga.core import mathmaker
from cotinga.core.env import ICON_THEME, BELTS_JSON, TITLES_JSON
from cotinga.core.env import DEFAULT_DOCSETUP
from cotinga.core import doc_setup
from cotinga.gui.core.list_manager import ListManagerPanel
from cotinga.gui.dialogs import FolderSelectDialog
from cotinga.gui.dialogs import run_message_dialog
from cotinga.core.env import LOCALEDIR, L10N_DOMAIN


class GeneratePanel(ListManagerPanel):

    def __init__(self, db, status, prefs, recollections, parentw,
                 mini_items_nb=2):
        # This panel is shown only if mathmaker is available
        self.parentw = parentw
        tr = translation(L10N_DOMAIN, LOCALEDIR, [prefs.language]).gettext

        self.recollections = recollections

        years_store = Gtk.ListStore(str)
        available_mmyears = mathmaker.available_years()
        for y in available_mmyears:
            years_store.append([y])

        self.mmyear_combo = Gtk.ComboBox.new_with_model(years_store)
        renderer = Gtk.CellRendererText()
        self.mmyear_combo.pack_start(renderer, False)
        self.mmyear_combo.add_attribute(renderer, 'text', 0)
        if recollections.mm_year in available_mmyears:
            self.mmyear_combo.set_active(
                available_mmyears.index(recollections.mm_year))
        else:
            self.mmyear_combo.set_active(0)
        self.mmyear_combo.connect('changed', self.on_mmyear_changed)

        self.available_levels = []
        self.update_available_levels(prefs)

        ListManagerPanel.__init__(self, db, status, prefs, recollections,
                                  self.available_levels,
                                  tr('Available levels'),
                                  mini_items_nb=mini_items_nb,
                                  setup_buttons_icons=False,
                                  editable=[False], enable_buttons=False,
                                  reorderable=False)

        info_label1 = Gtk.Label(self.tr('Select the levels you wish.'))
        self.attach_next_to(info_label1, self.treeview,
                            Gtk.PositionType.BOTTOM, 1, 1)

        self.rightgrid = Gtk.Grid()

        label1 = Gtk.Label()
        text = self.tr('Destination directory:')
        label1.set_markup(f'<span fgcolor="#595959"><b>{text}</b></span>')
        label1.props.margin_right = 10
        self.rightgrid.attach(label1, 0, 0, 1, 1)

        dest_dir = self.recollections.templates_dest_dir
        self.dest_dir = Gtk.Label()
        # self.dest_dir.props.margin_top = 10
        self.dest_dir.set_text(dest_dir)
        self.rightgrid.attach_next_to(self.dest_dir, label1,
                                      Gtk.PositionType.RIGHT, 1, 1)

        self.choosedir_button = Gtk.ToolButton.new()
        self.choosedir_button.set_vexpand(False)
        self.choosedir_button.props.margin_top = 10
        self.choosedir_button.props.margin_left = 10
        self.choosedir_button.connect('clicked', self.on_choosedir_clicked)
        self.choosedir_button.set_margin_bottom(10)
        self.rightgrid.attach_next_to(self.choosedir_button,
                                      self.dest_dir,
                                      Gtk.PositionType.RIGHT, 1, 1)

        label2 = Gtk.Label()
        text = self.tr('Year:')
        label2.set_markup(f'<span fgcolor="#595959"><b>{text}</b></span>')
        label2.props.margin_right = 10
        self.rightgrid.attach_next_to(label2, label1,
                                      Gtk.PositionType.BOTTOM, 1, 1)
        self.rightgrid.attach_next_to(self.mmyear_combo, label2,
                                      Gtk.PositionType.RIGHT, 1, 1)

        label3 = Gtk.Label()
        text = self.tr('Label to add to answers title:')
        label3.set_markup(f'<span fgcolor="#595959"><b>{text}</b></span>')
        label3.props.margin_top = 10
        label3.props.margin_right = 10
        self.rightgrid.attach_next_to(label3, label2,
                                      Gtk.PositionType.BOTTOM, 1, 1)
        self.answers_title_entry = Gtk.Entry()
        self.answers_title_entry.set_editable(True)
        self.answers_title_entry.props.margin_top = 10
        self.answers_title_entry.set_text('')
        self.rightgrid.attach_next_to(self.answers_title_entry, label3,
                                      Gtk.PositionType.RIGHT, 2, 1)

        self.insert_tpl_button = Gtk.ToolButton.new()
        self.insert_tpl_button.set_vexpand(False)
        self.insert_tpl_button.set_hexpand(False)
        self.insert_tpl_button.props.margin = 10
        self.insert_tpl_button.connect('clicked', self.on_insert_tpl_clicked)
        self.insert_tpl_button.set_margin_bottom(10)
        self.rightgrid.attach_next_to(self.insert_tpl_button,
                                      self.answers_title_entry,
                                      Gtk.PositionType.RIGHT, 2, 1)

        latex_tpl = recollections.infolabel_latex_tpl
        if not latex_tpl:
            default_setup = json.loads(
                DEFAULT_DOCSETUP[prefs.language].read_text())
            latex_tpl = default_setup['latex_tpl']['infolabel']
        self.latex_tpl_entry = Gtk.Entry()
        self.latex_tpl_entry.set_editable(True)
        self.latex_tpl_entry.props.margin_top = 10
        self.latex_tpl_entry.set_text(latex_tpl)
        self.latex_tpl_entry.connect('changed', self.on_tpl_changed)
        self.rightgrid.attach_next_to(self.latex_tpl_entry,
                                      self.insert_tpl_button,
                                      Gtk.PositionType.RIGHT, 2, 1)

        label4 = Gtk.Label()
        text = self.tr(r'Infolabel color:')
        label4.set_markup(f'<span fgcolor="#595959"><b>{text}</b></span>')
        label4.props.margin_top = 10
        label4.props.margin_right = 10
        label4.props.margin_left = 10
        self.rightgrid.attach_next_to(label4, label3,
                                      Gtk.PositionType.BOTTOM, 1, 1)

        self.infolabel_color = self.recollections.infolabel_color
        radiogrid = Gtk.Grid()
        radiogrid.props.margin_top = 10

        radio0 = Gtk.RadioButton.new_from_widget(None)
        radio0.set_label(self.tr('None'))
        radio0.connect('toggled', self.on_radio_toggled, 'none')
        radiogrid.attach(radio0, 0, 0, 1, 1)
        radio0.set_active(self.infolabel_color == 'none')

        radio1 = Gtk.RadioButton.new_from_widget(radio0)
        radio1.set_label(self.tr('Yellow'))
        radio1.connect('toggled', self.on_radio_toggled, 'yellow')
        radiogrid.attach_next_to(radio1, radio0, Gtk.PositionType.RIGHT, 1, 1)
        radio1.set_active(self.infolabel_color == 'yellow')

        radio2 = Gtk.RadioButton.new_from_widget(radio0)
        radio2.set_label(self.tr('Green'))
        radio2.connect('toggled', self.on_radio_toggled, 'green')
        radiogrid.attach_next_to(radio2, radio1, Gtk.PositionType.RIGHT, 1, 1)
        radio2.set_active(self.infolabel_color == 'green')

        radio3 = Gtk.RadioButton.new_from_widget(radio0)
        radio3.set_label(self.tr('Blue'))
        radio3.connect('toggled', self.on_radio_toggled, 'blue')
        radiogrid.attach_next_to(radio3, radio2, Gtk.PositionType.RIGHT, 1, 1)
        radio3.set_active(self.infolabel_color == 'blue')

        radio4 = Gtk.RadioButton.new_from_widget(radio0)
        radio4.set_label(self.tr('Pink'))
        radio4.connect('toggled', self.on_radio_toggled, 'pink')
        radiogrid.attach_next_to(radio4, radio3, Gtk.PositionType.RIGHT, 1, 1)
        radio4.set_active(self.infolabel_color == 'pink')

        self.rightgrid.attach_next_to(radiogrid, label4,
                                      Gtk.PositionType.RIGHT, 4, 1)

        label5 = Gtk.Label()
        text = self.tr(r'Infolabel opacity:')
        label5.set_markup(f'<span fgcolor="#595959"><b>{text}</b></span>')
        label5.props.margin_top = 10
        label5.props.margin_right = 10
        label5.props.margin_left = 10
        self.rightgrid.attach_next_to(label5, label4,
                                      Gtk.PositionType.BOTTOM, 1, 1)

        self.infolabel_opacity = self.recollections.infolabel_opacity
        self.opacity_slider = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL,
            0.0,    # minimum
            1.0,    # maximum
            0.1     # step
        )
        self.opacity_slider.set_digits(1)
        self.opacity_slider.set_draw_value(True)
        self.opacity_slider.set_has_origin(True)
        self.opacity_slider.set_value(self.infolabel_opacity)
        self.opacity_slider.connect('value-changed', self.on_opacity_changed)
        self.rightgrid.attach_next_to(self.opacity_slider, label5,
                                      Gtk.PositionType.RIGHT, 1, 1)

        self.generate_button = Gtk.ToolButton.new()
        self.generate_button.set_vexpand(False)
        self.generate_button.set_hexpand(False)
        self.generate_button.props.margin = 10
        self.generate_button.connect('clicked', self.on_generate_clicked)
        self.generate_button.set_margin_bottom(10)
        self.rightgrid.attach_next_to(self.generate_button, label5,
                                      Gtk.PositionType.BOTTOM, 1, 1)
        #
        self.attach_next_to(self.rightgrid, self.treeview,
                            Gtk.PositionType.RIGHT, 1, 1)

        self.setup_buttons_icons(ICON_THEME)
        self.set_buttons_sensitivity()

    @property
    def chosen_mmyear(self):
        return mathmaker.available_years()[self.mmyear_combo.get_active()]

    @property
    def templates_dirpath(self):
        return Path(self.dest_dir.get_text())

    def update_available_levels(self, prefs):
        mm_levels = mathmaker.available_levels(self.chosen_mmyear,
                                               use_venv=prefs.use_mm_venv,
                                               venv=prefs.mm_venv)
        levels_scale = doc_setup.load()['levels']
        self.available_levels = levels_scale[0:len(mm_levels)]

    def on_mmyear_changed(self, *args):
        self.recollections.mm_year = self.chosen_mmyear
        self.update_available_levels(self.prefs)
        self.store.clear()
        for L in self.available_levels:
            self.store.append([L])

    def on_choosedir_clicked(self, *args):
        dialog = FolderSelectDialog(self.db, self.status, self.prefs,
                                    self.recollections, self.parentw)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            self.dest_dir.set_text(path)
            self.recollections.templates_dest_dir = path
        dialog.destroy()

    def on_insert_tpl_clicked(self, *args):
        orig = self.answers_title_entry.get_text()
        new = orig + self.latex_tpl_entry.get_text()
        self.answers_title_entry.set_text(new)

    def on_tpl_changed(self, entry):
        self.recollections.infolabel_latex_tpl = entry.get_text()

    def on_radio_toggled(self, button, action):
        if button.get_active():
            self.infolabel_color = action
            self.recollections.infolabel_color = action

    def on_opacity_changed(self, slider):
        self.infolabel_opacity = slider.get_value()
        self.recollections.infolabel_opacity = slider.get_value()

    def on_generate_clicked(self, *args):
        levels_scale = doc_setup.load()['levels']
        selected = self.selection.get_selected_rows()[1]
        selection = [self.store[selected[i]][0]
                     for i in range(len(selected))]
        mm_levels = mathmaker.available_levels(self.chosen_mmyear,
                                               use_venv=self.prefs.use_mm_venv,
                                               venv=self.prefs.mm_venv)
        mc_belts_json = {mm: cot
                         for mm, cot in zip(mm_levels, levels_scale)}
        BELTS_JSON.write_text(json.dumps(mc_belts_json))

        selected_mm_levels = [mm_levels[levels_scale.index(s)]
                              for s in selection]

        infolabel = self.answers_title_entry.get_text()
        if infolabel:
            text = infolabel
            if self.infolabel_color != 'none':
                # yellow #F7DD7C
                # green #A9EBC7
                # pink #FFB6C1
                # blue #B3EAE4
                colors = {'yellow': '{rgb,255:red,247;green,221;blue,124}',
                          'green': '{rgb,255:red,169;green,235;blue,199}',
                          'blue': '{rgb,255:red,179;green,234;blue,228}',
                          'pink': '{rgb,255:red,255;green,182;blue,193}'}
                fillcolor = colors[self.infolabel_color]
                opacity = self.infolabel_opacity
                text = r'\handhighlight[fill={fc},opacity={op}]{{{txt}}}'\
                    .format(fc=fillcolor, op=opacity, txt=text)
            new_answers_title = r'\textbf{' + self.tr('Answers (<BELT>)') \
                + '} ' + r'\hfill ' + text
            mc_titles_json = {"answers_title": new_answers_title}
            TITLES_JSON.write_text(json.dumps(mc_titles_json))
        errors = []
        for mm_level, selected_level in zip(selected_mm_levels, selection):
            failed = mathmaker.create_template(
                mm_level, selected_level, use_venv=self.prefs.use_mm_venv,
                venv=self.prefs.mm_venv, dest_dir=self.templates_dirpath,
                infolabel=infolabel)
            if failed:
                errors.append(selected_level)
        if errors:
            levels_list = ', '.join(errors)
            msg = self.tr('An error has been reported during the creation of '
                          'the templates for these levels: {levels_list}')
            if len(errors) == 1:
                msg = self.tr('An error has been reported during '
                              'the creation of the template for '
                              'this level: {levels_list}')
            msg = msg.format(levels_list=levels_list)
            run_message_dialog(self.tr('Errors'),
                               msg,
                               'dialog-error', self.parentw)
        else:
            # Retrieve possible pictures
            pictures = []
            for f in Path(self.templates_dirpath).glob('*.tex'):
                for line in f.read_text().split('\n'):
                    pictures.extend(re.findall(r"\{([^{]*\.eps)\}", line))
            pictures = set(pictures)
            if pictures:
                mm_config = mathmaker.get_user_config(
                    use_venv=self.prefs.use_mm_venv, venv=self.prefs.mm_venv)
                pics_dir = mm_config['PATHS'].get('OUTPUT_DIR', None)
                if pics_dir:
                    for p in pictures:
                        shutil.copy2(Path.home() / pics_dir / p,
                                     Path(self.templates_dirpath))
            # Build answers files
            for mm_level in selected_mm_levels:
                errorcode = mathmaker.compile_tex_file(
                    mc_belts_json[mm_level], directory=self.templates_dirpath)
                if errorcode:
                    msg = self.tr('An error has been reported during the '
                                  'compilation of the template for this '
                                  'file: {file_name}')
                    msg = msg.format(file_name=f'{mm_level}.tex')
                    run_message_dialog(self.tr('Errors'),
                                       msg,
                                       'dialog-error', self.parentw)
                    return
                else:
                    pdf = Pdf.new()
                    filename = mathmaker.belt_filename(mc_belts_json[mm_level])
                    pdf_name = f'{filename}.pdf'
                    corrected_label = self.tr('CORRECTED')
                    corrected_pdf_name = \
                        f'{filename} {corrected_label}.pdf'
                    with Pdf.open(self.templates_dirpath / pdf_name) as src:
                        pdf.pages.extend(src.pages[-2:])
                    pdf.save(self.templates_dirpath / corrected_pdf_name)
                    pdf.close()
            run_message_dialog(self.tr('Finished!'),
                               self.tr('All templates have been successfully '
                                       'created.'),
                               'dialog-information', self.parentw)

    def buttons_icons(self):
        """Defines icon names and fallback to standard icon name."""
        # Last item of each list is the fallback, hence must be standard
        buttons = {'choosedir_button': ['folder-open'],
                   'generate_button': ['system-run'],
                   'insert_tpl_button': ['document-import']}
        return buttons

    def buttons_labels(self):
        """Define labels of buttons."""
        buttons = {'choosedir_button': self.tr('Choose'),
                   'generate_button': self.tr('Generate'),
                   'insert_tpl_button':
                   self.tr('Insert LaTeX template for a class')}
        return buttons

    def set_buttons_sensitivity(self):
        selected = self.selection.get_selected_rows()[1]
        self.generate_button.set_sensitive(selected)
