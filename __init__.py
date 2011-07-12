from xl import event
from bluetooth import *
import threading
import thread
import os
#setting a thread event to disable the child process from within the parent. We want to stop the bluetooth server when the plugin is disabled...
global mt
mt=threading.Event()
global ct
ct=threading.Event()
#creating a client thread. Not that i want more than one client at a time but to allow for that possibility to share between many peers..
sthr=[]
class ClientThread(threading.Thread):
    def __init__(self,exaile,client_sock,client_info,evt,cevt):
        self.evt=evt
        self.cevt=cevt
        self.exaile=exaile
        self.client_sock=client_sock
        self.client_sock.setblocking(False)
        self.client_info=client_info
        threading.Thread.__init__(self)
    def run(self):
        print "accepted Connection from", self.client_info
        exaile=self.exaile
        while not self.evt.is_set()or not self.cevt.is_set():
            try:
                data=self.client_sock.recv(1024)
                print self.client_info,":",data
                stuff=data.encode("utf-8")
                #controlling player thru the exaile object depending in the data recieved..simple flags...Pause,Next,Prev and Exit
                if stuff=="PAUSE":
                    if exaile.player.is_playing() or exaile.player.is_paused():
                       exaile.player.toggle_pause()
                    else:
                      exaile.queue.play()
                if stuff== "PREV":
                    exaile.queue.prev()
                if stuff=="NEXT":
                    exaile.queue.next()
                if stuff=="VOL_UP":
                    exaile.player.set_volume(5+exaile.player.get_volume())
                if stuff=="VOL_DOWN":
                        vol=exaile.player.get_volume()
                        if vol>=0:
                                exaile.player.set_volume(vol-5)
                if stuff=="EXIT":
                            break;
            except IOError as err: #fix this to prevent all client threads being disconnected#                
                pass

        print "disconnected: ", self.client_info;
        self.client_sock.close()
        self.disable()
        
    def disable(self):
        print "client threads dying"        
        self.cevt.set()

def btSvr(exaile):
    #contains all the client threads i create..
    threads=[]
    #bluetooth stuff...
    server_sock=BluetoothSocket( RFCOMM )
    server_sock.bind(("",PORT_ANY))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]
    #some website said that this was a popular uuid...planning to generate my own and use it..need to look into this further..
    uuid = "00001101-0000-1000-8000-00805F9B34FB"
    #more bluetooth stuff...
    advertise_service( server_sock, "MyExaileServer",
                           service_id = uuid,
                           service_classes = [ uuid, SERIAL_PORT_CLASS ],
                           profiles = [ SERIAL_PORT_PROFILE ],
#                           protocols = [ OBEX_UUID ]
                            )
    #this is the shit bro..
    i=0
    while not mt.is_set():
        try:
            #print "Waiting for connection on RFCOMM channel %d" % port
            #sets the I/O mode for server_sock.accept() as non blocking. that is to say that the lines after the line
            #            client_sock, client_info = server_sock.accept()
            #will continue in the parent thread. At every iteration if there is a connection a thread is started if not it checks for
            #the disable event (that is the thread event variable mt right on top..)            
            server_sock.setblocking(False)
            client_sock, client_info = server_sock.accept()
            if client_sock:
                thread1=ClientThread(exaile,client_sock, client_info,mt,ct)
                threads.append(thread1)
                thread1.start()
        except BluetoothError as err:
            #print err
            pass
    
    cleanup(server_sock,threads)
#my favourite function in this
def cleanup(server_sock,threads):  
    server_sock.close()
    for t in threads:
        t.disable()
    print "all cleant up"
    
#exailes needs these functions for this plugin to work..exaile object being passed around here and there...u can do lots of good stuff
#with it. these functions get called by the PluginManager object within exaile.

def enable(exaile):
    if (exaile.loading):
        event.add_callback(_enable, 'exaile_loaded')
    else:
        _enable(None, exaile, None)
 
def disable(exaile):
        print "setting event to quit"
        mt.set()
        print('I am being disabled.')
#found that exaile calls this when you quit exaile with the plugins turned on. this is pretty much the same as disable() above.
#except for the dramatic display msg.
def teardown(exaile):
        print "setting event to quit"
        mt.set()
        print('I am being torndown...')

 
def _enable(eventname, exaile, nothing):
    #event.add_callback(disable,'quit_application')
    mt.clear()
    #create server thread on enable...
    bt=threading.Thread(target=btSvr,args=(exaile,))
    sthr.append(bt)
    bt.start()
    print "i am enabled"
