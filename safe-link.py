from tkinter import *
import tkinter.messagebox
import multiprocessing
import threading
import time
from PIL import ImageGrab
import cv2
import sounddevice as sd
from win32api import GetSystemMetrics
import time
import socket
import numpy as np
import os
import pickle
import select
#os.chdir('C:\\Users\\username\\Desktop\\communication_app_pic')
root = Tk()
#socket.setdefaulttimeout(0.5)

class update_routine():
  
  def __init__(self,obj_frame1_bt_handler, obj_frame2, obj_frame3 , thread_lock , multi_lock):
    self.obj_frame2 = obj_frame2
    self.obj_frame3 = obj_frame3
    self.obj_frame1_bt_handler = obj_frame1_bt_handler
    self.update_routine_thread_lock = thread_lock#threading.Lock()
    self.update_routine_multiprocess_lock = multi_lock#multiprocessing.Lock()
    self.update_routine_thread = None
    self.thread_run_signal = False
    self.send_frame = []
    self.received_frame = [None,None]
    self.received_frame_zero_old = [[],[]]
    self.group_send_frame = []
    self.group_received_frame = []
    self.name_list = []
    self.msg_list = []
    self.view_enabler = 1
    self.start_the_client = 1
    self.start_the_server = 1

  def start_update_routine(self):
    self.thread_run_signal = True
    self.update_routine_thread = threading.Thread(target = self.run_update_routine_thread)
    self.update_routine_thread.start()

  def create_join_send_frame(self):
    self.update_routine_thread_lock.acquire()
    self.update_routine_multiprocess_lock.acquire()
    self.send_frame = []
    self.send_frame.append(self.obj_frame1_bt_handler.user)
    if not self.obj_frame3.msg_send_state:
      self.send_frame.append(self.obj_frame3.msg_to_send)
      self.obj_frame3.msg_send_state = True
    else:
      self.send_frame.append(None)
    if len(self.obj_frame1_bt_handler.obj_process_handler.screen_share_frame_list) > 5 and self.obj_frame1_bt_handler.obj_process_handler.screen_share_frame_signal[0]:
      self.send_frame.append(self.obj_frame1_bt_handler.obj_process_handler.screen_share_frame_list[0:5]) #works as it is
      #self.received_frame[1] = self.obj_frame1_bt_handler.obj_process_handler.screen_share_frame_list[0:10] #disable this later
      for var in range(0,4):
        try:
          self.obj_frame1_bt_handler.obj_process_handler.screen_share_frame_list.pop(0)
        except:
          print('exception happened while poping screen share frame list')
    else:
      self.send_frame.append(None)
    if len(self.obj_frame1_bt_handler.obj_process_handler.audio_record_list) >40 and self.obj_frame1_bt_handler.obj_process_handler.audio_record_signal[0]:
      self.send_frame.append(self.obj_frame1_bt_handler.obj_process_handler.audio_record_list[0:40])
      for var in range(0,39):
        try:
          self.obj_frame1_bt_handler.obj_process_handler.audio_record_list.pop(0)
        except:
          print('exception happened while popping audio record list')
    else:
      self.send_frame.append(None)
    if self.obj_frame1_bt_handler.view_user_stat:
      self.send_frame.append(self.obj_frame1_bt_handler.user_to_view)
    else:
      self.send_frame.append(None)
    self.update_routine_multiprocess_lock.release()
    self.update_routine_thread_lock.release()

  def frame_join_get_unpacker(self):
    self.obj_frame2.text_update=True
    if self.received_frame[0] != None and self.received_frame[0] != self.received_frame_zero_old:
      self.obj_frame2.change_text(list(self.received_frame[0]))
      self.received_frame_zero_old = [[self.received_frame[0][var][var2] for var2 in range(len(self.received_frame[0][var]))]for var in range(len(self.received_frame[0]))]
    if self.obj_frame1_bt_handler.obj_process_handler.frame_display_signal[0] and self.received_frame[1] != None and len(self.received_frame[1]) > 0:
      if self.obj_frame1_bt_handler.view_user_stat:
        for var in self.received_frame[1]:
          if var[0] == self.obj_frame1_bt_handler.user_to_view and var[1] != None:
            for var2 in var[1]:
              if var2 != None: #change made here undo if error arises
                try:
                  self.obj_frame1_bt_handler.obj_process_handler.frame_display_list.append(var2)
                except:
                  print('exception in frame display list appending')
            break
    if self.obj_frame1_bt_handler.obj_process_handler.audio_play_signal[0] and self.received_frame[1] != None and len(self.received_frame[1]) > 0:
      if self.obj_frame1_bt_handler.view_user_stat:
        for var in self.received_frame[1]:
          if var[0] == self.obj_frame1_bt_handler.user_to_view and var[2] != None:
            for var2 in var[2]:
              #if var2 != None: #change made here undo if error arises
              try:
                self.obj_frame1_bt_handler.obj_process_handler.audio_play_list.append(var2)
              except:
                print('exception in audio play list appending')
            break

  def frame_create_group_get_from_client(self):
    self.update_routine_thread_lock.acquire()
    self.update_routine_multiprocess_lock.acquire()
    self.group_send_frame = []
    temp_list2 = []
    temp_list3 = []
    if len(self.group_received_frame)>0:
      #print('the group received frame is :',self.group_received_frame) #disable this afterwards
      for var in self.group_received_frame:
        if var[1] != None:
          self.name_list.append(var[0]) #here we have a issue if there is no message then don't add them also the same goes for audio and video frame so add a condition and then try
          self.msg_list.append(var[1])
        temp_list=[]
        #if var[2] != None and var[3] != None:
        temp_list.append(var[0])
        temp_list.append(var[2])
        temp_list.append(var[3])
        temp_list2.append(temp_list)
      temp_list3.append(self.name_list)
      temp_list3.append(self.msg_list)
      self.group_send_frame.append(temp_list3)
      self.group_send_frame.append(temp_list2)
    self.received_frame = list(self.group_send_frame)
    self.update_routine_multiprocess_lock.release()
    self.update_routine_thread_lock.release()
        

  def view_user_checker(self):
    if self.obj_frame1_bt_handler.view_user_stat and self.view_enabler == 1:
      self.obj_frame1_bt_handler.obj_process_handler.request_process('disable_show_frame')
      self.obj_frame1_bt_handler.obj_process_handler.request_process('enable_show_frame')
      self.view_enabler = 0
    elif not self.obj_frame1_bt_handler.view_user_stat and self.view_enabler == 0:
      self.obj_frame1_bt_handler.obj_process_handler.request_process('disable_show_frame')
      self.view_enabler = 1

  def run_update_routine_thread(self):
    print('inside the run update routine thread')
    while self.thread_run_signal:
      #print('the received frame is :',self.received_frame ,'the send frame is ',self.send_frame ,'the length of the server_received_frame is:',len(self.obj_frame1_bt_handler.obj_process_handler.server_receive_frame)) #disable this afterwards
      if self.obj_frame1_bt_handler.join_stat:
        if self.start_the_client == 1 and self.obj_frame1_bt_handler.ip != None and self.obj_frame1_bt_handler.port!= None:
          self.obj_frame1_bt_handler.obj_process_handler.set_host_and_port(self.obj_frame1_bt_handler.ip , int(self.obj_frame1_bt_handler.port))
          self.obj_frame1_bt_handler.obj_process_handler.request_process('enable_client')
          self.start_the_client = 0
        self.create_join_send_frame()
        #print(self.send_frame) #disable this afterward
        if len(self.obj_frame1_bt_handler.obj_process_handler.client_send_frame) < 40: #added to regulate ram usage
          if self.send_frame[1] != None or self.send_frame[2] != None or self.send_frame[3] != None: #newly added disable if error is produced or does not work
            try:
              self.obj_frame1_bt_handler.obj_process_handler.client_send_frame.append(self.send_frame)
            except:
              print('error while appending client_send_frame in routine updater')
            #print(self.send_frame) #disable this afterwards
        if len(self.obj_frame1_bt_handler.obj_process_handler.client_received_frame) > 0:
          self.received_frame = self.obj_frame1_bt_handler.obj_process_handler.client_received_frame[0]
          try:
            self.obj_frame1_bt_handler.obj_process_handler.client_received_frame.pop(0)
          except:
            pass
        #print('the received frame in client is :',self.received_frame) #disable this afterwards
        self.frame_join_get_unpacker()
        self.view_user_checker()
        #time.sleep(0.05) #added this to slow down the client side as it was only spamming none values
      elif self.obj_frame1_bt_handler.create_stat:
        if self.start_the_server == 1 and self.obj_frame1_bt_handler.ip != None and self.obj_frame1_bt_handler.port!= None:
          self.obj_frame1_bt_handler.obj_process_handler.set_host_and_port(self.obj_frame1_bt_handler.ip , int(self.obj_frame1_bt_handler.port))
          self.obj_frame1_bt_handler.obj_process_handler.request_process('enable_server')
          self.start_the_server = 0
        self.group_received_frame = []
        self.create_join_send_frame()
        self.group_received_frame.append(self.send_frame)
        #print('the length of the server_receive_frame is',len(self.obj_frame1_bt_handler.obj_process_handler.server_receive_frame)) #disable this afterwards
        if len(self.obj_frame1_bt_handler.obj_process_handler.server_receive_frame) > 0:
          for val in self.obj_frame1_bt_handler.obj_process_handler.server_receive_frame[0]:
            self.group_received_frame.append(val) #check here
          try:
            self.obj_frame1_bt_handler.obj_process_handler.server_receive_frame.pop(0) #the pop not working as we are popping from server_receive_frame but frame_receive in server client handler is not being poped
          except:
            print('exception occurred while popping server_receive_frame')
        #if len(self.received_frame) > 0: #don't know if this is actually needed
        #self.obj_frame1_bt_handler.obj_process_handler.server_send_frame.append(self.received_frame)
        #print('yes',len(self.obj_frame1_bt_handler.obj_process_handler.frame_display_list))
        self.frame_create_group_get_from_client()
        if len(self.obj_frame1_bt_handler.obj_process_handler.server_send_frame) < 30:#added this to regulate ram usage
          self.obj_frame1_bt_handler.obj_process_handler.server_send_frame.append(self.received_frame) #shifted this from up to this position
        #print(self.received_frame)
        #add here the recv and send frames to the server
        self.frame_join_get_unpacker()
        #print('yes',len(self.obj_frame1_bt_handler.obj_process_handler.frame_display_list),self.received_frame[1])
        self.view_user_checker()
      elif self.start_the_client == 0 or self.start_the_server == 0:
        self.obj_frame1_bt_handler.obj_process_handler.request_process('disable_screen_share')
        self.obj_frame1_bt_handler.obj_process_handler.request_process('disable_show_frame')
        self.obj_frame1_bt_handler.obj_process_handler.request_process('disable_mic')
        self.obj_frame1_bt_handler.obj_process_handler.request_process('disable_audio')
        self.obj_frame1_bt_handler.obj_process_handler.request_process('disable_client')
        self.obj_frame1_bt_handler.obj_process_handler.request_process('disable_server')
        self.start_the_client = 1
        self.start_the_server = 1
        #self.obj_frame1_bt_handler.host_and_port_list[0] = None
        #self.obj_frame1_bt_handler.host_and_port_list[1] = None
        #pass
   

  def close_update_routine(self):
    self.update_routine_thread_lock.acquire()
    self.thread_run_signal = False
    self.update_routine_thread_lock.release()
    print('update routine closing')

  def join_update_routine(self):
    self.update_routine_thread.join()
    print('update routine joined with main')





