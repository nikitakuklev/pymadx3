import MadX as _MadX
import numpy as _np
import matplotlib.pyplot as _plt

class Survey : 
    def __init__(self):
        self._x_current = 0
        self._y_current = 0
        self._theta     = _np.pi
        self._beamline  = []
        self._x_coords  = []
        self._y_coords  = []
        self._lentotal  = 0

    def load(self, inputfilename) : 
        self._file = _MadX.Tfs(inputfilename)        
        i = 0
        for v in self._file.data['NAME']:
            self.step(self._file.data['ANGLE'][i],self._file.data['L'][i])
            i += 1
            
        print 'Number of elements: ',i
        

    def step(self,angle,length):
        self._theta += angle
        dx    = length * _np.cos(self._theta)
        dy    = length * _np.sin(self._theta)
        self._lentotal += length
        
        x_new = self._x_current - dx
        y_new = self._y_current - dy
        self._beamline.append([[self._x_current,x_new],[self._y_current,y_new]])
        self._x_current = x_new
        self._y_current = y_new
        self._x_coords.append(x_new)
        self._y_coords.append(y_new)

    def finalDiff(self):
        dx = self._beamline[-1][0][1] - self.x_current
        dy = self._beamline[-1][1][1] - self.y_current
        print 'Final dx ',dx
        print 'Final dy ',dy

        
    def plot(self) : 
        _plt.figure()
        _plt.plot(self._x_coords,self._y_coords,'b.')
        _plt.plot(self._x_coords,self._y_coords,'b-')
        _plt.xlabel('X (m)')
        _plt.ylabel('Y (m)')
        _plt.show()
        
