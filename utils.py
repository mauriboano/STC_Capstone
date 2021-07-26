#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from osgeo import gdal
import os
import numpy as np
import requests
import matplotlib.pyplot as plt
import pickle


# In[ ]:


#todo make this default if no datadir passed
defaultDataDir = '/content/drive/MyDrive/MAXAR/'


# In[ ]:


#check if we imported module
def test():
  """This function tests if we imported the module
  :rtype: None
  """
  print("Hello World")


# In[ ]:


#crop images
def crop_images_rand(datadir, overlap, pad = 0.0047):
  post_path = overlap[0]
  pre_path = overlap[1]
  bbox = overlap[2]

  post_path_name = post_path.split("/")[7].split(".")[0]
  pre_path_name = pre_path.split("/")[7].split(".")[0]
  #added exists = true so we still loop through other wise we get error.
  os.makedirs(datadir + 'hurricane_florence/testfolder/post{}_pre{}'.format(post_path_name, pre_path_name), exist_ok=True)
  # os.makedirs(datadir + 'hurricane_florence/overlaps/post{}_pre{}'.format(post_path_name, pre_path_name), exist_ok=True)

  xmin = np.random.uniform(bbox[0], bbox[2]-pad)
  xmax = xmin+pad
  ymin = np.random.uniform(bbox[3], bbox[1]-pad)
  ymax = ymin + pad

  bbox_rand = [xmin, ymax, xmax, ymin]

  post = gdal.OpenEx(post_path)
  post = gdal.Translate(datadir + 'hurricane_florence/testfolder/post{}_pre{}/crop_post_{}.png'.format(post_path_name, pre_path_name, post_path_name),
                      post,
                      projWin = bbox_rand,
                      format = 'PNG',
                      width = 480,
                      height = 480)
  
  post = None

  pre = gdal.OpenEx(pre_path)
  pre = gdal.Translate(datadir +'hurricane_florence/testfolder/post{}_pre{}/crop_pre_{}.png'.format(post_path_name, pre_path_name, pre_path_name),
                      pre,
                      projWin = bbox_rand,
                      format = 'PNG',
                      width = 480,
                      height = 480)
  pre = None

  
  print('finished {}+{}'.format(post_path_name, pre_path_name))


# In[ ]:


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


# In[ ]:


#Currently assumes all folders/subfolderes exist
def download_image(datadir, path, event = "", time = "pre"):
  
  filename = path.split("/")[-1:][0]

  r = requests.get(path, stream = True) 
  
  with open(datadir + event + "/{}/{}".format(time, filename), "wb") as file: 
      for block in r.iter_content(chunk_size = 1024): 
          if block: 
              file.write(block)


# In[ ]:


#function to check overlap between images
def overlap_check(post_path, pre_path):
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

  # else:
    # print("\n no overlap found between: post/{} and pre/{}".format(post_path_name, pre_path_name))


# In[ ]:


#TODO
def pre_post_Overlaps():
  # Calc overlaps for all pre post images

  if calcOverlaps:
  #perform checks
    overlaps = []
    for i in post_images:
      for j in pre_images:
        check = utils.overlap_check(i, j)
        if check is not None:
          overlaps.append(check)
      #print("post image "+i+" comparisons done")
    print("Found ", len(overlaps), "Overlaps")

  #save output to pickle so we dont have to rerun
    if savetoPickle:
      with open(datadir + 'overlaps.pkl', 'wb') as f:
        pickle.dump(overlaps,f)
      print("Pickled overlaps to", datadir + 'overlaps.pkl')
    
  else:
    print("No checks done")


# In[ ]:


#todo
#takes root folder, overlap list and event name
#saves as a 480x480 png
def crop_images_rand(datadir,overlap, event= "", pad = 0.0047):
  post_path = overlap[0]
  pre_path = overlap[1]
  bbox = overlap[2]

  post_path_name = post_path.split("/")[7].split(".")[0]
  pre_path_name = pre_path.split("/")[7].split(".")[0]
  #added exists = true so we still loop through other wise we get error.
  os.makedirs(datadir + event + '/testfolder/post{}_pre{}'.format(post_path_name, pre_path_name), exist_ok=True)
  # os.makedirs(datadir + 'hurricane_florence/overlaps/post{}_pre{}'.format(post_path_name, pre_path_name), exist_ok=True)

  xmin = np.random.uniform(bbox[0], bbox[2]-pad)
  xmax = xmin+pad
  ymin = np.random.uniform(bbox[3], bbox[1]-pad)
  ymax = ymin + pad

  bbox_rand = [xmin, ymax, xmax, ymin]

  post = gdal.OpenEx(post_path)
  post = gdal.Translate(datadir + event + '/testfolder/post{}_pre{}/crop_post_{}.png'.format(post_path_name, pre_path_name, post_path_name),
                      post,
                      projWin = bbox_rand,
                      format = 'PNG',
                      width = 480,
                      height = 480)
  
  post = None

  pre = gdal.OpenEx(pre_path)
  pre = gdal.Translate(datadir + event + '/testfolder/post{}_pre{}/crop_pre_{}.png'.format(post_path_name, pre_path_name, pre_path_name),
                      pre,
                      projWin = bbox_rand,
                      format = 'PNG',
                      width = 480,
                      height = 480)
  pre = None

  
  print('finished {}+{}'.format(post_path_name, pre_path_name))


# In[ ]:


def plot_image(path):
  dataset = gdal.OpenEx(path, gdal.GA_ReadOnly) 
  # Note GetRasterBand() takes band no. starting from 1 not 0
  band = dataset.GetRasterBand(1)
  arr = band.ReadAsArray()
  plt.imshow(arr)


# In[ ]:


def size_check(path):
  test = gdal.Open(path)
  width = test.RasterXSize
  height = test.RasterYSize
  gt = test.GetGeoTransform()
  minx = gt[0]
  miny = gt[3] + width*gt[4] + height*gt[5] 
  maxx = gt[0] + width*gt[1] + height*gt[2]
  maxy = gt[3]

  return print(maxx-minx) 
  print("/n") 
  print(maxy-miny)


# In[ ]:


if __name__ == "__main__":
   get_ipython().system(u"jupyter nbconvert '/content/drive/MyDrive/MAXAR/utils.ipynb' --to python ")

