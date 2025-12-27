import pathlib
import random
import time

from PIL import Image
from PySide6 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc

from redliner.common.persistent_dict import PersistentDict
from redliner.common import hex_to_rgb
from redliner.common.common import resource_path
from redliner.extensions.feature import Feature
from redliner.extensions.source_doc import SrcPage, FitzDoc
import moderngl
import numpy as np
from redliner.common.constants import DIFF_VERT, DIFF_FRAG, BG_FRAG, BG_VERT


class RenderPage:
    def __init__(self):
        self.lhs: None | SrcPage = None
        self.rhs: None | SrcPage = None
        self.features:list[Feature] = []
    @property
    def width(self):
        wmax = 0
        if self.lhs is not None:
            wmax = self.lhs.width
        if self.rhs is not None:
            wmax = max(wmax, self.rhs.width)
        return wmax

    @property
    def height(self):
        hmax = 0
        if self.lhs is not None:
            hmax = self.lhs.height
        if self.rhs is not None:
            hmax = max(hmax, self.rhs.height)
        return hmax

class Renderer:
    def __init__(self):
        self.ctx = moderngl.create_standalone_context(samples=4)
        self.prog_diff = self.ctx.program(
            vertex_shader=DIFF_VERT,
            fragment_shader=DIFF_FRAG,
        )
        self.prog_tile = self.ctx.program(
            vertex_shader=BG_VERT,
            fragment_shader=BG_FRAG,
        )
        self.page:RenderPage = RenderPage()
        self.lhs_tex: None | moderngl.Texture = None
        self.rhs_tex: None | moderngl.Texture = None
        self.vbo_diff: None | moderngl.Buffer = None
        self.vao_diff: None | moderngl.VertexArray = None

        points = [
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1]
        ]
        coords = np.dstack(points).T
        self.vbo_tile = self.ctx.buffer(coords.astype('f4').tobytes())
        self.vao_tile = self.ctx.simple_vertex_array(self.prog_tile, self.vbo_tile, 'inCoord')
        bg_tile = Image.open(resource_path("background_tile.png"))
        self.background_tex = self.ctx.texture((400, 400), 3, bg_tile.tobytes())
        self.background_tex.use(0)
        self.vao_tile.program["uTextureBGTile"] = 0
        self.regenerate()

    def set_page(self, page:RenderPage):
        if self.lhs_tex is not None:
            self.lhs_tex.release()
            self.lhs_tex = None
        if self.rhs_tex is not None:
            self.rhs_tex.release()
            self.rhs_tex = None
        self.page = page
        if page.lhs is not None:
            h, w, n = self.page.lhs.raster.shape
            self.lhs_tex = self.ctx.texture((w, h), n, self.page.lhs.raster.data, )
            self.lhs_tex.use(1)
        if page.rhs is not None:
            h, w, n = self.page.rhs.raster.shape
            self.rhs_tex = self.ctx.texture((w, h), n, self.page.rhs.raster.data, )
            self.rhs_tex.use(2)
        self.regenerate()


    def regenerate(self):

        if self.vbo_diff is not None:
            self.vbo_diff.release()
        if self.vao_diff is not None:
            self.vao_diff.release()
        points = [
            [0, 0],
            [self.page.width, 0],
            [self.page.width, self.page.height],
            [0, self.page.height]
        ]
        coords = np.dstack(points).T
        self.vbo_diff = self.ctx.buffer(coords.astype('f4').tobytes())
        self.vao_diff = self.ctx.simple_vertex_array(self.prog_diff, self.vbo_diff, 'inCoord')
        self.vao_diff.program["uTextureLHS"] = 1
        self.vao_diff.program["uTextureRHS"] = 2
        self.vao_diff.program["uPageWH"] = self.page.width, self.page.height
        if self.lhs_tex is None:
            self.vao_diff.program["uLHSWH"] = 0,0

        else:
            self.vao_diff.program["uLHSWH"] = self.page.lhs.width, self.page.lhs.height
        if self.rhs_tex is None:
            self.vao_diff.program["uRHSWH"] = 0,0

        else:
            self.vao_diff.program["uRHSWH"] = self.page.rhs.width, self.page.rhs.height

    def render(self,
               col_add:tuple,
               col_rem:tuple,
               col_hilight:tuple,
               do_hilight:bool = True,
               hilight_thresh:float=0.1,
               hilight_size:int=8,
               x:float = 0,
               y:float = 0,
               scale:float = 1,
               theta:float = 0,
               render_lhs = True,
               render_rhs = True,
               width:int = None,
               height:int = None) -> qtg.QImage:
        if width is None:
            width = self.page.width
        if height is None:
            height = self.page.height
        fbo:moderngl.Framebuffer = self.ctx.simple_framebuffer((width, height))
        fbo.use()
        fbo.clear(0.0, 1.0, 0.0, 1.0)

        self.vao_tile.program["uCanvasWH"] = width, height
        self.vao_tile.render(moderngl.TRIANGLE_FAN)


        self.vao_diff.program["uPos"] = x, y
        self.vao_diff.program["uScale"] = scale
        # self.vao_diff.program["uTheta"] = theta
        self.vao_diff.program["uCanvasWH"] = width, height
        self.vao_diff.program["doHilight"] = do_hilight
        self.vao_diff.program["hilightThresh"] = hilight_thresh
        self.vao_diff.program["hilightSize"] = hilight_size
        self.vao_diff.program["renderLHS"] = render_lhs
        self.vao_diff.program["renderRHS"] = render_rhs
        self.vao_diff.program["colAdd"] = col_add[0]/255, col_add[1]/255, col_add[2]/255
        self.vao_diff.program["colRem"] = col_rem[0]/255, col_rem[1]/255, col_rem[2]/255
        self.vao_diff.program["colHilight"] = col_hilight[0]/255, col_hilight[1]/255, col_hilight[2]/255

        self.vao_diff.render(moderngl.TRIANGLE_FAN)

        qim = qtg.QImage(fbo.read(), fbo.size[0], fbo.size[1], fbo.size[0]*3, qtg.QImage.Format.Format_RGB888)

        for attachment in fbo.color_attachments:
            attachment.release()
        if fbo.depth_attachment is not None:
            fbo.depth_attachment.release()
        fbo.release()

        return qim


