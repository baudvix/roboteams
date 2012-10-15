#!/usr/bin/env python

import pprint

import wx
import math
import time

import Queue
import threading
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
        self._new_maps = Queue.Queue()
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
        self.draw_mng = DrawMng()
        self.draw_mng.start()
        self.canvas = WxGLCanvas(mm_panel, self.draw_mng)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._update_map, self.timer)

        # --- arrange Map Monitor Panel ---
        mm_hbox.Add(c_panel, 1, wx.EXPAND | wx.LEFT, 10)
        #mm_hbox.Add(self.canvas, 1, wx.ALL, 10)
        mm_hbox.Add(self.canvas)
        mm_panel.SetSizer(mm_hbox)

        self.Show(True)
        self.test()
        self.timer.Start(100)

    def on_quit(self, e):
        self.Close()

    def on_check(self, e):
        eid = e.GetId()
        sel = e.GetSelection()
        print(sel)
        if eid == MAP_CHECKLIST:
            cd = self.map_list_box.GetClientData(sel)
            try:
                self.map_active_list.index(cd)
                print("remove")
                self.map_active_list.remove(cd)
            except ValueError:
                print("add")
                self.map_active_list.append(cd)
            self.draw_mng.active_maps = self.get_active_maps()
            self.draw_mng.flag_redraw = True
            self.canvas.flush()
        else:
            cd = self.trace_list_box.GetClientData(sel)
            try:
                self.trace_active_list.index(cd)
                self.trace_active_list.remove(cd)
            except ValueError:
                self.trace_active_list.append(cd)

    def _fake_register_map(self, title, client_data):
        self.map_list_box.Insert(title, 0, client_data)

    def _fake_register_trace(self, title, client_data):
        self.trace_list_box.Insert(title, 0, client_data)

    def dummy_register_map(self, new_map):
        wx.CallAfter(self.register_map, new_map)

    def register_map(self, new_map):
        id = self.map_id
        self.map_id += 1
        self.map_list_box.Insert(new_map.name, 0, id)
        self._maps.append({'id': id, 'map': new_map})

    def get_active_maps(self):
        m_list = []
        print("exec")
        for id_map in self.map_active_list:
            for a_map in self._maps:
                if a_map['id'] == id_map:
                    m_list.append(a_map['map'])
        return m_list

    def register_trace(self, new_trace, title):
        self.trace_list_box.Insert(title, new_trace)

    def _update_map(self, event):
        self.canvas.update()

    def test(self):
        self._fake_register_map("BERLIN", 0)
        self._fake_register_map("NEW YORK", 1)
        self._fake_register_map("FRANKFURT", 2)
        self._fake_register_map("TOKYO", 3)
        self._fake_register_map("LISBON", 4)
        self._fake_register_trace("BREMEN", 0)
        self._fake_register_trace("MIAMI", 1)
        self._fake_register_trace("DUBAI", 2)
        self._fake_register_trace("BANGKOK", 3)
        self._fake_register_trace("SEVILLE", 4)


class DrawColor():

    def __init__(self):
        self.map_color = [(0.1843, 0.549, 0),
                          (1, 0.549, 0),
                          (0.5843, 0, 0)]

    def calc_simple_color(self, value):
        if value >= 5:
            return self.map_color[0]
        if value >= 2:
            return self.map_color[1]
        else:
            return self.map_color[2]