class Communication_handler(): #added code to check and only send frame if available or inform no such frame available and move on to the next ; check that code
  def __init__(self,multi_list_manager , multi_lock):
    #the below is common for both group and join
    self.host_and_port_list = multi_list_manager.list()
    self.comm_multi_lock = multi_lock
    self.host_and_port_list.append(None)
    self.host_and_port_list.append(None)
    #for client variables set below
    self.client_run_signal = multi_list_manager.list()
    self.client_send_frame = multi_list_manager.list() #client list to send stuff; append the frames to send here
    self.client_received_frame = multi_list_manager.list() #client list to receive stuff and appended in it
    self.client_run_signal.append(False)
    self.client_process = None
    #for server variables set below
    self.server_run_signal = multi_list_manager.list()
    self.server_send_frame = multi_list_manager.list() #the list contains all the frames to send
    self.server_receive_frame = multi_list_manager.list() #the list contains all the frames received
    self.server_run_signal.append(False)
    self.server_process = None
    self.server_client_list = []

  def set_host_and_port(self,host,port):
    self.host_and_port_list[0] = host
    self.host_and_port_list[1] = port

  def tcp_send_protocol(self , signali , data , sock , ack_get_msg , ack_size):
    ack = None
    while signali[0]:
      try:
        sock.sendall(data)
        ack = sock.recv(ack_size)
        if ack == ack_get_msg:
          return True
      except:
        pass 
   

  def tcp_receive_protocol(self , signali , data_size , ack_send_msg , sock , check_data_len):
    while signali[0]:
      try:
        data = sock.recv(data_size)
        #print('the lenght of the data received is:',len(data),'the length supposed to receive:',data_size) #data is not being properly received
        if len(data) == data_size or not check_data_len: # remove if it causes problem
          sock.sendall(ack_send_msg)
          return data
      except:
        pass

  def start_client(self):
    self.client_run_signal[0] = True
    self.client_process = multiprocessing.Process(target = self.run_client_process , args = (self.client_send_frame , self.client_received_frame ,  self.client_run_signal , self.host_and_port_list))
    self.client_process.start()

  def run_client_process(self,frame_send,frame_receive,signal,handp_list):
    print(multiprocessing.current_process(),'client process')
    host = handp_list[0]
    port = handp_list[1]
    if host!=None and port!=None:
      socket.setdefaulttimeout(0.7)
      client_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      client_sock.connect((host,port))
      while signal[0]:
        if len(frame_receive) < 10: #added this part to controll ram usage and also the framereceive length  
          if len(frame_send) > 0:
            if self.tcp_send_protocol(signali = signal , data = b'cy' , sock = client_sock , ack_get_msg = b'oks0', ack_size = int(4) ):
              client_data_send = pickle.dumps(frame_send[0])
              self.tcp_send_protocol(signali = signal , data = pickle.dumps(len(client_data_send)) , sock = client_sock , ack_get_msg = b'oks1' , ack_size = int(4) )
              self.tcp_send_protocol(signali = signal , data = client_data_send , sock = client_sock , ack_get_msg = b'oks2' , ack_size = int(4))
              try:
                frame_send.pop(0)
              except:
                print('error while popping frame_send in cient side')
          else:
            self.tcp_send_protocol(signali = signal , data = b'cn' , sock = client_sock , ack_get_msg = b'oks0' , ack_size = int(4))
          while True:
            continue_val = self.tcp_receive_protocol(signali = signal , data_size = int(2) , ack_send_msg = b'okc0' , sock = client_sock , check_data_len = True)
            if continue_val == b'sy':
              try:
                #print('getting data form server')
                data_receive_from_server_len = self.tcp_receive_protocol(signali = signal , data_size = int(50) , ack_send_msg = b'okc1' , sock = client_sock , check_data_len = False )
                data_receive_from_server_len = pickle.loads(data_receive_from_server_len)
                #print('got data lenght form server, the length is :',data_receive_from_server_len)
                data_receive_from_server = self.tcp_receive_protocol(signali = signal , data_size = data_receive_from_server_len , ack_send_msg = b'okc2' , sock = client_sock , check_data_len = True)
                data_receive_from_server = pickle.loads(data_receive_from_server)
                #print('data received form server')
                try:
                  frame_receive.append(data_receive_from_server)
                  break
                except:
                  print('exception occured in client process while appending data from server to frame_receive')          
                  break
              except:
                print('error while receiving data from server')
            elif continue_val == b'sn':
              break
      print('exiting client')
      client_sock.close()
        
  def close_client(self):
    self.comm_multi_lock.acquire()
    self.client_run_signal[0] = False
    self.comm_multi_lock.release()
    print('closing client process')

  def join_client_process(self):
    self.client_process.join()
    print('client process joined')

  def start_server(self):
    self.server_run_signal[0] = True
    #print('the host and port are :',self.host_and_port_list)
    self.server_process = multiprocessing.Process(target = self.run_server_process , args = (self.server_send_frame , self.server_receive_frame ,  self.server_run_signal , self.host_and_port_list)) 
    self.server_process.start()

  def run_server_process(self , frame_send , frame_receive , signal , handp_list): #the value is not being passed on ckeck why
    print(multiprocessing.current_process(),'server process')
    host=handp_list[0]
    port=handp_list[1]
    if host != None and port != None:
      socket.setdefaulttimeout(0.7)
      server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      server_sock.bind((host,port)) 
      server_sock.listen(10)
      server_client_handler_thread = threading.Thread(target = self.server_client_handler , args = (signal,frame_send,frame_receive))
      server_client_handler_thread.start()
      while signal[0]:
        try:
          con , adr = server_sock.accept()
          self.server_client_list.append(con)
        except:
          #print('accept timeout exception')
          pass
      print('closing and exiting the server process')
      server_sock.close()
      server_client_handler_thread.join() #probably this is not the issue

  def server_client_handler(self,signal,frame_send,frame_receive):
    while signal[0]:
      temp_list = []
      for i in range(len(self.server_client_list)):
        if len(frame_receive) < 10: #added this part to controll ram usage and also the framereceive length
          while True:
            skip_cond = self.tcp_receive_protocol(signali = signal , data_size = int(2) , ack_send_msg = b'oks0' , sock = self.server_client_list[i] , check_data_len = True)
            if skip_cond == b'cy':
              try:
                #print('receiving data from client :',i)
                server_data_receive_len = self.tcp_receive_protocol(signali = signal , data_size = int(50) ,ack_send_msg = b'oks1' , sock = self.server_client_list[i] , check_data_len = False)
                server_data_receive_len = pickle.loads(server_data_receive_len)
                server_data_receive = self.tcp_receive_protocol(signali = signal , data_size = int(server_data_receive_len) , ack_send_msg = b'oks2' , sock = self.server_client_list[i] , check_data_len = True )
                server_data_receive = pickle.loads(server_data_receive)
                try:
                  temp_list.append(server_data_receive)
                except:
                  print('error encountered while appending temp_list in server client handler')
                break
              except:
                print('error while receiving data form client:',i)
            elif skip_cond == b'cn':
              #print('client has no data to send')
              break
        if len(frame_send) > 0:
          if self.tcp_send_protocol(signali = signal ,data = b'sy' , sock = self.server_client_list[i] , ack_get_msg = b'okc0' , ack_size = int(4)):
            #print('sending data to client')
            server_data_send = pickle.dumps(frame_send[0])
            self.tcp_send_protocol(signali = signal , data = pickle.dumps(len(server_data_send)), sock = self.server_client_list[i] , ack_get_msg = b'okc1' , ack_size = int(4))
            #print('sent the data length from server , the lenght is :',len(server_data_send))
            self.tcp_send_protocol(signali = signal , data = server_data_send , sock = self.server_client_list[i] , ack_get_msg = b'okc2' , ack_size = int(4))
            #print('sent the data form server')
            try:
              frame_send.pop(0)
            except:
              print('error in popping frame_send in server side')
        else:
          #print('no data to send to client')
          self.tcp_send_protocol(signali = signal , data = b'sn' , sock = self.server_client_list[i] , ack_get_msg = b'okc0' , ack_size = int(4))
        if len(temp_list) > 0 :
          try:
            frame_receive.append(temp_list) #undo this later
          except:
            print('error in appending the temp_list to frame_receive in server client handler')
    print('exiting server')

  def close_server(self):
    self.comm_multi_lock.acquire()
    self.server_run_signal[0] = False
    self.comm_multi_lock.release()
    print('closing the sever process')

  def join_server_process(self):
    self.server_process.join()
    print('server process joined')






