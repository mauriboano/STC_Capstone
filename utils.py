#!/usr/bin/env python
# coding: utf-8

from osgeo import gdal
import os
import numpy as np
import requests
import matplotlib.pyplot as plt
import pickle
from math import ceil
import simplekml
from google.colab import files

#check if we imported module
def test():
  """This function tests if we imported the module
  :rtype: None
  """
  print("Hello World")


def download_image(path, datadir = '/content/drive/MyDrive/MAXAR/', time = 'pre', disaster_folder_name = ''):
    
    """
    This function downloads one image from the MAXAR Open Data Program using the https://opendata.digitalglobe.com URL ending in .tif
    Data gets outputted to the provided datadir within the given disaster_name
    Function can be used by looping through a list of paths
    """

    filename = path.split("/")[-1:][0]

    r = requests.get(path, stream = True) 

    with open(datadir + disaster_folder_name + '/{}/{}'.format(time, filename), "wb") as file: 
        for block in r.iter_content(chunk_size = 1024): 
            if block: 
                file.write(block)
            
def plot_image(path):
    """
    This function is useful for plotting large .geotiffs
    NOTE: function plots a single band of data so colors will be off
    Useful for getting scale of the satellite image available when it cannot be opened by typical image processors
    """
    
    dataset = gdal.OpenEx(path, gdal.GA_ReadOnly) 
    # Note GetRasterBand() takes band no. starting from 1 not 0
    band = dataset.GetRasterBand(1)
    arr = band.ReadAsArray()
    plt.imshow(arr)
    
#function to check overlap between images
def overlap_check(post_path, pre_path):
    
    """
    This function checks whether two downloaded images share any overlapping area
    If so, it outputs a list containing the pre and post filepaths and the bounding box for the overlapping area in terms of latlongs
    Function can be used by looping over all combinations of pre and post images (double for loop)
    """
    
    # get post bounds
    post = gdal.Open(post_path)
    width = post.RasterXSize
    height = post.RasterYSize
    gt = post.GetGeoTransform()
    post_minx = gt[0]
    post_miny = gt[3] + width*gt[4] + height*gt[5] 
    post_maxx = gt[0] + width*gt[1] + height*gt[2]
    post_maxy = gt[3]

    # get pre bounds
    pre = gdal.Open(pre_path)
    width = pre.RasterXSize
    height = pre.RasterYSize
    gt = pre.GetGeoTransform()
    pre_minx = gt[0]
    pre_miny = gt[3] + width*gt[4] + height*gt[5] 
    pre_maxx = gt[0] + width*gt[1] + height*gt[2]
    pre_maxy = gt[3]

    # compare values
    check_minx = (post_minx <= pre_minx) & (post_maxx >= pre_minx)
    check_miny = (post_miny <= pre_miny) & (post_maxy >= pre_miny)
    check_maxx = (post_minx <= pre_maxx) & (post_maxx >= pre_maxx)
    check_maxy = (post_miny <= pre_maxy) & (post_maxy >= pre_maxy)

    # check if overlap exists
    overlap = (check_minx|check_maxx) & (check_miny|check_maxy)

    # get image names for output
    post_path_name = post_path.split("/")[7]
    pre_path_name = pre_path.split("/")[7]

    # get bounds of overlap, if it exists
    if overlap:
        if check_minx:
            overlap_minx = pre_minx
        else:
            overlap_minx = post_minx

        if check_miny:
            overlap_miny = pre_miny
        else:
            overlap_miny = post_miny

        if check_maxx:
            overlap_maxx = pre_maxx
        else:
            overlap_maxx = post_maxx

        if check_maxy:
            overlap_maxy = pre_maxy
        else:
            overlap_maxy = post_maxy

        print("Overlap found between: post/{} and pre/{}!".format(post_path_name, pre_path_name))
        return [post_path, pre_path, [overlap_minx, overlap_maxy, overlap_maxx, overlap_miny]]