class DrawMng(threading.Thread):

    def __init__(self):
        self._active_maps = []
        self._map_draw = map.MapModel('drawable map')
        self._map_draw.expand = [3, 3, 3, 3]
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
        self.max_new = True
        self.max_ex = 3
        self._flag_flush = False

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

    #PROPERTY --- flag_flush
    def fget_flag_flush(self):
        """The flag_flush property getter"""
        with self._lock:
            return self._flag_flush

    def fset_flag_flush(self, value):
        """The flag_flush property setter"""
        with self._lock:
            self._flag_flush = value
    flag_flush = property(fget_flag_flush, fset_flag_flush)

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

    def run(self):
        while not self._exit_flag:
            if self.flag_redraw:
                self.map_generate()
                self.calc_draw_value()
                self.calc_map()
                with self._lock:
                    self.flag_redraw = False
                continue
            for m in self._active_maps:
                if m.flag_redraw == True:
                    tt, rr, bb, ll = m.expand
                    self.max_new = False
                    if tt > self.max_ex:
                        self.max_ex = tt
                        self.max_new = True
                    if rr > self.max_ex:
                        self.max_ex = rr
                        self.max_new = True
                    if  bb > self.max_ex:
                        self.max_ex = bb
                        self.max_new = True
                    if ll > self.max_ex:
                        self.max_ex = ll
                        self.max_new = True
                    m.flag_redraw = False
            # if redraw:
                # self.map_generate()
                # self.calc_draw_value()
                # self.calc_map()
                # with self._lock:
                #     self.flag_redraw = False
                #     self._flag_flush = True
            update_map = False
            for m in self._active_maps:
                if m.flag_update == True:
                    update_map = True
                    m.flag_update = False
            if update_map:
                points = []
                for m in self._active_maps:
                    points.extend(m.latest_update)
                    m.latest_update = []
                self.update_points(points)

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

    def map_generate(self):
        self._map_draw = map.MapModel("map_draw")
        t_expand = [0, 0, 0, 0]
        for m in self.active_maps:
            m.latest_update = []
            for i in xrange(0, 4):
                if t_expand[i] < m.expand[i]:
                    t_expand[i] = m.expand[i]
        t, r, b, l = t_expand
        for x in xrange(l * -100, r * 100):
            for y in xrange(b * -100, t * 100):
                v = 0
                for m in self.active_maps:
                    v += m.get_point(x, y)
                self._map_draw.set_point(x, y, v)
        self.calc_draw_value()

    def calc_map(self):
        self._to_draw_squares = Queue.Queue()
        t, r, b, l = self._map_draw.expand
        for x in xrange(l * -100, r * 100):
            for y in xrange(b * -100, t * 100):
                value = self._map_draw.get_point(x, y)
                if not value == 0:
                    new_ele = self.calc_square(x, y, value)
                    self._to_draw_squares.put(new_ele)

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
        return
        t, r, b, l = self._map_draw.expand
        if (r + l) > (t + b):
            self._unit = 2.0 / ((r + l) * 100)
        else:
            self._unit = 2.0 / ((t + b) * 100)

        cx = (((r + l) / 2) - l) * -1
        cy = (((t + b) / 2) - t) * -1

        self._map_correction = (cx, cy)


class WxGLCanvas(GLCanvas):

    def __init__(self, parent, drwmng):
        GLCanvas.__init__(self, parent, -1,
            attribList=(wx.glcanvas.WX_GL_RGBA,
                wx.glcanvas.WX_GL_DOUBLEBUFFER,
                wx.glcanvas.WX_GL_DEPTH_SIZE, 24))

        wx.EVT_PAINT(self, self.on_draw)
        wx.EVT_SIZE(self, self.on_size)
        wx.EVT_WINDOW_DESTROY(self, self.on_destroy)
        wx.EVT_LEFT_UP(self, self.on_mouse)

        self.SetSize((500, 500))
        self.drwmng = drwmng

        self._redraw = False

        self._flag_flush = False
        self._exit_flag = False
        self._lock = threading.Lock()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(-1, 1, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

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

    def update(self):
        if not self._exit_flag:
            if self.drwmng.max_new:
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                ex = self.drwmng.max_ex
                gluOrtho2D(-ex, ex, -ex, ex)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
            if self._flag_flush or self.drwmng.flag_flush:
                self.SetCurrent()
                glLoadIdentity()
                self.clear_canvas()
                self.SwapBuffers()
                self.drwmng.flag_flush = False
                with self._lock:
                    self._flag_flush = False
                return
            if self._redraw:
                self._redraw = False
                self.drwmng.flag_redraw = True
                self.flush()
                return
            action = False
            sqa = []
            for _ in xrange(0, 100):
                if self.drwmng._to_draw_squares.empty():
                    break
                sqa.append(self.drwmng._to_draw_squares.get())
                action = True
            if action:
                self.SetCurrent()
                glLoadIdentity()
                self._draw_squares(sqa)
                # self._draw_triangles(tri)
                # self._draw_circles(cir)
                # self._draw_lines(lin)
                self.SwapBuffers()

    def flush(self):
        with self._lock:
            self._flag_flush = True

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
        self.clear_canvas()
        if self.drwmng.max_new:
            glMatrixMode(GL_PROJECTION)
            ex = self.drwmng.max_ex
            gluOrtho2D(-ex, ex, -ex, ex)
            glMatrixMode(GL_MODELVIEW)
        self.SwapBuffers()

    def on_size(self, event):
        pass

    def on_destroy(self, event):
        print "Destroying Window"

    def on_mouse(self, event):
        self.SetCurrent()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(-2, 2, -2, 2)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.SwapBuffers()
        print "click"


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