class Share_screen_handler(): #this screen module functionality has been checked and confirmed to work properly

  def __init__(self , multi_list_manager , multi_lock):
    self.screen_share_frame_list = multi_list_manager.list()#multiprocessing.Manager().list() #take the recorded frame from this list and send but pop right there and then
    self.screen_share_frame_signal = multi_list_manager.list()#multiprocessing.Manager().list()
    self.frame_display_list = multi_list_manager.list()#multiprocessing.Manager().list() #display the frame from this list
    self.frame_display_signal = multi_list_manager.list()#multiprocessing.Manager().list()
    self.record_lock = multi_lock#multiprocessing.Lock()
    self.display_lock = multi_lock#multiprocessing.Lock()
    self.screen_share_frame_signal.append(False)
    self.frame_display_signal.append(False)
    self.process_screen_share = None
    self.process_frame_display = None


  def start_record_frame(self):
    self.screen_share_frame_signal[0] = True
    for var in range(len(self.screen_share_frame_list)):
      try:
        self.screen_share_frame_list.pop(0)
      except:
        print('exception while clearing screen share frame list')
    self.process_screen_share = multiprocessing.Process(target = self.run_record_frame , args = (self.screen_share_frame_list,self.screen_share_frame_signal))
    self.process_screen_share.start()

  def run_record_frame(self,frame_list,signal):
    print(multiprocessing.current_process(),'video frame record process')
    width=GetSystemMetrics(0)
    height=GetSystemMetrics(1)
    while signal[0]:
      if len(frame_list) < 20:
        img = ImageGrab.grab(bbox = (0,0,width,height))
        frame_list.append(img)
      #else:
        #for itr in range(len(frame_list)): #might potential cause problems; did this to remove and refresh the list and keep it upto date
          #frame_list.pop(itr)
      time.sleep(0.041)

  def close_record(self):
    self.record_lock.acquire()
    self.screen_share_frame_signal[0] = False
    self.record_lock.release()
    print('closing screen share')

  def join_record(self):
    self.process_screen_share.join()
    print('record screen share has joined with process handler')

  def start_frame_dispaly(self):
    self.frame_display_signal[0] = True
    self.process_frame_display = multiprocessing.Process(target = self.run_frame_display , args = (self.frame_display_list,self.frame_display_signal))
    self.process_frame_display.start()

  def run_frame_display(self,frame_list,signal):
    print(multiprocessing.current_process(),'video frame display process')
    while signal[0]:
      if len(frame_list) >1:
        img_array = np.array(frame_list[0])
        if len(frame_list) > 2: #this worked so keep it
          frame_list.pop(0)
        frame = cv2.cvtColor(img_array,cv2.COLOR_BGR2RGB) 
        cv2.imshow('Screen share',frame)
        if cv2.waitKey(1) == ord('q'):
          signal[0]=False
          break  
      else:
       #signal[0]=False #change made here
       #break
       continue
    cv2.destroyAllWindows()

  def close_display(self):
    self.display_lock.acquire()
    self.frame_display_signal[0] = False
    self.display_lock.release()
    print('closing display frame')

  def join_display(self):
    self.process_frame_display.join()
    print('display screen share has joined with process handler')




