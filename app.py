from flask import Flask, render_template, Response, request, redirect, url_for,jsonify
import serial
import json
from webui import WebUI
import serial
import sys
import os
import random
import time
import csv
from dateutil.parser import parse

import threading
import struct
import datetime
from fpdf import FPDF, HTMLMixin
from datetime import date, timedelta

class HTML2PDF(FPDF, HTMLMixin):
    pass

global start 

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

createFolder('static/data_storage/')
createFolder('static/output/')
createFolder('static/csv/')

ser=0
flag={   "1":"False",
         "2":"False",
         "3":"False",
         "4":"False",
         "6":"False",
         "7":"False",
         "8":"False",
         "9":"False",
         "10":"False"}

app = Flask(__name__)
ui = WebUI(app, debug=True) 
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

byte_val={
         "1":bytearray([0x05,0x03,000,000,000,0x02,0xc5,0x8f]),                     ##20V
         "2":bytearray([0x08,0x03,000,000,000,0x02,0xc4,0x92]),                     ##30A
         "3":bytearray([0x03,0x03,000,000,000,0x04,0x45,0xeb]),                     ##kV
         "4":bytearray([0x07,0x03,000,000,000,0x02,0xc4,0x6d]),                     ##mA
         "5":bytearray([0x09,0x03,000,000,000,0x02,0xc5,0x43]),                     ##Insulation
         "6":bytearray([0x01,0x03,000,000,000,0x02,0xc4,0x0b]),                     ##Voltmeter
         "7":bytearray([0x0b,0x03,000,000,000,0x06,0xc5,0x62]),                     ##VAW
         "8":bytearray([0x02,0x03,000,000,000,0x02,0xc4,0x38]),                     ##MICRO
         "9":bytearray([0x04,0x03,000,000,000,0x02,0xc4,0x5e]),                     ##PF
         "10":bytearray([0x06,0x03,000,000,000,0x02,0xc5,0xbc]),                    ##FREQ
        }
@app.route('/')
@app.route('/<name>')
def hello(name=None):
    return render_template('main.html', name={"text":name}) 

def download_this_csv(result_data,name):
    result_data = json.loads(result_data)
    loc = 'static/csv/'+str(date.today())+'/single/'+str(result_data["device_id"])+"_"+str(result_data["datetime"])
    createFolder('static/csv/'+str(date.today())+'/single/')
    data_file = open(loc+'_data_file.csv', 'w',encoding="utf-8") 
    csv_writer = csv.writer(data_file) 
    header = ["Name","Result","Unit","Status"]
    csv_writer.writerow(header) 

    temp_list=[]

    for device in range(1,13):
        temp_dict={}

        temp_dict["Name"]=result_data[str(device)]["name"]
        temp_dict["Result"]=result_data[str(device)]["result"]
        temp_dict["Unit"]=result_data[str(device)]["param"]
        temp_dict["Status"]=result_data[str(device)]["status"]

    
        temp_list.append(temp_dict)
    
    
    for var in temp_list:

        csv_writer.writerow(var.values()) 
    
    data_file.close()  

    return "Success - Location = "+loc+'_data_file.csv'
    
    ##except :
  
def compute_float(bytes_rec):


    if (len(bytes_rec)==17):
        list1=[[bytes_rec[4],bytes_rec[3],bytes_rec[6],bytes_rec[5]],[bytes_rec[8],bytes_rec[7],bytes_rec[10],bytes_rec[9]],[bytes_rec[12],bytes_rec[11],bytes_rec[14],bytes_rec[13]]]
        final_val=list(struct.unpack('<f', bytearray(list1[0])))
        final_val1=list(struct.unpack('<f', bytearray(list1[1])))
        final_val2=list(struct.unpack('<f', bytearray(list1[2])))
        return [round(final_val[0],2),round(final_val1[0],2),round(final_val2[0],2)]

    if (len(bytes_rec)==13):
        list1=[[bytes_rec[4],bytes_rec[3],bytes_rec[6],bytes_rec[5]],[bytes_rec[8],bytes_rec[7],bytes_rec[10],bytes_rec[9]]]
        final_val=list(struct.unpack('<f', bytearray(list1[0])))
        final_val1=list(struct.unpack('<f', bytearray(list1[1])))
        return [round(final_val[0],2),round(final_val1[0],2)]

    else:
        list1=[bytes_rec[4],bytes_rec[3],bytes_rec[6],bytes_rec[5]]

        final_val=list(struct.unpack('<f', bytearray(list1)))
        return round(final_val[0],2)

