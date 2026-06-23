#!/usr/bin/env python3
# _*_ coding:UTF-8 _*_
import tkinter as tk
from tkinter import filedialog, messagebox
try:
    from PIL import Image, ImageTk #, ImageSequence
except Exception as e:
    print(f'Error importing PIL: {e}')
import os, sys
from threading import Thread
from graphicblock import Graphics
import configparser, logging
from settings import config, root, save_config  # 👈 Importamos config y root

# Configuramos el logging usando el config.ini
log_level = config.get('APP', 'log_level', fallback='DEBUG')

logging.basicConfig(
    #filename=root / "debug.log",
    #filemode='w',  # 'a' para añadir, 'w' para sobrescribir cada vez que se ejecuta
    level=getattr(logging, log_level),
    # ¡IMPORTANTE! Usamos %(name)s para ver de qué archivo viene el log
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    #datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(root / "debug.log", encoding="utf-8", mode='w', delay=True),
        # comentar la linea inferior si no quieres que se muestre en consola
        logging.StreamHandler(),
    ],
    )


logger = logging.getLogger(__name__)
logger.info(f'Logging initialized in {root / "debug.log"}')

__autor__='Hernani Aleman Ferraz'
__version__='v1.3'


class SpritePane(tk.Frame):
    ''' version: v1.3, with canva and image '''
    def __init__(self, parent, fileImagen=None, timer=None, **kvargs):
        tk.Frame.__init__(self, parent, **kvargs)
        logger.info(f'SpritePane: __init__ with fileImagen={fileImagen}, timer={timer}')
        parent.bind('<Configure>', self.on_resize)
        parent.bind('<Control-q>', lambda e: parent.quit())
        parent.bind('<Control-o>', self.file_open)
        parent.bind('<Control-s>', self.file_save)
        parent.bind('<d>', self.right_click)
        parent.bind('<a>', self.define_transform)
        parent.bind('<r>', self.reset)
        parent.bind('<Key>', self.on_key)
        # leer configuracion de canvas
        self.canvas_width = kvargs.get('width', config.getint('CANVAS', 'width', fallback=400))
        self.canvas_height = kvargs.get('height', config.getint('CANVAS', 'height', fallback=300))
        self.canvas_bg = config.get('CANVAS', 'bg_color', fallback='yellow')
        # 2. Leer directorio por defecto
        self.default_dir = config.get('APP', 'default_dir', fallback=os.getcwd())

        self.fileImagen= '' if fileImagen is None else fileImagen
        self.fileImagen = self.default_dir
        self.timer = 850 if timer is None else timer
        self.pathfile = tk.StringVar(value=self.fileImagen)
        self.transform = tk.BooleanVar(value=False)
        self.transform.trace_add('read', self.trace_transform )
        kv = {'path': self.fileImagen, 'transform':False }
        self.m_graphics = Graphics(**kv)
        self.m_img = self.m_graphics.getCurrentImg()
        #self.w = self.m_img.width
        #self.h = self.m_img.height

        self.m_graphics.config(width=self.canvas_width, height=self.canvas_height, transform=False)

        logger.info("w x h : {} x {}".format(self.canvas_width, self.canvas_height))
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg=self.canvas_bg)
        self.canvas.pack()
        self.m_photo = ImageTk.PhotoImage(self.m_img)

        self.c_img = self.canvas.create_image(self.canvas_width/2, self.canvas_height/2, image=self.m_photo)

        self.canvas.bind('<Enter>', self.enter)
        self.canvas.bind('<Leave>', self.leave)
        self.canvas.bind('<Button-3>', self.right_click)
        self.canvas.bind('<Button-1>', self.image_click)
        self.animating = True
        # self.animate(0)
        self.index = 0

    def on_resize(self, event):
        logger.info(f'on_resize: event {event}')
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.m_graphics.config(width=self.canvas_width, height=self.canvas_height)
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        self.canvas.coords(self.c_img, self.canvas_width/2, self.canvas_height/2)
        logger.info("on_resize: w x h : {} x {}".format(self.canvas_width, self.canvas_height))

    def trace_transform(self, x, y, z):
        logger.info(f'trace_info: {self.transform.trace_info()}')
        logger.info(f'trace_transform function, to read variable boolean: {x}, {y}, {z}')

    def define_transform(self, event):
        '''active mode transfor at dimension that img active'''
        logger.info(f'define_transform: {event}')
        if not self.transform.get():
            self.m_img = self.m_graphics.getCurrentImg()
            self.m_photo = ImageTk.PhotoImage(self.m_img)
            #self.w, self.h = self.m_img.width, self.m_img.height
            self.m_graphics.config(width=self.canvas_width, height=self.canvas_height, transform=True)
            #self.canvas.config(width=self.w, height=self.h)
            self.canvas.delete('ALL')
            self.c_img = self.canvas.create_image(self.canvas_width/2, self.canvas_height/2, image=self.m_photo)
            self.canvas.update()
            # logger.info("w x h : {} x {}".format(self.w, self.h))
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

    def right_click(self, event):
        #import os
        logger.info('right-click-canvas: file:->{}'.format(self.pathfile.get()))
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
        # logger.info(f'image_click: fls = {fl}')
        files = list(fl)
        logger.info(f'image_click: files = {files}')
        if fl:
            self.m_graphics.fromFile(largs=files)
            new_path = os.path.dirname(files[0])  # Tomamos el directorio del primer archivo seleccionado
            logger.info(f'file_open: new_path = {new_path}')
            config.set('APP', 'default_dir', new_path)  # Actualizamos el config
            self.pathfile.set(new_path)  # Actualizamos el pathfile con el primer archivo seleccionado
            self.file_open = new_path

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
    
    def on_key(self, event):
        from tkinter import messagebox
        logger.info(f'1. pressed: {repr(event.char)}')
        if event.char == 'i':
            
            texto = ("OPTIONS:\n\n"
                "• Click over picture area to load image.\n\n"
                "• a : ajustar imagen al tamaño de la ventana.\n\n"
                "• r: Reset all images, erase all image uploads.\n\n"
                "• (Control + s): Save to gif file.\n\n"
                "• (Control + o): Open image file(s).\n\n"
                "• (Control + q): Quit application.\n\n"
                "• x : Show window adjustment information.\n\n")
            
            messagebox.showinfo(title="Information", message=texto)
            
        if event.char == 'x':
            messagebox.showinfo(title="Ajuste de ventana", message="pendiente ...")


    def on_closing(self):
        """Maneja el cierre de la aplicación y guarda la configuración."""
        from tkinter import messagebox
        
        # 1. Preguntar al usuario
        if messagebox.askyesnocancel("Salir", "¿Desea guardar la configuración actual antes de salir?"):
            
            # Actualizamos el objeto config en memoria (usando self)
            #if self.pathfile.get():
            #    config.set('APP', 'default_dir', str(self.pathfile.get()))
            config.set('CANVAS', 'width', str(self.canvas_width-10))
            config.set('CANVAS', 'height', str(self.canvas_height))
            
            # Guardamos en disco
            save_config()
            logger.info("Configuración guardada al salir.")
            
            # Cerramos la ventana (self.master es la ventana root)
            self.master.destroy()
            
        elif messagebox.askyesno("Salir", "¿Está seguro que desea salir sin guardar?"):
            self.master.destroy()
        # Si pulsa Cancelar, no hace nada.


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
    # Leemos el tamaño desde el config para la ventana principal también
    w = config.getint('CANVAS', 'width', fallback=400)
    h = config.getint('CANVAS', 'height', fallback=600)
    root.geometry(f"{w+10}x{h+10}")
    #root.geometry("400x600")
    app = SpritePane(root) #, fileImagen='./../work/thumbails/cotton.gif', timer=200)
    app.pack(fill=tk.BOTH, expand=True)
    root.update_idletasks()
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    # app2 = SpritePane(root, fileImagen='Image/moving_text.gif')
    # app2.pack()
    # app3 = SpritePane(root, fileImagen='_Work/Thumbails/butt.gif')
    # app3.pack()
    #app4 = SpritePane(root, fileImagen='_Work/Thumbails/Bust.gif')
    root.mainloop()


if __name__ == '__main__':
    main()