class Audio_mic_handler(): #checked and confirmed to work properly
  
  def __init__(self , multi_list_manager , multi_lock):
    self.audio_record_list = multi_list_manager.list()#multiprocessing.Manager().list()
    self.audio_record_signal = multi_list_manager.list()#multiprocessing.Manager().list()
    self.audio_play_list = multi_list_manager.list()#multiprocessing.Manager().list()
    self.audio_play_signal = multi_list_manager.list()#multiprocessing.Manager().list()
    self.audio_record_lock = multi_lock# multiprocessing.Lock()
    self.audio_play_lock = multi_lock#multiprocessing.Lock()
    self.audio_play_signal.append(False)
    self.audio_record_signal.append(False)
    self.process_audio_record = None
    self.process_audio_play = None

  def start_audio_record(self):
    self.audio_record_signal[0] = True
    for var in range(len(self.audio_record_list)):
      try:
        self.audio_record_list.pop(0)
      except:
        print('exception while clearing audio record list')
    self.process_audio_record = multiprocessing.Process(target = self.run_audio_record , args = (self.audio_record_list,self.audio_record_signal))
    self.process_audio_record.start()

  def callback_record(self,input, output,frames,time,status):
    if len(self.record_list) < 1000:
      self.record_list.append(input)
    

  def run_audio_record(self,record_list,signal):
    print(multiprocessing.current_process(),'audio record process')
    self.record_list = record_list
    with sd.Stream(channels = 2 , callback = self.callback_record):
      while signal[0]:
        sd.sleep(1000)      
    sd.stop()
    #tkinter.messagebox.showinfo('exiting','exiting record audio')
      
  def close_audio_record(self):
    self.audio_record_lock.acquire()
    self.audio_record_signal[0] = False #this changed to False from True
    self.audio_record_lock.release()
    print('closing audio record')

  def join_audio_record(self):
    self.process_audio_record.join()
    print('audio record has joined with process handler')


  def start_audio_play(self):
    self.audio_play_signal[0] = True
    self.process_audio_play = multiprocessing.Process(target = self.run_audio_play , args = (self.audio_play_list,self.audio_play_signal))
    self.process_audio_play.start()

  def callback_play(self,input,output,frames,time,status):
    if len(self.play_list) > 0:
      #if len(self.play_list[0]) > 1: #change added here check it if this rectifies something
      output[:]=self.play_list[0]
      self.play_list.pop(0)
    else:
      output[:] = [[0.0,0.0]]

  def run_audio_play(self,play_list,signal):
    print(multiprocessing.current_process(),'audio play process')
    self.play_list = play_list
    with sd.Stream(channels = 2 , callback = self.callback_play):
      while signal[0]: #typo here ; now fixed
        sd.sleep(1000)
    sd.stop()
    #tkinter.messagebox.showinfo('exiting','exiting play audio')

  def close_audio_play(self):
    self.audio_play_lock.acquire()
    self.audio_play_signal[0] = False
    self.audio_play_lock.release()
    print('closing audio play')

  def join_audio_play(self):
    self.process_audio_play.join()
    print('audio play has joined process handler')



