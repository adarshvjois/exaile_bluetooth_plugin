import threading
from bluetooth import *
import os

class btSvr(threading.Thread):
    def __init__(self,exaile):
        self.evt=threading.Event()
        self.evt.clear()
        self.flag=True
        self.exaile=exaile
        self.client_sock=None
        self.client_info=None
        self.server_sock=BluetoothSocket( RFCOMM )
        self.server_sock.bind(("",PORT_ANY))
        self.server_sock.listen(1)

        self.port = self.server_sock.getsockname()[1]

        self.uuid = "00001101-0000-1000-8000-00805F9B34FB"

        advertise_service( self.server_sock, "SampleServer",
                           service_id = self.uuid,
                           service_classes = [ self.uuid, SERIAL_PORT_CLASS ],
                           profiles = [ SERIAL_PORT_PROFILE ],
#                           protocols = [ OBEX_UUID ]
                            )
                   
        print "Waiting for connection on RFCOMM channel %d" % self.port
        threading.Thread.__init__ ( self )

    def run(self):
        while self.evt.is_set()==False:
                print "here"
                exaile=self.exaile
	        self.client_sock, self.client_info = self.server_sock.accept()
	        print "Accepted connection from ", self.client_info
                data=" "    
            
                try:
		
                    while self.evt.is_set()==False:
                        print "now here"
                        data = self.client_sock.recv(10)        
                        print "received [%s]" % data 
                        stuff=data.decode("utf-8")
                        print "string=",stuff
                        if stuff=="PAUSE":
			                if exaile.player.is_paused() or not exaile.player.is_playing():
				                exaile.queue.play()
			                elif exaile.player.is_playing():
				                exaile.player.pause()
	                
                        if stuff== "PREV":
                            os.system("exaile -p")
                        if stuff=="NEXT":
                            os.system("exaile -n")
                        if stuff=="EXIT":
                            break;               
                except :
                        print "Unexpected error:", sys.exc_info()[0]

                print "disconnected"
                self.client_sock.close()
                
        print "exiting loop"

    def cleanup(self):
        if self.client_sock is not None and self.server_sock is not None:
            self.client_sock.close()
            self.server_sock.close()
            print "all done"
    def kill(self):
        self.cleanup()
        self.evt.set()
        SystemExit(0)

