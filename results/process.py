import pandas as pd 
import numpy as np
import os, sys
from scipy.stats import ttest_ind


def isvalid(df):
    # cond1 = (df["usertimes"] > df["systemtimes"]).all()
    cond1 = df.query("videos == '3.mp4'")["scores"].item() > df.query("videos == '4.mp4'")["scores"].item()
    cond2 = df.query("videos == '1.mp4'")["scores"].item() == df["scores"].max()
    cond3 = df.query("videos == '2.mp4'")["scores"].item() == df["scores"].min()
    cond4 = df.query("videos == '1.mp4'")["sanityscore"].item() == 2
    cond5 = df.query("videos == '2.mp4'")["sanityscore"].item() == 5
    #cond6 = (df.query("videos == '3.mp4'")["sanityscore"].item() == 5) or (df.query("videos == '3.mp4'")["sanityscore"].item() == 4) 
    return cond2 and cond3 and cond4 and cond5 #and cond6
    #return True

def process_one_file(filename):
    with open(filename, "r") as fin:
        lines = [l.strip("\n") for l in fin]
    scores = [int(v) for v in lines[0].split(',')]
    videos = [f"{v}.mp4" for v in lines[1].split(",")]
    moved_scores = []
    for i in [int(v) for v in lines[1].split(',')]:
        moved_scores.append(scores[i-1])
    scores = moved_scores
    videos = videos[:len(scores)]
    usertimes = [int(v) for v in lines[2].split(',')]
    systemtimes = [int(v) for v in lines[3].split(',')]
    userid = lines[4]
    sanityscore = [int(v) for v in lines[9].split(',')]
    df = pd.DataFrame()

    df["scores"] = scores
    df["videos"] = videos
    df["usertimes"] = usertimes
    df["systemtimes"] = systemtimes
    df["userid"] = userid
    df["sanityscore"] = sanityscore

    if isvalid(df):
        return df
    else:
        return None


filenames = os.listdir(".")
# print(filenames)

dfs = []
for file in filenames:
    if "txt" in file:
        df = process_one_file(file)

        try:
            df = process_one_file(file)

            if df is None:
                print(file, "is invalid!")
            else:
                dfs.append(df)
        except:
            pass

print("Got", len(dfs), "valid dataframes")
final_df = pd.concat(dfs)
final_df.to_csv("all.csv", index=None)

groupedby = final_df[["videos", "scores"]].groupby("videos")
print(ttest_ind(groupedby.get_group("3.mp4")["scores"], groupedby.get_group("5.mp4")["scores"], equal_var=False))


final_df[["videos", "scores"]].groupby("videos").mean().reset_index(drop=True).to_csv("mean.csv", index=None)
final_df[["videos", "scores"]].groupby("videos").var().reset_index(drop=True).to_csv("std.csv", index=None)
