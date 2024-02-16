#!/usr/bin/env python

"""
Read in a raster image and polygon shapefile and perform zonal statstic analysis and return a csv of the results for each band in the raster file. This script has been adapted to be run by the cal_val_stats jupyter notebook. 

It is used to extract out the fractional cover stats from imagery for the intergrated monitoring sites.


Author: Grant Staben
Modified Date: 18/11/2021

"""
from __future__ import print_function, division
import pdb
import fiona
import rasterio
import pandas as pd 
import argparse
from rasterstats import zonal_stats 
import sys
import os
import shutil
import glob



def getCmdargs():

    p = argparse.ArgumentParser(description="""Input a single or multiband raster to calcluate zonal statistics from the input shapefile. The script currently outputs a csv file containing the unique identifyer for each polygon, mean, std, median, min, max and count statstics for each polygon.""")

    p.add_argument("-i","--image", help="Input image to derive zonal stats from")
    
    p.add_argument("-a","--alltouch", default=False, help="select either True of False, True will increase the number of pixels used to produce the stats False reduces the number (default is %(default)s))")
        
    p.add_argument("-n","--nodata",default=None, help="define the no data value for the input raster image, the default is none (default is %(default)s))")
    
    p.add_argument("-s","--shape", help="shape file contiaing the zones needs to have a field defined as id")
    
    p.add_argument("-u","--uid", help="input the column name for the unique id field in the shapefile") 
    
    p.add_argument("-o","--csv", help="name of the output csv file containing the results")
    
    cmdargs = p.parse_args()
    
    if cmdargs.image is None:

        p.print_help()

        sys.exit()

    return cmdargs


def applyZonalstats(image,param, nodata, band, shape): # uid):
        
    """
    function to derive zonal stats for a single or multi band raster image
    """    
    # create an empty lists to write the results 
            
    zonestats = []
    siteID = []
    image_Name = []
    nodata = nodata
    
    with rasterio.open(image, nodata=nodata) as srci:
        affine = srci.transform
        array = srci.read(band)
        
        with fiona.open(shape) as src:
            
            zs = zonal_stats(src, array, affine=affine,nodata=nodata,stats=['count', 'min', 'max', 'mean','median','std'],all_touched=param) # using "all_touched=True" will increase the number of pixels used to produce the stats "False" reduces the number
                        
            # extract the image name from the opened file from the input file read in by rasterio
            imgName1 = str(srci)[:-11]
            imgName = imgName1[-43:] 
            imgDate = imgName[16:20]      
            #lztrme_p104r068_1987median_chm.img

            for zone in zs:
                zone_stats = zone
                count = zone_stats["count"]
                mean = zone_stats["mean"]
                Min = zone_stats["min"]
                Max = zone_stats['max']
                med = zone_stats['median']
                std = zone_stats['std']

                # put the individual results in a list and append them to the zonestats list
                result = [mean,std, med, Min, Max, count]
                zonestats.append(result)
                            
            # extract out the site number for the polygon
            for i in src:
                table_attributes = i['properties'] # reads in the attribute table for each record 
                        
                uid = table_attributes['uid']
                site = table_attributes['Site']
                obs_time = table_attributes['Date']
                long = table_attributes['C_Lon']
                lat = table_attributes['C_Lat']
                
                fpc = table_attributes['FPC']
                pers = table_attributes['PPC']
                crn = table_attributes['CC'] 
                
                bgg = table_attributes['BG']
                pvg = table_attributes['PVg'] 
                npvg = table_attributes['NPVg']
                pv = table_attributes['PV']          
                npv = table_attributes['NPV']
                bg = table_attributes['BG']
                ba_t = table_attributes['ba_trees']
                ba_s = table_attributes['ba_shrubs']
                ba_t = table_attributes['ba_total'] 
                #mid_b = table_attributes['mid_b']
                
                #over_g = table_attributes['over_g']
                #over_d = table_attributes['over_d']
                #over_b = table_attributes['over_b'] 
                #num_pts = table_attributes['num_points'] 
                #unoc = table_attributes['unoccluded'] 
                #obs_key = table_attributes['obs_key'] 
                         

                
                
                #site = table_attributes[uid] # reads in the id field from the attribute table and prints out the selected record 
                details = [uid, site, obs_time, long, lat, fpc, pers, crn, pvg, npvg, bgg, pv, npv, bg, ba_t, ba_s, ba_t]
                siteID.append(details)
                
                imageUsed = [imgName]
                image_Name.append(imageUsed)

        # join the elements in each of the lists row by row 
        finalresults =  [siteid + imU + zoneR for siteid, imU, zoneR in zip(siteID, image_Name, zonestats)]                     
        
        # close the vector and raster file 
        src.close() 
        srci.close() 

        # print out the file name of the processed image
        #print ((imgName1 + ' ' + 'band' + ' ' + str(band) + ' ' + 'is' + ' ' + 'complete')) 
                
    return(finalresults)


def mainRoutine():
        
    # read in the command arguments
    cmdargs = getCmdargs()
    image = cmdargs.image
    param = cmdargs.alltouch
    nodata= int(cmdargs.nodata)
    shape = cmdargs.shape 
    #uid = cmdargs.uid
    export_csv = cmdargs.csv
    
    # make a temp dir to save the individual band results 
    
    # make a temp dir to save the individual band results 
    tempIDir = './temp_individual_bands'
    
    # check if the temp dir exists and if it does remove it, otherwise create the new dir for the individual outputs
    check_if_dir_exists = os.path.isdir(tempIDir)
    if check_if_dir_exists == True:
        shutil.rmtree(tempIDir)
    else:    
        os.makedirs(tempIDir)
        
    with rasterio.open(image, nodata=nodata) as srci:
        
        bands = srci.indexes # this will return the number of spectral band for the input raster image as a tuple
        num_bands = len(bands)
    
    for band in bands:
        
        # creates the individual band csv file name
        bandResults = 'band_'+str(band)+'.csv'

        # run the zonal stats function 
        finalresults = applyZonalstats(image, param, nodata, band,shape) #, uid)
        
        # write out the individual band results to a list
        
        outputlist = []
        
        for i in finalresults:
        
            outputlist.append(i)    
        
        # convert the list to a pandas dataframe with a headers identifying the band number being processed
        headers = ['uid', 'Site', 'obs_time', 'longitude', 'latitude', 'FPC', 'PPC','CC', 'PVg', 'NPVg', 'BGg','PV', 'NPV', 'BG', 'ba_trees','ba_shrubs','ba_total','imName','mean_'+ str(band),'std_'+ str(band), 'median_'+ str(band), 'Min_'+ str(band),'Max_'+ str(band), 'count_'+ str(band)]
                                  
        output  = pd.DataFrame.from_records(outputlist,columns=headers)
              
        output.to_csv(tempIDir + '/'+ bandResults,index=False)
          
    
    # read in the individual band results and concatenate them to a single dataframe
    all_files = glob.glob(os.path.join(tempIDir, "*.csv"))     # advisable to use os.path.join as this makes concatenation OS independent
    
    df_from_each_file = (pd.read_csv(f) for f in all_files)
    concatenated_df   = pd.concat(df_from_each_file,ignore_index=False, axis=1)
    # export the results to a csv file
    concatenated_df = concatenated_df.loc[:,~concatenated_df.columns.duplicated()]
    concatenated_df.to_csv(export_csv) 
    
    # remove the temp dir and single band csv files
    shutil.rmtree(tempIDir)
    
    
if __name__ == "__main__":
    mainRoutine()   