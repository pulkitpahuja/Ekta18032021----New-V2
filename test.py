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

import threading
import struct
import datetime
from fpdf import FPDF, HTMLMixin


global ser
ser = serial.Serial("COM3",9600,serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE,timeout=.3)

temp = 0
while(temp == 0):
    ext_trigg_bytes=ser.read(5)
    print(ext_trigg_bytes)
    ## 12,4,195,c1,c2
    ##low,high=checksum_func(ext_trigg_bytes)
    ##if (low&0xff==ext_trigg_bytes[4] and high&0xff==ext_trigg_bytes[3]):
    if(len(ext_trigg_bytes)>0):
        if(ext_trigg_bytes[0] == 0x0c and ext_trigg_bytes[1] == 4 and ext_trigg_bytes[2] == 0xc3):
            temp = 1
            print(ext_trigg_bytes)
