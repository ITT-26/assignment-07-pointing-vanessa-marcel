# Methodology 
The study was conducted in a within-subjects design were every participant completed all levels of independent variables.
The independent variables were input device, target distance (Fitts'), target width (Fitts'), tunnel distance (Steering) and tunnel width (Steering).
The dependent variables are movement time for Fitts' Law and movement time and error rate for Steering Law.
Input device conditions were mouse, mouse with 150ms latency, touchpad and pointing input. 
The different target distances were 400, 350 and 300 (px). The different target widths were 30, 40 and 50.
For the Fitts' Law task the target amount was ten in all trials.
The different tunnel distances were 1500, 1000 and 500. The different tunnel widths were 150, 100 and 50.
The tasks were performed on full HD displays (1920 x 1090 px).
Every combination of the independent variables was tested three times in a row. Testing all combinations enabled the detection of possible interaction effects. 
Through testing each combination three times in a row the detection of small learning effects was also possible.

# Participants
Two members of this team and one external person participated. All participants used their right hand for interaction. The data of the participants can be found in the [data directory](../data/).


# Procedure
1. The study was devided into one block of performing the Fitts' Law task and one block of performing the Steering Law task. 
2. For each task the condition and trials were repeated 4 times in total, one time for every different input device condition.  
3. The order of Fitts' or Steering Law tasks and input modes was selected randomly before the study for all participants (via lucky wheel).
  - Results Patricpant 1:
    1. Fitts' Law
      - mouse
      - pointing
      - touchpad
      - mouse with latency
    2. Steering Law
      - pointing
      - mouse with latency
      - mouse
      - touchpad
  - Results Patricpant 2:
    1. Fitts' Law
      - mouse
      - touchpad
      - mouse with latency
      - pointing
    2. Steering Law
      - mouse with latency
      - pointing
      - mouse
      - touchpad
  - Results Patricpant 3:
    1. Steering Law
      - mouse
      - touchpad
      - mouse with latency
      - pointing
    2. Fitts' Law
      - mouse with latency
      - mouse
      - pointing
      - touchpad
3. Before the study the participants got the chance to try out the pointing input method and were guided to use it. Also, sensitivity was adpated if necesseray.
4. Then the right application ([`fitts_law.py`](../fitts_law.py) or [`steering_law.py`](../steering_law.py)) was manually started by the experimenters (who were also participants in two cases) with the corresponding parameters for every input device condition. If the input device condition was pointing the pointing input programm was also started manually by the  experimenter before beginning.
5. If necessary participants were instructed on how to perform the tasks and that breaks were possible after each iteration. For Fitts' Law participants were told that they needed to click the red circles as fast as possible and that an iteration always started with a click on the circle at the top. For Steering Law participants were told to cross the tunnel (red rectangle) from the left to the rights side as fast as possible but while paying attention not to leave the tunnel towards the top or the bottom since this would have been an error. They were also told that an iteration started when crossing the left green line from left to right and that the goal was to cross the right green line in the same manner.
6. For every input condition the Fitts' Law application chose a random combination of the target radii and target distances specified in the [`config.ini`](../config.ini) file. The Steering Law application also chose a random combination of the tunnel widths and tunnel distances with the values from the same file. The config file included three values for all the variables from the assignment sheet. These values were combined in each possible way, so for each task 9 combinations were formed.
7. For each input mode each chosen combination needed to be performed sequentially three times. 
8. After perfoming one combination three times, if there were remaining combinations the next combination was chosen. Otherwise the application ended and depending on the progress was restarted by the experimenter with the next input device or the next task application was started.
9. After all 216 repetitions (2x task block, 4x input devices, 9x combinations and 3x trials) the study ended. 
