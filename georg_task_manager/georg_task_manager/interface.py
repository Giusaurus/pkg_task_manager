from dataclasses import dataclass, field


@dataclass
class Vector2D:
    x: float = 0.0
    y: float = 0.0


@dataclass
class Vector3D:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class RobotState:

    
    # System
    

    current_task: str = "Idle"

    mission_running: bool = False
    mission_finished: bool = False

    emergency_stop: bool = False

    
    # Voice Status
    

    bell_recognized: bool = False

    is_listening_bell: bool = False

    is_greeting_guest: bool = False
    greeted_guest_voice: bool = False

    is_presenting_seat_voice: bool = False
    presented_seat_voice: bool = False

    
    # Navigation Status
    

    searching_door: bool = False
    reached_door: bool = False

    is_searching_seat: bool = False
    reached_seat: bool = False

    moving_to_door: bool = False
    moving_to_seat: bool = False

    position_door: Vector2D = field(
        default_factory=Vector2D
    )

    position_seat: Vector2D = field(
        default_factory=Vector2D
    )
    current_position = None
    current_orientation = None
    
    # Vision Status
    

    found_guest: bool = False

    vector_guest: Vector3D = field(
        default_factory=Vector3D
    )

    found_seat: bool = False

    vector_seat: Vector3D = field(
        default_factory=Vector3D
    )

    
    # Object Identification
    

    is_identifying_guest: bool = False
    identified_guest: bool = False

    is_identifying_seat: bool = False
    identified_seat: bool = False

    
    # Arm Status
    

    greeted_guest_arm: bool = False

    is_presenting_seat_arm: bool = False
    presented_seat_arm: bool = False