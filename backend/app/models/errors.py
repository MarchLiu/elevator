class ElevatorClosed(Exception):
    def __init__(self, elevator_id: int, level: int):
        self.elevator_id = elevator_id
        self.level = level

    def __str__(self):
        return f"Elevator {self.elevator_id} is closed at level {self.level}"
    
class ElevatorFull(Exception):
    def __init__(self, elevator_id: int, level: int):
        self.elevator_id = elevator_id
        self.level = level

    def __str__(self):
        return f"Elevator {self.elevator_id} is full at level {self.level}"
    
class ElevatorRunning(Exception):
    def __init__(self, elevator_id: int, level: int):
        self.elevator_id = elevator_id
        self.level = level

    def __str__(self):
        return f"Elevator {self.elevator_id} is running at level {self.level}"
    