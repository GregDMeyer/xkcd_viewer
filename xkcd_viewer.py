
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
from gi.repository.Pango import FontDescription

from os.path import isdir, isfile
from os import mkdir, listdir
import urllib.request as req
from urllib.error import URLError
import json
import pickle
from random import choice


def update_cache():

    # make dirs in a safe way
    try:
        mkdir('comics')
    except OSError as e:
        if not e.errno == 17:
            raise e

    try:
        mkdir('metadata')
    except OSError as e:
        if not e.errno == 17:
            raise e

    #print('Current comic number: ',end='')
    try:
        with req.urlopen('http://xkcd.com/info.0.json') as request:
             d = json.loads(request.read().decode('UTF-8'))
        current_number = d['num']
    	#print(current_number)
    except URLError: # no connection
        return max((int(x.split('.')[0]) for x in listdir('comics')))

    skip = [404, 1608, 1663 ]

    for i in range(1,current_number+1):

        if i in skip:
            continue

        if not any( [isfile('comics/'+str(i)+ext) for ext in ['.jpg','.png','.gif'] ] ):

            print('Getting comic',i)

            with req.urlopen('http://xkcd.com/'+str(i)+'/info.0.json') as request:
                d = json.loads(request.read().decode('UTF-8'))

            with req.urlopen(d['img']) as request:
                p = request.read()

            with open('comics/'+str(i)+'.'+d['img'].split('.')[-1],'wb') as imgfile:
                imgfile.write(p)

            if not isfile('metadata/'+str(i)):
                with open('metadata/'+str(i),'wb') as datfile:
                    pickle.dump(d,datfile)

    return current_number



class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='xkcd')

        self.maximize()

        # random comic log
        if not isfile('rand_remain'):
            self.rand_remain = [int(x.split('.')[0]) for x in listdir('comics')]
            with open('rand_remain','wb') as f:
                pickle.dump(self.rand_remain, f)
        else:
            with open('rand_remain','rb') as f:
                self.rand_remain = pickle.load(f)

        self.cur_num = max((int(x.split('.')[0]) for x in listdir('comics')))
        self.max_img = self.cur_num

        self.history = []
        self.hist_pos = -1
        
        self.box = Gtk.VBox(False, 0)
        self.add(self.box)
        self.box.show()
        
        self.button_box = Gtk.HBox(False,0)
        self.box.pack_start(self.button_box, False, False, 3)
        self.button_box.show()

        self.title_box = Gtk.HBox(False,0)
        self.box.pack_start(self.title_box, False, False, 20)
        self.title_box.show()

        self.swindow = Gtk.ScrolledWindow()
        self.box.pack_start(self.swindow, True, True, 0)
        self.swindow.show()

        self.imgbox = Gtk.HBox(False,0)
        self.swindow.add_with_viewport(self.imgbox)
        self.imgbox.show()

        self.image = Gtk.Image()
        self.imgbox.pack_start(self.image, True, False, 0)
        
        self.prev_button = Gtk.Button("< previous")
        self.prev_button.show()
        self.prev_button.connect("clicked",self.prev_image)
        self.prev_button.set_can_focus(False)
        self.button_box.pack_start(self.prev_button, True, True, 0)
        
        self.rand_button = Gtk.Button('random (' + str(self.max_img - len(self.rand_remain)) +'/'+ str(self.max_img) +')' )
        self.rand_button.show()
        self.rand_button.connect("clicked",self.rand_image)
        self.rand_button.set_can_focus(False)
        self.button_box.pack_start(self.rand_button, True, True, 0)
        
        self.next_button = Gtk.Button("next >")
        self.next_button.show()
        self.next_button.connect("clicked",self.next_image)
        self.next_button.set_can_focus(False)
        self.button_box.pack_start(self.next_button, True, True, 0)

        self.title_label = Gtk.Label()
        self.title_box.pack_start(self.title_label, True, True, 0)
        self.title_label.modify_font(FontDescription("' bold', 20"))
        self.title_label.show()

        # maybe just using selected buttons with arrow keys is better?
        self.connect('key_press_event',self.on_key_press)
        
        self.ch_img(self.cur_num)
        self.image.show()
        
        self.show()

    
    def ch_img(self,num,add_to_hist=True):
        self.cur_num = num
        self.img_file = get_fname(self.cur_num)
        self.image.set_from_file( self.img_file )

        if add_to_hist:

            if self.hist_pos < -1:
                self.history = self.history[:self.hist_pos+1]

            self.history.append(self.cur_num)
            self.hist_pos = -1

        try:
            self.rand_remain.remove( self.cur_num )
        except ValueError:
            pass

        self.rand_button.set_label('random (' + str(self.max_img - len(self.rand_remain)) +'/'+ str(self.max_img) +')')

        self.data = get_data(self.cur_num)

        self.image.set_tooltip_text( self.data['alt'] )
        self.set_title('xkcd '+str(num)+': '+self.data['safe_title'])
        self.title_label.set_text(str(num)+': '+self.data['safe_title'])

        # keep track
        with open('rand_remain','wb') as f:
            pickle.dump(self.rand_remain, f)


    def next_image(self, widget=None, user_data=None, index=None):
        
        if self.cur_num >= self.max_img:
            return

        self.ch_img(self.cur_num + 1)

       
    def prev_image(self, widget=None, user_data=None, index=None):

        if self.cur_num <= 1:
            return

        self.ch_img(self.cur_num - 1)


    def ch_in_series(self, direction='next', widget=None, user_data=None, index=None):
        '''
        If the comic is part of a series, get the next one in the series!
        '''

        if ' ' not in self.data['safe_title'] or self.data['safe_title'].split(' ')[-2] != 'Part' or not is_int_str(self.data['safe_title'].split(' ')[-1]):
            return

        num_in_series = int(self.data['safe_title'].split(' ')[-1])

        if direction == 'next':
            num_in_series += 1

        elif direction == 'prev':
            num_in_series -= 1

        # only get this data if we need to
        if not hasattr(self, 'all_comic_names'):
            self.all_comic_names = {}
            for fname in listdir('metadata'):
                with open('metadata/'+fname, 'rb') as f:
                    d = pickle.load(f)
                    self.all_comic_names[ d['safe_title'] ] = int(fname)

        ch_name = ' '.join( self.data['safe_title'].split(' ')[:-1] + [str(num_in_series)] )

        if ch_name in self.all_comic_names:
            self.ch_img( self.all_comic_names[ch_name] )

        return


    
    def rand_image(self, widget=None, user_data=None):
        if not len(self.rand_remain):
            self.rand_remain = [int(x.split('.')[0]) for x in listdir('comics')]
        self.ch_img(choice(self.rand_remain))


    def ch_by_history(self,direction):

        if direction == 'prev':
            # don't overdo it
            if -1 * self.hist_pos < len(self.history):
                self.hist_pos -= 1
                self.ch_img(self.history[self.hist_pos], add_to_hist=False)
                return

        if direction == 'next':
            if -1 * self.hist_pos > 1:
                self.hist_pos += 1
                self.ch_img(self.history[self.hist_pos], add_to_hist=False)
                return


    def on_key_press(self, widget=None, event=None, user_data=None):

        if event.keyval == 32: # space
            self.rand_image()
            return

        if event.keyval == 65361: # left arrow key
            self.ch_by_history('prev')
            return

        if event.keyval == 65362: # up arrow key
            self.next_image()
            return

        if event.keyval == 65363: # right arrow
            self.ch_by_history('next')
            return

        if event.keyval == 65364: # down arrow key
            self.prev_image()
            return

        if event.keyval == 98: # down arrow key
            self.ch_in_series(direction='prev')
            return

        if event.keyval == 110: # down arrow key
            self.ch_in_series(direction='next')
            return

        # print(event.keyval)

        
def get_fname(i):

    for ext in ['.jpg','.png','.gif']:
        if isfile('comics/'+str(i)+ext):
            return 'comics/'+str(i)+ext
    return None

def get_data(i):
    with open('metadata/'+str(i), 'rb') as f:
        d = pickle.load(f)

    return d

def is_int_str(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

        
if __name__ == '__main__':

    update_cache()

    win = MainWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()

    Gtk.main()