def checksum_func(bytearray):

    if (len(bytearray)==17):

        checksum=(0xffff)
      
        for num in range(0,15):
            
            lsb=bytearray[num]
            checksum=(checksum^lsb)
            for count in range(1,9):
                
                lastbit=checksum&0x0001
                checksum=checksum>>1
              
                if (lastbit==1):
                    
                    checksum=checksum^0xa001
          
        lowCRC = checksum>>8
        checksum = checksum<<8
        highCRC = checksum>>8
      
        return(lowCRC,highCRC)

    elif (len(bytearray)==13):

        checksum=(0xffff)
      
        for num in range(0,11):
            
            lsb=bytearray[num]
            checksum=(checksum^lsb)
            for count in range(1,9):
                
                lastbit=checksum&0x0001
                checksum=checksum>>1
              
                if (lastbit==1):
                    
                    checksum=checksum^0xa001
          
        lowCRC = checksum>>8
        checksum = checksum<<8
        highCRC = checksum>>8
      
        return(lowCRC,highCRC)

    else:
            
        checksum=(0xffff)
      
        for num in range(0,7):

                
            lsb=bytearray[num]
            checksum=(checksum^lsb)
            for count in range(1,9):
                    
                lastbit=checksum&0x0001
                checksum=checksum>>1
            
                if (lastbit==1):
                        
                    checksum=checksum^0xa001
    
        lowCRC = checksum>>8
        checksum = checksum<<8
        highCRC = checksum>>8
      
        return(lowCRC,highCRC)

def cal_checksum_func(arr):

    checksum=(0xffff)
    for num in range(0,len(arr)):

        lsb=arr[num] % 256
        checksum=(checksum^lsb)
        for count in range(1,9):
            lastbit=(checksum&0x0001)% 256
            checksum=checksum>>1

            if (lastbit==1):
                checksum=checksum^0xa001

    lowCRC = (checksum>>8)% 256
    checksum = checksum<<8
    highCRC = (checksum>>8)% 256
    return(lowCRC,highCRC)

def run_and_get_data(secondMicro,truth,device,maximum,minimum,com):
    master_list=[]
    ser.flushInput()
    ser.flushOutput()
    global byte_val
    global list_bool
    global change_timer
    global bytes_rec
    global final_rec
    global final_val0
    device=int(device)

    ##################################
    if(device==3):
        byte_to_write=bytearray([0x0c,0x03,160+device,000,000,0x04])
        low,high=cal_checksum_func(byte_to_write)
        byte_to_write.append(high)
        byte_to_write.append(low)
        ser.write(byte_to_write)
        ser.flush()  
        time.sleep(.7)
    elif(device>=5 and device<=8 and secondMicro=="false"):
        byte_to_write=bytearray([0x0c,0x03,160+device-1,000,000,0x04])
        low,high=cal_checksum_func(byte_to_write)
        byte_to_write.append(high)
        byte_to_write.append(low)
        ser.write(byte_to_write)
        ser.flush()  
        time.sleep(.6)
    elif(device==8 and secondMicro=="true"):
        byte_to_write=bytearray([0x0c,0x03,160+device,000,000,0x04])
        low,high=cal_checksum_func(byte_to_write)
        byte_to_write.append(high)
        byte_to_write.append(low)
        ser.write(byte_to_write)
        ser.flush()  
        time.sleep(.6)
    elif(device == 1 or device == 2):
        byte_to_write=bytearray([0x0c,0x03,160+device,000,000,0x04])
        low,high=cal_checksum_func(byte_to_write)
        byte_to_write.append(high)
        byte_to_write.append(low)
        ser.write(byte_to_write)
        ser.flush()  
        time.sleep(.6)
    elif(device==10):
        byte_to_write=bytearray([0x0c,0x03,160+device-1,000,000,0x04])
        low,high=cal_checksum_func(byte_to_write)
        byte_to_write.append(high)
        byte_to_write.append(low)
        ser.write(byte_to_write)
        ser.flush()  
        time.sleep(.6)
    ##################################
    try:     
        if (device==7): 

            ser.write(byte_val[str(device)])   
            ser.flush()  
            time.sleep(.6)
            bytes_rec=ser.read(17)
            if (len(bytes_rec)<17):

                bytes_rec=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
              

        elif(device==3):
            ser.write(byte_val[str(device)])  
            ser.flush()   
            time.sleep(.6)
            
            bytes_rec=ser.read(13)
        
            if (len(bytes_rec)<13):
                bytes_rec=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
        
        else:
            print("Sending",byte_val[str(device)])
            ser.write(byte_val[str(device)])     
            ser.flush()
            time.sleep(.6)
            bytes_rec=ser.read(9)
        
            if (len(bytes_rec)<9):
                bytes_rec=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00])
          
          
        import re
        print("RECV",re.findall('..',bytes_rec.hex()))         
                
                
    except:
            
        if(device==7):
            bytes_rec=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
        
        elif(device==3):
            bytes_rec=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
        
        else:
            bytes_rec=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00])
        
    low,high=checksum_func(bytes_rec)
        
    if (device==7):                 ##VAW DEVICE
            
        if (low&0xff==bytes_rec[16] and high&0xff==bytes_rec[15]):

            final_rec=bytes_rec
            print("CHECKSUM MATCHED")
        else:

            new_byte=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
            final_rec=new_byte

    elif(device==3):                ##KV DEVICE
        if (low&0xff==bytes_rec[12] and high&0xff==bytes_rec[11]):

            final_rec=bytes_rec
            print("CHECKSUM MATCHED")
                 
        else:

            new_byte=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
            final_rec=new_byte
         
    else:
        if (low&0xff==bytes_rec[8] and high&0xff==bytes_rec[7]):

            final_rec=bytes_rec
            print("CHECKSUM MATCHED")
              
              
        else:

            new_byte=bytearray([0x00,0x00,000,000,000,0x00,0x00,0x00])
            final_rec=new_byte
              
