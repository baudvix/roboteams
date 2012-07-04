#!/usr/bin/env python

import wx
import math
import random

import Queue
import threading

from wx.glcanvas import GLCanvas
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from mcc.model import map

APP_EXIT = 1


class Gui(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(Gui, self).__init__(*args, **kwargs)
        self.map_active_list = []
        self.trace_active_list = []
        self.initUI()

    def initUI(self):

        # --- Main ---
        self.SetSize((1280, 1024))
        self.SetTitle('MCC Monitor')
        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)

        # --- Menu ---
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        qmi = wx.MenuItem(file_menu, APP_EXIT, '&Quit\tCtrl+Q')
        file_menu.AppendItem(qmi)

        self.Bind(wx.EVT_MENU, self.on_quit, id=APP_EXIT)

        menu_bar.Append(file_menu, '&File')
        self.SetMenuBar(menu_bar)

        # --- Map Monitor Panel ---
        mm_panel = wx.Panel(self, -1)
        mm_hbox = wx.BoxSizer(wx.HORIZONTAL)

        #  -- Control Panel --
        c_panel = wx.Panel(mm_panel, -1)
        c_vbox = wx.BoxSizer(wx.VERTICAL)

        #   - Map List -
        self.map_list_box = wx.CheckListBox(c_panel, -1)
        self.map_list_box.ExtraStyle = wx.LB_MULTIPLE
        self.Bind(wx.EVT_CHECKLISTBOX, self.on_check_map)

        #   - Trace List -
        self.trace_list_box = wx.CheckListBox(c_panel, -1)
        self.trace_list_box.ExtraStyle = wx.LB_MULTIPLE
        self.Bind(wx.EVT_CHECKLISTBOX, self.on_check_trace)

        # -- arrange Control --
        c_vbox.Add(self.map_list_box, 1, wx.EXPAND | wx.ALL, 5)
        c_vbox.Add(self.trace_list_box, 1, wx.EXPAND | wx.ALL, 5)
        c_panel.SetSizer(c_vbox)

        #  -- opengl --
        self.canvas = WxGLCanvas(mm_panel)

        # --- arrange Map Monitor Panel ---
        mm_hbox.Add(c_panel, 0.3, wx.EXPAND | wx.LEFT, 20)
        #mm_hbox.Add(self.canvas, 1, wx.ALL, 10)
        mm_hbox.Add(self.canvas)
        mm_panel.SetSizer(mm_hbox)
        self.test()
        self.Show(True)

    def on_quit(self, e):
        self.Close()

    def on_check_map(self, e):
        cd = self.map_list_box.GetClientData(e.GetSelection())
        try:
            self.map_active_list.index(cd)
            self.map_active_list.remove(cd)
        except ValueError:
            self.map_active_list.append(cd)

    def on_check_trace(self, e):
        cd = self.trace_list_box.GetClientData(e.GetSelection())
        try:
            self.trace_active_list.index(cd)
            self.trace_active_list.remove(cd)
        except ValueError:
            self.trace_active_list.append(cd)

    def fake_register_map(self, title, client_data):
        self.map_list_box.Insert(title, 0, client_data)

    def fake_register_trace(self, title, client_data):
        self.trace_list_box.Insert(title, 0, client_data)

    def register_map(self, new_map):
        self.map_list_box.Insert(new_map.name, new_map)

    def register_trace(self, new_trace, title):
        self.trace_list_box.Insert(title, new_trace)

    def notify_map_change(self, redraw=False):
        if redraw:
            self.canvas.map_generate(self.map_active_list)

    def notify_trace_change(self, redraw=False):
        if redraw:
            pass

    def test(self):
        self.fake_register_map("BERLIN", 0)
        self.fake_register_map("NEW YORK", 1)
        self.fake_register_map("FRANKFURT", 2)
        self.fake_register_map("TOKYO", 3)
        self.fake_register_map("LISBON", 4)
        self.fake_register_trace("BREMEN", 0)
        self.fake_register_trace("MIAMI", 1)
        self.fake_register_trace("DUBAI", 2)
        self.fake_register_trace("BANGKOK", 3)
        self.fake_register_trace("SEVILLE", 4)


