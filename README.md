# pkg_task_manager

This is the Task Manager for the Pib Robot "Georg". It allows the creation of different
tasks, which can be fullfilled in costumized, modular missions by the usage of actions. 
Each task will be fulfilled in sequence and a priority can be assigned.


The priority determines, how the discard of the task is handled by the task manager:

LOW: The task will be discarded after the initial try.

MID: The task will be retried after the next task in sequence. Another failure will discard the task.

HIGH: The Task will be retried three more times (can be adjusted to the own desire). If the retries are
      used up, the task will be discarded.
      
Critical: Works the same as the HIGH priority, but instead of just discarding the task, the mission
          will be stopped after the retries are used up.


# Setup for currently implemented tasks/modules:


## Terminal 1 (for Navigation_Action_Server_Room):

source install/setup.bash

ros2 run navigate_server navigate_action_server \
--node-name nav_room_server \
--action-name /nav/navigate_room_x

## Terminal 2 (for Navigation_Action_Server_Object):

source install/setup.bash

ros2 run navigate_server navigate_action_server \
--node-name nav_object_server \
--action-name /nav/navigate_object_x

## Terminal 3 (for Drive Tasks):  
source install/setup.bash

ros2 run drive_route_server drive_route_action_server

## Terminal 4 (for the Gesture_Action_Server): 
source install/setup.bash

ros2 run pib_gestures_action pib_gestures_server.py 

## Terminal 5 (for the Listen_Action_Server): 
source install/setup.bash

ros2 run voice_assistant listen_action_server

## Terminal 6 (for Task_Manager_Node):  
source install/setup.bash

ros2 run robot_task_manager task_manager
