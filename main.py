from classes import *
from Preprocessing import *

import itertools
from math import comb

from operator import attrgetter

from tkinter import *

import xlsxwriter

MAX_PACKAGE_SIZE = 1500

# converts list to list of lists
def l2lol(lst): 
  return [[el] for el in lst] 

# Next-Fit algorithm
# Fills packages in the reference case
# datasets is array of datasets to be packed
def NF(datasets):
  # create array of all signals to be packed
  signals = []
  # create array of all paths for packets
  paths = []
  for data in datasets:
    signals+=data.signals
    paths.append(data.path)
  # create first package
  p=Package(paths)
  # create list of all packages and assign first package
  packages=[p]
  # j is package counter
  j=0
  for i in range(0, len(signals)):
    # check if signal fits to the package
    # if it fits then put it inside
    if(signals[i].size+packages[j].size <=MAX_PACKAGE_SIZE):
      packages[j].add_signal(signals[i])
    # if it does not fit in package then create new one
    else:
      pnew = Package(paths)
      pnew.add_signal(signals[i])
      packages.append(pnew)
      j+=1
  return packages 

# Determines the reference case schedule of packing for each FCI
def Ref(FCIs):
  for i in range(0, len(FCIs)):
    # package creation times within FCI
    times = []
    for ds in FCIs[i].datasets:
      times += ds.ti
    times = sorted(times,reverse=False)
    times = list(dict.fromkeys(times))
    time_schedule = []
    for time in times:
      # list of datasets sent in this time moment
      sent = []
      for ds in FCIs[i].datasets:
        # check if dataset is sent in this time moment
        if time in ds.ti:
          # add dataset to the list
          sent.append(ds)
      # all datasets will be sent separately
      package_type = l2lol(sent)
      # list of packages
      packages = []
      for j in range(0, len(package_type)):
        # perform packing
        subpackages = NF(package_type[j]) 
        packages += subpackages
      time_schedule.append(packages)
    # assign package sending schedule to the FCI
    FCIs[i].schedule(times,time_schedule)


# function that creates list of all combinations of packing given datasets ds
def packingtypes(ds):
  dsc = ds.copy()
  lst = []
  lst.append(ds)
  lotypes = []
  lotypes.append(lst)
  # list of all packing combinations
  combinations = []
  for i in range(1, int(len(ds)/2)+1):
    for c in itertools.combinations(ds, i):
      combinations.append(list(c))
  if len(ds)%2==0:
    x = int(comb(len(ds),int(len(ds)/2))/2)
    del combinations[len(combinations)-x:len(combinations)]
  for l in combinations:
        lista = []
        lista.append(l.copy())
        for i in l:
          dsc.remove(i)
        k = dsc.copy()
        lista.append(k.copy())
        lotypes.append(lista.copy())
        dsc+=l
  lotypes.append(l2lol(ds))
  return lotypes


# Sort class instances by size in descending order
def sort_desc(objects):
  return sorted(objects,key=lambda x: x.size,reverse=True)


# Cost function
def cost_fun(packages):
  # cost function value
  res = 0
  for package in packages:
    # segments over which package needs to be sent 
    segs = []
    # exclude duplicate segments
    for path in package.paths:
      for segment in path:
        if(not (segment in segs)):
          segs.append(segment)
    # value is calculated as package size multiplied by the number of segments
    res += len(segs)*package.size
  return res


# Bin-packing algorithm
# Best-Fit Decreasing 
def BFD(pt):
  # all signals to be packed
  signals = []
  # all paths for packets
  paths = []
  for k in range(0,len(pt)):
    signals_to_send = []
    # Do not send signals that are allowed to be missed
    for i in range(0,len(pt[k].signals)):
      if(pt[k].signals[i].miss_left==0):
        signals_to_send.append(pt[k].signals[i])
        # reset the number of allowed misses
        pt[k].signals[i].miss_left = pt[k].signals[i].num_all_miss
      else:
        # decrease the number of allowed misses if signal is not sent
        pt[k].signals[i].miss_left -= 1
    signals+=signals_to_send
    paths.append(pt[k].path)
  # list of packages
  packages = []
  # create first package
  if(len(signals) > 0):
    p=Package(paths)
    # list of all packages
    packages.append(p)
    # sort signals by size in descending order
    DSD=sort_desc(signals)
    for i in range(0, len(DSD)):
      # sort already created packages by size in descending order
      PSD=sort_desc(packages)
      for j in range(0, len(PSD)):
        fit=0
        # check if signal fits to the package
        if(DSD[i].size+PSD[j].size <= MAX_PACKAGE_SIZE):
          PSD[j].add_signal(DSD[i])
          # if fits continue with the next signal
          # else try with the next package
          fit=1
          break
      # if it does not fit in any existing package then create new one
      if(fit==0):
        pnew = Package(paths)
        pnew.add_signal(DSD[i])
        packages.append(pnew)
  return packages