def crop_images_iter(overlap, datadir = '/content/drive/MyDrive/MAXAR/', disaster_folder_name = '', pad = 0.0047, fringe = False):
    """
    This functions takes in the list provided by the `overlap_check` function and cuts large image pairs into many smaller image pairs with designated pad value
    Requires a datadir and disaster_folder_name
    Function can be used to cut all overlapping areas using a for loop
    Fringe value dictates whether we want to create additional pictures for overhang area of overlapping region that isn't captured by the final images along the right and bottom. WILL CAUSE DUPLICATED AREA TO BE COVERED, BUT IS THE ONLY WAY TO ENSURE 100% COVERAGE OF OVERLAP IS SEGMENTED INTO SMALLER IMAGES. Typically this won't be an issue because the borders of the overlapping region for at least one of the images will contain the black outskirts of the mask which contain no data. Recommended to leave as False.
    """
    
    post_path = overlap[0]
    pre_path = overlap[1]
    bbox = overlap[2]

    x_count = ceil(abs((bbox[0]-bbox[2])/pad))
    y_count = ceil(abs((bbox[1]-bbox[3])/pad))  

    if not fringe:
        x_count = x_count - 1
        y_count = y_count - 1

    post_path_name = post_path.split("/")[7].split(".")[0]
    pre_path_name = pre_path.split("/")[7].split(".")[0]
    #added exists = true so we still loop through other wise we get error.
    os.makedirs(datadir + disaster_folder_name+ '/iter_overlaps/post{}_pre{}'.format(post_path_name, pre_path_name), exist_ok=True)

    for i in range(y_count):
        for j in range(x_count):
            # add to leftmost range
            xmin = bbox[0] + (pad * j)
            xmax = bbox[0] + (pad * (j+1))

            # subtract from topmost range
            ymin = bbox[1] - (pad * (i+1))
            ymax = bbox[1] - (pad * i)

            if fringe:
                # check if we are in the extra region on the right and adjust accordingly
                if j+1 == x_count:
                    xmin = bbox[2] - pad
                    xmax = bbox[2]

                # check if we are in the extra region on the bottom and adjust accordingly
                if i+1 == y_count:
                    ymin = bbox[3] 
                    ymax = bbox[3] + pad

            bbox_iter = [xmin, ymax, xmax, ymin]

            post = gdal.OpenEx(post_path)
            post = gdal.Translate(datadir + disaster_folder_name + '/iter_overlaps/post{}_pre{}/{}-{}_post.png'.format(post_path_name, pre_path_name, j+1, i+1),
                              post,
                              projWin = bbox_iter,
                              maskBand = 'none',
                              format = 'PNG',
                              width = 480,
                              height = 480)

            post = None

            pre = gdal.OpenEx(pre_path)
            pre = gdal.Translate(datadir + disaster_folder_name+ '/iter_overlaps/post{}_pre{}/{}-{}_pre.png'.format(post_path_name, pre_path_name, j+1, i+1),
                              pre,
                              projWin = bbox_iter,
                              maskBand = 'none',
                              format = 'PNG',
                              width = 480,
                              height = 480)
            pre = None


            print('finished {}+{}, {}-{}'.format(post_path_name, pre_path_name, j+1, i+1))

def crop_images_rand(overlap, datadir = '/content/drive/MyDrive/MAXAR/', disaster_folder_name = '', pad = 0.0047):
    """
    This functions takes in the list provided by the `overlap_check` function and cuts a single, random small image pair from a large image pair with designated pad value
    Requires a datadir and disaster_folder_name
    Function can be used to cut many random samples of overlapping area
    Recommended that the `crop_images_iter` version be used for production (while `crop_images_rand` can be useful for testing)
    """
    post_path = overlap[0]
    pre_path = overlap[1]
    bbox = overlap[2]

    post_path_name = post_path.split("/")[7].split(".")[0]
    pre_path_name = pre_path.split("/")[7].split(".")[0]
    #added exists = true so we still loop through other wise we get error.
    os.makedirs(datadir + disaster_folder_name + '/rand_overlaps/post{}_pre{}'.format(post_path_name, pre_path_name), exist_ok=True)

    xmin = np.random.uniform(bbox[0], bbox[2]-pad)
    xmax = xmin+pad
    ymin = np.random.uniform(bbox[3], bbox[1]-pad)
    ymax = ymin + pad

    bbox_rand = [xmin, ymax, xmax, ymin]

    post = gdal.OpenEx(post_path)
    post = gdal.Translate(datadir + disaster_folder_name + '/rand_overlaps/post{}_pre{}/crop_post_{}.png'.format(post_path_name, pre_path_name, post_path_name),
                      post,
                      projWin = bbox_rand,
                      maskBand = 'none',
                      format = 'PNG',
                      width = 480,
                      height = 480)

    post = None

    pre = gdal.OpenEx(pre_path)
    pre = gdal.Translate(datadir + disaster_folder_name + '/rand_overlaps/post{}_pre{}/crop_pre_{}.png'.format(post_path_name, pre_path_name, pre_path_name),
                      pre,
                      projWin = bbox_rand,
                      maskBand = 'none',
                      format = 'PNG',
                      width = 480,
                      height = 480)
    pre = None


    print('finished {}+{}'.format(post_path_name, pre_path_name))
    