####### EEE#########3
        
    if (device==7):
        i=0
        temp=2
        maximum = maximum.split(",")
        minimum=minimum.split(",")
        for val in compute_float(final_rec):
            print(compute_float(final_rec))
            if (val<=float(maximum[i]) and val>=float(minimum[i])):
                master_list.append(val)
                i+=1
            else:
                if (truth=="true" and temp==i):
                    to_write=bytearray([0x0b,0x03,155,000,000,0x04])
                    master_list.append(val)
                    low,high=cal_checksum_func(to_write)
                    to_write.append(high)
                    to_write.append(low)
                    ser.write(to_write)
                    time.sleep(.5)
                    print("RELAY ON")
                    temp=i
                    i+=1
                else:
                    i+=1
                    master_list.append(val)
                    pass
    elif (device==3):
        for val in compute_float(final_rec):
            master_list.append(val)
              
    else:
        if (compute_float(final_rec)<=float(maximum) and compute_float(final_rec)>=float(minimum)):
            final_val=compute_float(final_rec)
        else:
            final_val=compute_float(final_rec)
            if(truth=="true" and flag[str(device)]=="False"):
                to_write=bytearray([byte_val[str(device)][0],0x03,155,000,000,0x04])
                low,high=cal_checksum_func(to_write)
                to_write.append(high)
                to_write.append(low)
                ser.write(to_write)
                time.sleep(.5)
                print("RELAY On")
                flag[str(device)]="True"
            else:
                pass

    if (device==7):
        
        temp_dict={"vals":master_list}
        return json.dumps(temp_dict)

    if (device==3):
        
        temp_dict={"vals":master_list}
        return json.dumps(temp_dict)

    else:
        return final_val

def start_sequence(com):     ##turn 1st relay ON and 2nd relay OFF
    print("START SEQ")
    start = True
    to_write=bytearray([0x03,0x03,155,000,000,0x04])
    low,high=cal_checksum_func(to_write)
    to_write.append(high)
    to_write.append(low)   
    ser.write(to_write) 
    time.sleep(.5)
    
def stop_sequence(com): 
    time.sleep(.5)
     ##turn 1st relay OFF and 2nd relay ON
    to_write=bytearray([0x03,0x03,215,000,000,0x04])
    low,high=cal_checksum_func(to_write)
    to_write.append(high)
    to_write.append(low)   
    ser.write(to_write) 
    flag["1"]="False"
    global start
    start = False
    print("RELAY OFF",to_write)
    time.sleep(1)
    ###########################
    to_write=bytearray([0x0c,0x03,170,000,000,0x04])
    low,high=cal_checksum_func(to_write)
    to_write.append(high)
    to_write.append(low)
    ser.write(to_write)
    ser.flush()  
    time.sleep(1)
    
