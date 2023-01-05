#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import numpy as np
import glob
from multiprocessing import Pool
import time

# Read csv's, Replace NA and negative values
def readCSV(path):
    all_files = glob.glob(path + "/*.csv")
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        df = df.iloc[: , 1:]
        df.drop(['ID','id','fraction','Date','X','Y','class'], axis=1, inplace=True)
        li.append(df)
    sample = pd.read_csv(filename)
    class_sample = sample['class']
    frame = pd.concat(li,axis=1)
    frame = frame.fillna(0)
    frame = frame.abs().astype(int)
    return frame,class_sample

# Interpolation function
def interpolate(pixel,seq_len=222,bands=3):
    arr = np.array(pixel)
    # Reshape array according to sequence length
    arr = arr.reshape((seq_len,bands))
    arr_T = arr.T
    # Split into different bands. Add df4,df5..etc. if more than 3 bands.
    df1 = pd.DataFrame(arr_T[0])
#     df1[df1 < 0] = 0
    df2 = pd.DataFrame(arr_T[1])
#     df2[df2 < 0] = 0
    df3 = pd.DataFrame(arr_T[2])
#     df3[df3 < 0] = 0
    # Make sure all zeros are replaced
    df1 = df1.replace(0,np.nan)
    df2 = df2.replace(0,np.nan)
    df3 = df3.replace(0,np.nan)
    # Linear interpolation
    df1.interpolate(method = 'linear',inplace=True)
    # Make sure replaces values when above method fails (eg. above method fails to interpolate when there are zeros in first two indexes of the data frame)
    df1.replace(to_replace=np.nan, method='bfill',inplace=True)
    df2.interpolate(method = 'linear',inplace=True)
    df2.replace(to_replace=np.nan, method='bfill',inplace=True)
    df3.interpolate(method = 'linear',inplace=True)
    df3.replace(to_replace=np.nan, method='bfill',inplace=True)
    df1 = df1.T
    df2 = df2.T
    df3 = df3.T
    # Group the bands and reshape
    cat = np.concatenate((df1,df2,df3),axis=0)
    cat = cat.T
    cat = cat.reshape(seq_len*bands,)
    new_band = pd.DataFrame(cat)
    for i in range(len(pixel)):
        pixel[i] = new_band.iloc[i]
        
    return pixel


# Main function
def main():
    # Sequence length and no of bands
    seq_len = 222
    bands = 3
    # Load the csvs into array
    csv_path = "TrainingData/"
    frame,class_sample = readCSV(csv_path)
    print("Loaded csv's")
    # Do the interpolation. Use muitlple cores by using map elastic function
    t1 = time.time()
    p = Pool()
    result_arr = p.map(interpolate,[frame.iloc[i] for i in range(len(frame))])
    p.close()
    p.join()
    print("Time Took for Interpolation in seconds:",time.time()-t1)
    # Reshape the array, Convert to dataframe and save the pickle
    result_arr = np.reshape(result_arr,(len(result_arr),seq_len*bands))
    df = pd.DataFrame(result_arr)
    new_frame = pd.concat([df,class_sample],axis=1)
    new_frame.to_pickle("StudyRegionTraining.pkl")


if __name__ == "__main__":
    main()

