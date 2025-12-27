import tempfile
import time
import webbrowser

from PySide6 import QtWidgets as qtw, QtCore as qtc, QtGui as qtg
from PySide6.QtGui import QSurfaceFormat, QOpenGLContext, QOffscreenSurface
from PySide6.QtOpenGL import QOpenGLFramebufferObjectFormat, QOpenGLFramebufferObject
from PySide6.QtPdf import QPdfDocument
import fitz
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
import numpy as np

def qt_render_pdf_page_to_qimage(path, page_number, scale):
    document = QPdfDocument(None)
    document.load(path)
    doc = fitz.open(path)
    page = doc.load_page(page_number)
    rendered = document.render(page_number, qtc.QSize(int(page.mediabox_size.x*scale), int(page.mediabox_size.y*scale)))
    return rendered

class Feature:
    pass

class RenderWidget(QOpenGLWidget):
    signalMouseClick = qtc.Signal(float, float, qtc.Qt.MouseButton) # canvas X,Y
    signalMouseMove = qtc.Signal(float, float)
    signalMouseRelease = qtc.Signal(float, float, qtc.Qt.MouseButton)
    signalKeyPressed = qtc.Signal(float, float, qtc.Qt.Key)
    signalKeyReleased = qtc.Signal(float, float, qtc.Qt.Key)
    
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.features = {}
        self.i = 0
        self.clean = False
        self.initialized = False
        self.x = 0 # pixels, top-left is center
        self.y = 0
        self.angle = 0 # degrees
        self.scale = 1
        self.setFocusPolicy(qtc.Qt.FocusPolicy.StrongFocus)
        qtc.QTimer.singleShot(1, self.initializeGL)

    def initializeGL(self):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)

        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glEnable(GL_POLYGON_SMOOTH)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        self.initialized = True

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def paintGL(self):
        if not self.initialized:
            return
        self.do_draw(self.x, self.y, self.width(), self.height(), self.scale, self.angle)
        return super().paintGL()

    def do_draw(self, x = 0, y = 0, w = None, h = None, s = 1, a = 0):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if w is None:
            w = 640 #self.image.width()
            h = 480 #self.image.height()
            x = -w/2
            y = h/2

        def cnv_xy_to_disp(_x: float, _y: float):
            """Go from image XY to viewport XY"""
            _x += x
            _y -= y
            _x *= s
            _y *= s
            _x, _y = _x * np.cos(a) + _y * np.sin(a), _x * np.cos(a - np.pi / 2) + _y * np.sin(a - np.pi / 2)
            _x += w / 2
            _y += h / 2
            return _x, _y

        def disp_xy_to_cnv(_x: float, _y: float):
            """Go from viewport XY to image XY"""
            # print(x, y)
            _x -= w / 2
            _y -= h / 2
            r = np.sqrt(_x ** 2 + _y ** 2)
            t = np.arctan2(-_y, _x)
            r /= s
            t += a
            _x, _y = r * np.cos(t), r * np.sin(t)
            # x += self.x / self.scale
            # y -= self.y / self.scale
            # x /= self.scale
            # y /= self.scale
            _x -= x
            _y += y
            return _x, _y

        def disp_to_gl(_x: float, _y: float):
            return 2 * _x / w - 1, 1 - 2 * _y / h

        def cnv_xy_to_gl(_x: float, _y: float):
            return disp_to_gl(*cnv_xy_to_disp(_x, _y))

        glLoadIdentity()
        # if self.image is not None:
        #     glBlendEquation(GL_FUNC_ADD)
        #     glBegin(GL_QUADS)
        #     glColor3f(1.0, 1.0, 1.0)
        #     glTexCoord2f(0, 1); glVertex2f(*cnv_xy_to_gl(0, 0))
        #     glTexCoord2f(1, 1); glVertex2f(*cnv_xy_to_gl(self.image.width(), 0))
        #     glTexCoord2f(1, 0); glVertex2f(*cnv_xy_to_gl(self.image.width(), self.image.height()))
        #     glTexCoord2f(0, 0); glVertex2f(*cnv_xy_to_gl(0, self.image.height()))
        #     glEnd()

        #     glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        #     glBindTexture(GL_TEXTURE_2D, self.texture_id)
        #     glBegin(GL_QUADS)
        #     glTexCoord2f(0, 1); glVertex2f(*cnv_xy_to_gl(0, 0))
        #     glTexCoord2f(1, 1); glVertex2f(*cnv_xy_to_gl(self.image.width(), 0))
        #     glTexCoord2f(1, 0); glVertex2f(*cnv_xy_to_gl(self.image.width(), self.image.height()))
        #     glTexCoord2f(0, 0); glVertex2f(*cnv_xy_to_gl(0, self.image.height()))
        #     glEnd()
        #     glBindTexture(GL_TEXTURE_2D, 0)

        glBlendEquation(GL_FUNC_ADD)
        glBlendFunc(GL_ONE, GL_ONE)


        glBegin(GL_TRIANGLES)
        glColor3f(1.0, 0.0, 0.0)
        glVertex2f(-0.5, 0.3)
        glColor3f(0.0, 0.0, 0.0)
        glVertex2f(0.6, 0.6)
        glColor3f(1.0, 1.0, 1.0)
        glVertex2f(0.3, -0.6)
        glEnd()

    def add_feature(self, f:Feature)->int:
        self.features[self.i] = f
        self.i += 1
        self.clean = False
        return self.i-1
    
    def remove_feature(self, i:int):
        self.features.pop(i)
        self.clean = False

    def mousePressEvent(self, a0):
        self.signalMouseClick.emit(a0.pos().x(), a0.pos().y(), a0.button())

    def mouseMoveEvent(self, a0):
        self.signalMouseMove.emit(a0.pos().x(), a0.pos().y())

    def mouseReleaseEvent(self, a0):
        self.signalMouseClick.emit(a0.pos().x(), a0.pos().y(), a0.button())
        
    def keyPressEvent(self, a0):
        self.signalKeyPressed.emit(a0.key())
        
    def keyReleaseEvent(self, a0):
        self.signalKeyReleased.emit(a0.key())