class RenderWidget(qtw.QLabel):
    def __init__(self, parent = None):
        self.parent = parent
        super().__init__()
        self.pd = PersistentDict()
        self.renderer = Renderer()
        self.x = 0
        self.y = 0
        self.scale = 1
        self.theta = 0
        self.mouse_stack = []
        self.mouse_button = qtc.Qt.MouseButton.NoButton
        self.mouse_hover = 0,0
        self.setFocusPolicy(qtc.Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.home()

    def keyPressEvent(self, a0):
        if a0.key() == qtc.Qt.Key.Key_Left:
            self.redraw(rh=False)
        if a0.key() == qtc.Qt.Key.Key_Right:
            self.redraw(lh=False)
        self.parent.keyPressEvent(a0)

    def keyReleaseEvent(self, a0):
        self.redraw()

    def set_page(self, page:RenderPage):
        if self.renderer.page.lhs is None and self.renderer.page.rhs is None:
            self.renderer.set_page(page)
            self.home()
        else:
            self.renderer.set_page(page)
            self.redraw()

    def wheelEvent(self, a0):
        # the idea is that the point at mx, my should not move on the screen after scrolling.
        cx, cy = self.mouse_coords_to_canvas(*self.mouse_hover)
        self.scale *= (1+a0.angleDelta().y()/500)
        if self.scale < 0.01:
            self.scale = 0.01
        cx2, cy2 = self.mouse_coords_to_canvas(*self.mouse_hover)
        self.x += cx2-cx
        self.y += cy2-cy
        self.redraw()

    def mouse_coords_to_canvas(self, mx:float, my:float) -> tuple:
        return mx/self.scale-self.x, my/self.scale-self.y

    def canvas_to_mouse_coords(self, cx:float, cy:float) -> tuple:
        return (cx+self.x)*self.scale, (cy+self.y)*self.scale


    def mousePressEvent(self, ev):
        self.mouse_button = ev.button()
        self.mouse_stack = [[ev.pos().x(), ev.pos().y()]]

    def mouseMoveEvent(self, ev):
        if self.mouse_button == qtc.Qt.MouseButton.MiddleButton or self.mouse_button == qtc.Qt.MouseButton.LeftButton:
            # pan
            dx, dy = ev.pos().x()-self.mouse_stack[-1][0], ev.pos().y()-self.mouse_stack[-1][1]
            self.x += dx/self.scale
            self.y += dy/self.scale
            self.redraw()
        if self.mouse_button != qtc.Qt.MouseButton.NoButton:
            self.mouse_stack.append([ev.pos().x(), ev.pos().y()])
        self.mouse_hover = ev.pos().x(), ev.pos().y()

    def home(self):
        self.scale = min(self.width()/(self.renderer.page.width or 1), self.height()/(self.renderer.page.height or 1))
        self.x = 0
        self.y = 0
        self.redraw()

    def mouseReleaseEvent(self, ev):
        self.mouse_button = qtc.Qt.MouseButton.NoButton

    def redraw(self, lh=True, rh=True):
        px = self.renderer.render(hex_to_rgb(self.pd["added_color"]),
                                  hex_to_rgb(self.pd["removed_color"]),
                                  hex_to_rgb(self.pd["highlighter_color"]),
                                  self.pd["highlighter_en"],
                                  1-self.pd["highlighter_sensitivity"]/100,
                                  self.pd["highlighter_size"],
                                  self.x,
                                  self.y,
                                  self.scale,
                                  self.theta,
                                  lh,
                                  rh,
                                  self.width(),
                                  self.height())
        self.setPixmap(qtg.QPixmap.fromImage(px))
        self.setMinimumSize(qtc.QSize(64, 64))

    def export(self, path):
        if self.renderer.page.lhs is not None or self.renderer.page.rhs is not None:
            im = self.renderer.render(hex_to_rgb(self.pd["added_color"]),
                                hex_to_rgb(self.pd["removed_color"]),
                                hex_to_rgb(self.pd["highlighter_color"]),
                                self.pd["highlighter_en"],
                                1 - self.pd["highlighter_sensitivity"] / 100,
                                self.pd["highlighter_size"])
            if path == ":clipboard:":
                cb = qtw.QApplication.clipboard()
                cb.clear(mode=cb.Mode.Clipboard)
                cb.setPixmap(qtg.QPixmap.fromImage(im), mode=cb.Mode.Clipboard)
            else:
                im.save(path)