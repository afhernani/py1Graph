
import math
try:
    from PIL import Image, ImageOps, ImageDraw
except:
    from pil import Image, ImageOps, ImageDraw
from imageblock import ImageBlock
import os

class Graphics():
    def __init__(self, width=None, height=None, **kvargs):
        '''
        Graphics imageblock tuning engine
            parameters:
                width, heigth -> frame setting
                kvargs => kv = {'path':'path/to/file',
                                'lpath': ['path/to/file', 'path/to/file1', ...]
                                'transform':False }

        '''
        # if kvargs:
        # self.path = None
        self.width = None
        self.height = None
        self.transform = False
        self.imgBox = None
        self.kvargs = kvargs
        for key, valor in kvargs.items():
            if key == 'path':
                path = os.path.abspath(valor)
                # print(self.path)
                if self.imgBox is None:
                    self.imgBox = ImageBlock(pathfile=path)
                else:
                    self.imgBox.fromFile(path=path)
            if key == 'lpath':
                if self.imgBox is None:
                    self.imgBox = ImageBlock(largs=valor)
                else:
                    self.imgBox.fromFile(largs=valor)
            if key =='transform':
                self.transform = valor
            print(f"{key} - {valor}")
            
        if width and height:
            self.width = width
            self.height = height

        print(self.width, self.height, self.kvargs)

    def config(self, **kvargs):
        self.kvargs = kvargs
        if kvargs.get('path', None) is not None or kvargs.get('largs', None) is not None:
            self.imgBox = None    
        for key, valor in kvargs.items():
            if key == 'path':
                if self.imgBox is None:
                    self.imgBox = ImageBlock(pathfile=valor)
                else:
                    self.imgBox.fromFile(path=valor)
            if key == 'lpath':
                if self.imgBox is None:
                    self.imgBox = ImageBlock(largs=valor)
                else:
                    self.imgBox.fromFile(largs=valor)
            if key =='transform':
                self.transform = valor
            if key =='width':
                self.width = valor
            if key =='height':
                self.height = valor
            print(f"{key} - {valor}")
        '''if self.imgBox:
            self.imgBox.bind('<Update>', self.on_update)'''

    def on_update(self):
        ''' actualizamos la imagen'''
        print('on_update have lunch')
        pass

    def fromFile(self, path=None, largs=[]):
        if self.imgBox:
            self.imgBox.fromFile(path=path, largs=largs)

    def getCurrentImg(self)->Image:
        if self.imgBox:
            if self.transform:
                return self.engine((self.width, self.height),
                              self.imgBox.getCurrentImagen())
            else:
                return self.imgBox.getCurrentImagen()

    def getImagenSecuencia(self, index):
        if self.imgBox:
            if self.transform:
                return self.engine((self.width, self.height),
                              self.imgBox.getImagenSecuencia(index))
            else:
                return self.imgBox.getImagenSecuencia(index)
        
    def getNextImg(self)->Image:
        if self.imgBox:
            if self.transform:
                return self.engine((self.width, self.height),
                              self.imgBox.getNextImagen())
            else:
                return self.imgBox.getNextImagen()
        
    def getSequencies(self):
        if self.imgBox:
            return self.imgBox.getSecuencies()         
                
    def engine(self, size=None, img=None ) -> Image:
        print('#### Engine ###')
        if not size or not img:
            return None
        '''
        if img.mode in ('RGB', 'P'):
            img.convert('RGB')
            ventana = Image.new('RGBA', img.size, (0, 0, 0, 255))
            ventana.save('ventana.png')
            ventana.paste(img, mask=ventana.split()[3])
            print('original mode:', img.mode, 'convert to:', ventana.mode)
            img = ventana'''
            
        if size == img.size:
            return img
        tamiz = Image.new('RGBA', size, (0, 0, 0, 255)) # transparente
        # print('size:', size, '\norignal mode:', img.mode, '\ninfo:', img.info)
        r, p = self.getScale(size, img.size)
        img_new = ImageOps.scale(img, r, 3)
        # return img_new
        tamiz.paste(img_new, p)
        return tamiz

    '''
    fill_color = ''  # your background
    image = Image.open(file_path)
    if image.mode in ('RGBA', 'LA'):
        background = Image.new(image.mode[:-1], image.size, fill_color)
        background.paste(image, image.split()[-1])
        image = background
    im.save(hidpi_path, file_type, quality=95)
    '''     

    def getScale(self, marco=None, marco2=None)-> tuple:
        '''return scale and centred possition img
            parammeter:
                marco: size imagen fin
                marco2: size imagen initial '''
        print('escala -')
        if not marco or not marco2:
            return 1.0
        w, h = marco
        w2, h2 = marco2
        x, y = 0, 0
        print('valores: ',w, h, w2, h2)
        f = w/h
        f2 = w2/h2
        print('relaciones ancho-alto:', f, f2)
        l = math.hypot(w, h)
        l2 = math.hypot(w2, h2)
        print('hipotemas:', l, l2)
        a = math.acos((w/l))
        a2 = math.acos((w2/l2))
        print('angulos:', a, a2)
        if a == a2:
            r = w/w2
            p = (0, 0)
        elif a < a2:
            r =h/h2
            y = 0
            x = int(abs(w - w2*r)/2)
            p = (x, y)
        elif a > a2:
            r =w/w2
            x = 0
            y = int(abs(h - h2*r)/2)
            p = (x, y)
        else:
            r = 1.0
            p = (0, 0)
        print('devuelve:', r, p)
        return (r, p)

    def reset(self, *args):
        if self.imgBox:
            self.imgBox.reset()

    def savetofile(self, source=None):
        '''create gif file from frames
            parameter:
                source: str name file to save
        '''
        source = 'unknow.gif' if source is None else source
        imgs = []
        self.transform = False
        for indx in range(self.imgBox.count):
            img = self.getImagenSecuencia(indx)
            imgs.append(img)
        # obtenemos todas las imagenes
        self.width, self.height = ImageBlock.whichWH(imgs=imgs)
        self.transform = True
        imgs.clear()
        for indx in range(self.imgBox.count):
            img = self.getImagenSecuencia(indx)
            imgs.append(img)
        imgs[0].save(source,
               save_all=True,
               append_images=imgs[1:],
               duration=1000,
               loop=0)