class RenderWidget2(QOpenGLWidget):
    signalClick = qtc.Signal(float, float, qtc.Qt.MouseButton) # canvas X,Y
    signalDrag = qtc.Signal(float, float)
    signalRelease = qtc.Signal(float, float, qtc.Qt.MouseButton)
    signalKeyPressed = qtc.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.image:qtg.QImage|None = None
        self.x = 0 # pixels, top-left is center
        self.y = 0
        self.mouse_coords = (0, 0)
        self.mouse_start = (0, 0)
        self.last_mouse = (0, 0)
        self.last_angle = 0
        self.last_scale = 1
        self.mouse_buf = []
        self.angle = 0 # degrees
        self.scale = 1
        self.image = None

        qtc.QTimer.singleShot(1, self.home)
        self.setFocusPolicy(qtc.Qt.FocusPolicy.StrongFocus)
        self.texture_id = None

    def set_image(self, image:qtg.QImage | None):
        if image is None:
            self.image = None
            self.home()
        else:
            self.image = image.copy()
            
            self.initializeGL()
            self.home()

    def initializeGL(self):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)

        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glEnable(GL_POLYGON_SMOOTH)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

        if self.image is not None:
            glEnable(GL_MULTISAMPLE)
            qimage = self.image.convertToFormat(qtg.QImage.Format.Format_RGBA8888)
            width = qimage.width()
            height = qimage.height()

            # Get image data as bytes
            image_data = qimage.bits().asstring(width * height * 4)
            self.texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                         GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glGenerateMipmap(GL_TEXTURE_2D)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def paintGL(self):
        self.do_draw(self.x, self.y, self.width(), self.height(), self.scale, self.angle)
        # self.do_draw()
        mx, my = self.disp_xy_to_cnv(*self.mouse_coords)
        mgx, mgy = self.cnv_xy_to_gl(mx, my)
        w, h, x, y, a, s = self.width(), self.height(), self.x, self.y, self.angle, self.scale
        hc = h/2
        wc = w/2


        glBlendEquation(GL_FUNC_SUBTRACT)
        glBlendFunc(GL_ONE, GL_ONE)
        glColor3f(0.5, 0.5, 0.5)



        if self.last_mouse is None:
            glBegin(GL_LINES)
            glVertex2f(-1, mgy)
            glVertex2f(1, mgy)
            glVertex2f(mgx, -1)
            glVertex2f(mgx, 1)
            glEnd()
        else:
            if s != self.last_scale:
                r1 = np.sqrt((self.last_mouse[0]-wc)**2+(self.last_mouse[1]-hc)**2)
                r2 = np.sqrt((self.mouse_coords[0]-wc)**2+(self.mouse_coords[1]-hc)**2)
                glBegin(GL_LINE_LOOP)
                for i in range(45):
                    dx = np.cos(np.radians(i*8))*r1 * (2/self.width())
                    dy = np.sin(np.radians(i*8))*r1 * (2/self.height())
                    glVertex2f(dx, dy)
                glEnd()
                glBegin(GL_LINE_LOOP)
                for i in range(45):
                    dx = np.cos(np.radians(i*8))*r2 * (2/self.width())
                    dy = np.sin(np.radians(i*8))*r2 * (2/self.height())
                    glVertex2f(dx, dy)
                glEnd()
            if a != self.last_angle:
                glBegin(GL_LINES)

                glVertex2f(0, 0)
                glVertex2f(mgx, mgy)
                glVertex2f(0, 0)
                glVertex2f(*self.cnv_xy_to_gl(*self.disp_xy_to_cnv(*self.last_mouse)))
                glEnd()
            if s == self.last_scale and a == self.last_angle:
                msx, msy = self.cnv_xy_to_gl(*self.disp_xy_to_cnv(*self.mouse_start))
                glBegin(GL_LINES)
                glVertex2f(-1, msy)
                glVertex2f(1, msy)
                glVertex2f(msx, -1)
                glVertex2f(msx, 1)
                glVertex2f(-1, mgy)
                glVertex2f(1, mgy)
                glVertex2f(mgx, -1)
                glVertex2f(mgx, 1)
                glEnd()



    def do_draw(self, x = 0, y = 0, w = None, h = None, s = 1, a = 0):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if w is None:
            w = self.image.width()
            h = self.image.height()
            x = -w/2
            y = h/2

        def cnv_xy_to_disp(_x: float, _y: float):
            """Go from image XY to viewport XY"""
            _x += x
            _y -= y
            _x *= s
            _y *= s
            _x, _y = _x * np.cos(a) + _y * np.sin(a), _x * np.cos(a - np.pi / 2) + _y * np.sin(a - np.pi / 2)
            _x += w / 2
            _y += h / 2
            return _x, _y

        def disp_xy_to_cnv(_x: float, _y: float):
            """Go from viewport XY to image XY"""
            # print(x, y)
            _x -= w / 2
            _y -= h / 2
            r = np.sqrt(_x ** 2 + _y ** 2)
            t = np.arctan2(-_y, _x)
            r /= s
            t += a
            _x, _y = r * np.cos(t), r * np.sin(t)
            # x += self.x / self.scale
            # y -= self.y / self.scale
            # x /= self.scale
            # y /= self.scale
            _x -= x
            _y += y
            return _x, _y

        def disp_to_gl(_x: float, _y: float):
            return 2 * _x / w - 1, 1 - 2 * _y / h

        def cnv_xy_to_gl(_x: float, _y: float):
            return disp_to_gl(*cnv_xy_to_disp(_x, _y))

        glLoadIdentity()
        if self.image is not None:
            glBlendEquation(GL_FUNC_ADD)
            glBegin(GL_QUADS)
            glColor3f(1.0, 1.0, 1.0)
            glTexCoord2f(0, 1); glVertex2f(*cnv_xy_to_gl(0, 0))
            glTexCoord2f(1, 1); glVertex2f(*cnv_xy_to_gl(self.image.width(), 0))
            glTexCoord2f(1, 0); glVertex2f(*cnv_xy_to_gl(self.image.width(), self.image.height()))
            glTexCoord2f(0, 0); glVertex2f(*cnv_xy_to_gl(0, self.image.height()))
            glEnd()

            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 1); glVertex2f(*cnv_xy_to_gl(0, 0))
            glTexCoord2f(1, 1); glVertex2f(*cnv_xy_to_gl(self.image.width(), 0))
            glTexCoord2f(1, 0); glVertex2f(*cnv_xy_to_gl(self.image.width(), self.image.height()))
            glTexCoord2f(0, 0); glVertex2f(*cnv_xy_to_gl(0, self.image.height()))
            glEnd()
            glBindTexture(GL_TEXTURE_2D, 0)

        glBlendEquation(GL_FUNC_ADD)


        glBegin(GL_TRIANGLES)
        glColor3f(1.0, 0.0, 0.0)
        glVertex2f(*cnv_xy_to_gl(50, 150))
        glColor3f(0.0, 0.0, 0.0)
        glVertex2f(*cnv_xy_to_gl(350, 150))
        glColor3f(1.0, 1.0, 1.0)
        glVertex2f(*cnv_xy_to_gl(150, 50))
        glEnd()

    def render_to_image(self):
        if self.image is None:
            return
        width, height = self.image.width(), self.image.height()
        fmt = QSurfaceFormat()
        fmt.setVersion(2, 1)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CompatibilityProfile)
        QSurfaceFormat.setDefaultFormat(fmt)
        ctx = QOpenGLContext()
        ctx.setFormat(fmt)
        ctx.create()

        surface = QOffscreenSurface()
        surface.setFormat(fmt)
        surface.create()

        ctx.makeCurrent(surface)

        self.initializeGL()

        # Create offscreen framebuffer
        fbo_format = QOpenGLFramebufferObjectFormat()
        fbo_format.setAttachment(QOpenGLFramebufferObject.Attachment.CombinedDepthStencil)

        fbo = QOpenGLFramebufferObject(width, height, fbo_format)

        fbo.bind()
        glViewport(0, 0, width, height)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.do_draw()

        glFlush()
        pixels = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
        image = qtg.QImage(pixels, width, height, qtg.QImage.Format.Format_RGBA8888)
        image = image.mirrored()
        fbo.release()

        return image


    def cnv_xy_to_disp(self, x:float, y:float):
        """Go from image XY to viewport XY"""
        w, h = self.width(), self.height()
        x += self.x
        y -= self.y
        x *= self.scale
        y *= self.scale
        x, y = x*np.cos(self.angle) + y*np.sin(self.angle), x*np.cos(self.angle-np.pi/2) + y*np.sin(self.angle-np.pi/2)

        x += w/2
        y += h/2
        return x, y

    def disp_xy_to_cnv(self, x:float, y:float):
        """Go from viewport XY to image XY"""
        w, h = self.width(), self.height()
        x -= w/2
        y -= h/2
        r = np.sqrt(x**2+y**2)
        t = np.arctan2(-y, x)
        r /= self.scale
        t += self.angle
        x, y = r*np.cos(t), r*np.sin(t)
        x -= self.x
        y += self.y
        return x, y

    def disp_to_gl(self, x:float, y:float):
        return 2*x/self.width()-1, 1-2*y/self.height()

    def cnv_xy_to_gl(self, x:float, y:float):
        return self.disp_to_gl(*self.cnv_xy_to_disp(x, y))

    def home(self):
        self.angle = 0
        self.last_angle = 0

        if self.image is None:
            self.x = 0
            self.y = 0
            self.scale = 1
            self.last_scale = 1
        else:
            self.scale = min(self.width()/self.image.width(), self.height()/self.image.height())
            self.last_scale = self.scale
            self.x = -self.image.width()/2
            self.y = self.image.height()/2
        self.repaint()

    def mouseMoveEvent(self, ev: qtg.QMouseEvent) -> None:
        self.mouse_coords = ev.pos().x(), ev.pos().y()
        if ev.buttons() == qtc.Qt.MouseButton.MiddleButton or \
                (ev.buttons() == qtc.Qt.MouseButton.LeftButton and ev.modifiers() == qtc.Qt.KeyboardModifier.ControlModifier):
            if self.last_mouse is not None:
                dx = (ev.pos().x() - self.last_mouse[0])/self.scale
                dy = (ev.pos().y() - self.last_mouse[1])/self.scale
                self.x += dx*np.cos(self.angle)+dy*np.sin(self.angle)
                self.y += dx*np.cos(self.angle+np.pi/2)+dy*np.sin(self.angle+np.pi/2)
            self.last_mouse = ev.pos().x(), ev.pos().y()
        elif ev.buttons() == qtc.Qt.MouseButton.RightButton:
            if self.last_mouse is not None:
                dc1x = self.last_mouse[0]-self.width()/2
                dc2x = ev.pos().x()-self.width()/2

                dc1y = self.last_mouse[1]-self.height()/2
                dc2y = ev.pos().y()-self.height()/2

                dc1 = np.sqrt(dc1y**2+dc1x**2)
                dc2 = np.sqrt(dc2y**2+dc2x**2)
                if not (dc1 > 16 and dc2 > 16):
                    return

                ds = dc2 / dc1

                t1 = np.arctan2(dc1y,dc1x)
                t2 = np.arctan2(dc2y,dc2x)
                dt = (t2-t1)

                modifiers = qtw.QApplication.keyboardModifiers()
                if modifiers == qtc.Qt.KeyboardModifier.ShiftModifier:
                    self.scale = self.last_scale
                else:
                    self.scale = max(0.001,self.last_scale*ds)
                self.angle = self.last_angle + dt

        self.repaint()

    def mousePressEvent(self, ev):
        self.mouse_coords = ev.pos().x(), ev.pos().y()
        self.mouse_start = self.mouse_coords
        self.last_mouse = ev.pos().x(), ev.pos().y()
        self.mouse_buf += ev.pos().x(), ev.pos().y()
        self.last_angle = self.angle
        self.last_scale = self.scale

    def mouseReleaseEvent(self, ev: qtg.QMouseEvent) -> None:
        self.last_mouse = None

    def wheelEvent(self, a0):
        last_scale = self.scale
        self.scale = max(0.001, self.scale*(1+a0.angleDelta().y()/1000))
        dx, dy = a0.position().x()-self.width()/2, a0.position().y()-self.height()/2
        dxs, dys =  dx*(last_scale/self.scale-1)/self.scale, dy*(last_scale/self.scale-1)/self.scale
        dr =np.sqrt(dxs**2+dys**2)
        dt = np.arctan2(dys,dxs)
        self.x += dr*np.cos(dt-self.angle)
        self.y += dr*np.sin(dt-self.angle)

        self.repaint()

    def keyPressEvent(self, a0):
        if a0.key() == qtc.Qt.Key.Key_Home:
            print('home')
            self.home()
        if a0.key() == qtc.Qt.Key.Key_End:
            im = self.render_to_image()
            if im is not None:
                im.save("out.png")
                webbrowser.open("out.png")


