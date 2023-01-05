# LandCoverMapping - Crop classification using Sentinel-1

## Downloading data (Step-1):
1. Go to website https://search.asf.alaska.edu/#/. Create a free account.
2. Import the polygon (shapefile) to filter out the region. Make sure the .shp file is in lat-long projection format. You can also draw the polygon by yourself. *Note: This is not the labels .shp file, this is a rectangular polygon file.
3. Go to filter, select L1 GRD-HD data in the filetype, IW for mode, VV+VH for the polarization and give the desired start and end dates.
4. Add to download cart and download the python script file in the data download option.
5. Create a folder "raw_images" and run the python script to download images in the folder.

## Processing raw data (Step-2):
1. The processing is done using SNAP's python bindings. Follow the instructions from this site https://sigon.gitlab.io/post/2017-11-10-install-snap-ubuntu/ to set up SNAP and configure it to use within a seperate conda environment. Refer the SNAP_environment.yml file
2. Make sure you can launch snap from command line. Once the setup is done, go to the installed directory/snap/etc. Open the properties file, change the snap.jai.tileCacheSize and snap.jai.defaultTileSize depending on your RAM size. I gave cachesize as 10240 and tilesize as 5120.
3. Open python script 'SNAP_Processing.py', give the paths of shapefile(region of interest to cut), raw images, destination directory for the processed images accordingly and then run the script.

## Translating, Mosiacing, cropping SNAPPed data and generating training data (Step-3):
1. Deactivate all the environments and modules.Load the following module versions R/4.0.2 gdal/2.4.1 proj4/4.9.3 geos/3.6.3 python/3.6/anaconda
2. Run the script 'ReprojectFiles.r'. This script splits the input image into each bands and reproject to a desired extent. Make sure the right projection is given in the extent variable. The images are saved in the SNAP_processed folder inside which each directory corresponds all the individual files for a given day.
3. Run the script 'MosaicFiles.r'. This script lopps thourgh all the sub directories and mosiac all images for a given day. The final images are stored in the 'final_img' folder
4. Once all the final images are generated, the last step in processing data is to generate csv's for training the model. Run the script 'GenerateCsv.r' which loops through all the  images in the folder - final_img and generates csv's with uniform pixels, their band values and their corresponding labels for each image. Csv's are saved in the folder - 'TrainingData'

## Loading the csv and Interpolation (Step-4):
1. Load the python/3.6/anaconda. Make sure you to setup a seperate environment for pytorch related tasks. Refer pytorch_environment.yml file.
2. Run the python code 'LoadCsv.py'. This script loads the generated csv's in the previous step into an array and interpolate the NaN or zero values based on pandas interpolation functions. Resulting is an array with shape - (Total no of pixels x 666) if sequence length is 222 days and there are 3 bands. The interpolation is set to run on multiple cores and the resulting file is saved as pandas data frame - 'StudyRegionTraining.pkl'

## Training the LSTM model (Step-5):
1. Run the notebook 'TrainLSTM.ipynb'. The notebook loads the training data generated from the previos step 'StudyRegionTraining.pkl'. Input the sequence length (ie. number of temporal images). Train it for desired number of epochs. The model is saved as 'StudyRegionModel.pth'

## Load the test data images (Step-6):
1. Run the notebook 'LoadTestData.ipynb'. This notebook loads all the images from the 'final_img' folder into one big array using rasterio function. This array is passed to the interpolation function which was using during the training to fill the zero values. The interpolated data is then stored as 'interpolatedStudyRegion.npy'

## Generating the final prediction file (Step-7):
1. Run the notebook 'TestPrediction.ipynb'. This notebook loads the intepolated data 'interpolatedStudyRegion.npy' and pass the data through the trained model -'StudyRegionModel.pth'. Uses a sample tiff test file to create a image profile and transfers the predictions to the sample image. The final predicted images is saved as 'studyRegionPrediction.tif'
Note: Use GPU nodes only for training (Step-5) and testing the model (Step-7)


