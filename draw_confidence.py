# %%
import pandas as pd 
import numpy as np
import os, sys
import scipy.stats as st
from scipy.stats import ttest_ind
import datetime
import pathlib

confidence_level = 0.95
radius = 0.5

def get_numbers_until_converge(confidence_interval, radius):
    numbers_until_converge = np.zeros(9)
    def isvalid(df):
        # cond1 = (df["usertimes"] > df["systemtimes"]).all()
        cond0 = df.query("videos == '5.mp4'")["scores"].item() >= df.query("videos == '6.mp4'")["scores"].item()

        cond2 = df.query("videos == '1.mp4'")["scores"].item() == df["scores"].max()
        cond3 = df.query("videos == '2.mp4'")["scores"].item() == df["scores"].min()
        cond4 = df.query("videos == '1.mp4'")["sanityscore"].item() == 2
        cond5 = df.query("videos == '2.mp4'")["sanityscore"].item() == 5
        #cond6 = (df.query("videos == '3.mp4'")["sanityscore"].item() == 5) or (df.query("videos == '3.mp4'")["sanityscore"].item() == 4) 
        return cond0 and cond2 and cond3 and cond4 and cond5 #and cond6
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
        # videos = [f"{v}.mp4" for v in range(1, 10)]
        videos = videos[:len(scores)]
        usertimes = [int(v) for v in lines[2].split(',')]
        systemtimes = [int(v) for v in lines[3].split(',')]
        userid = lines[4]
        sanityscore = [int(v) for v in lines[9].split(',')]
        end_t = os.path.getmtime(filename)
        timestamps = []
        for i in range(len(usertimes)):
            sum = 0
            for j in range(i+1, len(usertimes)):
                sum+=usertimes[j]
            sum /= 1000
            timestamps.append(end_t - sum -1.68*10**9)

        #print(timestamps, usertimes)
        df = pd.DataFrame()

        df["scores"] = scores
        df["videos"] = videos
        df["usertimes"] = usertimes
        df["systemtimes"] = systemtimes
        df["userid"] = userid
        df["sanityscore"] = sanityscore
        df["end_time"] = timestamps
        #print(df["end_time"])
        

        if isvalid(df):
            return df
        else:
            return None



    # %%
    #Set files
    filenames = []
    # os.listdir("/dataheart/hanchen/qoe_platform/QoE_experiments_2023apr/results_ow1/")

    for filepath in pathlib.Path("/dataheart/hanchen/qoe_platform/QoE_experiments_2023apr/results_ow1/").glob('**/*'):
        filenames.append(str(filepath))



    # %%
    # Load files
    dfs = []
    for file in filenames:
        if "txt" in file:
            df = process_one_file(file)
            try:
                df = process_one_file(file)
                if df is None:
                    print(file, "is invalid!")
                else:
                    #print(df)
                    dfs.append(df)
            except:
                pass
    final_df = pd.concat(dfs)

    groupedby = final_df[["videos", "scores"]].groupby("videos")


    #print(final_df[["videos", "scores"]].groupby("videos").mean().reset_index(drop=True))

            

    # %%
    sorted_df = pd.concat(dfs).sort_values(by = ["end_time"])
    sorted_df.to_csv("/dataheart/hanchen/qoe_platform/QoE_experiments_2023apr/temp.csv")
    #print(len(dfs))

    # %%
    def get_confidence(data):
        return st.t.interval(alpha=confidence_level, df=len(data)-1, loc=np.mean(data), scale=st.sem(data)) 


    # %%
    flags = np.zeros(7)
    counters = np.zeros(7)
    num_until_confident_not_equal = np.zeros(7)
    stored_numbers = []
    sum = 0

    for i in range(7):
        stored_numbers.append([])

    for index, row in sorted_df.iterrows():
        # #print(row)
        id = int(row["videos"].split('.')[0])
        quality = int(row["scores"])
        stored_numbers[id].append(quality)
        
        confidence = get_confidence(stored_numbers[id])
        if (id == 3 or id == 4):
            # #print(id, stored_numbers[id], stored_numbers[5], ttest_ind(stored_numbers[5], stored_numbers[id], equal_var=False))
            ttest = ttest_ind(stored_numbers[5], stored_numbers[id], equal_var=False)
            
            if(abs(ttest.statistic) > st.t.ppf(q=1-.05, df = len(stored_numbers[5]) + len(stored_numbers[id])) and num_until_confident_not_equal[id]==0 and len(stored_numbers[5]) + len(stored_numbers[id])>15):
                num_until_confident_not_equal[id] = len(stored_numbers[id])

        
        # if (np.mean(stored_numbers[id]) - confidence[0]<radius and numbers_until_converge[id-2] ==0):
        print(id, st.sem(stored_numbers[id]))
        
        if (st.sem(stored_numbers[id])< radius and numbers_until_converge[id-2] ==0 and len(stored_numbers[id])>10):
            sum+=1
            numbers_until_converge[id-2] = len(stored_numbers[id])
            print(id, stored_numbers[id],confidence[0])

    loss60_numbers = stored_numbers[5]
    #print("number of tests until confident they are not equal for 1st stall: ", num_until_confident_not_equal[3])
    #print("number of tests until confident they are not equal for 2nd stall: ", num_until_confident_not_equal[4])
    #print("with enough confidence: ",sum)

    # %%
    #Set files
    filenames = []
    # os.listdir("/dataheart/hanchen/qoe_platform/QoE_experiments_2023apr/results_ow1/")

    for filepath in pathlib.Path("/dataheart/hanchen/qoe_platform/QoE_experiments_2023apr/results_ow2/").glob('**/*'):
        filenames.append(str(filepath))



    # %%
    # Load files
    dfs = []
    for file in filenames:
        if "txt" in file:
            df = process_one_file(file)
            try:
                df = process_one_file(file)
                if df is None:
                    print(file, "is invalid!")
                else:
                    #print(df)
                    dfs.append(df)
            except:
                pass
            

    # %%
    sorted_df = pd.concat(dfs).sort_values(by = ["end_time"])
    sorted_df.to_csv("/dataheart/hanchen/qoe_platform/QoE_experiments_2023apr/temp.csv")
    #print(len(dfs))

    # %%
    def get_confidence(data):
        return st.t.interval(alpha=confidence_level, df=len(data)-1, loc=np.mean(data), scale=st.sem(data)) 


    # %%
    flags = np.zeros(7)
    counters = np.zeros(7)
    num_until_confident_not_equal = np.zeros(7)
    stored_numbers = []
    sum = 0

    for i in range(7):
        stored_numbers.append([])

    for index, row in sorted_df.iterrows():
        # #print(row)
        id = int(row["videos"].split('.')[0])
        quality = int(row["scores"])
        stored_numbers[id].append(quality)
        confidence = get_confidence(stored_numbers[id])
        if (id == 3 or id == 4):
            ttest = ttest_ind(loss60_numbers, stored_numbers[id], equal_var=False)
            # if (len(stored_numbers[id]) > 15):
                # print(id, ttest.pvalue)        
            if(abs(ttest.statistic) > st.t.ppf(q=1-.05, df = len(loss60_numbers) + len(stored_numbers[id])) and num_until_confident_not_equal[id]==0 and  len(stored_numbers[id])>15):
                #print(np.mean(stored_numbers[id]), np.mean(loss60_numbers))
                num_until_confident_not_equal[id] = len(stored_numbers[id])


        # if (np.mean(stored_numbers[id]) - confidence[0]<radius and numbers_until_converge[id+2] ==0):
        print(id, st.sem(stored_numbers[id]))
        if (st.sem(stored_numbers[id])< radius and numbers_until_converge[id+2] ==0  and len(stored_numbers[id])>10):
            sum+=1
            numbers_until_converge[id+2] = len(stored_numbers[id])
            #print(id, stored_numbers[id],confidence[0])


    #print("number of tests until confident they are not equal for 1st stall: ", num_until_confident_not_equal[3])
    #print("number of tests until confident they are not equal for 2nd stall: ", num_until_confident_not_equal[4])
    #print("with enough confidence: ",sum)

    return numbers_until_converge
    # %%

confidence_levels = [1]#[0.975, 0.95, 0.9, 0.8]
radiuses = [0.2]

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt


pp = PdfPages('all_confidence_graph.pdf')

for i in confidence_levels:
    for j in radiuses:
        cur_num = get_numbers_until_converge(i, j)
        print(cur_num)

        cur_num.sort()
        graph = plt.figure()
        plt.plot(range(1,9), cur_num[1:])
        plt.title(f"standard error: {str(j)}")
        pp.savefig(graph)

pp.close()