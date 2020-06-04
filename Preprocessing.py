import classes
import pandas as pd
import re
from classes import *

# convert arbitrary list to a single list
def flatten(data_temp):
  data = []
  for sublist in data_temp:
    for item in sublist:
      data.append(item)
  return data  

# check if a variable is "Not a Number" (undefined or unrepresentable)
def isNaN(num):
    return num != num  

# function to load data from the "Signals" Excel sheet and initialise Signal class instances
def load_signals():
	# Load signals table from excel sheet (Topology 1)
	signals_excel = pd.read_excel(r'Network.xlsx', sheet_name='Signals')
	# Load signals table from excel sheet (Topology 2)
	#signals_excel = pd.read_excel(r'Network2.xlsx', sheet_name='Signals')
	# Load signals table from excel sheet (Topology 3)
	#signals_excel = pd.read_excel(r'Network3.xlsx', sheet_name='Signals')
	# Single out the allowed misses and size columns data
	signals_temp = pd.DataFrame(signals_excel, columns=['Allowed misses','Size (B)'])
	# Convert to list where each element is a list of two ints
	signals_temp = signals_temp.values.tolist()
	
	# Initialize a list of instances of a Signal class 
	signals = []
	# Fill the signals list
	for i in range(0, len(signals_temp)):
		signals.append(Signal(i+1, signals_temp[i][0], signals_temp[i][1]))


	return signals


# function to load data from the "Controllers" Excel sheet and initialise Controller class instances
def load_controllers():
	# Load Switches table from excel sheet (Topology 1)
	controllers_excel = pd.read_excel(r'Network.xlsx', sheet_name='Controllers')
	# Load Switches table from excel sheet (Topology 2)
	#controllers_excel = pd.read_excel(r'Network2.xlsx', sheet_name='Controllers')
	# Load Switches table from excel sheet (Topology 3)
	#controllers_excel = pd.read_excel(r'Network3.xlsx', sheet_name='Controllers')

	# Single out columns and convert it to the list
	controllers_temp = pd.DataFrame(controllers_excel, columns=['Controller', 'Tasks', 'Switches'])
	controllers_temp = controllers_temp.values.tolist()

	# Extract the controllers and tasks
	controllers_tmp = []
	tasks_tmp = []
	switches_tmp = []
	# Extract numbers from the string
	for dataset in controllers_temp:	
		controllers_tmp.append(list(map(int, re.findall('\d+', dataset[0]))))
		tasks_tmp.append(list(map(int, re.findall('\d+', dataset[1]))))
		switches_tmp.append(list(map(int, re.findall('\d+', dataset[2]))))
	controllers_tmp = flatten(controllers_tmp)
	switches_tmp = flatten(switches_tmp)

	# Initialize the controllers instances
	controllers = []
	for i in range(0, len(controllers_tmp)):
		temp = []
		for j in range(tasks_tmp[i][0], tasks_tmp[i][1]+1):
			temp.append(j)
		controllers.append(Controller(i+1, temp, switches_tmp[i]))
		
	return controllers

# function to load data from the "Tasks" Excel sheet and initialise Task and Dataset class instances
def load_tasks(controllers, signals):
	# Load tasks table from excel sheet (Topology 1)
	tasks_excel = pd.read_excel(r'Network.xlsx', sheet_name='Tasks')
	# Load tasks table from excel sheet (Topology 2)
	#tasks_excel = pd.read_excel(r'Network2.xlsx', sheet_name='Tasks')
	# Load tasks table from excel sheet (Topology 3)
	#tasks_excel = pd.read_excel(r'Network3.xlsx', sheet_name='Tasks')

	# Single out the all columns except the first (task name) and the Signals column
	tasks_temp = pd.DataFrame(tasks_excel, columns=['Task period','Task execution time','Signals reading period'])
	# Convert to list where each element is a list of "int, string, int"
	tasks_temp = tasks_temp.values.tolist()
	
	# Single out the Signals column and convert it to the single list
	signals_temp = pd.DataFrame(tasks_excel, columns=['Signals'])
	signals_temp = signals_temp.values.tolist()
	signals_temp = flatten(signals_temp)	
	# Extract the first and the last signal number from a string for every task
	task_dataset = []
	for dataset in signals_temp:
		task_dataset.append(list(map(int, re.findall('\d+', dataset))))
	# Initialize a list of instances of a Task and Dataset classes
	tasks = []
	datasets = []
	# Fill the tasks list
	for i in range(0, len(tasks_temp)):
		temp = []
		for j in range(task_dataset[i][0], task_dataset[i][1]+1):
			for k in range(0,len(signals)):
				if(j == signals[k].ID):
					temp.append(signals[k])
		datasets.append(Dataset(tasks_temp[i][2], temp))
		tasks.append(Task(i+1, tasks_temp[i][0], tasks_temp[i][1], datasets[i]))
		for c in controllers:
			if(tasks[i].ID in c.tasks):
				# if controller c contains the task tasks[i] then add that controller to the dataset[i]
				datasets[i].addController(c)
				break
		

	return tasks, datasets	
	