def run_serial(com):
    try:
        global ser
        
        ser = serial.Serial("COM"+com, 9600,serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE,timeout=1)
        time.sleep(.5)
        return "true"
    except :
        return "false"

def turn_off_device_relay(device,com):
    time.sleep(.5)
    to_write=bytearray([byte_val[str(device)][0],0x03,215,000,000,0x04])
    low,high=cal_checksum_func(to_write)
    to_write.append(high)
    to_write.append(low)   
    ser.write(to_write) 
    print("RELAY OFF",to_write)
    flag[str(device)]="False"
    time.sleep(1)

def get_dates(start_date,end_date):
    sdate = datetime.datetime.strptime(start_date, '%Y-%m-%d')   # start date
    edate = datetime.datetime.strptime(end_date, '%Y-%m-%d')   # end date
    print(sdate,edate)
    delta = edate - sdate       # as timedelta
    lst = []
    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        lst.append(day.strftime('%Y-%m-%d'))
    
    return lst

def overall_csv(data):
    print(data)
    x = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S%p")
    loc = 'static/csv/'+str(date.today())+'/Overall/'+str(x)
    createFolder('static/csv/'+str(date.today())+'/Overall/')
    data_file = open(loc+'_data_file.csv', 'w',encoding="utf-8") 
    csv_writer = csv.writer(data_file) 
    header = ["Device","20V","30A","kV","mA","Insulation","Voltmeter","VAW-V","VAW-A","VAW-W","MicroAmpere-1","PF","Freq.","MicroAmpere-2","Timestamp"]
    csv_writer.writerow(header) 
    temp_list=[]

    for obj in data:
        temp_dict={}
        temp_dict["Device"]=obj["device_id"]
        temp_dict["20V"] = str(obj["1"]["status"])
        temp_dict["30A"] = str(obj["2"]["status"])
        temp_dict["kV"] = str(obj["3"]["result"])
        temp_dict["mA"] = str(obj["4"]["status"])
        temp_dict["Insulation"] = str(obj["5"]["status"])
        temp_dict["Voltmeter"] = str(obj["6"]["status"])
        temp_dict["VAW-V"] = str(obj["7"]["status"])
        temp_dict["VAW-A"] = str(obj["8"]["status"])
        temp_dict["VAW-W"] = str(obj["9"]["status"])
        temp_dict["MicroAmpere-1"] = str(obj["10"]["status"])
        temp_dict["PF"] = str(obj["11"]["status"])
        temp_dict["Freq."] = str(obj["12"]["status"])
        try:
            temp_dict["MicroAmpere-2"] = str(obj["13"]["status"])
        except:
            temp_dict["MicroAmpere-2"] = str("__")

        temp_dict["Timestamp"]=obj["datetime"]
        temp_list.append(temp_dict)
    
    for var in temp_list:
        csv_writer.writerow(var.values()) 
    
    data_file.close()  

    return "Success - Location = "+loc+'_data_file.csv'

@app.route('/csv_dated',methods = ['GET', 'POST', 'DELETE'])
def csv_dated():
     if request.method == 'POST':
        data =request.get_json(force=True)
        print(data)
        start_date = data["start_date"]
        end_date = data["end_date"]
        print(start_date,end_date)
        lst = get_dates(start_date,end_date)
        to_send=[]
        for d in lst:
            try:
                files = os.listdir('./static/output/'+d+'/')
            except:
                return "Failure.Files For These Date Don't Exist"
            for file in files:
                with open('./static/output/'+d+'/'+file) as f:
                    json_data = json.load(f)
                    to_send.append(json_data)

        return overall_csv(to_send)
   
@app.route('/sequence_init',methods = ['GET', 'POST', 'DELETE'])
def sequence_init():
    if request.method == 'POST':
        data =request.form.to_dict()
        global start

        if(data["type"]=="start"):
            start = True
            start_sequence(data["com_port"])
        else:
            start = False
            stop_sequence(data["com_port"])

        return "500"


@app.route('/turn_off_relay',methods = ['GET', 'POST', 'DELETE'])
def turn_off_relay():  ## turn of individual device relay irrespective of state
    if request.method == 'POST':
        data =request.form.to_dict()

        turn_off_device_relay(data["device"],data["com_port"])

        return "OFF"

