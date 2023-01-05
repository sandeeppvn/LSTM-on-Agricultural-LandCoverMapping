#module load R/4.0.2 gdal/2.4.1 proj4/4.9.3 geos/3.6.3 python/3.6/anaconda

#Load the libaries
library(raster)
library(rgdal)

mainDir = "SNAP_processed/2019"
extent = "490509 1494667 952261 1909204"


# Files list
files_list <- list.files(mainDir,pattern=".tif",full.names=FALSE,recursive = FALSE,include.dirs = FALSE)
files_list = sort(files_list)
print(files_list)

# Loop through every image
for(img in files_list) {

# Create a subdir for every day according to it's name
subDir = substr(img,0,25)
dir.create(file.path(mainDir, subDir), showWarnings = FALSE)
name1 = substr(img,0,32)
# Create the following subdirs for easy tracking
dir.create(file.path(mainDir, subDir,"bands"), showWarnings = FALSE)
dir.create(file.path(mainDir, subDir,"scaled"), showWarnings = FALSE)
dir.create(file.path(mainDir, subDir,"reprojected"), showWarnings = FALSE)
dir.create(file.path(mainDir, subDir,"reprojected","band1"), showWarnings = FALSE)
dir.create(file.path(mainDir, subDir,"reprojected","band2"), showWarnings = FALSE)
dir.create(file.path(mainDir, subDir,"reprojected","band3"), showWarnings = FALSE)

# Split every image into seperate bands
img1_band1 = paste0("gdal_translate -of GTiff -b 1 ",mainDir,"/",img," ",mainDir,"/",subDir,"/bands/",name1,"_band1.tif")
img1_band2 = paste0("gdal_translate -of GTiff -b 2 ",mainDir,"/",img," ",mainDir,"/",subDir,"/bands/",name1,"_band2.tif")
img1_band3 = paste0("gdal_translate -of GTiff -b 3 ",mainDir,"/",img," ",mainDir,"/",subDir,"/bands/",name1,"_band3.tif")

system(img1_band1)
system(img1_band2)
system(img1_band3)

# Scale the bands to remove the decimals
img1_band1_corr = paste0("gdal_calc.py -A ",mainDir,"/",subDir,"/bands/",name1,"_band1.tif --outfile ",mainDir,"/",subDir,"/scaled/",name1,"_band1.tif --calc '1000 * A.astype(float)' --NoDataValue 0 --type Int16")
img1_band2_corr = paste0("gdal_calc.py -A ",mainDir,"/",subDir,"/bands/",name1,"_band2.tif --outfile ",mainDir,"/",subDir,"/scaled/",name1,"_band2.tif --calc '1000 * A.astype(float)' --NoDataValue 0 --type Int16")
img1_band3_corr = paste0("gdal_calc.py -A ",mainDir,"/",subDir,"/bands/",name1,"_band3.tif --outfile ",mainDir,"/",subDir,"/scaled/",name1,"_band3.tif --calc '1 * A.astype(float)' --NoDataValue 0 --type Int16")


system(img1_band1_corr)
system(img1_band2_corr)
system(img1_band3_corr)

# Reproject the bands according to desired extent
img1_band1_proj = paste0("gdalwarp -tr 30 -30 -te ",extent," -t_srs '+proj=utm +zone=47 +datum=WGS84 +units=m +no_defs +ellps=WGS84 +towgs84=0,0,0' -dstnodata 0 ",mainDir,"/",subDir,"/scaled/",name1,"_band1.tif ",mainDir,"/",subDir,"/reprojected/band1/",name1,"_band1_prj.tif")
img1_band2_proj = paste0("gdalwarp -tr 30 -30 -te ",extent," -t_srs '+proj=utm +zone=47 +datum=WGS84 +units=m +no_defs +ellps=WGS84 +towgs84=0,0,0' -dstnodata 0 ",mainDir,"/",subDir,"/scaled/",name1,"_band2.tif ",mainDir,"/",subDir,"/reprojected/band2/",name1,"_band2_prj.tif")
img1_band3_proj = paste0("gdalwarp -tr 30 -30 -te ",extent," -t_srs '+proj=utm +zone=47 +datum=WGS84 +units=m +no_defs +ellps=WGS84 +towgs84=0,0,0' -dstnodata 0 ",mainDir,"/",subDir,"/scaled/",name1,"_band3.tif ",mainDir,"/",subDir,"/reprojected/band3/",name1,"_band3_prj.tif")


system(img1_band1_proj)
system(img1_band2_proj)
system(img1_band3_proj)

}
