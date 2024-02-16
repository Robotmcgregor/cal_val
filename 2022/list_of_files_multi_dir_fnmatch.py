#!/usr/bin/env python
"""
This script finds all the files based on the end of the file name in a given folder and sub folders
and returns a list showing the path and file based on the part file name given using fnmatch. 


Created on Wed Jan 13 10:41:41 2016

Grant Staben

Modified: 15/11/2021
"""

import fnmatch
import os
import argparse
import sys
import csv
import fnmatch

def getCmdargs():
    """
    Command line arguments to indentify the directory and the file extentin to create a list for
    """
    p = argparse.ArgumentParser()

    p.add_argument("-d","--direc", help="path to directory to look in")
    
    p.add_argument("-e","--endfilen", help="end of the file name e.g. h99m2.img")

    p.add_argument("-o","--txtfile", help="name of out put txt file containing the list of files")
    
    
    cmdargs = p.parse_args()
    
    if cmdargs.direc is None:

        p.print_help()

        sys.exit()

    return cmdargs
    


def listdir(dirname,endfilename):
    """
    this function will return a list of files in a directory for the given file extention. 
    """
    list_img = []
    
    
    for root, dirs, files in os.walk(dirname):
        for file in files:
            if fnmatch.fnmatch(file, endfilename):
                img = (os.path.join(root, file))
                list_img.append(img)
                print (img)
    
    return list_img

   
def mainRoutine():
    
    cmdargs = getCmdargs() # instantiate the get command line function
    
    direc = cmdargs.direc 
    endfilename = cmdargs.endfilen
    
    txtname = cmdargs.txtfile
    
 
    list_img = listdir(direc,endfilename)
     
    
    # assumes that filelist is a flat list, it adds a  
    with open(txtname, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        for file in list_img:
            writer.writerow([file])

if __name__ == "__main__":
    mainRoutine()