class Process_handler(Share_screen_handler,Audio_mic_handler,Communication_handler):

  def __init__(self,multi_list_manager,multi_lock):
    self.process_request_list = multi_list_manager.list()#multiprocessing.Manager().list()
    self.continuity_signal_list = multi_list_manager.list()#multiprocessing.Manager().list()
    self.continuity_signal_list.append(False)
    self.p_handler = None
    self.lock = multi_lock#multiprocessing.Lock()
    Share_screen_handler.__init__(self,multi_list_manager,multi_lock)
    Audio_mic_handler.__init__(self,multi_list_manager,multi_lock)
    Communication_handler.__init__(self,multi_list_manager,multi_lock)

  def request_process(self,requested_process):
    self.lock.acquire()
    if self.continuity_signal_list[0]:
      self.process_request_list.append(requested_process)
    self.lock.release()

  def start(self):
    self.continuity_signal_list[0] = True
    self.p_handler = multiprocessing.Process(target = self.run , args = (self.process_request_list,self.continuity_signal_list,self.lock))
    self.p_handler.start()

  def run(self,process_request_list,continuity_signal_list,lock):
    print(multiprocessing.current_process(),'process handler process')
    req_list = process_request_list
    con_list = continuity_signal_list
    loop_cond = True
    while loop_cond:
      lock.acquire()
      loop_cond = con_list[0]
      if len(req_list) > 0:
        get = req_list[0]
        req_list.pop(0)
      else:
        lock.release()
        continue
      lock.release()
      if get == 'enable_screen_share':
        #tkinter.messagebox.showinfo('output','en share screen') #be sure to disable this later
        #print('screen en')
        Share_screen_handler.start_record_frame(self)
        #pass
      elif get == 'disable_screen_share':
        #tkinter.messagebox.showinfo('output','dis share screen')
        #print('screen dis')
        Share_screen_handler.close_record(self)
        #self.frame_display_list = self.screen_share_frame_list #checking mechanism ; buggy 
        #pass
      elif get == 'enable_show_frame':
        Share_screen_handler.start_frame_dispaly(self)
        #pass
      elif get == 'disable_show_frame':
        Share_screen_handler.close_display(self)
        #pass
      elif get == 'enable_mic':
        #tkinter.messagebox.showinfo('output','en mic')
        #print('mic en')
        Audio_mic_handler.start_audio_record(self)
        #pass
      elif get == 'disable_mic':
        #tkinter.messagebox.showinfo('output','dis mic')
        #print('mic dis')
        Audio_mic_handler.close_audio_record(self)
        #pass
      elif get == 'enable_audio':
        #tkinter.messagebox.showinfo('output','en audio')
        #print('audio en')
        Audio_mic_handler.start_audio_play(self)
        #pass
      elif get == 'disable_audio':
        #tkinter.messagebox.showinfo('output','dis audio')
        #print('audio dis')
        Audio_mic_handler.close_audio_play(self)
        #pass
      elif get =='enable_client':
        Communication_handler.start_client(self)
      elif get == 'disable_client':
        Communication_handler.close_client(self)
      elif get == 'enable_server':
        Communication_handler.start_server(self)
      elif get == 'disable_server':
        Communication_handler.close_server(self)

    Share_screen_handler.close_display(self)
    Share_screen_handler.close_record(self)
    Audio_mic_handler.close_audio_play(self)
    Audio_mic_handler.close_audio_record(self)
    Communication_handler.close_client(self)
    Communication_handler.close_server(self)
    try:
      self.join_audio_play()
    except:
      print('audio play not yet started')
    try:
      self.join_audio_record()
    except:
      print('audio record not yet started')
    try:
      self.join_display()
    except:
      print('screen share display not yet started')
    try:
      self.join_record()
    except:
      print('screen share record not yet started')
    try:
      self.join_client_process()
    except:
      print('client not yet started')
    try:
      self.join_server_process()
    except:
      print('server not yet started')


  def close(self):
    self.lock.acquire()
    self.continuity_signal_list[0] = False
    self.lock.release()
    print('closing process handler')

  def join(self):
    self.p_handler.join()
    print('process handler has joined main')




