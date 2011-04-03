#!/usr/bin/env python
# encoding: utf-8
"""
censusgeodownload.py

Created by Matthew Waite on 2011-04-02.

"""
import os
from ftplib import FTP
import zipfile

def handleDownload(block):
    file.write(block)

def unzipper():
    current = os.getcwd()
    files = os.listdir(current)
    for archive in files:
        try:
            fh = open(archive, 'rb')
            z = zipfile.ZipFile(fh)
            for name in z.namelist():
                outfile = open(name, 'wb')
                outfile.write(z.read(name))
                outfile.close()
            fh.close()
        except:
            continue

states = ["01", "02", "04", "05", "06", "08", "09", "10", "11", "12", "13", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "44", "45", "46", "47", "48", "49", "50", "51", "53", "54", "55", "56", "60", "66", "72", "78"]

geos = [('states', 'geo/tiger/TIGER2010/STATE/2010/', 'us', 'state10'), ('counties', '/geo/tiger/TIGER2010/COUNTY/2010/', 'us', 'county10'), ('county-subdivisions', '/geo/tiger/TIGER2010/COUSUB/2010/', 'state', 'cousub10'), ('places','/geo/tiger/TIGER2010/PLACE/2010/', 'state', 'place10'), ('tracts','/geo/tiger/TIGER2010/TRACT/2010/', 'state', 'tract10')]
    
# Connect to the Census FTP server
ftp = FTP('ftp2.census.gov')
ftp.login()

for level in geos:
    if os.path.exists(level[0]):
        pass
    else:
        os.mkdir(level[0])

    os.chdir(level[0])
    # Set the current FTP directory
    ftp.cwd(level[1])
    
    if level[2]!="state":
        filename = "tl_2010_"+level[2]+"_"+level[3]+".zip"
        print 'Opening local file ' + filename
        file = open(filename, 'wb')
        print 'Getting ' + filename
        ftp.retrbinary('RETR ' + filename, handleDownload)
        print 'Closing file ' + filename
        file.close()
    else:
        for state in states:
            try:
                filename = "tl_2010_"+state+"_"+level[3]+".zip"
                print 'Opening local file ' + filename
                file = open(filename, 'wb')
                print 'Getting ' + filename
                ftp.retrbinary('RETR ' + filename, handleDownload)
                print 'Closing file ' + filename
                file.close()
            except:
                continue

    unzipper()
    os.chdir('..')

print ftp.close()