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
    _dll_file = os.path.split(__file__)[0] + '/SharedLib.dll'
    
    def __init__(self, port='COM1'):
        self._dll = ctypes.WinDLL(self._dll_file)
        
        self.port = ctypes.c_char_p(port)
        self._position_offset = ctypes.c_int32(0)
        self.connected = ctypes.c_bool(False)
        self._key = ctypes.c_int32(0)
        self._wavelength = ctypes.c_double(0.)
        self._position = ctypes.c_int32(0)
        self._new_position = ctypes.c_int32(0)
        self._dummy = ctypes.c_int32(0)
        self._cluster = Cluster(0.,0.,0.,0.,0.)
        self._cluster1 = Cluster1(False,0,'')
        
        
        self._check(self._dll.MC_Connect(self.port, 
                       ctypes.pointer(self._position_offset), 
                       ctypes.pointer(self.connected), 
                       ctypes.pointer(self._key), 
                       ctypes.pointer(self._cluster), 
                       ctypes.pointer(self._wavelength), 
                       ctypes.pointer(self._position))) 
    
    def _check(self, val):
        if val==60 or val==59 or val==0: ## error reading motor profile seems to be irrelevant...
            return
        if val:
            raise ValueError('DLL returned error code ' + str(val))
        
    def move_to_wavelength(self, val_nm, hp_mode=False):
        self._check(self._dll.MC_Move_to_Wavelength(ctypes.c_double(val_nm),
                                             self._position_offset,
                                             ctypes.pointer(self._cluster),
                                             self._key,
                                             ctypes.c_bool(hp_mode),
                                             ctypes.pointer(self._cluster1),
                                             self._position,
                                             ctypes.pointer(self._key),
                                             ctypes.pointer(self._wavelength),
                                             ctypes.pointer(self._new_position)))
        self.watch()
        
    def calibrate(self, current_wavelength):
        cancel_out = ctypes.c_bool(False)
        wavelength_out = ctypes.c_double(0.)
        self._check(self._dll.MC_Calibrate(current_wavelength,
                                         ctypes.pointer(self._cluster),
                                         ctypes.byref(cancel_out),
                                         ctypes.byref(wavelength_out)))
        
    def watch(self):
        actual_position = ctypes.c_int32(0)
        wavelength = ctypes.c_double(0.)
        offset = ctypes.c_int(0)
        self._check(self._dll.MC_Watch(self._key,
                                       self._position,
                                       ctypes.byref(self._cluster),
                                       self._position_offset,
                                       ctypes.byref(self._cluster1),
                                       ctypes.byref(actual_position),
                                       ctypes.byref(wavelength),
                                       ctypes.byref(offset)))
        self._position = actual_position
        self._wavelength = wavelength
        self._position_offset = offset
        
    def get_profile(self):
        max_speed = ctypes.c_double(0.)
        speed_nm_s = ctypes.c_double(0.)
        acc_nm_s = ctypes.c_double(0.)
        dec_nm_s = ctypes.c_double(0.)
        self._check(self._dll.MC_GetProfile(self._key,
                               ctypes.pointer(self._cluster),
                               ctypes.pointer(self._cluster1),
                               ctypes.byref(max_speed),
                               ctypes.byref(speed_nm_s),
                               ctypes.byref(acc_nm_s),
                               ctypes.byref(dec_nm_s)))
        return max_speed.value, speed_nm_s.value, acc_nm_s.value, dec_nm_s.value
    
    def set_profile(self, speed_nm_s, acc_nm_s, dec_nm_s):
        self._check(self._dll.MC_SetProfile(self._key,
                               ctypes.pointer(self._cluster),
                               ctypes.c_double(speed_nm_s),
                               ctypes.pointer(self._cluster1),
                               ctypes.c_double(acc_nm_s),
                               ctypes.c_double(dec_nm_s),
                               ctypes.byref(self._dummy)))
    
    @property
    def wavelength(self):
        return self._wavelength
    
    @property
    def speed_nm_s(self, val):
        (max_speed, speed_nm_s, acc_nm_s, dec_nm_s) = self.get_profile()
        return speed_nm_s
    
    @speed_nm_s.setter
    def speed_nm_s(self, val):
        (max_speed, speed_nm_s, acc_nm_s, dec_nm_s) = self.get_profile()
        self.set_profile(val, acc_nm_s, dec_nm_s)
        return val
    
    @property
    def acc_nm_s(self, val):
        (max_speed, speed_nm_s, acc_nm_s, dec_nm_s) = self.get_profile()
        return acc_nm_s
    
    @acc_nm_s.setter
    def acc_nm_s(self, val):
        (max_speed, speed_nm_s, acc_nm_s, dec_nm_s) = self.get_profile()
        self.set_profile(speed_nm_s, val, dec_nm_s)
        return val
    
    @property
    def dec_nm_s(self, val):
        (max_speed, speed_nm_s, acc_nm_s, dec_nm_s) = self.get_profile()
        return dec_nm_s
    
    @dec_nm_s.setter
    def dec_nm_s(self, val):
        (max_speed, speed_nm_s, acc_nm_s, dec_nm_s) = self.get_profile()
        self.set_profile(speed_nm_s, acc_nm_s, val)
        return val
    
    def waypoint_patrol(self):
        self._check(self._dll.MC_Patrol_Waypoints_GUI(self._key, 
                                                      ctypes.pointer(self._cluster),
                                                      self._wavelength))
    
                                            