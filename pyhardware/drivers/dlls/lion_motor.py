import ctypes
import os

class Cluster(ctypes.Structure):
    _fields_ = [("CoeffA",ctypes.c_double),
                ("CoeffB",ctypes.c_double),
                ("CoeffC",ctypes.c_double),
                ("MaxWl", ctypes.c_double),
                ("MinWl", ctypes.c_double)]

class Cluster1(ctypes.Structure):
    _fields_ = [("status", ctypes.c_bool),
                ("code", ctypes.c_int32),
                ("source", ctypes.c_char*1000)]

class SacherMotorController(object):
    dll_file = os.path.split(__file__)[0] + '/SharedLib.dll'
    
    def __init__(self, port='COM1'):
        self.dll = ctypes.WinDLL(self.dll_file)
        
        self.port = ctypes.c_char_p(port)
        self.position_offset = ctypes.c_int32(0)
        self.connected = ctypes.c_bool(False)
        self.key = ctypes.c_int32(0)
        self.wavelength = ctypes.c_double(0.)
        self.position = ctypes.c_int32(0)
        self.dummy = ctypes.c_int32(0)
        self.cluster = Cluster(0.,0.,0.,0.,0.)
        self.cluster1 = Cluster1(False,0,'')
        
        
        self.check(self.dll.MC_Connect(self.port, 
                       ctypes.pointer(self.position_offset), 
                       ctypes.pointer(self.connected), 
                       ctypes.pointer(self.key), 
                       ctypes.pointer(self.cluster), 
                       ctypes.pointer(self.wavelength), 
                       ctypes.pointer(self.position))) 
    
    def check(self, val):
        if val:
            raise ValueError('DLL returned error code ' + str(val))
        
    def move_to_wavelength(self, val_nm, hp_mode=True):
        self.check(self.dll.MC_Move_to_Wavelength(ctypes.c_double(val_nm),
                                             self.position_offset,
                                             ctypes.pointer(self.cluster),
                                             self.key,
                                             ctypes.c_bool(hp_mode),
                                             ctypes.pointer(self.cluster1),
                                             self.position,
                                             ctypes.pointer(self.key),
                                             ctypes.pointer(self.wavelength),
                                             ctypes.pointer(self.dummy)))
        
    def calibrate(self, current_wavelength):
        self.check(self.dll.MC_Calibrate())