# function to load data from the "Switches" Excel sheet and initialise Switch class instances
def load_switches(controllers):
	# Load Switches table from excel sheet (Topology 1)
	switches_excel = pd.read_excel(r'Network.xlsx', sheet_name='Switches')
	# Load Switches table from excel sheet (Topology 2)
	#switches_excel = pd.read_excel(r'Network2.xlsx', sheet_name='Switches')
	# Load Switches table from excel sheet (Topology 3)
	#switches_excel = pd.read_excel(r'Network3.xlsx', sheet_name='Switches')


	# Single out columns and convert it to the list
	switches_temp = pd.DataFrame(switches_excel, columns=['Switch', 'FCIs'])
	switches_temp = switches_temp.values.tolist()

	# Extract the switches and fcis
	switches_tmp = []
	fcis_tmp = []
	for dataset in switches_temp:	
		switches_tmp.append(list(map(int, re.findall('\d+', dataset[0]))))
		fcis_tmp.append(list(map(int, re.findall('\d+', dataset[1]))))
	switches_tmp = flatten(switches_tmp)

	# Initialise switches
	switches = []
	for i in range(0, len(switches_tmp)):
		temp = []
		for j in range(fcis_tmp[i][0], fcis_tmp[i][1]+1):
			temp.append(j)
		switches.append(Switch(i+1, temp))
		for c in controllers:
			# If controller c is connected to the switch switches[i], add that controller to the switch
			if(c.switch == switches[i].ID):
				switches[i].addController(c.ID)

	return switches

# function to load data from the "FCIs" Excel sheet and initialise FCI class instances
def load_fcis(datasets):
	# Load FCIs table from excel sheet (Topology 1)
	fcis_excel = pd.read_excel(r'Network.xlsx', sheet_name='FCIs')
	# Load FCIs table from excel sheet (Topology 2)
	#fcis_excel = pd.read_excel(r'Network2.xlsx', sheet_name='FCIs')
	# Load FCIs table from excel sheet (Topology 3)
	#fcis_excel = pd.read_excel(r'Network3.xlsx', sheet_name='FCIs')

	# Single out the Signals column and convert it to the single list
	signals_temp = pd.DataFrame(fcis_excel, columns=['Signals'])
	signals_temp = signals_temp.values.tolist()
	signals_temp = flatten(signals_temp)
	
	# Extract the first and the last signal number from a string for every FCI
	fci_dataset = []
	for dataset in signals_temp:
		fci_dataset.append(list(map(int, re.findall('\d+', dataset))))
	
	# Initialize a list of instances of a Signal class
	fcis = []
	# Fill the fcis list
	for i in range(0, len(fci_dataset)):

		temp = []

		for dataset in datasets:
			if(dataset.signals[0].ID >= fci_dataset[i][0] and dataset.signals[len(dataset.signals)-1].ID <= fci_dataset[i][1]):
				temp.append(dataset)

		fcis.append(FCI(i+1, temp))

		# add this FCI to its datasets
		for j in range(0, len(fcis[i].datasets)):
			fcis[i].datasets[j].addFCI(fcis[i])

	return fcis

