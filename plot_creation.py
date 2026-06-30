import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


def add_fitts_index_of_difficulty_column(data):
    pass


def prepate_steering_data(data):
    data = data.copy()
    data["difficulty"] = data["path_d"] / data["path_w"]
    data["duration"] = (data["end_timestamp"] - data["start_timestamp"]) * 1000
    return data

# plot for comparison of all trials fitts time
# plot for comparison of all trials steering time
# plot for comparsion error rate of all trials steering law
# gestirchelte linien für trials 1-3?


def read_steering_data():
    data_dir = "./data/"
    dfs = []
    for dirpath, dirnames, filenames in os.walk(data_dir):
        for file in filenames:
            if file.endswith(".csv") and file[:8] == "steering":
                full_path = os.path.join(dirpath, file)
                df = pd.read_csv(full_path)
                dfs.append(df)

    complete_df = pd.concat(dfs)
    return complete_df


def create_steering_time_plot(data):
    data = data.copy()
    fig = plt.figure()

    relevant = data[data["success"] == True]

    mouse_data = relevant[relevant["input_mode"] == "mouse"]
    pose_data = relevant[relevant["input_mode"] == "pose"]
    latency_data = relevant[relevant["input_mode"] == "latency"]
    touchpad_data = relevant[relevant["input_mode"] == "touchpad"]
    
    mouse_grouped = mouse_data.groupby("difficulty")["duration"].mean().reset_index()
    pose_grouped = pose_data.groupby("difficulty")["duration"].mean().reset_index()
    latency_grouped = latency_data.groupby("difficulty")["duration"].mean().reset_index()
    touchpad_grouped = touchpad_data.groupby("difficulty")["duration"].mean().reset_index()


    plt.figure(figsize=(10, 5))

    # print(len(mouse_data), len(latency_data), len(pose_data), len(touchpad_data))
    plt.scatter(mouse_data["difficulty"], mouse_data["duration"], label='mouse values', color='blue')
    plt.plot(mouse_grouped["difficulty"], mouse_grouped["duration"], label='mouse mean', color='blue')
    
    plt.scatter(latency_data["difficulty"], latency_data["duration"], label='mouse with latency values', color='orange')
    plt.plot(latency_grouped["difficulty"], latency_grouped["duration"], label='mouse with latency mean', color='orange')
    
    plt.scatter(pose_data["difficulty"], pose_data["duration"], label='pointing input values', color='green')    
    plt.plot(pose_grouped["difficulty"], pose_grouped["duration"], label='pointing input mean', color='green')
    
    plt.scatter(touchpad_data["difficulty"], touchpad_data["duration"], label='touchpad values', color='red')
    plt.plot(touchpad_grouped["difficulty"], touchpad_grouped["duration"], label='touchpad mean', color='red')
    
    plt.xlabel('steering law difficulty (D/W)')
    plt.ylabel('completion time in ms')
    plt.legend()
    plt.title('Comparison of Completion Times for Successfull Steering Law Trials')
    plt.savefig("./plots/steering_times.png")


complete_df = read_steering_data()
complete_df = prepate_steering_data(complete_df)
create_steering_time_plot(complete_df)
