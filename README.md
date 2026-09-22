# pkg_task_manager

This is the Task Manager for the Pib Robot "Georg". It allows the creation of different
tasks, which can be fullfilled in costumized, modular missions. Each task will be fulfilled
in sequence and a priority can be assigned.

The priority determines, how the discard of the task is handled by the task manager:

LOW: The task will be discarded after the initial try.

MID: The task will be retried after the next task in sequence. Another failure will discard the task.

HIGH: The Task will be retried three more times (can be adjusted to the own desire). If the retries are
      used up, the task will be discarded.
      
Critical: Functions the same as the HIGH priority, but instead of just discarding the task, the mission
          will be stopped after the retries are used 
            up.


Instructions for currently implemented tasks/modules:


