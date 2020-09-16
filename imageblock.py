#!/usr/bin/env python3
# _*_ coding:UTF-8 _*_
try:
    from PIL import Image, ImageSequence, ImageDraw
except:
    from pil import Image, ImageSequence, ImageDraw
import os

class ImageBlock():

    def __init__(self, pathfile=None, largs=[]):
        self.eCalls = {}
        self.datos = {'image': Image, 'index': 0, 'count': 0, 'error': None}
        self.imgx = self.CreateImg()
        self.index, self.count, self.error = 0, 0, None
        self.ext = ['.gif', '.GIF', '.jpg', '.JPG', '.png', '.PNG', '.webp', '.WEBP']
        self.frames = []
        try:
            self.fromFile(path=pathfile, largs=largs)
            # set imagen default 1/2
            i = int(self.index/2)
            self.getImagenSecuencia(i)
        except Exception as e:
            self.error = e.args
            print('excepcion init process class', self.__class__.__name__)
            print('exception:', e.args)
    
    def bind(self, key, function):
        ''' evento de vinculacion
                parameters:
                    key: name event
                    function: function asosiate
         '''
        self.eCalls[key] = function
    
    def invoke(self, key, *args):
        ''' invoke event for execute function
                parameters:
                    key : event lunch
                    *args: pass name of arguments to function with key
            ####
            '<Update>' -> Actualiza imagen
         '''
        function = self.eCalls.get(key, lambda: 'invalid event')
        function(*args)

    def reset(self, *args):
        self.index, self.count, self.error = 0, 0, None
        self.frames.clear()

    def getImagenSecuencia(self, index)->Image:
        ''' devuelve la imagen del index indicado 
            parametro:
                index: de 0 a count-1
                '''
        # print('getImagenSecuencia')
        count = self.count
        if index >= count or index < 0:
           return self.imgx
        self.index = index
        file, v = self.frames[index]
        try:
            if v == -1:
                # no existe más imagenes.
                self.imgx = Image.open(file).copy()
            elif v >= 1:
                # esto es una animación y corresponde al indice v-1 la que se extrae
                self.imgx = ImageSequence.Iterator(Image.open(file))[v-1].copy()
            else:
                self.error = 'Not extract file from frames '
        except Exception as e:
            self.error = 'getImagenSecuencia' + e.args
            print(e.args)
            
        return self.imgx.copy()

    def getCurrentImagen(self)-> Image:
        '''return de current image that refer index'''
        if len(self.frames)==0:
            return self.imgx
        else:
            return self.getImagenSecuencia(self.index)

    def getNextImagen(self):
        ''' return la siguiente imagen '''
        index = self.index
        count = self.count
        index += 1
        if index >= count or index < 0:
            index = 0

        self.index = index
        return self.getImagenSecuencia(index)

    def getPeviousImagen(self):
        ''' return la imagen previa '''
        index = self.index
        count = self.count
        index -= 1
        if index >= count or index < 0:
            index = count - 1

        self.index = index
        return self.getImagenSecuencia(index)

    def getSecuencies(self):
        ''' return all paths of images into the secuencies'''
        return self.frames

    def fromFile(self, path=None, largs=[]):
        '''load Imagen from file mode read only -open-close.
        parameter:
               path: string path file
               largs: list files to load
        '''
        if not path and not largs:
            print('not imageblock path or largs')
            return
        ext = tuple(self.ext)
        _colect_frames = []
        try:
            if path:
                # print('path is not none')
                abspath = os.path.abspath(path)
                # print(abspath)
                if os.path.exists(abspath):
                    if abspath.endswith(ext):
                        # print('load ...', abspath)
                        # self.frames.append(Image.open(abspath).copy())
                        _colect_frames.append(abspath)
                        # self.frames.append(abspath)
                else:
                    raise ValueError(f"No se pudo abrir: {abspath}")
            for file in largs:
                # print('files in largs')
                abspath = os.path.abspath(file)
                # print(abspath)
                if os.path.exists(abspath):
                    if abspath.endswith(ext):
                        _colect_frames.append(abspath)
                        # print('load ...', abspath)
                        # self.frames.append(Image.open(abspath).copy())
                        # self.frames.append(abspath)
                    else:
                        raise ValueError(f"No se pudo abrir: {abspath}")

            self.selectframesfromfiles(_colect_frames)
        
        except Exception as e:
            self.error = e
            print('error fromFile:', e)

    def selectframesfromfiles(self, colection=[]):
        # print('selectframesfromfiles function')
        for item in colection:
            self.type_file_to_analize(item)
        # TODO: lunch event actualizacin.
        if self.eCalls.get('<Update>') != None:
            self.invoke('<Update>') # Actualiza end image loaded

    def analizeGIF(self, argument):
        'analizamos si tiene animation'
        # print('analizeGif')
        try:
            img = Image.open(argument)
            nf = img.n_frames
            if nf == 1:
                self.frames.append((argument, -1))
                self.count += 1
            else:
                for inde in range(1, nf+1):
                    self.frames.append((argument, inde ))
                    self.count += 1
            self.imgx = ImageSequence.Iterator(img)[nf-1].copy()
            self.index = self.count -1
            img.close()

        except Exception as e:
            print('exception selectframesfromfiles: ', e.args, argument)

    def analizeJPG(self, argument):
        '''no es un fichero animado'''
        self.frames.append((argument, -1))
        self.imgx = Image.open(argument)
        self.count += 1
        self.index = self.count -1

    def analizeWEBP(self, argument):
        '''por ahora no hace nada, TODO: tendremos en cuenta si es no animacion'''
        # self.frames.append((argument, -1))
        # self.imgx = Image.open(argument).copy()
        # self.count += 1
        # self.index = self.count -1
        pass

    def analizePNG(self, argument):
        ''' png no animado '''
        self.frames.append((argument, -1))
        self.imgx = Image.open(argument)
        self.count += 1
        self.index = self.count -1

    def type_file_to_analize(self, argument):
        etc = '.' + argument.split('.')[-1]
        etc = etc.upper()
        switcher = {
            '.GIF': self.analizeGIF,
            '.JPG': self.analizeJPG,
            '.JPEG': self.analizeJPG,
            '.PNG': self.analizePNG,
            '.WEBP':self.analizeWEBP
        }
        func = switcher.get(etc, lambda: "Invalid month")
        # ejecutamos la función
        func(argument)

    def CreateImg(self)->Image:
        im = Image.new('RGBA', (320, 240), (0, 0, 0, 255)) 
        draw = ImageDraw.Draw(im)
        p1 = (0, 0, im.size[0], im.size[1])
        p2 = (0, im.size[1], im.size[0], 0)
        draw.line(p1, fill=(255,0,0), width=20)
        draw.line(p2, fill=(255,0,0), width=20)
        # im.save('x.png')
        # os.startfile('x.png')
        return im

    @staticmethod
    def whichWH(imgs=[])-> tuple:
        ''' get (w, h) maxima from a group of images
            parameters:
                imgs=[] : list of images
            return
                tuple size = w,h : maximum or 0, 0 it is not posible
        '''
        import types
        z = 0, 0
        if len(imgs) >= 1:
            try:
                if isinstance(imgs[0].size, tuple):
                    w, h = 0, 0
                    for itm in imgs:
                        if w < itm.size[0]:
                            w = itm.size[0]
                        if h < itm.size[1]:
                            h = itm.size[1]
                    z = w, h
            except AttributeError as e:
                print(str(e.args))
        return z


if __name__ == '__main__':
    block = ImageBlock('./Image/Tiger.gif')
    print(len(block.frames), block.count)
    l = ['./Image/avatar.jpg', './Image/disenho.png', './Image/medusa.jpg','./Image/srcimg05.jpg']
    block.fromFile(largs=l)
    print('leng:', block.count)
    print('conten:', block.frames)
    # cargar algo que no existe
    block.fromFile('mi_imagen.webp')
    block.getCurrentImagen().show()
    pos = int(block.count/2 -1)
    block.getImagenSecuencia(pos).show()
    print(block.getCurrentImagen().height)



