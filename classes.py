import math

# returns all activation times within hyperperiod based on period
def times(period, hyperperiod):
  times = []
  for i in range(1, int(hyperperiod / period) + 1):
    times.append(i*period)
  return times

# calculates least common multiple of two numbers (a,b)
def lcm(a, b):
    return abs(a*b) // math.gcd(a, b)

# calculates least common multiple of array of numbers
def lcmm(args):
  if(len(args)==2):
    return lcm(args[0],args[1])
  else:
    arg0 = args[0]
    args.remove(args[0])
    return lcm(arg0, lcmm(args))

class Segment:
  def __init__(self,ID,node1,node2):
    self.ID = ID
    self.node1=node1
    self.node2=node2
    self.occ = 0
  # used to increase the occupancy for given size of data
  def occupancy(self,size):
    self.occ += size

  # defines equal operator between instances of class Segment
  def __eq__(self, other):
    return self.ID == other.ID
  # defines not equal operator between instances of class Segment
  def __ne__(self, other):
    return not self.__eq__(other)

class Dataset:
  def __init__(self, period, signals):
    self.period = period
    self.signals = signals
    
  def addFCI(self, FCI):
    self.FCI = FCI
    self.ti=times(self.period,FCI.hyperperiod)

  def addController(self, c):
    self.controller = c  

  def addPath(self,path):
    self.path = path 

class Package:
  def __init__(self,paths):
    self.size = 33
    self.signals = []
    self.period = 0
    self.paths = paths

  def assign_period(self,time):
    self.period = time

  # method to add signal to the package and increase the size of the package
  def add_signal(self, signal):  
    self.signals.append(signal)
    self.size += signal.size


class FCI:
  def __init__(self, ID, datasets):
    self.ID = ID
    self.datasets = datasets
    periods=[]
    for ds in datasets:
      periods.append(ds.period)
    self.hyperperiod = lcmm(periods)
  
  def schedule(self, times, timeschedule):
    self.timeschedule = timeschedule
    self.times = times

class Controller:
  def __init__(self, ID, tasks, sw):
    self.ID = ID
    self.tasks = tasks
    self.switch = sw

class Task:
  def __init__(self, ID, period, exec_time, dataset):
    self.ID = ID
    self.period = period
    self.exec_time = exec_time
    self.dataset = dataset

class Switch:
  def __init__(self, ID, FCIs):
    self.ID = ID
    self.FCIs = FCIs
    self.controllers = []
  
  def addController(self, c):
    self.controllers.append(c)       

class Signal:
  def __init__(self, ID, num_all_miss, size):
    self.ID = ID
    self.num_all_miss = num_all_miss
    self.miss_left = 0
    self.size = size