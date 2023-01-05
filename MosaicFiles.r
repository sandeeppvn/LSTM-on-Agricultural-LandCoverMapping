#module load R/4.0.2 gdal/2.4.1 proj4/4.9.3 geos/3.6.3 python/3.6/anaconda

# Load the libraries
library(raster)
library(rgdal)

# Give shapefile
shapeDir = "shapefiles"
shapeFile = "NewStudy_reproject.shp"

# Src and Dest Dirsa
imageDir = "/gpfs/data1/cmsgp/LCLUCgroup/Sandeep/SNAP_processed/2019" #change this directory
mosaicDir = "mosaiced/2019"
finalImg = "final_img/2019"

# Loop through the reprojected images
dir_list <- list.dirs(imageDir,full.names=FALSE,recursive = FALSE)
for(subDir in dir_list) {
#dir.create(file.path(mosaicDir ,subDir), showWarnings = FALSE)
print(subDir)

# Merge the bands
merge_band1 = paste0("gdalbuildvrt ",mosaicDir,"/",subDir,"_band1.vrt ",imageDir,"/",subDir,"/reprojected/band1/*.tif")
merge_band2 = paste0("gdalbuildvrt ",mosaicDir,"/",subDir,"_band2.vrt ",imageDir,"/",subDir,"/reprojected/band2/*.tif")
merge_band3 = paste0("gdalbuildvrt ",mosaicDir,"/",subDir,"_band3.vrt ",imageDir,"/",subDir,"/reprojected/band3/*.tif")


system(merge_band1)
system(merge_band2)
system(merge_band3)


final_band1 = paste0("gdal_translate ",mosaicDir,"/",subDir,"_band1.vrt ",mosaicDir,"/",subDir,"_band1.tif")
final_band2 = paste0("gdal_translate ",mosaicDir,"/",subDir,"_band2.vrt ",mosaicDir,"/",subDir,"_band2.tif")
final_band3 = paste0("gdal_translate ",mosaicDir,"/",subDir,"_band3.vrt ",mosaicDir,"/",subDir,"_band3.tif")

system(final_band1)
system(final_band2)
system(final_band3)

# Crop the bands

band1_cropped = paste0("gdalwarp -of GTiff -cutline ",shapeDir,"/",shapeFile," -crop_to_cutline ",mosaicDir,"/",subDir,"_band1.tif ",mosaicDir,"/",subDir,"_cropped_band1.tif")
band2_cropped = paste0("gdalwarp -of GTiff -cutline ",shapeDir,"/",shapeFile," -crop_to_cutline ",mosaicDir,"/",subDir,"_band2.tif ",mosaicDir,"/",subDir,"_cropped_band2.tif")
band3_cropped = paste0("gdalwarp -of GTiff -cutline ",shapeDir,"/",shapeFile," -crop_to_cutline ",mosaicDir,"/",subDir,"_band3.tif ",mosaicDir,"/",subDir,"_cropped_band3.tif")


system(band1_cropped)
system(band2_cropped)
system(band3_cropped)

# Save the final image
final_vrt = paste0("gdalbuildvrt -separate ",finalImg,"/",subDir,".vrt ",mosaicDir,"/",subDir,"_cropped_band1.tif ",mosaicDir,"/",subDir,"_cropped_band2.tif ",mosaicDir,"/",subDir,"_cropped_band3.tif")
final_img = paste0("gdal_translate ",finalImg,"/",subDir,".vrt ",finalImg,"/",subDir,".tif")

system(final_vrt)
system(final_img)





}
