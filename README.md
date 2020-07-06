## Openbox Logout Menu

Gtk3/Cairo based logout menu for the Openbox Window Manager.

![oblogout](https://user-images.githubusercontent.com/614513/86627660-5b5b4680-bfd1-11ea-8bba-622054574c66.png)

This is a fork of: https://github.com/Cloudef/oblogout-fork

* oblogout by:
     - Andrew Williams <andy@tensixtyone.com>

* Originally based on code by:
     - adcomp <david.madbox@gmail.com>
     - iggykoopa <etrombly@yahoo.com>

* Modified by Daniel [Trizen](https://github.com/trizen) Șuteu to work on Python 3.

# INSTALLATION

 - Run `./setup.py install`
 - Customise the config (`/etc/oblogout.conf`) as desired

# RUN

 - Run via the `oblogout` command


# CONFIGURATION OPTIONS

## SETTINGS

 - Backend  = Choose backend to use with oblogout's shutdown/restart operations
      - HAL
      - ConsoleKit ( Uses UPower for suspend/hibernate )

 - Monitor  = Specify which monitor oblogout will appear in.


## LOOKS

 - Opacity = Opacity percentage of Cario rendered backgrounds
 - Bgcolor = Colour name or hex code (#ffffff) of the background color

 - Buttontheme = Icon theme for the buttons, must be in the themes folder of the
                 package, or in ~/.themes/<name>/oblogout/
 - Buttons = List and order of buttons to show


## BUTTONS

 - cancel      = Cancel logout/shutdown
 - restart     = Restart
 - shutdown    = Shutdown
 - suspend     = Suspend
 - hibernate   = Hibernate
 - safesuspend = Suspend/Hibernate mix, writes Hibernate file then suspends
 - lock        = Lock session
 - switch      = Switch user


## SHORTCUTS

 - For each button type, define a key to use. Case insenstive.


## COMMANDS

 - Same as the buttons, define a command per button type


# LICENSE

```
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
```
