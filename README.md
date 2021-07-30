# Final Project Repository for the UVA School of Data Science Summer 2021 Save the Children Capstone Project
#### Project Team (University of Virginia MSDS candidates, graduating August 2021)
* Sam Tyree (jst6jz@virginia.edu)
* Maurizio Boano (mb6fs@virginia.edu)
* Anvar Sarbanov (as5da@virginia.edu)
* Travis Moore (trm2yf@virginia.edu)


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

The deep learning models provided in this repository are based on the xView2 Challenge first-place model developed by Victor Durnov in 2020 (https://github.com/vdurnov/xview2_1st_place_solution). The focus of this project is to deploy a working version of that model for Save the Children.

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
* HOW AND WHERE ARE THESE IMAGES NOW SAVED?

### Run Preprocessed Images Through a Pretrained Neural Network
In this stage, you will execute code to run the predictive model on the preprocessed images that you obtained in the steps above. The result of this is a pair of images that show building localization (highlighting the structures in the pre-disaster image), and damage classification (which buildings are damaged, and what's the level of damage).

#### Prepare the Model
There are two versions of the predictive model included in this repo - one that uses CPUs for processing, and one that uses GPUs. We created a CPU version for testing due to the high cost and limited availability of GPUs. In a production environment, the GPU version will be required due to the large volume of image data that will need to be included. Besides code that is included in the GPU version to take advantage of GPU processing, the two versions are identical. The instructions below are focused on the CPU version, but the same will apply for the GPU version.
* Clone this repository to your local drive
* Copy the 'durnov_model_cpu_version' folder and its contents to your working directory
* Download trained model weights from the source (https://vdurnov.s3.amazonaws.com/xview2_1st_weights.zip)
  * Extract the weight files to the ‘weights’ subdirectory (these are large files)
* There are eight sample image pairs already included in the 'test/images' subdirectory. If using new images pairs, place both the pre- and post-disaster images in the 'test/images' subdirectory
  * Each image pair takes approximately 15-20 minutes to run in the CPU version, so plan accordingly
  * File names should be in this format (what's important is the sequence number and the indication of pre- and post-disaster):
    * guatemala-volcano_00000003_pre_disaster
    * guatemala-volcano_00000003_post_disaster

#### Run the Model
Now that the model has been prepared following the steps above, you will execute the code to create building localization and damage classification image outputs. There is a bash script file that is in the main working directory, called ‘predict.sh’. This script contains all the instructions to execute the model, running the prediction .py files in the correct order and placing the model outputs in a new directory called 'submission'.
* Open a terminal window and change (cd) to the main project working directory where the 'predict.sh' bash script is located
* Type ‘bash predict.sh’ at the command prompt and the model run will begin
  * Be patient - one pair of before/after images takes 15-20 minutes to run with CPUs
* When complete, you will receive the message ‘submission created!’
* There will be two new image files in a new directory called ‘submission’. These are the localization and damage prediction files that are model outputs

#### Interpret Model Results
The model is actually an ensemble of four different deep learning algorithms, each with three seeds. At the end, the model will determine which model output has the best precision, and those localization and damage classification images will be placed in the 'submission' directory. The model will identify four levels of damage in the damage classification output image using color coding.

<img src="https://user-images.githubusercontent.com/87451510/127698919-3ffabf87-778a-4384-8764-fe37453994f3.png" width="600">

Below is an example of pre- and post-disaster images that were run through the model, followed by the damage classification output image.

<img src="https://user-images.githubusercontent.com/87451510/127699836-146fd35d-603c-4292-879f-fab570df8e2f.png" height="310"> <img src="https://user-images.githubusercontent.com/87451510/127699847-db136c61-0683-42e4-97b3-5b4239da1ad9.png" height="310"> <img src="https://user-images.githubusercontent.com/87451510/127699071-d8c60f02-7ccb-43f8-b282-197fbeeebd00.png" height="310">