class Group_handler():
  def __init__( self , root):
    self.root = root
    self.user = None
    self.ip = None
    self.port = None
    self.password = None
    self.create_stat = False
    self.join_stat = False

  def group_window(self):
    self.group_win = Toplevel(self.root)
    self.group_win.title('Group Configure')
    self.group_win.geometry('500x300')
    self.group_win.grab_set()
    self.group_win.configure(bg = '#404040')
    self.group_win.resizable(False,False)
    self.lb_user = Label(self.group_win , text = 'Username:' , bg = '#404040' , fg = '#FFFFFF')
    self.lb_ip = Label(self.group_win , text = 'IP:' , bg = '#404040' , fg = '#FFFFFF')
    self.lb_port = Label(self.group_win , text = 'Port:' , bg = '#404040' , fg = '#FFFFFF')
    self.lb_pass = Label(self.group_win , text = 'Password:' , bg = '#404040' , fg = '#FFFFFF')
    self.t_user = Text(self.group_win , height =1 , width =30 , bg = '#A0A0A0' ,fg = '#FFFFFF' , border = 0 )
    self.t_ip = Text(self.group_win , height =1 , width =30 , bg = '#A0A0A0' ,fg = '#FFFFFF' , border = 0 )
    self.t_port = Text(self.group_win , height =1 , width =30 , bg = '#A0A0A0' ,fg = '#FFFFFF' , border = 0 )
    self.t_pass = Text(self.group_win , height =1 , width =30 , bg = '#A0A0A0' ,fg = '#FFFFFF' , border = 0 )
    self.bt_join = Button(self.group_win , text = 'Join' , bg = '#808080' , fg = '#FFFFFF' , activebackground = '#585858' , activeforeground = '#FFFFFF' , border = 0 , height = 1 , width = 15 , command = self.bt_join_action)
    self.bt_create = Button(self.group_win , text = 'Create' , bg = '#808080' , fg = '#FFFFFF' , activebackground = '#585858' , activeforeground = '#FFFFFF' , border = 0 , height = 1 , width = 15 , command = self.bt_create_action)
    self.bt_disconnect = Button(self.group_win , text = 'Disconnect' , bg = '#808080' , fg = '#FFFFFF' , activebackground = '#585858' , activeforeground = '#FFFFFF' , border = 0 , height = 1 , width = 15 , command = self.bt_disconnect_action)
    self.lb_user.place(x=50,y=50)
    self.lb_ip.place(x= 50 , y=90)
    self.lb_port.place(x= 50 , y=130)
    self.lb_pass.place(x= 50 , y=170)
    self.t_user.place(x= 140 ,y=50)
    self.t_ip.place(x= 140 ,y=90)
    self.t_port.place(x= 140 ,y=130)
    self.t_pass.place(x= 140 ,y=170)
    self.bt_join.place(x = 50 , y = 230)
    self.bt_create.place(x = 190 , y = 230)
    self.bt_disconnect.place(x = 330 , y = 230)

  def get_all_info(self):
    self.user = self.t_user.get("1.0",'end-1c')
    self.ip = self.t_ip.get("1.0",'end-1c')
    self.port = self.t_port.get("1.0",'end-1c')
    self.password = self.t_pass.get("1.0",'end-1c')
    if self.user == '' and self.ip == '' and self.port == '' and self.password == '':
      tkinter.messagebox.showinfo('Error!','Please enter appropriate values for each label given')
      self.ip , self.port , self.user , self.password = None , None , None , None
      return False
    if self.port.isdigit() and int(self.port) > 1000 and int(self.port) < 65535:
      self.port = int(self.port)
    else:
      self.port = None
      tkinter.messagebox.showinfo('Error!','Please enter a valid port value')
    if self.ip == 'localhost' or (self.ip.replace('.','').isdigit() and  len([int(st) for st in list(map(str,self.ip.split('.'))) if int(st) >=0 and int(st)<256]) == 4 ):
      pass
    else:
      self.ip = None
      tkinter.messagebox.showinfo('Error!','Please check the IP address value')
    #if self.user == '' and self.ip == '' and self.port == '' and self.password == '':
      #tkinter.messagebox.showinfo('Error!','Please enter appropriate values for each label given')
      #self.ip , self.port , self.user , self.password = None , None , None , None
    print(self.user , self.ip , self.port , self.password)
    if self.user != None and self.ip != None and self.port != None and self.password != None:
      return True
    else:
      return False


  def bt_join_action(self):
    if not self.create_stat:
      if self.get_all_info():
        self.join_stat = True
      #else:
        #tkinter.messagebox.showinfo('Error!','please Enter values')
    else:
      tkinter.messagebox.showinfo('Error!','Please disconnect this group before attempting to join')
    #pass


  def bt_create_action(self):
    if not self.join_stat:
      if self.get_all_info():
        self.create_stat = True
      #else:
        #tkinter.messagebox.showinfo('Error!','please enter values')
    else:
      tkinter.messagebox.showinfo('Error!','Please close disconnect before creating a group')
    #pass

  def bt_disconnect_action(self):
    if not self.join_stat and not self.create_stat:
      tkinter.messagebox.showinfo('Error!' , 'You have not joined or created any groups!')
    elif self.join_stat:
      self.join_stat = False #disconnect the from the group 
      tkinter.messagebox.showinfo('Info','Disconnected from the group')
    elif self.create_stat:
      self.create_stat = False #disconnect the group
      tkinter.messagebox.showinfo('Info','Closed the group')
    #pass