class MultipagePreviewer(qtw.QListWidget):
    def __init__(self, renderer:RenderWidget):
        super().__init__()
        self.images = []
        self.image_items = []
        self.scale = 5
        self.setFixedWidth(128)
        self.renderer = renderer

    def selectionChanged(self, selected, deselected):
        if selected:
            self.images[selected.indexes()[0].row()](self.scale, self.renderer.set_image)
        else:
            self.renderer.set_image(None)
        return super().selectionChanged(selected, deselected)
    

    def set_images(self, images:list):
        """
            images - list of image fetch request callables. 
                Argument 1 of the callable is the render scale. 
                Argument 2 of the callable is the callback
        """
        self.clear()
        self.images = images
        self.image_items.clear()
        for i, im in enumerate(images):
            item = qtw.QListWidgetItem()
            item.setSizeHint(qtc.QSize(120, 120))
            self.addItem(item)
            self.image_items.append(item)
            im(0.1, lambda img, _i=i: self.set_preview(_i, img))

    def set_preview(self, idx, img:qtg.QImage):
        print(idx)
        if idx > len(self.images):
            return
        lb = qtw.QLabel()
        lb.setScaledContents(True)
        lb.setPixmap(qtg.QPixmap.fromImage(img))
        self.setItemWidget(self.image_items[idx], lb)