# function that creates paths to controllers in datasets
def createPaths(datasets, segments, switches):
	for i in range(0, len(datasets)):
		p = []

		# Find the starting switch in the path
		for j in range(0, len(switches)):
			if(datasets[i].FCI.ID in switches[j].FCIs):
				break
		nodeFirst = switches[j]
		nodeLocal = switches[j]

		# Find the final switch in the path
		for w in range(0, len(switches)):
			if(datasets[i].controller.ID in switches[w].controllers):
				break
		nodeLast = switches[w]

		# This while loop iterates on switches
		nodeIDhistory = []
		l = 0
		while(l < len(datasets)):
			nodeIDhistory.append(nodeLocal.ID)
			# If a controller is connected to the switch, a search is performed up to that controller. Then the while loop is terminated.
			if(nodeLocal == nodeLast):
				break
			# If a controller is not connected to the current switch, the search procedure goes to the next switch and the segment is added to the path.
			else:	
				for k in range(0, len(segments)):
					if(segments[k].node1 == nodeLocal and type(segments[k].node2) == type(nodeLocal) and segments[k].node2.ID not in nodeIDhistory):
						nodeLocal = segments[k].node2
						p.append(segments[k])
						break
					if(segments[k].node2 == nodeLocal and type(segments[k].node1) == type(nodeLocal) and segments[k].node1.ID not in nodeIDhistory):
						nodeLocal = segments[k].node1
						p.append(segments[k])
						break
			# If the first switch in the only switch in the path.
			if(k == 12):
				nodeLocal = nodeFirst
				p = []
			l+=1

		# The part of the path from the first to the last switch is found.
		# Now the part of the path from the last switch to the controller needs to be found.
		contFirst = datasets[i].controller
		contLocal = contFirst
		p_local = []
		q = 0
		while(q < len(datasets)):
			if(contLocal == nodeLast):
				break
			for k in range(0, len(segments)):
				if(segments[k].node2 == contLocal):
						p_local.append(segments[k])
						contLocal = segments[k].node1
						break
			q+=1

		# Finding a path from the last switch to the last controller. Node is the last switch.
		for q in range(0, len(p_local)):
			p.append(p_local[len(p_local)-1-q])	
		datasets[i].addPath(p)


# function that initializes network segments
def load_segments(controllers, switches, fcis):
	segments = []

# Topology 1
	segments.append(Segment(1, switches[0], controllers[7]))
	segments.append(Segment(2, switches[0], controllers[8]))
	segments.append(Segment(3, controllers[8], controllers[9]))
	segments.append(Segment(4, switches[0], switches[1]))

	segments.append(Segment(5, switches[1], switches[2]))
	segments.append(Segment(6, switches[1], controllers[5]))
	segments.append(Segment(7, switches[1], controllers[6]))

	segments.append(Segment(8, switches[2], controllers[3]))
	segments.append(Segment(9, controllers[3], controllers[4]))
	segments.append(Segment(10, switches[2], switches[3]))

	segments.append(Segment(11, switches[3], controllers[0]))
	segments.append(Segment(12, switches[3], controllers[1]))
	segments.append(Segment(13, switches[3], controllers[2]))

# Topology 2
	#segments.append(Segment(1, switches[1], controllers[7]))
	#segments.append(Segment(2, switches[0], controllers[8]))
	#segments.append(Segment(3, controllers[8], controllers[9]))
	#segments.append(Segment(4, switches[0], switches[1]))

	#segments.append(Segment(5, switches[1], switches[2]))
	#segments.append(Segment(6, switches[1], controllers[5]))
	#segments.append(Segment(7, switches[2], controllers[6]))

	#segments.append(Segment(8, switches[2], controllers[3]))
	#segments.append(Segment(9, controllers[3], controllers[4]))
	#segments.append(Segment(10, switches[2], switches[3]))

	#segments.append(Segment(11, switches[3], controllers[0]))
	#segments.append(Segment(12, switches[2], controllers[1]))
	#segments.append(Segment(13, switches[3], controllers[2]))

# Topology 3
	#segments.append(Segment(1, switches[1], controllers[7]))
	#segments.append(Segment(2, switches[0], controllers[9]))
	#segments.append(Segment(3, controllers[9], controllers[8]))
	#segments.append(Segment(4, switches[0], switches[1]))

	#segments.append(Segment(5, switches[1], switches[2]))
	#segments.append(Segment(6, switches[1], controllers[5]))
	#segments.append(Segment(7, switches[1], controllers[6]))

	#segments.append(Segment(8, switches[2], controllers[4]))
	#segments.append(Segment(9, controllers[4], controllers[3]))
	#segments.append(Segment(10, switches[2], switches[3]))

	#segments.append(Segment(11, switches[2], controllers[0]))
	#segments.append(Segment(12, switches[1], controllers[1]))
	#segments.append(Segment(13, switches[3], controllers[2]))

	return segments




# function that calls all above implemented functions are returns created list of classes' instances
def loadFromExcel():
	signals = load_signals()
	controllers = load_controllers()
	tasks, datasets = load_tasks(controllers, signals)
	switches = load_switches(controllers)	
	fcis = load_fcis(datasets)

	segments = load_segments(controllers, switches, fcis)
	createPaths(datasets, segments, switches)

	return signals, controllers, tasks, datasets, switches, fcis, segments


