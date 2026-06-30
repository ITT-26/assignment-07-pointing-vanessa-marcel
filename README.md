[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/KfEU5Azw)

# Task 1 - Pose-Based Pointing Technique
- The pointing technique is in [`pointing_input.py`](./pointing_input.py).
- It can be started with `python pointing_input.py`.
- The input has a sensitivty that is set to 50 by default. Higher or lower values are possible as well. They can be passed by command line e.g.: `python pointing_input.py 60`.
- Possibly the sensitivity needs to be adjusted to the person using the programm.
- Pointer movement also depends on the distance from the camera. Moving closer enables faster movements while moving further away is for slower and more precise movements.
- The pointer is moved based on the tracked index finger. Movement ist only possible when the index finger is above the joint between hand and index finger. So you can turn your hand upside down or simply form a fist to disable input. When doing this, clicking is also disabled.
- Clicking is done by simply bringing the thumb and middle finger of the tracked hand together.
- It is not possible to use two hands for interaction. 
- The application can be stopped by pressing `ESC` or `q`.

# Task 2 - Fitts’ Law Application
- The Fitts' Law Application is in [`fitts_law.py`](./fitts_law.py).
- It can be started with `python fitts_law.py`.
- Target widths, distances and the amount of targets can be set in the [`config.ini`](./config.ini) file under `[FLCONFIG]`. Multiples values seperated by commas are possible for widths and distances.
- Participant ID, number of trials and input mode for the application can be set by command line.
- The first command line parameter is the participant ID. The second paremter is the number of trials per combination. The last parameter is the number of the input mode. 
- The index modes are: 0 = poiting input, 1 = mouse, 2 = mouse with latency, 3 = touchpad
- An example for starting the application with parameters is `python fitts_law.py 1 3 1`. 

# Task 3 - Steering Law Application
- The Steering Law application is in [`steering_law.py`](./steering_law.py).
- It can be started with `python steering_law.py`.
- Tunnel widths and distances can be set in the [`config.ini`](./config.ini) file under `[SLCONFIG]`. Multiples values seperated by commas are possible.
- Participant ID, number of trials and input mode for the application can be set by command line.
- The first command line parameter is the participant ID. The second paremter is the number of trials per combination. The last parameter is the number of the input mode. 
- The index modes are: 0 = poiting input, 1 = mouse, 2 = mouse with latency, 3 = touchpad
- An example for starting the application with parameters is `python steering_law.py 2 2 2`. 
- A trial is started when crossing the left green line of the tunnel from left to right and ends when the right line is crossed.
- When the top or bottom of the tunnel is crossed during a trial, the trial is canceled and the trial is recoreded as unsuccessful like in the paper introducing the Steering Law task.

# Task 4 - Adding Latency
- Latency (150 ms) is added to the applications when starting them in the latency input mode (third parameter = 2).

# Task 5 - Evaluating Input Techniques
- Files documenting the study can be found in the [`study_documents`](./study_documents/) directory.
- The data gathered in the study can be found in the [`data`](./data/) directory. There is a subdirectory for every input method.
- The plots can be found in the [`plots`](./plots/) directory. Code for the creation is in [`plot_creation.py`](./plot_creation.py).


 