if __name__ == '__main__':
    '''
    kira = Image.open('kira.jpg')
    lienzo = Image.new('RGB', kira.size, (255, 255, 255))
    img = Image.open('sonriza.jpg')

    img2 = Image.open('kokonete_spd.jpg')
    r, p = escala(kira.size, img2.size)
    print('r:', r, 'p:', p)
    img_new = ImageOps.scale(img2, r, 3)
    print('scalade:', img_new.size)
    lienzo.paste(img_new, p)
    lienzo.save('kokonete_in_lienzo.jpg')
    os.startfile('kokonete_in_lienzo.jpg')
    
    inspeccion = Image.open('inspeccion.jpg')
    r, p = escala(kira.size, inspeccion.size)
    print('r:', r, 'p:', p)
    img_new = ImageOps.scale(inspeccion, r, 3)
    lienzo.paste(img_new, p)
    lienzo.save('inspeccion_kira_size.jpg')
    os.startfile('inspeccion_kira_size.jpg')

    zorras = Image.open('zorras.jpg')
    r, p = escala(kira.size, zorras.size)
    img_new = ImageOps.scale(zorras, r, 3)
    lienzo.paste(img_new, p)
    lienzo.save('zorras_kira_size.jpg')
    os.startfile('zorras_kira_size.jpg')

    concha = Image.open('concha.jpg')
    r, p = escala(kira.size, concha.size)
    img_new = ImageOps.scale(concha, r, 3)
    lienzo.paste(img_new, p)
    lienzo.save('concha_kira_size.jpg')
    os.startfile('concha_kira_size.jpg')

    grande = Image.open('Grande.jpg')
    r, p = escala(kira.size, grande.size)
    img_new = ImageOps.scale(grande, r, 3)
    lienzo.paste(img_new, p)
    lienzo.save('gramde_kira_size.jpg')
    os.startfile('gramde_kira_size.jpg')
    
    lechada = Image.open('lechada.png')
    # paso = Image.new('P', (640,480))
    lienzo = Engine((640,480), lechada)
    lienzo.save('lechada2.png')
    os.startfile('lechada2.png')

    boss = Image.open('boss.png')
    # paso = Image.new('P', (640,480))
    lienzo = Engine((200,150), boss)
    lienzo.save('boss-2.png')
    os.startfile('boss-2.png')
    '''
    
    kv = {'path':'fat.gif', 'transform':True }
    graphi = Graphics(200, 150, **kv)
    # graphi.getSequencies()
    n = graphi.imgBox.index
    print('n fat.gif:', n)
    img = graphi.getCurrentImg()
    
    if img:
        img.save('corriente.gif', 'GIF')
    graphi.fromFile(path='lala.gif')
    n = graphi.imgBox.index
    print('n fat.gif:', n)
    img = graphi.getCurrentImg()
    print('get current:', graphi.imgBox.index)
    if img:
        img.save('lala-corrnt.gif', 'GIF')
    a = ['norma.gif','old-mother.gif']
    graphi.config(width=400, height=600, lpath=a)
    n = graphi.imgBox.index
    print('index graphi:', n)
    graphi.imgBox.index = 38
    img = graphi.getCurrentImg()
    if img:
        img.save('lala-siguex.gif', 'GIF')
    lista = graphi.getSequencies()
    print(lista)
    print(len(lista), graphi.imgBox.index)
    print('WWWWWWWW')
    
'''
mirar fichero create_imagenes.py
'''