@app.route('/check_ext_trigg',methods = ['GET', 'POST', 'DELETE'])
def check_ext_trigg():  ## turn of individual device relay irrespective of state
    if request.method == 'POST':
        ##global ser
        ##ser = serial.Serial("COM"+com, 9600,serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE,timeout=1)
        temp = 0
        while(temp == 0):
            if(start==True):
                temp=1
            ext_trigg_bytes=ser.read(5)
            time.sleep(0.5)
            ## 12,4,195,c1,c2
            ##low,high=checksum_func(ext_trigg_bytes)
            ##if (low&0xff==ext_trigg_bytes[4] and high&0xff==ext_trigg_bytes[3]):
            if(len(ext_trigg_bytes)>0):
                if(ext_trigg_bytes[0] == 0x0c and ext_trigg_bytes[1] == 4 and ext_trigg_bytes[2] == 0xc3):
                    temp = 1
        return "1"

@app.route('/check_stop_trigg',methods = ['GET', 'POST', 'DELETE'])
def check_stop_trigg():  ## turn of individual device relay irrespective of state
    if request.method == 'POST':
        ##global ser
        ##ser = serial.Serial("COM"+com, 9600,serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE,timeout=1)
        temp = 0
        while(temp == 0):
            ext_trigg_bytes=ser.read(5)
            ## 12,4,195,c1,c2
            ##low,high=checksum_func(ext_trigg_bytes)
            ##if (low&0xff==ext_trigg_bytes[4] and high&0xff==ext_trigg_bytes[3]):
            if(len(ext_trigg_bytes)>0):
                if(ext_trigg_bytes[0] == 0x0c and ext_trigg_bytes[1] == 4 and ext_trigg_bytes[2] == 0xc6):
                    temp = 1
        return "1"
    
@app.route('/get_fac_data',methods = ['GET', 'POST', 'DELETE'])
def get_fac_data():
    if request.method == 'POST':
        tempdict={"save_status":"Failed","transfer_status":"Failed"}
        data =request.form.to_dict()

        ##SERIAL PORT DATA TRANSFER TO METER TAKES PLACE HERE##
        try:
            with open('static/data_storage/'+data["calib_number"]+'.json', 'w') as outfile:
                json.dump(data, outfile)
            tempdict["save_status"]="Success"
        except:
            tempdict["save_status"]="Failed"

        return jsonify(tempdict)

@app.route('/save_curr_config',methods = ['GET', 'POST', 'DELETE'])
def save_curr_config():
    if request.method == 'POST':
        data =request.get_json(force=True)
        try:        
            with open('static/data_storage/'+data["device_id"]+'.json', 'w') as outfile:
                json.dump(data, outfile)
            return "Success"
        except:
            return "Failure"
        
@app.route('/save_result',methods = ['GET', 'POST', 'DELETE'])
def save_result():
    if request.method == 'POST':
        global start
        start = False
        data =request.get_json(force=True)
        createFolder('static/output/'+str(date.today()))
        try:
            with open('static/output/'+str(date.today())+'/'+data["device_id"]+" " +data["datetime"]+'.json', 'w') as outfile:
                json.dump(data, outfile)
            return "Success"
        except:
            return "Failure"
  
@app.route('/load_data',methods = ['GET', 'POST', 'DELETE'])
def load_data():
    return render_template('load_data.html')      
              
        
        

@app.route('/load_config',methods = ['GET', 'POST', 'DELETE'])
def load_config():
    if request.method == 'POST':
        global start
        start = False
        data =request.form.to_dict()

        try:
            f = open("static/data_storage/"+data["device_id"]+".json",) 
            data_ext = json.load(f) 

            return jsonify(data_ext)
        except:
            return "No File Found"

@app.route('/connected',methods = ['GET', 'POST', 'DELETE'])
def connected():
    global start
    start = False
    if request.method == 'POST':
        data =request.form.to_dict()
        
        return run_serial(data["com_port"])


@app.route('/run_task',methods = ['GET', 'POST', 'DELETE'])
def run_task():
    if request.method == 'POST':
        data =request.form.to_dict()
        if(data["secondMicro"]=="true"):
            val=run_and_get_data("true",data["truth"],data["device"],data["maximum"],data["minimum"],data["com"])
        else:
            val=run_and_get_data("false",data["truth"],data["device"],data["maximum"],data["minimum"],data["com"])
        return str(val)

@app.route('/download_csv',methods = ['GET', 'POST', 'DELETE'])
def download_csv():
    if request.method == 'POST':
        data =request.get_json(force=True)
        print(data["name"])
        return download_this_csv(data["data"],data["name"])
   

        
if __name__ == "__main__":
    ui.run()        
        

        