# Main part of the algorithm
# Function that updates the packing schedule and content of all packages in each FCI
def Optimal(FCIs):
  global signals
  for i in range(0, len(FCIs)):
    # package creation times
    times = []
    for ds in FCIs[i].datasets:
      times += ds.ti
    times = sorted(times,reverse=False)
    times = list(dict.fromkeys(times))
    time_schedule = []
    for time in times:
      # list of datasets sent in this time moment
      sent = []
      for ds in FCIs[i].datasets:
        # check if dataset is sent in this time moment
        if time in ds.ti:
          # add dataset to the list
          sent.append(ds)
      # all possible packing type combinations
      list_of_package_types = packingtypes(sent)
      # all possible sets of packages
      lopackages = []
      # list of cost functions values for each set of packages 
      cfuns = []
      temp = []
      for w in range(0, len(signals)):
        temp.append(signals[w].miss_left)
      for package_type in list_of_package_types:
        for w in range(0, len(signals)):
          signals[w].miss_left = temp[w]
        # list of packages for the specific type
        packages = []
        for j in range(0, len(package_type)):
          # perform bin-packing
          subpackages = BFD(package_type[j])
          packages += subpackages
        lopackages.append(packages)
        cfuns.append(cost_fun(packages))
      # find set with minimal cost function value
      mini = cfuns.index(min(cfuns))
      # list of pakets (type Package) that need to be sent in time moment "time"
      best = lopackages[mini]
      time_schedule.append(best)
    # assign package sending schedule to the FCI
    FCIs[i].schedule(times,time_schedule)
    

# functions that calculates segments' occupancy
def calculateSegmentsOccupancy(FCIs):
  global segments
  # set occupancy of all segments to zero
  for i in range(0,len(segments)):
    segments[i].occ=0

  # get the execution time from the GUI input
  execTime = int(e.get())

  # loop that goes through all FCIs and calculates occupancy
  for fci in FCIs:
    # calculate num. of times the calculation will performed (num. of times the FCIs packing behaviour in its hyperperiod will be repeated)
    N = math.floor(execTime / fci.hyperperiod)
    # pl - packet list in one time moment
    for pl in fci.timeschedule:
      # going through packets in the packet list
      for p in pl:
        segs = []
        # exclude duplicate segments for packet p - provjeriti validnost, mozda ne treba duplikate iskljucivati ako se paket salje kroz vise pathova
        for path in p.paths:
          for segment in path:
            if(not (segment in segs)):
              segs.append(segment)
        for s in segs:
          # the same occupancy will be generated N times
          s.occupancy(N*p.size)

    # calculate network occupancy in time moments between the N-multiple of the fci hyperperiod and the execution time
    Sum = N * fci.hyperperiod + fci.times[0]
    i = 1
    while(Sum <= execTime):
      for p in fci.timeschedule[i]:
        segs = []
        # exclude duplicate segments for packet p - provjeriti validnost, mozda ne treba duplikate iskljucivati ako se paket salje kroz vise pathova
        for path in p.paths:
          for segment in path:
            if (not (segment in segs)):
              segs.append(segment)
        for s in segs:
          s.occupancy(p.size)
      Sum += fci.times[i]
      i += 1

# calculate total network occupancy as the sum of the network occupancy of all segments
def networkOccupancy(segments):
  list = []
  for s in segments:
    list.append(s.occ)
  return sum(list)

# find and return the biggest hyperperiod among the FCIs
def optimization_time(fcis):
  time=[]
  for fci in fcis:
    time.append(max(fci.times))
  return max(time)
  
# find and return the length of the longest list in the list of lists
def find_max_list_len(lista):
    list_len = [len(i) for i in lista]
    return max(list_len)

