#!/usr/bin/env python3
# _*_ coding:UTF-8 _*_
import tkinter as tk
from tkinter import filedialog
try:
    from PIL import Image, ImageTk #, ImageSequence
except:
    from pil import Image, ImageTk #, ImageSequence
import os, sys
from threading import Thread
from graphicblock import Graphics
import configparser, logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

__autor__='Hernani Aleman Ferraz'
__version__='v1.2'

class SpritePane(tk.Frame):
    ''' version: v1.2, with canva and image '''
    def __init__(self, parent, fileImagen=None, timer=None, **kvargs):
        tk.Frame.__init__(self, parent, **kvargs)
        logger.info('SpritePane: init')
        parent.bind('<Control-s>', self.file_save)
        parent.bind('<a>', self.define_transform)
        parent.bind('<r>', self.reset)
        parent.bind('<Key>', self.key)
        self.fileImagen= '' if fileImagen is None else fileImagen
        self.timer = 850 if timer is None else timer
        self.pathfile = tk.StringVar(value=self.fileImagen)
        self.transform = tk.BooleanVar(value=False)
        self.transform.trace_add('read', self.trace_transform )
        kv = {'path': self.fileImagen, 'transform':False }
        self.m_graphics = Graphics(**kv)
        self.m_img = self.m_graphics.getCurrentImg()
        self.w = self.m_img.width
        self.h = self.m_img.height
        self.m_graphics.config(width=self.w, height=self.h, transform=False)

        logger.info("w x h : {} x {}".format(self.w, self.h))
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
        logger.info(f'trace_info: {self.transform.trace_info()}')
        logger.info(f'trace_transform function, to read variable boolean: {x}, {y}, {z}')

    def define_transform(self, event):
        '''active mode transfor at dimension that img active'''
        logger.info(f'define_transform: {event}')
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
            logger.info("w x h : {} x {}".format(self.w, self.h))
            self.transform.set(True)
        else:
            self.m_graphics.config(transform=False)
            self.transform.set(False)

    def animate(self, counter):
        logger.info('## animate ##')
        if not self.animating:
            return
        try:
            self.index = counter
            # self.m_img.paste(self.m_graphics.getImagenSecuencia(self.index))
            self.m_img  = self.m_graphics.getImagenSecuencia(self.index)
            self.m_photo = ImageTk.PhotoImage(self.m_img)
            logger.info(f"animate -> Mode: {self.m_img.mode}, Photo: {self.m_photo}")
            self.canvas.itemconfig(self.c_img, image=self.m_photo)
            if self.m_graphics.imgBox.count > 0:
                self.after(self.timer, lambda: self.animate((counter+1)% self.m_graphics.imgBox.count))
        except Exception as e:
            logger.error(f'animate exception: {str(e.args)}')

    def enter(self, event):
        logger.info('enter: {}'.format(event))
        #if self.m_graphics.has_files():
        self.animating = True
        self.animate(self.index)
    
    def leave(self, event):
        logger.info('leave: {}'.format(event))
        self.animating = False

    def double_click(self, event):
        #import os
        logger.info('double-click-canvas: file:->{}'.format(self.pathfile.get()))
        logger.info('basename: -> {}'.format(os.path.basename(self.pathfile.get())))
        logger.info('split: -> {}'.format(os.path.split(self.pathfile.get())))
        logger.info('dirname: -> {}'.format(os.path.dirname(self.pathfile.get())))
        logger.info('directorio activo: -> {}'.format(os.getcwd()))
        address= [os.getcwd(), 'videos', os.path.basename(self.pathfile.get())]
        logger.info(f'address: {address}')
        #obtener el nombre del fichero de video
        _video_name = os.path.basename(self.pathfile.get()).split("_thumbs_")[0]
        _video = os.path.join(os.path.dirname(self.pathfile.get()), './../',  _video_name)
        logger.info(f'video -> {_video}')
        if os.path.isfile(_video):
            thread = Thread(target=self.tarea, args=("ffplay " + "\"" + _video + "\"",))
            thread.daemon = True
            thread.start()

    def image_click(self, event):
        logger.info(f'image_click: event {self.__class__.__name__}')
        logger.info(f'event: {event}')
        self.file_open()
        
    def file_open(self, *args):
        ftypes = [('Gif files', '*.gif'),('PNG files', '*.png'),('JPG files', '*.jpg'), ('All files', '*')]
        dlg = filedialog.Open(self, filetypes=ftypes, multiple=True)
        fl = dlg.show()
        logger.info(f'image_click: fls = {fl}')
        files = list(fl)
        logger.info(f'image_click: files = {files}')
        if fl:
            self.m_graphics.fromFile(largs=files)

    def file_save(self, *args):
        logger.info('file_save: {}'.format(args))
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
            file_n = filedialog.asksaveasfile(mode='wb+', **options)
            if file_n is None:
                return
        else:
            # return la cadena de referencia del fichero - aun no creado
            file_n = filedialog.asksaveasfilename(**options)
            if not file_n:
                return
        logger.info(f'file -> {file_n}')
        self.m_graphics.savetofile(file_n)
    
    def key(self, event):
        from tkinter import messagebox
        logger.info(f'1. pressed: {repr(event.char)}')
        # logger.info(f'2. pressed: {event.char}')
        if event.char == 'i':
            #master = tk.Tk()
            #master.title("Information")
            #master.geometry("400x400")
            texto = ("OPTIONS:\n\n"
                "• Click over picture area to load image.\n\n"
                "• a : Rescale the canvas to the original dimensions of the image.\n\n"
                "• r: Reset all images, erase all image uploads.\n\n"
                "• (Control + s): Save to gif file.\n\n"
                "• x : Show window adjustment information.\n\n")
            
            messagebox.showinfo(title="Information", message=texto)
            #msg = tk.Message(master, text=texto)
            #msg.config(bg='lightgreen', font=('times', 12, 'italic'))
            #msg.pack()
            #master.mainloop()
            #tk.mainloop()
        if event.char == 'x':
            messagebox.showinfo(title="Ajuste de ventana", message="pendiente ...")
            

    @staticmethod
    def tarea(args=None):
        if not args:
            return
        os.system(args)

    def reset(self, *args):
        if self.m_graphics:
            self.m_graphics.reset()
        self.index = 0

def main():
    root = tk.Tk()
    root.title("py1graph; push 'i' for information.")
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
