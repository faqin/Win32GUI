import time
import ctypes
from ctypes import wintypes
import win32api
import win32con
import win32gui

'''
ref:
    https://gist.github.com/mouseroot/6128651
    http://www.christophekeller.com/hello-world-in-python-using-win32/
    https://stackoverflow.com/questions/5353883/python3-ctype-createwindowex-simple-example
    http://code.activestate.com/recipes/208699-calling-windows-api-using-ctypes-and-win32con/
    https://riptutorial.com/winapi/example/13881/create-a-new-thread
    https://stackoverflow.com/questions/50576770/python-ctype-windll-kernel32-createthread-parameter-value
    https://blog.csdn.net/tangaowen/article/details/6054123
'''

GetMessageA = ctypes.windll.user32.GetMessageA
GetMessageW = ctypes.windll.user32.GetMessageW
GetModuleHandleA = ctypes.windll.kernel32.GetModuleHandleA
GetModuleHandleW = ctypes.windll.kernel32.GetModuleHandleW
CreateWindowExA = ctypes.windll.user32.CreateWindowExA
CreateWindowExW = ctypes.windll.user32.CreateWindowExW
RegisterClassExA = ctypes.windll.user32.RegisterClassExA
RegisterClassExW = ctypes.windll.user32.RegisterClassExW
DispatchMessageA = ctypes.windll.user32.DispatchMessageA
DispatchMessageW = ctypes.windll.user32.DispatchMessageW

CreateThread = ctypes.windll.kernel32.CreateThread
SetLayeredWindowAttributes = ctypes.windll.user32.SetLayeredWindowAttributes

LPTHREAD_START_ROUTINE = ctypes.WINFUNCTYPE(ctypes.wintypes.DWORD, ctypes.wintypes.LPVOID)
WNDPROCTYPE = ctypes.WINFUNCTYPE(ctypes.c_int, wintypes.HWND, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM)

class WNDCLASSEX(ctypes.Structure): # tagWNDCLASSEXA
    _fields_ = [("cbSize"       , ctypes.c_uint),
                ("style"        , ctypes.c_uint),
                ("lpfnWndProc"  , WNDPROCTYPE),
                ("cbClsExtra"   , ctypes.c_int),
                ("cbWndExtra"   , ctypes.c_int),
                ("hInstance"    , wintypes.HANDLE),
                ("hIcon"        , wintypes.HICON),
                ("hCursor"      , wintypes.HANDLE),
                ("hbrBackground", wintypes.HBRUSH),
                ("lpszMenuName" , wintypes.LPCWSTR),
                ("lpszClassName", wintypes.LPCWSTR),
                ("hIconSm"      , wintypes.HICON),]

