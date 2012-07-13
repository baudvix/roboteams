#!/usr/bin/env python

import wx
import math
import random
import pprint

import Queue
import threading
import time

from wx.glcanvas import GLCanvas
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from mcc.model import map

APP_EXIT = 1
MAP_CHECKLIST = wx.NewId()
TRACE_CHECKLIST = wx.NewId()


class Gui(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(Gui, self).__init__(*args, **kwargs)
        self.map_active_list = []
        self.trace_active_list = []
        self.map_id = 0
        self.trace_id = 0
        self._maps = []
        self._traces = []
        self.initUI()

    def initUI(self):

        # --- Main ---
        self.SetSize((682, 527))
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
        self.map_list_box = wx.CheckListBox(c_panel, MAP_CHECKLIST)
        self.map_list_box.ExtraStyle = wx.LB_MULTIPLE
        self.Bind(wx.EVT_CHECKLISTBOX, self.on_check, id=MAP_CHECKLIST)

        #   - Trace List -
        self.trace_list_box = wx.CheckListBox(c_panel, TRACE_CHECKLIST)
        self.trace_list_box.ExtraStyle = wx.LB_MULTIPLE
        self.Bind(wx.EVT_CHECKLISTBOX, self.on_check, id=TRACE_CHECKLIST)

        # -- arrange Control --
        c_vbox.Add(self.map_list_box, 1, wx.EXPAND | wx.ALL, 5)
        c_vbox.Add(self.trace_list_box, 1, wx.EXPAND | wx.ALL, 5)
        c_panel.SetSizer(c_vbox)

        #  -- opengl --
        self.canvas = WxGLCanvas(mm_panel)
        self.draw_mng = DrawMng(self.canvas)
        self.canvas.start()
        self.draw_mng.start()

        # --- arrange Map Monitor Panel ---
        mm_hbox.Add(c_panel, 1, wx.EXPAND | wx.LEFT, 10)
        #mm_hbox.Add(self.canvas, 1, wx.ALL, 10)
        mm_hbox.Add(self.canvas)
        mm_panel.SetSizer(mm_hbox)

        self.Show(True)

    def on_quit(self, e):
        self.Close()

    def on_check(self, e):
        eid = e.GetId()
        sel = e.GetSelection()

        if eid == MAP_CHECKLIST:
            cd = self.map_list_box.GetClientData(sel)
            try:
                self.map_active_list.index(cd)
                self.map_active_list.remove(cd)
            except ValueError:
                self.map_active_list.append(cd)
            self.draw_mng.active_maps = self.get_active_maps()
            self.draw_mng.flag_redraw = True
        else:
            cd = self.trace_list_box.GetClientData(sel)
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
        id = self.map_id
        self.map_id += 1
        self.map_list_box.Insert(new_map.name, 0, id)
        self._maps.append({'id': id, 'map': new_map})

    def get_active_maps(self):
        m_list = []
        for id_map in self.map_active_list:
            for a_map in self._maps:
                if a_map['id'] == id_map:
                    m_list.append(a_map['map'])
        return m_list

    def register_trace(self, new_trace, title):
        self.trace_list_box.Insert(title, new_trace)

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


class DrawColor():

    def __init__(self):
        self._max_value = 0
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

    def calc_color(self, squares):
        for square in squares:
            if self._max_value < square[4]:
                self._max_value = square[4]
            square[4] = self.map_color[int((square[4] / self._max_value) * 11)]
        return squares

    def calc_simple_color(self, value):
        if value >= 5:
            return self.map_color[0]
        if value >= 2:
            return self.map_color[5]
        else:
            return self.map_color[11]


class DrawMng(threading.Thread):

    def __init__(self, canvas):
        self._canvas = canvas

        self._active_maps = []
        self._map_draw = map.MapModel('drawable map')
        self._map_draw.expand = [1, 1, 0, 0]
        self._colors = DrawColor()

        self._unit = 0.0125
        self._map_correction = (0, 0)
        self._zoom_factor = 0.5

        self._exit_flag = False
        self._lock = threading.Lock()
        threading.Thread.__init__(self)

        self._to_draw_squares = Queue.Queue()

        self.calc_draw_value()

        self.flag_redraw = False

    #PROPERTY --- exit_flag
    def fget_exit_flag(self):
        """The exit_flag property getter"""
        with self._lock:
            return self._exit_flag

    def fset_exit_flag(self, value):
        """The exit_flag property setter"""
        with self._lock:
            self._exit_flag = value
            self._canvas.exit_flag = value
    exit_flag = property(fget_exit_flag, fset_exit_flag)

    #PROPERTY --- active_maps
    def fget_active_maps(self):
        """The active_maps property getter"""
        with self._lock:
            return self._active_maps

    def fset_active_maps(self, value):
        """The active_maps property setter"""
        with self._lock:
            self._active_maps = value
            self.flag_redraw = True
    active_maps = property(fget_active_maps, fset_active_maps)

    def update_canvas(self):
        while not self._to_draw_squares.empty():
            self._canvas.squares.put(self._to_draw_squares.get())

    def run(self):
        while not self._exit_flag:
            if self.flag_redraw:
                self._canvas.flush()
                self.map_generate()
                self.calc_draw_value()
                self.calc_map()
                self.update_canvas()
                with self._lock:
                    self.flag_redraw = False
                continue
            t, r, b, l = self._map_draw.expand
            redraw = False
            for m in self._active_maps:
                if m.flag_redraw == True:
                    tt, rr, bb, ll = m.expand
                    if tt > t or rr > r or bb > b or ll > l:
                        redraw = True
                    m.flag_redraw = False
            if redraw:
                self._canvas.flush()
                self.map_generate()
                self.calc_draw_value()
                self.calc_map()
                self.update_canvas()
                with self._lock:
                    self.flag_redraw = False
            update = False
            for m in self._active_maps:
                if m.flag_update == True:
                    update = True
                    m.flag_update = False
            if update:
                points = []
                for m in self._active_maps:
                    points.extend(m.latest_update)
                    m.latest_update = []
                self.update_points(points)
            time.sleep(0.1)

    def update_points(self, points):
        self._map_draw.increase_points(points)
        self._map_draw.latest_update = []
        if self._map_draw.flag_redraw:
            self.calc_draw_value()
            self.calc_map()
            self._map_draw.flag_redraw = False
        else:
            for p in points:
                x, y = p
                new_ele = self.calc_square(x, y, self._map_draw.get_point(x, y))
                self._to_draw_squares.put(new_ele)
        self.update_canvas()

    def map_generate(self):
        self._map_draw = map.MapModel("map_draw")
        t_expand = [0, 0, 0, 0]
        for m in self.active_maps:
            m.latest_update = []
            for i in range(0, 4):
                if t_expand[i] < m.expand[i]:
                    t_expand[i] = m.expand[i]
        t, r, b, l = t_expand
        for x in range(l * -100, r * 100):
            for y in range(b * -100, t * 100):
                v = 0
                for m in self.active_maps:
                    v += m.get_point(x, y)
                self._map_draw.set_point(x, y, v)
        self.calc_draw_value()

    def calc_map(self):
        self._to_draw_squares = Queue.Queue()
        t, r, b, l = self._map_draw.expand
        for x in range(l * -100, r * 100):
            for y in range(b * -100, t * 100):
                value = self._map_draw.get_point(x, y)
                if not value == 0:
                    new_ele = self.calc_square(x, y, value)
                    self._to_draw_squares.put(new_ele)
        self.update_canvas()

    def calc_square(self, x, y, val):
        cx, cy = self._map_correction
        #cx, cy = (self._map_correction) * 100
        x1 = (x - cx) * self._unit - 1
        y1 = (y - cy) * self._unit - 1
        x2 = (x + 1 - cx) * self._unit - 1
        y2 = (y + 1 - cy) * self._unit - 1
        c = self._colors.calc_simple_color(val)
        return [x1, y1, x2, y2, c]

    def calc_draw_value(self):
        t, r, b, l = self._map_draw.expand
        if (r + l) > (t + b):
            self._unit = 2.0 / ((r + l) * 100)
        else:
            self._unit = 2.0 / ((t + b) * 100)

        cx = (((r + l) / 2) - l) * -1
        cy = (((t + b) / 2) - t) * -1

        self._map_correction = (cx, cy)


class WxGLCanvas(GLCanvas, threading.Thread):

    def __init__(self, parent):
        GLCanvas.__init__(self, parent, -1,
            attribList=(wx.glcanvas.WX_GL_RGBA,
                wx.glcanvas.WX_GL_DOUBLEBUFFER,
                wx.glcanvas.WX_GL_DEPTH_SIZE, 24))

        wx.EVT_PAINT(self, self.on_draw)
        wx.EVT_SIZE(self, self.on_size)
        wx.EVT_WINDOW_DESTROY(self, self.on_destroy)

        self.SetSize((500, 500))
        self.squares = Queue.Queue()
        self.triangles = Queue.Queue()
        self.circles = Queue.Queue()
        self.lines = Queue.Queue()

        self._redraw = False

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
        self._exit_flag = False
        self._lock = threading.Lock()
        threading.Thread.__init__(self)

    #PROPERTY --- exit_flag
    def fget_exit_flag(self):
        """The exit_flag property getter"""
        with self._lock:
            return self._exit_flag

    def fset_exit_flag(self, value):
        """The exit_flag property setter"""
        with self._lock:
            self._exit_flag = value
    exit_flag = property(fget_exit_flag, fset_exit_flag)

    def run(self):
        while not self._exit_flag:
            if self._redraw:
                self._redraw = False
            action = False
            sqa = []
            while not self.squares.empty():
                sqa.append(self.squares.get())
                action = True
            tri = []
            while not self.triangles.empty():
                tri.append(self.triangles.get())
                action = True
            cir = []
            while not self.circles.empty():
                cir.append(self.circles.get())
                action = True
            lin = []
            while not self.lines.empty():
                lin.append(self.lines.get())
                action = True
            if action:
                self.SetCurrent()
                glLoadIdentity()
                self._draw_squares(sqa)
                self._draw_triangles(tri)
                self._draw_circles(cir)
                self._draw_lines(lin)
                self.SwapBuffers()
            time.sleep(0.1)

    def flush(self):
        self.squares = Queue.Queue()
        self.triangles = Queue.Queue()
        self.circles = Queue.Queue()
        self.lines = Queue.Queue()
        self.SetCurrent()
        glLoadIdentity()
        self.clear_canvas()
        self.SwapBuffers()

    def clear_canvas(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def _draw_lines(self, lines):
        glBegin(GL_LINES)
        for line in lines:
            self._draw_line(line[0], line[1], line[2], line[3], line[4])
        glEnd()

    def _draw_line(self, x1, y1, x2, y2, color):
        r, g, b = color
        glColor3f(r, g, b)
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)

    def _draw_triangles(self, traingles):
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

    def _draw_circles(self, circles):
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

    def _draw_squares(self, squares):
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

    def on_draw(self, event):
        self._redraw = True
        self.SetCurrent()
        glLoadIdentity()
        self.clear_canvas()
        self.SwapBuffers()

    def example_map_color(self):
        squares = []
        length = 2.0 / 12
        y1, y2 = (-1, 1)
        for c in range(0, 12):
            squares.append([(c * length) - 1, y1, ((c + 1) * length) - 1, y2, self.map_color[c]])
        return squares

    def on_size(self, event):
        pass

    def on_destroy(self, event):
        print "Destroying Window"


class ViewMng():

    def __init__(self):
        pass

    def run(self):
        #print 'run'
        self.app = wx.App()
        self.gui = Gui(None, -1)
        t = threading.Thread(target=self.app.MainLoop)
        #t.setDaemon(1)
        t.start()

if __name__ == '__main__':
    vm = ViewMng()
    vm.run()