class List_handler():

  def __init__(self, root):
    self.root = root
    self.user_to_view = None
    self.view_user_stat = False

  def list_window(self):
    self.list_win = Toplevel(self.root)
    self.list_win.geometry('400x150')
    self.list_win.grab_set()
    self.list_win.title('Select User')
    self.list_win.resizable(False,False)
    self.list_win.configure(bg = '#404040')
    self.lb_user = Label(self.list_win , text = 'View User:' , bg = '#404040' , fg = '#FFFFFF')
    self.t_user_view = Text(self.list_win , height =1 , width =30 , bg = '#A0A0A0' ,fg = '#FFFFFF' , border = 0 )
    self.bt_view = Button(self.list_win , text = 'View' , bg = '#808080' , fg = '#FFFFFF' , activebackground = '#585858' , activeforeground = '#FFFFFF' , border = 0 , height = 1 , width = 15 , command = self.get_user_to_view)
    self.lb_user.place(x = 50 , y = 50)
    self.t_user_view.place( x = 130 , y = 50)
    self.bt_view.place(x=150 , y= 100)

  def get_user_to_view(self):
    self.user_to_view = self.t_user_view.get("1.0",'end-1c')
    self.view_user_stat = True
    if self.user_to_view == 'none':
      self.view_user_stat = False
    print(self.user_to_view)





class Frame1_bt_handler(Group_handler,List_handler):

  def __init__(self, root , obj_process_handler):
    self.obj_process_handler = obj_process_handler
    self.root_this = root
    self.share_val = 0
    self.mic_val = 0
    self.audio_val = 0
    Group_handler.__init__(self,root)
    List_handler.__init__(self,root)

 
  def set_share_bt(self,bt):
    self.bt_share_pic = bt

  def set_mic_bt(self, bt):
    self.bt_mic_pic = bt

  def set_audio_bt(self,bt):
    self.bt_audio_pic = bt
    
  def bt_group(self):
    Group_handler.group_window(self)


  def bt_share(self):
    if self.share_val == 0 and (self.create_stat or self.join_stat):
       self.share_val =1
       self.img_share = PhotoImage(file = 'C:\\Users\\username\\Desktop\\communication_app_pic\\screen_share.png').subsample(12,12)
       self.bt_share_pic.config(image = self.img_share )
       self.obj_process_handler.request_process('enable_screen_share')  # check and enable this later
    elif self.share_val == 1:
        self.share_val =0
        self.img_share = PhotoImage(file = 'C:\\Users\\username\\Desktop\\communication_app_pic\\screen_share_slashed.png').subsample(12,12)
        self.bt_share_pic.config(image = self.img_share )
        self.obj_process_handler.request_process('disable_screen_share')
        #self.obj_process_handler.request_process('enable_show_frame') #for checking purpose as noted above it is extremely buggy
    #print('hey')
    #self.root_this.update()
    #pass

  def bt_mic(self):
    if self.mic_val == 0 and (self.create_stat or self.join_stat):
      self.mic_val =1
      self.img_mic = PhotoImage(file = 'C:\\Users\\username\\Desktop\\communication_app_pic\\mic.png').subsample(12,12)
      self.bt_mic_pic.config(image = self.img_mic)
      self.obj_process_handler.request_process('enable_mic')
    elif self.mic_val == 1:
      self.mic_val = 0
      self.img_mic = PhotoImage(file = 'C:\\Users\\username\\Desktop\\communication_app_pic\\mic_slashed.png').subsample(12,12)
      self.bt_mic_pic.config(image = self.img_mic)
      self.obj_process_handler.request_process('disable_mic')


  def bt_audio(self):
    if self.audio_val == 0 and (self.create_stat or self.join_stat):
      self.audio_val =1
      self.img_audio = PhotoImage(file = 'C:\\Users\\username\\Desktop\\communication_app_pic\\audio.png').subsample(12,12)
      self.bt_audio_pic.config(image = self.img_audio)
      self.obj_process_handler.request_process('enable_audio')
    elif self.audio_val == 1:
      self.audio_val = 0
      self.img_audio = PhotoImage(file = 'C:\\Users\\username\\Desktop\\communication_app_pic\\audio_slashed.png').subsample(12,12)
      self.bt_audio_pic.config(image = self.img_audio)
      self.obj_process_handler.request_process('disable_audio')


  def bt_list(self):
    #List_handler.list_window(self)
    if self.join_stat or self.create_stat:
      List_handler.list_window(self)
    #print(self.user_to_view) #test to see if we can get the variables value; it works we can use it
 






class Frame1():
    
  def __init__(self,root):
    #global root
    self.frame1 = Frame(root, height = 50 , width  = 400 , bg = '#404040')
    self.gui_list_frame1 = []
    self.img1 = PhotoImage(file = 'C:\\Users\\username\\Desktop\\communication_app_pic\\group.png').subsample(12,12)
    self.gui_list_frame1.append( Button(self.frame1,image = self.img1 , height = 5, width = 10 , bg ='#404040' , fg = '#A9A9A9' , activeforeground = '#A9A9A9' , activebackground = '#404040' , border = 0 , command = obj_bt.bt_group))
    self.img2 = PhotoImage(file = 'C:\\Users\\username\\Desktop\\communication_app_pic\\screen_share_slashed.png').subsample(12,12)
    self.gui_list_frame1.append( Button(self.frame1,image = self.img2 , height = 5, width = 10 , bg ='#404040' , fg = '#A9A9A9' , activeforeground = '#A9A9A9' , activebackground = '#404040' , border = 0 , command = obj_bt.bt_share))
    self.img3 = PhotoImage(file = 'C:\\Users\\username\\Desktop\\communication_app_pic\\mic_slashed.png').subsample(12,12)
    self.gui_list_frame1.append( Button(self.frame1,image = self.img3 , height = 5, width = 10 , bg ='#404040' , fg = '#A9A9A9' , activeforeground = '#A9A9A9' , activebackground = '#404040' , border = 0 , command = obj_bt.bt_mic))
    self.img4 = PhotoImage(file = 'C:\\Users\\username\\Desktop\\communication_app_pic\\audio_slashed.png').subsample(12,12)
    self.gui_list_frame1.append( Button(self.frame1,image = self.img4 , height = 5, width = 10 , bg ='#404040' , fg = '#A9A9A9' , activeforeground = '#A9A9A9' , activebackground = '#404040' , border = 0 , command = obj_bt.bt_audio))
    self.img5 = PhotoImage(file = 'C:\\Users\\username\\Desktop\\communication_app_pic\\listimg.png').subsample(12,12)
    self.gui_list_frame1.append( Button(self.frame1,image = self.img5 , height = 5, width = 10 , bg ='#404040' , fg = '#A9A9A9' , activeforeground = '#A9A9A9' , activebackground = '#404040' , border = 0 , command = obj_bt.bt_list))
    self.gui_list_frame1.append( Label(self.frame1,height= 3 , width =1, bg ='#404040') )
    self.frame1.grid(row =0, column =0 , sticky = N+S+E+W)
    Grid.rowconfigure(self.frame1 , 0 , weight = 1)
    for i in range(len(self.gui_list_frame1)):
      self.gui_list_frame1[i].grid(row = 0 ,column = i , sticky = N+S+E+W)
      Grid.columnconfigure(self.frame1, i , weight = 1)
    Grid.columnconfigure(self.frame1,len(self.gui_list_frame1)-1,weight =0 )
    


