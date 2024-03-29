"""
TODO: make 2 different UUIDs, one for controller communication and one for raft
TODO: make driving commands 0.05 seconds longer to prevent driving lag
TODO: tone down THROTTLE in MOTOR_CONFIG

# main.py should contain the following steps
1. Spin up 3 threads each running RecvFromAgents running advertise()
2. Spin up 3 more threads each running ConnectToAgents running connect()
  * stay at this step until at least 2 threads have successfully connected
3. Start raft passing in the BT channels from steps 1 and 2
  a. there should be 2 threads, one for handling sending and one for handling receiving
  b. each channel from step 2 should send a 'hello' message 
  c. start raft in the follower position; they should timeout and start an election
  - raft should detect when a BT channel is dead (i.e. it hasn't received anything 
    in a while) and should go back to step a, waiting for a 'hello'

(after election) --> Becomes leader
  1. Start listening for controller by running advertise with RecvFromAgent
  2. Connect to controller and start driving with leader_drive
  - I assume that the raft threads will handle being a leader by sending heartbeats
  - Transition out of leader state should do the following
    i. kill connection with the controller
    ii. stop leader_drive

(after election) --> Becomes follower
  1. Start opencv in a process/thread passing a buffer we can listen to
  2. Start anti-collision in a process/thread passing the same buffer from step 1
  3. Start follower_drive passing the same buffer from step 1
  - I assume that the raft threads will handle being a follower by sending heartbeats
  - Transistion out of follower state should do the following 
    i. kill the opencv thread/process
    ii. kill the anti-collision process/thread
    iii. stop follower_drive

(during election) --> Handle election
  1. Do nothing
  - maybe we should blink an LED or something? ORRRR we could give each bot a multi-color
    LED. The LED could be red when following, blue electing, green when leading, blink red
    when error?
"""
raise NotImplementedError