#example data
def downloadTurkeyEq(datadir):
  get_ipython().system(u'wget "https://opendata.digitalglobe.com/events/turkey-earthquake20/pre-event/2020-04-27/105001001CC33300/105001001CC33300.tif" -P datadir +"turkey_earthquake/pre"')
  get_ipython().system(u'wget "https://opendata.digitalglobe.com/events/turkey-earthquake20/pre-event/2020-04-27/105001001CC33200/105001001CC33200.tif" -P datadir +"turkey_earthquake/pre"')
  get_ipython().system(u'wget "https://opendata.digitalglobe.com/events/turkey-earthquake20/pre-event/2020-04-27/105001001CC33200/105001001CC33200.tif" -P datadir +"turkey_earthquake/pre"')
  get_ipython().system(u'wget "https://opendata.digitalglobe.com/events/turkey-earthquake20/pre-event/2020-07-14/10300500A4F8E700/10300500A4F8E700.tif" -P datadir +"turkey_earthquake/pre"')
  get_ipython().system(u'wget "https://opendata.digitalglobe.com/events/turkey-earthquake20/post-event/2020-11-03/1040010063C47D00/1040010063C47D00.tif" -P datadir +"turkey_earthquake/post"')
  get_ipython().system(u'wget "https://opendata.digitalglobe.com/events/turkey-earthquake20/post-event/2020-11-03/10400100625EF300/10400100625EF300.tif" -P datadir +"turkey_earthquake/post"')
  get_ipython().system(u'wget "https://opendata.digitalglobe.com/events/turkey-earthquake20/post-event/2020-11-05/10300100B07F8900/10300100B07F8900.tif" -P datadir +"turkey_earthquake/post"')
  get_ipython().system(u'wget "https://opendata.digitalglobe.com/events/turkey-earthquake20/post-event/2020-11-05/10300100B0552000/10300100B0552000.tif" -P datadir +"turkey_earthquake/post"')
  get_ipython().system(u'wget "https://opendata.digitalglobe.com/events/turkey-earthquake20/post-event/2020-11-07/10300100B0280300/10300100B0280300.tif" -P datadir +"turkey_earthquake/post"')
  get_ipython().system(u'wget "https://opendata.digitalglobe.com/events/turkey-earthquake20/post-event/2020-10-31/10300500AAF98600/10300500AAF98600.tif" -P datadir +"turkey_earthquake/post"')
  print("Downloaded Turkey Earthquake images")



def create_kml(overlaps, datadir = '/content/drive/MyDrive/MAXAR/', subfolder = 'kml', filename = '', region_color = '990000ff', download = True):
    """
    This function takes as input the list of overlaps and uses it to create a kml file that can be uploaded to Google Maps (or Google Earth)
    From there you can see on an interactive map which areas you have coverage for in the overlapping regions
    The end of the function prints directions to follow to work with the now downloaded .kml file
    """
    
    kml = simplekml.Kml()
    count = 1
    for i in overlaps:
        pol = kml.newpolygon(name="Overlap "+str(count),
                          outerboundaryis=[(i[2][0], i[2][1]), (i[2][2], i[2][1]), (i[2][2], i[2][3]), (i[2][0], i[2][3]), (i[2][0], i[2][1])])
        pol.style.polystyle.color = region_color  # default is transparent red
        count += 1
    kml.save(datadir+subfolder+"/"+filename+".kml")
    if download:
        files.download(datadir+subfolder+"/"+filename+".kml")
    
    print("""
    Once downloaded: \n\n
    -navigate to https://www.google.com/maps/d/ \n
    -click "+ CREATE A NEW MAP" button \n
    -click "Import" hyperlink in default first "Untitled layer" \n
    -upload .kml file from downloads folder \n
    \n 
    You can now see the various areas where we have available satellite imagery from before and after the event. Note that these overlapping areas can overlap because we have multiple pre and post image pairs that cover the same overlapping area.
    
    """)

