# load-balance-agents


## Running the simulation
The simulation can be run by launching the `router-game.py`.
```bash
python3 router-game.py
```


## Configuration
The system has the following constants set by default (these can be found in the `Node.py` file):
```python
THROUGHPUT_META_MEAN = 100 # the mean of the Gaussian from which the throu
THROUGHPUT_META_STD = 10
MAX_PERSISTENCE = 7
MIN_PERSISTENCE = 1

PACKETS_STD_MEAN = THROUGHPUT_META_STD
MARIAN_CONSTANT = 3.0
ALPHA = 2
BETA = 0.01
```

1. **THROUGHPUT_META_MEAN**  
  Mean of the Gaussian from which we draw the Node's throughput
2.THROUGHPUT_META_STD . 
  Mean of the Gaussian from which we draw the Node's throughput
3. **MAX_PERSISTENCE and MIN_PERSISTENCE**   
  These two variables restrict the node's ability to change coalitions. Each node is assigned a persistence value from the range (MIN_PERSISTENCE, MAX_PERSISTENCE). This number determines the minimum number of turns the node has to stay in the coalition.
4. **PACKETS_STD_MEAN**  
  The mean of the standard deviation for drawing the packets in a given turn for a given node. This determines the std of the distribution from which a given node will have its packets drawn.
5. **ALPHA and BETA**   
  Two variables influencing the cost function. ALPHA diminishes the packet loss if the node is in the coalition and BETA amplifies the penalty for having too large coalitions
  
