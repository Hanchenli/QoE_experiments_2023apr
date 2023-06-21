# %%
import pandas as pd 
import numpy as np
import os, sys
import scipy.stats as st
from scipy.stats import ttest_ind
import datetime
import pathlib
result_path = sys.argv[1]
graph_path = sys.argv[2]

confidence_level = 0.95
radius = 0.5
numbers_until_converge = np.zeros(9)

def isvalid(df):
    # cond1 = (df["usertimes"] > df["systemtimes"]).all()
    # cond0 = df.query("videos == '5.mp4'")["scores"].item() >= df.query("videos == '6.mp4'")["scores"].item()

    cond2 = df.query("videos == '1.mp4'")["scores"].item() == df["scores"].max()
    cond3 = df.query("videos == '2.mp4'")["scores"].item() == df["scores"].min()
    cond4 = df.query("videos == '1.mp4'")["sanityscore"].item() == 2
    cond5 = df.query("videos == '2.mp4'")["sanityscore"].item() == 5
    #cond6 = (df.query("videos == '3.mp4'")["sanityscore"].item() == 5) or (df.query("videos == '3.mp4'")["sanityscore"].item() == 4) 
    return  cond2 and cond3 and cond4 and cond5 #and cond6
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

    # print(timestamps, usertimes)
    df = pd.DataFrame()

    df["scores"] = scores
    df["videos"] = videos
    df["usertimes"] = usertimes
    df["systemtimes"] = systemtimes
    df["userid"] = userid
    df["sanityscore"] = sanityscore
    df["end_time"] = timestamps
    # print(df["end_time"])
    

    if isvalid(df):
        return df
    else:
        return None



# %%
#Set files
filenames = []
# os.listdir("/dataheart/hanchen/qoe_platform/QoE_experiments_2023apr/results_ow1/")

for filepath in pathlib.Path(f"{result_path}/").glob('**/*'):
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
                # print(df)
                dfs.append(df)
        except:
            pass
final_df = pd.concat(dfs)

groupedby = final_df[["videos", "scores"]].groupby("videos")


# print(final_df[["videos", "scores"]].groupby("videos").mean().reset_index(drop=True))

        

# %%
sorted_df = pd.concat(dfs).sort_values(by = ["end_time"])
sorted_df.to_csv("/dataheart/hanchen/qoe_platform/QoE_experiments_vidplat1/temp.csv")
# print(len(dfs))

# %%
def get_confidence(data):
    return st.t.interval(alpha=confidence_level, df=len(data)-1, loc=np.mean(data), scale=st.sem(data)) 


# %%
flags = np.zeros(7)
counters = np.zeros(7)
num_until_confident_not_equal = np.zeros(7)
stored_numbers = []
sum = 0

for i in range(10):
    stored_numbers.append([])

for index, row in sorted_df.iterrows():
    # print(row)
    id = int(row["videos"].split('.')[0])
    # print(id)
    quality = int(row["scores"])
    if (id > 2):
        stored_numbers[id-3].append(quality)


# %%
# print(stored_numbers[9])


def first_time_right(mean_intervals):
    max_i = [mean_intervals.index(x) for x in sorted(mean_intervals, reverse=True)][0]
    second_maxi = [mean_intervals.index(x) for x in sorted(mean_intervals, reverse=True)][1]
    local_mean_intervals = [[],[],[],[],[],[],[],[]]
    for checkpoint in range(6,26):
        for i in range(8):
            local_mean_intervals[i]= (np.mean(stored_numbers[i][:checkpoint]))

        if ([local_mean_intervals.index(x) for x in sorted(local_mean_intervals, reverse=True)][0] == max_i):
            if([local_mean_intervals.index(x) for x in sorted(local_mean_intervals, reverse=True)][1] == second_maxi):
                return checkpoint

# %%
intervals = [5, 10, 15, 20, 25]
mean_intervals = [[],[],[],[],[],[],[],[]]
std_intervals = [[],[],[],[],[],[],[],[]]
import matplotlib.pyplot as plt
for checkpoint in intervals:
    means = []
    stds = []
    print(stored_numbers[0][:checkpoint])

    for i in range(8):
        mean_intervals[i]= (np.mean(stored_numbers[i][:checkpoint]))
        means.append(np.mean(stored_numbers[i][:checkpoint]))
        # print(stored_numbers[i][:checkpoint])
        std_intervals[i].append(np.std(stored_numbers[i][:checkpoint]) / np.sqrt(checkpoint))
        stds.append(np.std(stored_numbers[i][:checkpoint]) / np.sqrt(checkpoint))

    fig = plt.figure(figsize = (10, 6))

    x = np.array(["FEC 0", "FEC 25", "FEC 50", "FEC 75", "FEC 90"])
    print(mean_intervals)
    for i in range(5):
        plt.bar(x[i], mean_intervals[i], width = 0.5)

    plt.ylim(0, 5)
    # plt.xlim(0, 60)
    plt.legend(
    )
    if (checkpoint == 25):
        print("csv", graph_path, mean_intervals)
        print("first_time", first_time_right(mean_intervals))

    plt.title(f"Number of users is :{str(checkpoint)}")
    plt.savefig(f"/dataheart/hanchen/qoe_platform/QoE_experiments_vidplat1/graphs/{graph_path}/{str(checkpoint)}.png")
    plt.show()

    # mean_intervals.append(means)
    # std_intervals.append(stds)



    # print(stds[1])
    # # Build the plot
    # fig, ax = plt.subplots()
    # ax.bar(range(8), means,
    #     yerr=stds,
    #     align='center',
    #     alpha=0.5,
    #     ecolor='black',
    #     capsize=10)

    # # ax.set_xticks(x_pos)
    # # ax.set_xticklabels(labels)
    # ax.yaxis.grid(True)
    # plt.show()

# %%