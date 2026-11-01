# Lab 1 

# Building Packages

From the workspace root:

```bash
cd ~/ros2_ws

colcon build --symlink-install

source install/setup.bash
```


# Step 1: turn_away Node

The `turn_away` node subscribes to:

```text
/obstacle
```

and publishes:

```text
/cmd_vel
```

Run simulation:

```bash
ros2 launch diffdrive_bot control.launch.py
```

Run the node:

```bash
ros2 run my_robot_nodes turn_away
```

Verify connections:

```bash
rqt_graph
```

Expected:

```text
/obstacle
    |
    v
/turn_away
    |
    v
/cmd_vel
```

---

# Step 2: Parameters

Parameters:

```text
forward_speed
turn_speed
```

List parameters:

```bash
ros2 param list /turn_away
```

Get parameter values:

```bash
ros2 param get /turn_away forward_speed
```

```bash
ros2 param get /turn_away turn_speed
```

Update forward speed:

```bash
ros2 param set /turn_away forward_speed 0.4
```

Update turn speed:

```bash
ros2 param set /turn_away turn_speed 1.0
```

---

# Step 3: RobotStatus Message

Message:

```text
my_robot_interfaces/msg/RobotStatus
```

Contents:

```text
string state
float32 obstacle_distance
```

Verify:

```bash
ros2 interface show \
my_robot_interfaces/msg/RobotStatus
```

Monitor:

```bash
ros2 topic echo /robot_status
```

---

# Step 4: Services

## Enable / Disable Node

Enable:

```bash
ros2 service call \
/turn_away_enable \
std_srvs/srv/SetBool \
"{data: true}"
```

Disable:

```bash
ros2 service call \
/turn_away_enable \
std_srvs/srv/SetBool \
"{data: false}"
```

---

## SetTurnSpeed Service

Definition:

```text
float32 turn_speed
---
bool success
string message
```

Verify:

```bash
ros2 interface show \
my_robot_interfaces/srv/SetTurnSpeed
```

Valid request:

```bash
ros2 service call \
/set_turn_speed \
my_robot_interfaces/srv/SetTurnSpeed \
"{turn_speed: 1.0}"
```

Invalid request:

```bash
ros2 service call \
/set_turn_speed \
my_robot_interfaces/srv/SetTurnSpeed \
"{turn_speed: 3.0}"
```

---

# Step 5: Rotate Action

Action:

```text
my_robot_interfaces/action/Rotate
```

Definition:

```text
float32 angle
---
float32 turned
---
float32 turned
```

Verify:

```bash
ros2 interface show \
my_robot_interfaces/action/Rotate
```

Start server:

```bash
ros2 run my_robot_nodes rotate_server
```

Send goal:

```bash
ros2 action send_goal \
--feedback \
/rotate \
my_robot_interfaces/action/Rotate \
"{angle: 1.57}"
```


---

# Step 6: Square Driver

The `square_driver` node is an action client for:

```text
/drive_distance
/rotate
```

It:

1. Drives forward
2. Rotates 90°
3. Repeats four times
4. Returns close to its start position

Run:

```bash
ros2 run my_robot_nodes square_driver
```

Expected output:

```text
Driving side 1
Turning corner 1

Driving side 2
Turning corner 2

Driving side 3
Turning corner 3

Driving side 4
Turning corner 4

Square complete
```

---

# Step 7: Launch File

Launch everything together:

```bash
ros2 launch my_robot_nodes square.launch.py
```

Custom side length:

```bash
ros2 launch my_robot_nodes square.launch.py side_length:=0.8
```

The launch file starts:

```text
control.launch.py
rotate_server
square_driver
```

---



## Nodes

```bash
ros2 node list
```

---

## Topics

```bash
ros2 topic list
```
# What did not work:
