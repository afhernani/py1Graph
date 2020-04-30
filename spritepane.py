# !/usr/bin/env python3
# _*_ coding:UTF-8 _*_
import tkinter as tk
from tkinter import filedialog
try:
    from PIL import Image, ImageTk #, ImageSequence
except:
    from pil import Image, ImageTk #, ImageSequence
import os
from threading import Thread
from graphicblock import Graphics

__autor__='Hernani Aleman Ferraz'
__version__='v1.2'

class SpritePane(tk.Frame):
    ''' version: v1.2, with canva and image '''
    def __init__(self, parent, fileImagen=None, timer=None, **kvargs):
        tk.Frame.__init__(self, parent, **kvargs)
        parent.bind('<G>', self.file_save)
        parent.bind('<A>', self.define_transform)
        parent.bind('<Key>', self.key)
        self.fileImagen= fileImagen
        if not fileImagen:
            self.fileImagen = './Image/sprite.gif'
        self.timer = timer
        if not timer:
            self.timer = 850
        self.pathfile = tk.StringVar(value=self.fileImagen)
        self.transform = tk.BooleanVar(value=False)
        self.transform.trace('r', self.trace_transform )
        kv = {'path': self.fileImagen, 'transform':False }
        self.m_graphics = Graphics(**kv)
        self.m_img = self.m_graphics.getCurrentImg()
        self.w = self.m_img.width
        self.h = self.m_img.height
        self.m_graphics.config(width=self.w, height=self.h, transform=False)

        print("w x h : {} x {}".format(self.w, self.h))
        self.canvas = tk.Canvas(self, width=self.w, height=self.h, bg="yellow")
        self.canvas.pack()
        self.m_photo = ImageTk.PhotoImage(self.m_img)

        self.c_img = self.canvas.create_image(self.w/2, self.h/2, image=self.m_photo)

        self.canvas.bind('<Enter>', self.enter)
        self.canvas.bind('<Leave>', self.leave)
        self.canvas.bind('<Double-Button-1>', self.double_click)
        self.canvas.bind('<Button-1>', self.image_click)
        self.animating = True
        # self.animate(0)
        self.index = 0

    def trace_transform(self, x, y, z):
        print('trace_info', self.transform.trace_info())
        print('trace_transform function, to read variable boolean:', x, y, z)

    def define_transform(self, event):
        '''active mode transfor at dimension that img active'''
        print('define_transform:', event)
        if not self.transform.get():
            self.m_img = self.m_graphics.getCurrentImg()
            self.m_photo = ImageTk.PhotoImage(self.m_img)
            self.w = self.m_img.width
            self.h = self.m_img.height
            self.m_graphics.config(width=self.w, height=self.h, transform=True)
            self.canvas.config(width=self.w, height=self.h)
            self.canvas.delete('ALL')
            self.c_img = self.canvas.create_image(self.w/2, self.h/2, image=self.m_photo)
            self.canvas.update()
            print("w x h : {} x {}".format(self.w, self.h))
            self.transform.set(True)
        else:
            self.m_graphics.config(transform=False)
            self.transform.set(False)

    def animate(self, counter):
        print('animate')
        if not self.animating:
            return
        try:
            self.index = counter
            # self.m_img.paste(self.m_graphics.getImagenSecuencia(self.index))
            self.m_img  = self.m_graphics.getImagenSecuencia(self.index)
            self.m_photo = ImageTk.PhotoImage(self.m_img)
            print(self.m_img.mode, self.m_photo)
            self.canvas.itemconfig(self.c_img, image=self.m_photo)
            
            self.after(self.timer, lambda: self.animate((counter+1)% self.m_graphics.imgBox.count))
        except Exception as e:
            print('animate exception:', e.args)

    def enter(self, event):
        self.animating = True
        self.animate(self.index)
    
    def leave(self, event):
        self.animating = False

    def double_click(self, event):
        #import os
        print('double-click-canvas: file:->{}'.format(self.pathfile.get()))
        print('basename: -> ', os.path.basename(self.pathfile.get()))
        print('split: -> ', os.path.split(self.pathfile.get()))
        print('dirname: -> ', os.path.dirname(self.pathfile.get()))
        print('directorio activo: -> ', os.getcwd())
        address= [os.getcwd(), 'videos', os.path.basename(self.pathfile.get())]
        print(address)
        #obtener el nombre del fichero de video
        _video_name = os.path.basename(self.pathfile.get()).split("_thumbs_")[0]
        _video = os.path.join(os.path.dirname(self.pathfile.get()), './../',  _video_name)
        print('video ->', _video)
        if os.path.isfile(_video):
            thread = Thread(target=self.tarea, args=("ffplay " + "\"" + _video + "\"",))
            thread.daemon = True
            thread.start()

    def image_click(self, event):
        print('image_click: event', self.__class__.__name__)
        print('event: ', event)
        self.file_open()
        
    def file_open(self, *args):
        ftypes = [('Gif files', '*.gif'),('PNG files', '*.png'),('JPG files', '*.jpg'), ('All files', '*')]
        dlg = filedialog.Open(self, filetypes=ftypes, multiple=True)
        fl = dlg.show()
        print(f'image_click: fls = {fl}')
        files = list(fl)
        print(f'image_click: files = {files}')
        if fl:
            self.m_graphics.fromFile(largs=files)

    def file_save(self, *args):
        fileTypes = [('Gif files', '*.gif'),('PNG files', '*.png'),('JPG files', '*.jpg'), ('All files', '*')]
        dirName = os.getcwd()
        fileName = "spritpane-"
        title = 'Save file'
        asFile = False
        # define options for opening
        options = {}
        options['defaultextension'] = '*.gif'
        options['filetypes'] = fileTypes
        options['initialdir'] = dirName
        options['initialfile'] = fileName
        options['title'] = title
        if asFile:
            # referencia al fichero abierto
            file = filedialog.asksaveasfile(mode='wb+', **options)
        else:
            # return la cadena de referencia del fichero - aun no creado
            file = filedialog.asksaveasfilename(**options)
        print('file -> ', file)
        return file
        # TODO: aqui a�adimos lo que queremos hacer

    def key(self, event):
        print('1. pressed:', repr(event.char))
        print('2. pressed:', event.char )

    @staticmethod
    def tarea(args=None):
        if not args:
            return
        os.system(args)


def main():
    root = tk.Tk()
    root.geometry("400x600")
    app = SpritePane(root) #, fileImagen='./../work/thumbails/cotton.gif', timer=200)
    app.pack()
    # app2 = SpritePane(root, fileImagen='Image/moving_text.gif')
    # app2.pack()
    # app3 = SpritePane(root, fileImagen='_Work/Thumbails/butt.gif')
    # app3.pack()
    #app4 = SpritePane(root, fileImagen='_Work/Thumbails/Bust.gif')
    root.mainloop()


if __name__ == '__main__':
    main()
