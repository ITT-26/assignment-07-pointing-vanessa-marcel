import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


def add_fitts_index_of_difficulty_column(data):
    data = data.copy()
    data["difficulty"] = np.log2(data["target_d"]/data["target_w"] + 1)
    return data

def add_fitts_mt_column(data):
    data = data.copy()
    data["mt"] = np.nan

    for i in range(1, len(data)):
        if data.iloc[i]["target_id"] != 0:
            data.loc[i, "mt"] = (
                data.iloc[i]["timestamp"] -
                data.iloc[i-1]["timestamp"]
            )

    return data

def add_fitts_throughput_column(data):
    data = data.copy()
    data["throughput"] = data["difficulty"] / data["mt"]
    return data

def transform_fitts_to_single_line_cond(data):
    data = data.copy()
    mean_mt = (
        data
        .groupby(["iteration", "pid", "input", "difficulty"])["mt"]
        .mean()
        .reset_index()
    )
    return mean_mt

def prep_fitts_data(data):
    data = data.copy()
    data = add_fitts_index_of_difficulty_column(data)
    data = add_fitts_mt_column(data)
    data = transform_fitts_to_single_line_cond(data)
    data = add_fitts_throughput_column(data)
    return data

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

def read_fitts_data():
    data_dir = "./data/"
    dfs = []
    for dirpath, dirnames, filenames in os.walk(data_dir):
        for file in filenames:
            if file.endswith(".csv") and file[:5] == "fitts":
                full_path = os.path.join(dirpath, file)
                df = pd.read_csv(full_path)
                dfs.append(df)

    complete_df = pd.concat(dfs)
    return complete_df

def create_fitts_mt_plot(data):
    inputs = data["input"].unique()

    fig, axes = plt.subplots(
        2, 2,
        figsize=(12, 8),
        sharex=True,
        sharey=True
    )

    axes = axes.flatten()

    for ax, input_mode in zip(axes, inputs):
        subset = data[data["input"] == input_mode]

        subset = subset.sort_values("difficulty")

        ax.scatter(
            subset["difficulty"],
            subset["mt"]
        )

        mean_data = (
            subset
            .groupby("difficulty")["mt"]
            .mean()
            .reset_index()
            .sort_values("difficulty")
        )

        ax.plot(
            mean_data["difficulty"],
            mean_data["mt"],
            linewidth=2,
            label="Mean MT"
)

        ax.set_title(input_mode)
        ax.set_xlabel("ID (bits)")
        ax.set_ylabel("MT (s)")

    plt.tight_layout()
    plt.savefig("./plots/fitts_mt_subplots.png")

def create_throughput_per_input_plot(data):
    data = data.copy()

    tp_per_participant = (
        data
        .groupby(["pid", "input", "iteration"])["throughput"]
        .mean()
        .reset_index()
    )

    inputs = tp_per_participant["input"].unique()

    plt.figure(figsize=(8, 5))

    box_data = [
        tp_per_participant[
            tp_per_participant["input"] == inp
        ]["throughput"]
        for inp in inputs
    ]

    plt.boxplot(
        box_data,
        tick_labels=inputs
    )

    # Scatter participant values
    for pos, inp in enumerate(inputs, start=1):
        values = tp_per_participant.loc[
            tp_per_participant["input"] == inp,
            "throughput"
        ]

        # Small horizontal jitter
        x = np.random.normal(pos, 0.04, len(values))

        plt.scatter(
            x,
            values,
            alpha=0.8
        )

    plt.xlabel("Input Method")
    plt.ylabel("Throughput (bits/s)")
    plt.title("Fitts' Law Throughput Across Input Methods")

    plt.savefig("./plots/throughput_by_input.png")


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


steering_df = read_steering_data()
steering_df = prepate_steering_data(steering_df)
create_steering_time_plot(steering_df)

fitts_df = read_fitts_data()
fitts_df = prep_fitts_data(fitts_df)
create_fitts_mt_plot(fitts_df)
create_throughput_per_input_plot(fitts_df)
