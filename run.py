#!/usr/bin/env python3

from xkcd_viewer import *
from os import chdir
from os.path import dirname, abspath

rundir = dirname(abspath(__file__))

chdir(rundir)

update_cache()

win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()

Gtk.main()
