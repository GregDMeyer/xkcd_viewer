# xkcd viewer

This is a viewer for the wonderful webcomic [xkcd](https://www.xkcd.com/). You may ask... I can just go to the website. What is the point of this?

Well, there are a few reasons:

 * Offline viewing. It's nice for plane rides!
 * Improved "random" functionality: keeps track of what comics you've seen (and this data is saved!), so when you hit "random" you always see new content. Only when you've seen everything does it clear out the history!
 * Comic series: for comics that are part of a series (like [this](https://xkcd.com/341/), for example), the 'b' and 'n' keys can be used to move back and forth in the series, even if the comics weren't published one after the other.

The hover-text works too!

Easily run just by typing `python3 xkcd_viewer.py`, or in a file browser, double clicking the desktop file!

#### Keyboard shortcuts:
 * <kbd>&uarr;</kbd> and <kbd>&darr;</kbd> arrow keys go through comics in order. 
 * <kbd>Space</kbd> goes to a random comic (that you haven't seen).
 * <kbd>&larr;</kbd> and <kbd>&rarr;</kbd> go back or forward in history.
 * <kbd>B</kbd> and <kbd>N</kbd> are "before" and "next" in a series (see above).

#### Requirements

 * Python 3
 * PyGObject (see [this website](https://python-gtk-3-tutorial.readthedocs.io/en/latest/index.html))
 * GTK+ 3
 * Acceptance of the fact that you are reading comics instead of going outside.

#### TODO:

There is some stuff to work on:

 * Download comics in the background, so you don't have to wait for them all
 * There are some weird encoding issues. For example when the alt-text has unusual characters in it, they display incorrectly.
 * It doesn't handle interactive comics well... maybe it should give a link instead for these!

----

[This gist](https://gist.github.com/jayrambhia/2018336) was a jumping off point for this code. :)
