import random
import time

from PIL import Image
from PyQt6 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc

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
        self.ctx = moderngl.create_standalone_context()
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
        self.vao_diff.program["uTheta"] = theta
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
    def __init__(self):
        super().__init__()
        self.ctx = moderngl.create_standalone_context()
        self.prog = self.ctx.program(
            vertex_shader=DIFF_VERT,
            fragment_shader=DIFF_FRAG,
        )
        self.fbo:moderngl.Framebuffer = self.ctx.simple_framebuffer((self.width(), self.height()))
        self.i = 0
        self.lt = time.time()
        self.x = 0
        self.setFocusPolicy(qtc.Qt.FocusPolicy.StrongFocus)
        self.y = 0

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.fbo = self.ctx.simple_framebuffer((self.width(), self.height()))
        self.redraw()

    def keyPressEvent(self, ev):
        print('event')
        if ev.key() == qtc.Qt.Key.Key_Space:
            self.x = random.random()
            self.y = random.random()
            print(self.x, self.y)
            self.redraw()

    def redraw(self):
        ...


if __name__ == "__main__":
    doc_lhs = FitzDoc("lhs", r"C:\Users\caleb\Documents\lhs.pdf")
    doc_rhs = FitzDoc("rhs", r"C:\Users\caleb\Documents\rhs.pdf")

    page = RenderPage()
    page.lhs = doc_lhs.page(0, 72)
    page.rhs = doc_rhs.page(0, 72)

    renderer = Renderer()
    renderer.set_page(page)
    im = renderer.render(0, 0, 1, 0, 640, 480)
    im.save("out.png")
    import webbrowser
    webbrowser.open("out.png")