class Frame2():

  def __init__(self,root):
    self.text_update = False
    self.new_text_list = [[],[]]
    self.root = root
    self.frame2 = Frame(root, height = 500, width = 400 , bg = '#404040')
    self.msg_box = Text(self.frame2 , height = 10 ,width = 100 , bg = '#505050' ,border = 0 , fg = '#FFFFFF' , font=("Helvetica", 15))
    #self.msg_box.insert(END , 'test string plz remove later !!!')
    self.msg_box.tag_config('User' , foreground  = '#FFFF00')
    self.msg_box.configure(state = 'disabled')
    self.frame2.grid(row =1, column =0 , sticky = N+S+E+W)
    self.msg_box.grid(row =0, column =0 , sticky = N+S+E+W)
    Grid.columnconfigure(self.frame2,0,weight =1)
    Grid.rowconfigure(self.frame2,0,weight =1)

  def change_text(self,msg_new_list):
    self.new_text_list = msg_new_list
    if self.text_update == True:
      self.msg_box.configure(state = NORMAL)
      self.msg_box.delete(1.0,END)
      user_names = self.new_text_list[0]
      user_msg = self.new_text_list[1]
      for i in range(len(user_names)):
        self.msg_box.insert(END, '\n\n'+user_names[i]+':\n\n','User')
        self.msg_box.insert(END, user_msg[i]+'\n')
        for i in range(50):
          self.msg_box.insert(END, ' -')
      self.msg_box.see(END)
      self.msg_box.configure(state = 'disabled')
      self.text_update = False





class Frame3():

  def __init__(self, root):
    self.msg_to_send = ''
    self.msg_send_state = True
    self.frame3 = Frame(root, height = 100, width = 400 , bg = '#505050')
    self.text_box =  Text(self.frame3 ,height = 5 ,width =30 , bg ='#404040' , border = 0 ,fg = '#FFFFFF' , font=("Helvetica", 12))
    self.img1 = PhotoImage(file = 'C:\\Users\\username\\Desktop\\communication_app_pic\\send.png').subsample(7,7)
    self.bt_send = Button(self.frame3, image = self.img1 ,height = 5 , width =100 , bg = '#505050' , border = 0 , activebackground = '#505050' , command = self.get_send_msg)
    self.lb_space1 = Label(self.frame3 , bg = '#505050' , height = 5 ,width = 1)
    self.lb_space2 = Label(self.frame3 , bg = '#505050' , height = 5 ,width = 1)
    self.lb_space3 = Label(self.frame3 , bg = '#505050' , height = 1 ,width = 1)
    self.frame3.grid(row = 2 , column = 0 , sticky = N+S+E+W)
    self.lb_space2.grid(row = 0 ,column = 0 ,sticky = N+S+E+W)
    self.text_box.grid(row =0 , column = 1, sticky = N+S+E+W)
    self.bt_send.grid(row = 0, column = 2 , sticky = N+S+E+W)
    self.lb_space1.grid(row =0 , column = 3 , sticky = N+S+E+W)
    self.lb_space3.grid(row = 1 , column = 0 , sticky = N+S+E+W)
    #self.lb_space2.grid(row = 0 ,column = 0 ,sticky = N+S+E+W)
    Grid.columnconfigure(self.frame3,0,weight =0)
    Grid.columnconfigure(self.frame3,1,weight =1 )
    Grid.columnconfigure(self.frame3,2,weight =0 )
    Grid.columnconfigure(self.frame3,3,weight =0 )
    Grid.rowconfigure(self.frame3,0,weight =1)
    Grid.rowconfigure(self.frame3,1,weight =0)

  def get_send_msg(self):
    if self.msg_send_state:
      self.msg_to_send = self.text_box.get("1.0",'end-1c')
      self.text_box.delete(1.0,END)
      #print(self.msg_to_send)
      self.msg_send_state = False #need to check this value and only if it is False send the msg also after sending need to change it to True
      #return msg_to_send
    else:
      tkinter.messagebox.showinfo('Error!','An error has been encountered, unable to send message please try again later')
    

if __name__ == '__main__':
  root.title('Safe Link')
  root.geometry('1000x600')
  obj_frame = []
  multi_lock = multiprocessing.Lock()
  multi_list_manager = multiprocessing.Manager()
  thread_lock = threading.Lock()
  obj_process_handler = Process_handler(multi_list_manager,multi_lock)
  obj_process_handler.start()
  obj_bt = Frame1_bt_handler(root , obj_process_handler)
  obj_frame.append( Frame1(root) )
  obj_frame.append( Frame2(root) )
  obj_frame.append( Frame3(root) )
  obj_update_routine = update_routine(obj_bt,obj_frame[1],obj_frame[2],thread_lock,multi_lock)
  obj_update_routine.start_update_routine()
  obj_bt.set_share_bt(obj_frame[0].gui_list_frame1[1])
  obj_bt.set_mic_bt(obj_frame[0].gui_list_frame1[2])
  obj_bt.set_audio_bt(obj_frame[0].gui_list_frame1[3])
  Grid.rowconfigure(root , 0 , weight = 0)
  Grid.rowconfigure(root , 1 , weight = 1)
  Grid.rowconfigure(root , 2 , weight = 0)
  Grid.columnconfigure(root , 0 ,weight = 1)
  root.mainloop()
  obj_process_handler.close()
  obj_process_handler.join()
  obj_update_routine.close_update_routine()
  obj_update_routine.join_update_routine()
