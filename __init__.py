from xl import event
from bluetooth import *
import thread
import btSvr

t=[]
def enable(exaile):
    if (exaile.loading):
        event.add_callback(_enable, 'exaile_loaded')
    else:
        _enable(None, exaile, None)
 
def disable(exaile):
        for thr in t:
                thr.kill()
        print('I am being disabled.')

 
def _enable(eventname, exaile, nothing):   
	bt=btSvr.btSvr(exaile)
	t.append(bt)
	bt.start()

