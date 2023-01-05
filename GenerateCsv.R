# Load the libraries
library(raster)
library(rgdal)
library(parallel)
library(sf)
library(exactextractr)
library(dplyr)
library(data.table)
library(sqldf)
library(doMC)
registerDoMC(30)

mainDir = "/gpfs/data1/cmongp/Sandeep/Github/LandCoverMappingRajesh/final_img/2018"

# Load the shapefile with labels
shapefile=readOGR('/gpfs/data1/cmongp/Sandeep/Github/LandCoverMappingRajesh/shapefiles','landcoverLabels2018')
shp=data.frame(shapefile)
shp=shp[c(1,2)]

# Loop through every image
x = sort(list.files(mainDir,pattern=".tif"))

#for(i in seq(1, length(x), 1)) {
foreach(i=1:length(x)) %dopar% {

    # Print which image number out of the total number of images we are on
    print(paste("Processing Image number: ", i, " out of ", length(x)))

    # Stack the image to pass to exact_extract function to extract pixels and it's labels
    raster=stack(paste0(mainDir,"/",x[i]))

    extract = extract(raster, shapefile, df=T, cellnumbers=T, weights=T)

    # Get X and Y coordinates
    extract2=cbind(extract,coordinates(raster)[extract[,2],])

    # Make a table to rename the columns
    extract_table=data.table(extract2)
    colnames(extract_table)=c("id", "cell", "band1", "band2", "band3", "weight", "X","Y")

    # Convert the table back to a dataframe
    extract_df=data.frame(extract_table)
    
    # Join two tables corresponding to ID
    final_data=sqldf('select * from extract_df LEFT JOIN shp ON extract_df.id=shp.id')

    # Remove pixels with less occupancy size? Can we use weight instead of fraction?
    # final_data=subset(final_data,final_data$fraction>0.70)

    file_name = substr(names(raster)[1],18,25)
    # Save the csv with corresponding date
    final_data['Date'] = file_name
    write.csv(final_data,paste0("TrainingData/",file_name,".csv"),row.names=T)
}












