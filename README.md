# The purpose of this repo is to highlight the `utils.py` module

This is a forked repository of the capstone project completed in the final two semesters of my Masters in Data Science program at the University of Virginia. For detailed information on the full project, visit the parent repo [`trm2yf/STC_Capstone`](https://github.com/trm2yf/STC_Capstone). All original project members and acknowledgements are still included at the bottom of this README.

### The `utils.py` module is a custom collection of functions to be used as a preprocessing pipeline of bitemporal satellite images that feed into a siamese neural network for detecting infrastructure damage. The functions within the module itself are well documented, but examples of their implementation are available within the `sample_image_processing_with_utils.ipynb` Jupyter notebook. The core purpose and flow of the pipeline is outlined in the original README documentation below:

## Preprocess Geotiff Images
* After importing the utils.py module from this repository, you can run the test function to confirm it is properly loaded.
* From here, you can either use the download_image function to download any large geotiffs from Maxar Open Data to your designated file path (recommended to use Google Colab + Google Drive). Or, alternatively you can run the downloadTurkeyEq function to get the 4 pre- and 6 post-earthquake images available from Maxar Open Data portal for this natural disaster.
    * You can also visualize any of these large images using plot_image function at this point
* Once the images are imported, the script will loop over all pre- and post-disaster image pair combinations (double for loop) and apply the overlap_check function to check which pre and post pairs share area
    * At this point you can run create_kml and follow the onscreen instructions to plot these available polygons in an interactive Google Map
* Next, either run the crop_images_iter or crop_images_rand function to split any overlapping area between two images into smaller sized images that the model is able to read (480px by 480px).
    * The difference between these two functions is that crop_images_iter will loop over the entire overlapping area and provide as many smaller sized images as possible, while crop_images_rand will output a single random smaller sized image located within the overlapping range. We recommend crop_images_iter for production environments where completeness is crucial and crop_images_rand for general testing

## Original Project Team (University of Virginia MSDS)
* Sam Tyree (jst6jz@virginia.edu)
* Maurizio Boano (mb6fs@virginia.edu)
* Anvar Sarbanov (as5da@virginia.edu)
* Travis Moore (trm2yf@virginia.edu)

## Original Project Acknowledgments
We thank the following people for their help and support: UVA Professor Jon Kropko for his thoughtful guidance and direction through the capstone process; UVA Professor Bill Baesner for serving as a liaison between Save the Children and Maxar; Will Low from Save the Children International for his humanitarian vision, knowledge, and guidance; and Maxar for being eager partners and data providers.