class Win32Gui(object):
    def __init__(self, Ex=True, Unicode = True):
        self.Ex = Ex
        if self.Ex:
            if Unicode:
                self.GetMessage = GetMessageW
                self.CreateWindowEx = CreateWindowExW
                self.RegisterClassEx = RegisterClassExW
                self.GetModuleHandle = GetModuleHandleW
                self.DispatchMessage = DispatchMessageW
            else:
                self.GetMessage = GetMessageA
                self.CreateWindowEx = CreateWindowExA
                self.RegisterClassEx = RegisterClassExA
                self.GetModuleHandle = GetModuleHandleA
                self.DispatchMessage = DispatchMessageA
        else:
            self.GetMessage = GetMessageW
            self.CreateWindowEx = CreateWindowExW
            self.RegisterClassEx = RegisterClassExW
            self.GetModuleHandle = GetModuleHandleW
            self.DispatchMessage = DispatchMessageW
        pass

    def RGB(self, r=0, g=0, b=0):
        rgb = 0xff & (int(r) | int(g) << 8 | int(b) << 16)
        return rgb

    def GetLTRB(self, titlename):
        hwnd = win32gui.FindWindow(0, titlename)
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        return left, top, right, bottom

    def GetDesktopHW(self):
        w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        return h, w

    def GetModuleHandleX(self):
        if self.Ex:
            hInstance = self.GetModuleHandle(0)
        else:
            hInstance = win32api.GetModuleHandle()
        return hInstance

    def GetWndClassEx(self, hInstance, WndProc, szWindowClass='DesktopApp', Transparent=True):
        WndClassEx                   = WNDCLASSEX()
        WndClassEx.cbSize            = ctypes.sizeof(WNDCLASSEX)
        WndClassEx.style             = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        WndClassEx.lpfnWndProc       = WNDPROCTYPE(WndProc)
        WndClassEx.cbClsExtra        = 0
        WndClassEx.cbWndExtra        = 0
        WndClassEx.hInstance         = hInstance
        WndClassEx.hIcon             = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        WndClassEx.hCursor           = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        if Transparent:
            WndClassEx.hbrBackground = self.RGB(0,0,0)
        else:
            WndClassEx.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
        WndClassEx.lpszMenuName      = None
        WndClassEx.lpszClassName     = szWindowClass
        WndClassEx.hIconSm           = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        return WndClassEx

    def GetWndClasss(self, hInstance, WndProc, szWindowClass='DesktopApp', Transparent=True):
        WndClass                = win32gui.WNDCLASS()
        WndClass.style          = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        WndClass.lpfnWndProc    = WndProc
        WndClass.hInstance      = hInstance
        WndClass.hIcon          = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        WndClass.hCursor        = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        if Transparent:
            WndClass.hbrBackground = self.RGB(0,0,0)
        else:
            WndClass.hbrBackground  = win32gui.GetStockObject(win32con.WHITE_BRUSH)
        WndClass.lpszClassName  = szWindowClass
        return WndClass

    def GetWndClassX(self, hInstance, WndProc, szWindowClass='DesktopApp', Transparent=True):
        if self.Ex:
            WndClass = self.GetWndClassEx(hInstance, WndProc, szWindowClass, Transparent=Transparent)
        else:
            WndClass = self.GetWndClasss(hInstance, WndProc, szWindowClass, Transparent=Transparent)
        return WndClass

    def RegisterClassX(self, WndClass):
        try:
            if self.Ex:
                WndClassAtom = self.RegisterClassEx(ctypes.byref(WndClass))
            else:
                WndClassAtom = win32gui.RegisterClass(WndClass)
        except Exception as e:
            WndClassAtom = None
            print(e)
            raise e
        return WndClassAtom

    def CreateWindowX(self, WndClass, WinGuiClassAtom, szTitle, Transparent=True):
        hight, width = self.GetDesktopHW()
        if self.Ex:
            if Transparent:
                # hWindow = self.CreateWindowEx(
                #     win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED,
                #     WndClass.lpszClassName,
                #     szTitle,
                #     win32con.WS_POPUP,
                #     0,
                #     0,
                #     width,
                #     hight,
                #     0,
                #     0,
                #     WndClass.hInstance,
                #     None)
                hWindow = self.CreateWindowEx(
                    win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED,
                    WndClass.lpszClassName,
                    szTitle,
                    win32con.WS_POPUP,
                    0,
                    0,
                    width,
                    hight,
                    0,
                    0,
                    WndClass.hInstance,
                    None)
            else:
                hWindow = self.CreateWindowEx(
                    win32con.WS_EX_TOPMOST,
                    WndClass.lpszClassName,
                    szTitle,
                    win32con.WS_OVERLAPPEDWINDOW, # win32con.WS_OVERLAPPEDWINDOW | win32con.WS_CAPTION
                    0,
                    0,
                    width,
                    hight,
                    0,
                    0,
                    WndClass.hInstance,
                    None)
        else:
            if Transparent:
                hWindow = win32gui.CreateWindow(
                    WinGuiClassAtom,                   #it seems message dispatching only works with the atom, not the class name
                    szTitle,
                    win32con.WS_OVERLAPPEDWINDOW,
                    0,
                    0,
                    width,
                    hight,
                    0,
                    0,
                    WndClass.hInstance,
                    None)
            else:
                hWindow = win32gui.CreateWindow(
                    WinGuiClassAtom,                   #it seems message dispatching only works with the atom, not the class name
                    szTitle,
                    win32con.WS_OVERLAPPEDWINDOW,
                    win32con.CW_USEDEFAULT,
                    win32con.CW_USEDEFAULT,
                    win32con.CW_USEDEFAULT,
                    win32con.CW_USEDEFAULT,
                    0,
                    0,
                    WndClass.hInstance,
                    None)
                # hWindow = win32gui.CreateWindow(
                #     WinGuiClassAtom,                   #it seems message dispatching only works with the atom, not the class name
                #     szTitle,
                #     win32con.WS_POPUP,
                #     0,
                #     0,
                #     width,
                #     hight,
                #     0,
                #     0,
                #     WndClass.hInstance,
                #     None)
        return hWindow

    def WindowMainLoopX(self, hWindow, Transparent=True):
        # Show & update the window
        if Transparent:
            rgb = self.RGB(0, 0, 0)
            SetLayeredWindowAttributes(hWindow, 0, rgb, win32con.LWA_COLORKEY)
        win32gui.ShowWindow(hWindow, win32con.SW_SHOWNORMAL)
        win32gui.UpdateWindow(hWindow)

        lpmsg = ctypes.pointer(wintypes.MSG())
        while self.GetMessage(lpmsg, 0, 0, 0) != 0:
            # Dispatch messages
            # win32gui.PumpMessages()
            ctypes.windll.user32.TranslateMessage(lpmsg)
            self.DispatchMessage(lpmsg)

            # 使辅助窗口一直盖在游戏窗口上
            # ctypes.windll.user32.MoveWindow(hWindow, 0, 23, width, hight-23, True)
            # win32gui.CloseWindow(hWindow)
            # time.sleep(1)
        return None

    def CreateGUi(self, WndProc=None, szTitle='Hello, World!', Transparent=True):
        hInstance = self.GetModuleHandleX()
        WndClass = self.GetWndClassX(hInstance, WndProc, Transparent=Transparent)
        WndClassAtom = self.RegisterClassX(WndClass)
        hWindow = self.CreateWindowX(WndClass, WndClassAtom, szTitle, Transparent=Transparent)
        if hWindow:
            self.WindowMainLoopX(hWindow, Transparent=Transparent)
        return hWindow, hInstance, WndClass
    pass


if __name__ == "__main__":
    def Render(hWnd):
        hDC, paintStruct = win32gui.BeginPaint(hWnd)

        rect = win32gui.GetClientRect(hWnd)
        win32gui.DrawText(
            hDC,
            'Hello send by Python via Win32!',
            -1,
            rect,
            win32con.DT_SINGLELINE | win32con.DT_CENTER | win32con.DT_VCENTER)

        win32gui.EndPaint(hWnd, paintStruct)
        pass

    def WndProc(hWnd, message, wParam, lParam):
        if message == win32con.WM_PAINT:
            Render(hWnd)
            return 0
        elif message == win32con.WM_CREATE:
            return 0
        elif message == win32con.WM_DESTROY:
            print('Being destroyed')
            win32gui.PostQuitMessage(0)
            return 0
        else:
            return win32gui.DefWindowProc(hWnd, message, wParam, lParam)

    Instance = Win32Gui(True)
    Instance.CreateGUi(WndProc, Transparent=True)