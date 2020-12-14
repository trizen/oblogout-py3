#!/usr/bin/env python

# Edited by Daniel "Trizen" Șuteu to work on Python 3.

# Crunchbang Openbox Logout
#   - GTK/Cairo based logout box styled for Crunchbang
#
#    Andrew Williams <andy@tensixtyone.com>
#
#    Originally based on code by:
#       adcomp <david.madbox@gmail.com>
#       iggykoopa <etrombly@yahoo.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import os
import sys
import configparser
import io
import logging
import gettext
import string

import gi
gi.require_version('Gtk', '3.0')

try:
    from gi.repository import Gtk
    from gi.repository import Gdk
    from gi.repository import GdkPixbuf
    # from gi.repository import GdkX11
except:
    print("pyGTK missing, install python-gobject")
    sys.exit()
try:
    import cairo
except:
    print("Cairo modules missing, install python-cairo")

try:
    from PIL import Image, ImageFilter
except:
    print("PIL missing, install python-imaging")
    sys.exit()

class OpenboxLogout():

    cmd_shutdown = "shutdown -h now"
    cmd_restart = "reboot"
    cmd_suspend = "pmi action suspend"
    cmd_hibernate = "pmi action hibernate"
    cmd_safesuspend = ""
    cmd_lock = "gnome-screensaver-command -l"
    cmd_switch = "gdm-control --switch-user"
    cmd_logout = "openbox --exit"

    def __init__(self, config=None, local=None):

        if local:
            self.local_mode = True
        else:
            self.local_mode = False

        # Start logger and gettext/i18n
        self.logger = logging.getLogger(self.__class__.__name__)

        if self.local_mode:
            gettext.install('oblogout', 'mo')
        else:
            gettext.install('oblogout', '%s/share/locale' % sys.prefix)

        # Load configuration file
        self.load_config(config)

        # Start the window
        self.__init_window()

    def __init_window(self):
        # Start pyGTK setup
        self.window = Gtk.Window()
        self.window.set_title(_("Openbox Logout"))

        self.window.connect("destroy", self.quit)
        self.window.connect("key-press-event", self.on_keypress)
        self.window.connect("window-state-event", self.on_window_state_change)

        # TODO: fix me
        #if not self.window.is_composited():
        if True:
            self.logger.debug("No compositing, enabling rendered effects")
            # Window isn't composited, enable rendered effects
            self.rendered_effects = True
        else:
            # Link in Cairo rendering events
            #self.window.connect('expose-event',self.on_expose)
            self.window.connect('screen-changed', self.on_screen_changed)
            self.on_screen_changed(self.window)
            self.rendered_effects = False

        self.window.set_size_request(620,200)
        self.window.override_background_color(0, Gdk.RGBA(*Gdk.color_parse("black").to_floats()))

        self.window.set_decorated(False)
        self.window.set_position(Gtk.WindowPosition.CENTER)

        # Check monitor
        screen  = Gdk.Screen.get_default()
        if screen.get_n_monitors() < self.monitor:
           self.monitor = screen.get_n_monitors()

        geometry = screen.get_monitor_geometry(self.monitor)
        width    = geometry.width
        height   = geometry.height

        x = geometry.x
        y = geometry.y

        # Create the main panel box
        self.mainpanel = Gtk.HBox()

        # Create the button box
        self.buttonpanel = Gtk.HButtonBox()
        self.buttonpanel.set_spacing(10)

        # Pack in the button box into the panel box, with two padder boxes
        self.mainpanel.pack_start(Gtk.VBox(), False, False, 0)
        self.mainpanel.pack_start(self.buttonpanel, True, False, 0)
        self.mainpanel.pack_start(Gtk.VBox(), False, False, 0)

        # Add the main panel to the window
        self.window.add(self.mainpanel)

        for button in self.button_list:
            self.__add_button(button, self.buttonpanel)

        self.window.set_app_paintable(True)
        self.window.resize(width, height)
        self.window.realize()

        # GdkX11
        if self.rendered_effects == True:
            self.logger.debug("Stepping though render path")
            w = Gdk.get_default_root_window()
            surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
            pb = Gdk.pixbuf_get_from_surface(surface, 0, 0, width, height)
            #pb = pb.get_from_drget_pixelsawable(w,w.get_colormap(),x,y,0,0,width,height)
            #pb = pb.get_pixels()

            self.logger.debug("Rendering Fade")
            # Convert Pixbuf to PIL Image
            wh = (pb.get_width(),pb.get_height())
            pilimg = Image.frombytes("RGB", wh, pb.get_pixels())
            pilimg = pilimg.point(lambda p: (p * self.opacity) / 255 )

            # "Convert" the PIL to Pixbuf via PixbufLoader
            buf = io.BytesIO()
            pilimg.save(buf, "ppm")
            del pilimg
            loader = GdkPixbuf.PixbufLoader.new_with_type("pnm")
            loader.write(buf.getvalue())
            pixbuf = loader.get_pixbuf()

            # Cleanup IO
            buf.close()
            loader.close()

            # TODO: fix me
            #pixmap, mask = pixbuf.render_pixmap_and_mask()
            cr = cairo.Context(surface)
            Gdk.cairo_set_source_pixbuf(cr, pixbuf, width, height)
            cr.paint()
            pixmap = pixbuf
        else:
            pixmap = None

        if pixmap:
            True
            #self.window.Drawable.draw_pixbuf(pixbuf, 0, 0, 0, 0, width, height)
            #self.window.window.set_back_pixmap(pixmap, False)

        self.window.move(x,y)

    def load_config(self, config):
        """ Load the configuration file and parse entries, when encountering a issue
            change safe defaults """

        self.parser = configparser.ConfigParser()
        self.parser.read(config)

        # Set some safe defaults
        self.opacity = 50
        self.button_theme = "default"
        self.bgcolor = Gdk.color_parse("black")
        self.monitor = 0
        blist = ""

        # Check if we're using HAL, and init it as required.
        if self.parser.has_section("settings"):

            if self.parser.has_option("settings","backend"):
               self.backend = self.parser.get("settings","backend")
            else:
               self.backend = ""

            if self.parser.has_option("settings", "monitor"):
               self.monitor = self.parser.getint("settings", "monitor")

        # TODO: fix me
        # ~ if self.backend == "HAL" or self.backend == "ConsoleKit":
        if False:
            from .dbushandler import DbusController
            self.dbus = DbusController(self.backend)
            if self.dbus.check() == False:
               del self.dbus
               self.backend = ""
        else:
            self.backend = ""

        # Check the looks section and load the config as required
        if self.parser.has_section("looks"):

            if self.parser.has_option("looks", "opacity"):
                self.opacity = self.parser.getint("looks", "opacity")

            if self.parser.has_option("looks","buttontheme"):
                self.button_theme = self.parser.get("looks", "buttontheme")

            if self.parser.has_option("looks", "bgcolor"):
                try:
                    self.bgcolor = Gdk.color_parse(self.parser.get("looks", "bgcolor"))
                except:
                    self.logger.warning(_("Color %s is not a valid color, defaulting to black") % self.parser.get("looks", "bgcolor"))
                    self.bgcolor = Gdk.color_parse("black")

            if self.parser.has_option("looks", "opacity"):
                blist = self.parser.get("looks", "buttons")

        # Parse shortcuts section and load them into a array for later reference.
        if self.parser.has_section("shortcuts"):
            self.shortcut_keys = self.parser.items("shortcuts")
            self.logger.debug("Shortcut Options: %s" % self.shortcut_keys)


        # Parse in commands section of the configuration file. Check for valid keys and set the attribs on self
        if self.parser.has_section("commands"):
            for key in self.parser.items("commands"):
                self.logger.debug("Setting cmd_%s as %s" % (key[0], key[1]))
                if key[0] in ['logout', 'restart', 'shutdown', 'suspend', 'hibernate', 'safesuspend', 'lock', 'switch']:
                    if key[0]: setattr(self, "cmd_" + key[0], key[1])

        # Load theme information from local directory if local mode is set
        if self.local_mode:
            self.theme_prefix = "./data/themes"
        else:
            self.theme_prefix = "%s/share/themes" % sys.prefix

        self.img_path = "%s/%s/oblogout" % (self.theme_prefix, self.button_theme)

        if os.path.exists("%s/.themes/%s/oblogout" % (os.environ['HOME'], self.button_theme)):
            # Found a valid theme folder in the userdir, use that
            self.img_path = "%s/.themes/%s/oblogout" % (os.environ['HOME'], self.button_theme)
            self.logger.info("Using user theme at %s" % self.img_path)
        else:
            if not os.path.exists("%s/%s/oblogout" % (self.theme_prefix, self.button_theme)):
                self.logger.warning("Button theme %s not found, reverting to default" % self.button_theme)
                self.button_theme = 'foom'


        # Parse button list from config file.
        validbuttons = ['cancel', 'logout', 'restart', 'shutdown', 'suspend', 'hibernate', 'safesuspend', 'lock', 'switch']
        buttonname = [_('cancel'), _('logout'), _('restart'), _('shutdown'), _('suspend'), _('hibernate'), _('safesuspend'), _('lock'), _('switch')]

        if not blist:
            L = validbuttons
        elif blist == "default":
            L = validbuttons
        else:
            L = list([button.lstrip().rstrip() for button in blist.split(",")])

        # Validate the button L
        for button in L:
            if not button in validbuttons:
                self.logger.warning(_("Button %s is not a valid button name, removing") % button)
                L.remove(button)
            else:
                if self.backend:
                    if not self.dbus.check_ability(button):
                        self.logger.warning(_("Can't %s, disabling button" % button))
                        L.remove(button)

        if len(L) == 0:
            self.logger.warning(_("No valid buttons found, resetting to defaults"))
            self.button_list = validbuttons
        else:
            self.logger.debug("Validated Button List: %s" % L)
            self.button_list = L


    def on_expose(self, widget, event):

        cr = widget.window.cairo_create()

        if self.supports_alpha == True:
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.0) # Transparent
        else:
            cr.set_source_rgb(1.0, 1.0, 1.0) # Opaque white

        # Draw the background
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()

        (width, height) = widget.get_size()
        cr.set_source_rgba(self.bgcolor.red, self.bgcolor.green, self.bgcolor.blue, float(self.opacity)/100)

        cr.rectangle(0, 0, width, height)
        cr.fill()
        cr.stroke()
        return False

    def on_screen_changed(self, widget, old_screen=None):

        # TODO: fix me
        # To check if the display supports alpha channels, get the colormap
        screen = widget.get_screen()
        colormap = screen.get_rgba_colormap()
        if colormap == None:
            self.logger.debug("Screen does not support alpha channels!")
            colormap = screen.get_rgb_colormap()
            self.supports_alpha = False
        else:
            self.logger.debug("Screen supports alpha channels!")
            self.supports_alpha = True

        # Now we have a colormap appropriate for the screen, use it
        widget.set_colormap(colormap)

    def on_window_state_change(self, widget, event, *args):
        if event.new_window_state & Gdk.WindowState.FULLSCREEN:
            self.window_in_fullscreen = True
        else:
            self.window_in_fullscreen = False

    def __add_button(self, name, widget):
        """ Add a button to the panel """

        box = Gtk.VBox()

        image = Gtk.Image()
        if os.path.exists("%s/%s.svg" % (self.img_path, name)):
            image.set_from_file("%s/%s.svg" % (self.img_path, name))
        else:
            image.set_from_file("%s/%s.png" % (self.img_path, name))
        image.show()

        button = Gtk.Button()
        button.set_relief(2)    # RELIEF_NONE
        button.override_background_color(0, Gdk.RGBA(*Gdk.color_parse("black").to_floats()))
        button.set_focus_on_click(False)
        button.set_border_width(0)
        button.set_property('can-focus', False)
        button.add(image)
        button.show()
        box.pack_start(button, False, False, 0)
        button.connect("clicked", self.click_button, name)

        label = Gtk.Label(_(name))
        label.override_color(0, Gdk.RGBA(*Gdk.color_parse("white").to_floats()))
        box.pack_end(label, False, False, 0)

        widget.pack_start(box, False, False, 0)

    def click_button(self, widget, data=None):
        if (data == 'logout'):
            self.__exec_cmd(self.cmd_logout)

        elif (data == 'restart'):
            if self.backend:
                self.dbus.restart()
            else:
                self.__exec_cmd(self.cmd_restart)

        elif (data == 'shutdown'):
            if self.backend:
                self.dbus.shutdown()
            else:
                self.__exec_cmd(self.cmd_shutdown)

        elif (data == 'suspend'):
            self.window.hide()
            self.__exec_cmd(self.cmd_lock)
            if self.backend:
                self.dbus.suspend()

            else:
                self.__exec_cmd(self.cmd_suspend)

        elif (data == 'hibernate'):
            self.window.hide()
            self.__exec_cmd(self.cmd_lock)
            if self.backend:
                self.dbus.hibernate()
            else:
                self.__exec_cmd(self.cmd_hibernate)

        elif (data == 'safesuspend'):
            self.window.hide()

            if self.backend:
                self.dbus.safesuspend()
            else:
                self.__exec_cmd(self.cmd_safesuspend)

        elif (data == 'lock'):
            self.__exec_cmd(self.cmd_lock)

        elif (data == 'switch'):
            self.__exec_cmd(self.cmd_switch)

        self.quit()

    def on_keypress(self, widget=None, event=None, data=None):
        self.logger.debug("Keypress: %s/%s" % (event.keyval, Gdk.keyval_name(event.keyval)))
        for key in self.shortcut_keys:
            if event.keyval == Gdk.keyval_to_lower(Gdk.keyval_from_name(key[1])):
                self.logger.debug("Matched %s" % key[0])
                self.click_button(widget, key[0])

    def __exec_cmd(self, cmdline):
        self.logger.debug("Executing command: %s", cmdline)
        os.system(cmdline)

    def quit(self, widget=None, data=None):
        Gtk.main_quit()

    def run_logout(self):
        self.window.show_all()
        Gtk.main()