# function that writes results to the Excel
def exportResultsToExcel(fcis, segments):
  # create Results.xslx Excel file
  writer = pd.ExcelWriter(r'Results.xlsx', engine='xlsxwriter')
  # loop that goes through the FCIs
  for i in range(0, len(fcis)):
    content = [] # content to be written
    for j in range(0, len(fcis[i].timeschedule)):
      temp = [fcis[i].times[j]] # packing moments
      temp.append(len(fcis[i].timeschedule[j])) # number of packets
      for k in range(0, len(fcis[i].timeschedule[j])):
        temp.append(fcis[i].timeschedule[j][k].size) # packet's sizes
        IDs = []
        for h in range(0, len(fcis[i].timeschedule[j][k].signals)):
          IDs.append(fcis[i].timeschedule[j][k].signals[h].ID) # IDs of signals in the packets
        temp.append(IDs)
      content.append(temp)
    length = find_max_list_len(content)
    print(length)  
    packet_num = int((length-2)/2)
    string = ['Time moments']
    string.append('Number of packets')
    for l in range(0, packet_num):
      string.append('Packet ' + str(l+1) + ' size (B)')
      string.append('Packet ' + str(l+1) + ' signals')    
    df = pd.DataFrame(content)
    df.to_excel(writer, sheet_name='FCI' + str(i+1), index=False, header=string)

  # write the occupancy of the segments and total network on the last sheet
  content = []
  suma = 0
  for i in range(0, len(segments)):
    temp = ['Segment ' + str(i+1)]
    suma +=  segments[i].occ
    temp.append(segments[i].occ)  
    content.append(temp)
  content.append(['Total network occupancy', suma])
  df = pd.DataFrame(content)
  df.to_excel(writer, sheet_name='Network occupancy', index=False, header=['Segments', 'Network occupancy per segments (B)'])

  writer.save()

# defines the behaviour of GUI button for calculating the network occupancy
# prints the occupancy to the label
def ButtonOcc():
  global signals, controllers, tasks, datasets, switches, fcis, segments
  calculateSegmentsOccupancy(fcis)
  e1.delete(0, END)
  Len = 10 - len(str(networkOccupancy(segments))) - 1
  spaces = str(' ') * Len
  e1.insert(0, str(networkOccupancy(segments)) + spaces + 'B')

# defines the behaviour of GUI button for running the reference case
# sets occupancy of every segment to zero and runs the reference case
def ButtonRef():
  global signals, controllers, tasks, datasets, switches, fcis, segments
  signals, controllers, tasks, datasets, switches, fcis, segments = loadFromExcel()
  for i in range(0,len(segments)):
    segments[i].occ=0
  Ref(fcis)

# defines the behaviour of GUI button for running the proposed approach
# sets occupancy of every segment to zero and runs the proposed algorithm
def ButtonOptimal():
  global signals, controllers, tasks, datasets, switches, fcis, segments
  signals, controllers, tasks, datasets, switches, fcis, segments = loadFromExcel()
  for i in range(0,len(segments)):
    segments[i].occ=0
  Optimal(fcis)


# code for running the algorithm without the GUI
# MAIN

#signals, controllers, tasks, datasets, switches, fcis, segments = loadFromExcel()

#Ref(fcis)
#Optimal(fcis)
#calculateSegmentsOccupancy(fcis)
#occupancy=networkOccupancy(segments)
#exportResultsToExcel(fcis, segments)
# end of the code for running the algorithm without the GUI


# GUI architecture
root = Tk()

e = Entry(root, width = 10, fg='black', bg='white', borderwidth = 2)
e.grid(row=0,column=1)

e1 = Entry(root, width = 10, fg='black', bg='white', borderwidth = 2)
e1.grid(row=1,column=1)

labelOcc = Label(root, text='Total network occupancy:')
labelOcc.grid(row=1,column=0)

labelOT = Label(root, text='Execution time (ms):')
labelOT.grid(row=0,column=0)

buttonAlgRef = Button(root, text='Run reference case', height=3, width=25, command=ButtonRef, fg='black', bg='white')
buttonAlgRef.grid(row=2,column=0)

buttonAlgOpt = Button(root, text='Run optimal solution', height=3, width=25, command=ButtonOptimal, fg='black', bg='white')
buttonAlgOpt.grid(row=2,column=1)

buttonOcc = Button(root, text='Calculate network occupancy', height=3, width=25, command=ButtonOcc, fg='black', bg='white')
buttonOcc.grid(row=3,column=0)

buttonExport = Button(root, text='Export to excel', height=3, width=25, command=lambda: exportResultsToExcel(fcis, segments), fg='black', bg='white')
buttonExport.grid(row=3,column=1)

root.mainloop()