class WxGLCanvas(GLCanvas):

    def __init__(self, parent):
        GLCanvas.__init__(self, parent, -1,
            attribList=(wx.glcanvas.WX_GL_RGBA,
                wx.glcanvas.WX_GL_DOUBLEBUFFER,
                wx.glcanvas.WX_GL_DEPTH_SIZE, 24))
        wx.EVT_PAINT(self, self.on_draw)
        wx.EVT_SIZE(self, self.on_size)
        wx.EVT_WINDOW_DESTROY(self, self.on_destroy)
        self.SetSize((980, 980))

        self._map_draw = map.MapModel('drawable map')
        self._unit = 0.0125
        self._map_correction = (0, 0)

        self._zoom_factor = 0.5

        self._to_draw_squares = Queue.Queue()
        self.map_color = [(0.0549, 0.3608, 0.0196),
                          (0.102, 0.4471, 0.0431),
                          (0.149, 0.5098, 0.0588),
                          (0.1922, 0.5725, 0.0784),
                          (0.4275, 0.6275, 0.1176),
                          (0.6588, 0.6863, 0.1529),
                          (0.8824, 0.7372, 0.1804),
                          (0.9255, 0.6471, 0.1804),
                          (0.9373, 0.5255, 0.1569),
                          (0.9451, 0.4039, 0.1490),
                          (0.9490, 0.2863, 0.1333),
                          (0.9255, 0.2431, 0.1333),
                          (0.8824, 0.251, 0.1373)]

    #PROPERTY --- unit
    def fget_unit(self):
        """The unit property getter"""
        return self._unit

    def fset_unit(self, value):
        """The unit property setter"""
        self._unit = value
    unit = property(fget_unit, fset_unit)

    #PROPERTY --- zoom_factor
    def fget_zoom_factor(self):
        """The zoom_factor property getter"""
        return self._zoom_factor

    def fset_zoom_factor(self, value):
        """The zoom_factor property setter"""
        self._zoom_factor = value
    zoom_factor = property(fget_zoom_factor, fset_zoom_factor)

    def update_points(self, points):
        self._map_draw.increase_points(points)
        self.map_propotional()
        if self._map_draw.need_redraw:
            self.calc_draw_value()
            self.draw_map()
        else:
            for p in points:
                x, y = p
                cx, cy = self._map_correction
                dx -= cx
                dy -= cy
                self._to_draw_squares.put(self.calc_color(
                    [dx, dy,
                     dx + 1,
                     dy + 1,
                     self._map_draw.get_point(x, y)],
                    self._map_draw.max_free_count))

    def map_propotional(self):
        t, r, b, l = self._map_draw.expand
        while (t + b) < (r + l):
            self._map_draw.expand_map(2)
            b += 1
        while (r + l) < (t + b):
            self._map_draw.expand_map(1)
            r += 1

    def map_generate(self, active_map):
        self._map_draw = map.MapModel("map_draw")
        t_expand = [0, 0, 0, 0]
        for m in active_map:
            for i in range(0, 4):
                if t_expand[i] < active_map.expand[i]:
                    t_expand[i] = active_map.expand[i]
        t, r, b, l = t_expand
        for x in range(l * -100, r * 100):
            for y in range(b * -100, t * 100):
                v = 0
                for m in active_map:
                    v += m.get_point(x, y)
                self._map_draw = v
        self.draw_map()

    def calc_draw_value(self):
        t, r, b, l = self._map_draw.expand
        self.unit = 2.0 / ((r + l) * 100)

        cx = (((r + l) / 2) - l) * -1
        cy = (((t + b) / 2) - t) * -1

        self._map_correction(cx, cy)

    def draw_map(self):
        squares = []
        t, r, b, l = self._map_draw.expand
        cx, cy = self._map_correction
        cx *= 100
        cy *= 100
        for x in range(l * -100, r * 100):
            for y in range(b * -100, t * 100):
                value = self._map_draw.get_point(x, y)
                if not value == 0:
                    squares.append([(x - cx) * self.unit,
                                    (y - cy) * self.unit,
                                    (x + 1 - cx) * self.unit,
                                    (y + 1 - cy) * self.unit, value])
        squares = self.calc_color(squares, self._map_draw.max_free_count)
        for s in squares:
            self._to_draw_squares.put(s)

    def draw_lines(self, lines):
        glBegin(GL_LINES)
        for line in lines:
            self._draw_line(line[0], line[1], line[2], line[3], line[4])
        glEnd()

    def _draw_line(self, x1, y1, x2, y2, color):
        r, g, b = color
        glColor3f(r, g, b)
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)

    def draw_triangles(self, traingles):
        glBegin(GL_TRIANGLES)
        for triangle in traingles:
            self._draw_triangle(traingle[0], triangle[1], triangle[2])
        glEnd()

    def _draw_triangle(self, x, y, color):
        r, g, b = color
        size = self._zoom_factor * self._unit
        glColor3f(r, g, b)
        glVertex3f(x, y + size, 0)
        glVertex3f(x + size, y - size, 0)
        glVertex3f(x - size, y - size, 0)

    def draw_circles(self, circles):
        glBegin(GL_TRIANGLE_FAN)
        for circle in circles:
            self._draw_circle(circles[0], circles[1], circles[2], circles[3])
        glEnd()

    def _draw_circle(self, x, y, r, color):
        r, g, b = color
        glColor3f(r, g, b)
        angle = 0
        while(angle < 360):
            glVertex2f(x + math.sin(angle) * r, y + math.cos(angle) * r)
            angle = angle + 1
        glEnd()

    def draw_squares(self, squares):
        glBegin(GL_QUADS)
        for square in squares:
            self._draw_square(square[0], square[1], square[2], square[3], square[4])
        glEnd()

    def _draw_square(self, x1, y1, x2, y2, color):
        r, g, b = color
        glColor3f(r, g, b)
        glVertex3f(x1, y1, 0)
        glVertex3f(x1, y2, 0)
        glVertex3f(x2, y2, 0)
        glVertex3f(x2, y1, 0)

    def calc_color(self, squares, max_value):
        for square in squares:
            square[4] = self.map_color[int((square[4] / max_value) * 11)]
        self.draw_squares(squares)

    def on_draw(self, event):
        print 'on_draw'
        self.SetCurrent()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # tmp_squares = self.map_color_example()
        # self.draw_squares(tmp_squares)
        # self.draw_triangle(0, 0, (1, 1, 1))

        # test_squares = self.map_random_squares()
        # self.draw_squares(test_squares)
        squares = []
        while not self._to_draw_squares.empty:
            squares.append(self._to_draw_squares.get())
        self.draw_squares(squares)

        self.SwapBuffers()
        return

    def map_color_example(self):
        squares = []
        length = 2.0 / 12
        y1, y2 = (-1, 1)
        for c in range(0, 12):
            squares.append([(c * length) - 1, y1, ((c + 1) * length) - 1, y2, self.map_color[c]])
        return squares

    def map_random_squares(self):
        squares = []
        steps = int(2.0 / self._unit)
        for x in range(0, steps):
            for y in range(0, steps):
                c = random.randint(0, 11)
                sx = (x * self._unit) - 1
                sy = (y * self._unit) - 1
                squares.append([sx, sy, sx + self._unit, sy + self._unit, self.map_color[c]])
        return squares

    def on_size(self, event):
        pass

    def on_destroy(self, event):
        print "Destroying Window"


class ViewMng():

    def __init__(self):
        pass

    def run(self):
        print 'run'
        self.app = wx.App()
        self.gui = Gui(None, -1)
        self.app.MainLoop()
        t = threading.Thread(target=self.app.MainLoop)
        t.setDaemon(1)
        t.start()

if __name__ == '__main__':
    vm = ViewMng()
    vm.run()
