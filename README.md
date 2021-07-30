# Final Project Repository for the UVA School of Data Science Summer 2021 Save the Children Capstone Project

## Abstract
The researchers conducted a review of existing machine learning methods to detect infrastructure damage using satellite imagery and neural networks. The research sponsor, Save the Children, seeks to leverage such detection methods to identify areas of likely human displacement following disaster events, and deploy humanitarian assistance quickly and efficiently. Several algorithmic methods were examined, and it was determined that a deep learning solution using a Siamese Neural Network was superior for infrastructure damage detection. The researchers also developed a data preprocessing pipeline to source satellite imagery from a leading satellite operator, followed by performing image analysis and further processing to predict using appropriate data.

## About this Repository
This repository contains the information, files, and links necessary to perform the following actions:
* Preprocess satellite images in geotiff format
* Run preprocessed images through a pretrained neural network
* View new localization and damage classification images as an output of the model

With two exceptions, the files that are required to perform the actions above are included in this repo.
1. Trained model weights must be downloaded separately. Due to their large size, they are not included in this repo, but can be found at this link: https://vdurnov.s3.amazonaws.com/xview2_1st_weights.zip
2. Only a few sample input image pairs are included in this repo for demonstration purposes. New images will need to be obtained from either the xView2 Challenge website (https://www.xview2.org/dataset), or a geotiff provider such as Maxar (https://www.maxar.com/open-data)

## How to Run the Model
The steps below describe how to use the files and code in this repository. There are two main sections: Preprocess satellite images in geotiff format, and Run preprocessed images through a pretrained neural network. There are no dependencies between these steps - you can run the model without preprocessing the images (albeit on a small set of sample images), and you can preprocess geotiff images without any need to run the output through the prediction model.

### Preprocess Satellite Images in Geotiff Format
There are two reasons that satellite images may need to be preprocessed before they can be run through the predictive model.
1. The model expects images in .png format, so files in .tif format will first need to be converted. If the pre- and post-disater images are already sized and positioned (as they are in the xView2 dataset), the need to still be run through a utility to convert the file type to .png. A utility called XXXX.py has been provided to perform this function, if needed.
2. Geotiffs from providers like Maxar are not only in .tif format, they also are not cleaned and formatted as overlapping pre- and post-disaster images. The pre- and post-disaster images that they provide may have areas of overlap, and those areas need to be identified so the images can be cropped and positioned. Included in the repo is a util.py file that performs these actions on a set of images that the user provides.

#### Convert .tif Images to .png Format
WRITE ABOUT THIS UTILITY

#### Preprocess Geotiff Images
* After importing the utils.py module from this repository, you can run the `test` function to confirm it is properly loaded.
* From here, you can either use the `download_image` function to download any large geotiffs from Maxar Open Data to your designated file path (recommended to use Google Colab + Google Drive). Or, alternatively you can run the `downloadTurkeyEq` function to get the 4 pre- and 6 post-earthquake images available from Maxar Open Data portal for this natural disaster.
  * You can also visualize any of these large images using `plot_image` function at this point
* Once the images are imported, the script will loop over all pre- and post-disaster image pair combinations (double for loop) and apply the `overlap_check` function to check which pre and post pairs share area
  * At this point you can run `create_kml` and follow the onscreen instructions to plot these available polygons in an interactive Google Map
* Next, either run the `crop_images_iter` or `crop_images_rand` function to split any overlapping area between two images into smaller sized images that the model is able to read (480px by 480px).
  * The difference between these two functions is that `crop_images_iter` will loop over the entire overlapping area and provide as many smaller sized images as possible, while `crop_images_rand` will output a single random smaller sized image located within the overlapping range. We recommend `crop_images_iter` for production environments where completeness is crucial and `crop_images_rand` for general testing

