# Banker


Banker is ad bidding manneger, the project main files:
I'm have used python 3.7.3 for this project

  - banker-master.py - the server that synchronize between his slaves
  - banker-slave.py - the slave server, this server take care of the API
  - bider.py - a testing file to check that the flow is working

# How to run?
You can decied which port you want to run the slaves(default for onlt the first is 4201), For this task I can handle onlt one master, and I'm assuming his port is 5000 so no need to change that
```
python banker-master.py
```

``` 
python banker-slave.py [port - optional for the first server]
```

```
python bider.py [port - no need to set if using the default one]
```
# Bugs
- When you try to run mltiple slaves the socket.io dosent work well(please take a note that the code can hanlde the micro-service pattern)
- Sometimes you need to keep the slaves running and restart the master(this bug is not in all of the terminals but in some of them), somehow in the pycharm editor this bug dosen't exists
# Edge cases
- For the sake of the task I'm using only memory and not using db's
- You can't run mltiple masters
- If one of the slaves 'died', you can't recover the money and the data back

