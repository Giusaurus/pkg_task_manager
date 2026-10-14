import py_trees

from georg_task_manager.tasks_bt import Listening_BT, Gesture_BT, Navigate_BT, ReturnToIdle_BT
from georg_task_manager.tasks.priority import LOW, MID, HIGH, CRITICAL

MAP_PATH = "/home/giu/georg_maps/Nav_Test_V3.yaml"


def get_mission_bt(robot, state):
    root = py_trees.composites.Sequence(name="Test Mapping", memory=True)
    root.add_children([
        #Listening_BT.build(robot, state, "DOORBELL", timeout_sec=60.0, priority=HIGH),
        #Gesture_BT.build(robot, state, "look_at", -1000.0, 0.0, 100.0),
        #Gesture_BT.build(robot, state, "point_to", -2000.0, 0.0, 100.0),
        Navigate_BT.build(robot, state, "Seat", MAP_PATH, priority=HIGH),
        #Listening_BT.build(robot, state, "SPEECH"),
        #Gesture_BT.build(robot, state, "look_at", -1000.0, 0.0, 100.0),
        #Gesture_BT.build(robot, state, "greet_person", -1000.0, 0.0, 100.0),
        Navigate_BT.build(robot, state, "Water", MAP_PATH, priority=HIGH),
        Navigate_BT.build(robot, state, "Exit", MAP_PATH, priority=HIGH),
        Navigate_BT.build(robot, state, "Entrance", MAP_PATH, priority=HIGH),
        ReturnToIdle_BT.build(robot, state),
    ])
    return root