# Protocol, Plots and utils imports
import MyGUICommons, Novonix_Protocol, Defs, myProgressBar, utils, re, csv, numpy, matplotlib.pyplot, scipy.interpolate, math
from MyGUICommons import exit
from Novonix_Protocol import *
from Defs import *
from myProgressBar import *
from scipy.interpolate import spline
from utils import *

# Run Method
def run(info):
	# 1. Formating the files
	if(info.Plot_Protocol == Plot_Protocol_Novonix):
		for n_file in range(0,len(info.Plot_Files)):
			format(info.Plot_Files[n_file],info.Plot_Precision)
	elif(info.Plot_Protocol == Plot_Protocol_BaSyTec):
		for n_file in range(0,len(info.Plot_Files)):
			print('BaSyTec format')
	elif(info.Plot_Protocol == Plot_Protocol_Xanes):
		for n_file in range(0,len(info.Plot_Files)):
			print('Xanes format')


	# 2. Plotting
	if(info.Plot_Protocol == Plot_Protocol_Novonix):
		for n_file in range(0,len(info.Plot_Files)):
			newfilename = standard_formated_name(info.Plot_Files[n_file])
			Plot2d().plot(newfilename,info.Plot_Destination,info.Plot_XData+4,info.Plot_YData+4,info.Plot_Cycle,
							info.Plot_Title,Novonix_Table[info.Plot_XData],Novonix_Table[info.Plot_YData],True)
			#else:
			#	Plot2d().plot2y()

	elif(info.Plot_Protocol == Plot_Protocol_BaSyTec):
		print("BaSyTec")
	elif(info.Plot_Protocol == Plot_Protocol_Xanes):
		print("Xanes")

	# 3. That's all folks :) ...
	exit()



















class Plot2d():

	def __plotColumbic__(self,file,dest,col,plottitle,plotx,ploty):
		print('Columbic')
		# 1. Setting plot labels and retrieving the csv information
		print('3: ',end="")
		matplotlib.pyplot.title(plottitle)
		print('|||',end="")
		matplotlib.pyplot.xlabel(plotx)
		print('||||',end="")
		matplotlib.pyplot.ylabel(ploty)
		print('||| 100%')
		
		charge, discharge = [], []
		information = []
		cycle = 1

		# 5. Plotting
		print('4: Plotting... total estimate time: 15s')
		line = file.readline()
		matplotlib.interactive(True)

		while(re.match('^$', line ) is None):
			# a. tokenizing line
			tokens = line.split(',')

			while(re.match('^$', line ) is None and cycle == -int(tokens[1])):
				# b. storing the information
				value = float(tokens[col])

				if(int(tokens[1]) < 0 and value != 0):
					discharge.append(value)

				# c. reading the new line
				line = file.readline()
				tokens = line.split(',')

			cycle = cycle + 1

			while(re.match('^$', line ) is None and cycle == int(tokens[1])):
				# b. storing the information
				value = float(tokens[col])

				if(int(tokens[1]) > 0):
					charge.append(value)

				# c. reading the new line
				line = file.readline()
				tokens = line.split(',')

			# d. incrementing the cycle
			if(len(discharge) > 1 and len(charge) > 1 and (max(discharge)-min(discharge)) != 0):	
				information.append(((max(charge)-min(charge))/(max(discharge)-min(discharge)))*100)

			charge, discharge = [], []

		print(dest + '/' + plottitle + '.png')
		matplotlib.pyplot.plot(information,'-')

		# 6 . Closing the opened file
		matplotlib.pyplot.show()
		print('5: |||||||||| 100%')
		file.close()

		# 7. Thats all folks :) ...
		print('6: |||||||||| 100%')
		



















	def __average__(self, V, window):
		return sum(V)/window

	def __delta__(self, V, cond, window):
		if cond == 'f':
			return self.__average__(V[window+1:], window)-self.__average__(V[window-math.ceil(window/2):window+math.ceil(window/2)], window)
		elif cond == 'b':
			return self.__average__(V[window-math.ceil(window/2):window+math.ceil(window/2)], window) - self.__average__(V[:window-1], window)

	def __differentiate__(self, V, Q, window):
		dVdQ = []
		plotx = []

		for i in range(window, len(V)-window-1, window):
			dVdQ.append(((self.__delta__(V[i-window:i+window+1], 'f', window)/self.__delta__(Q[i-window:i+window+1], 'f', window)) + (self.__delta__(V[i-window:i+window+1], 'b', window)/self.__delta__(Q[i-window:i+window+1],'b', window)))*(1/2))
			plotx.append(Q[i])

		return dVdQ, plotx

	def __plotDVA__(self,file,dest,plottitle,plotx_title,ploty_title):
		print('DVA')
		cycle_test = 1
		
		# 1. Setting plot labels and retrieving the csv information
		print('3: ',end="")
		matplotlib.pyplot.title(plottitle)
		print('|||',end="")
		matplotlib.pyplot.xlabel(plotx_title)
		print('||||',end="")
		matplotlib.pyplot.ylabel(ploty_title)
		print('||| 100%')
		
		Q = []
		V = []
		dQdV = []
		cycle, cur_file = 1, 1

		# 2. Plotting
		print('4: Plotting... total estimate time: 15s')
		line = file.readline()
		matplotlib.interactive(True)
		matplotlib.pyplot.figure(cur_file)
		
	

		while(re.match('^$', line ) is None):
			# a. tokenizing line
			tokens = line.split(',')
			#print('while de fora')

			while(re.match('^$', line ) is None and cycle ==  abs(int(tokens[1]))):
				# b. storing the information
				#print('while de dentro')
				valueQ = float(tokens[7]) #capacitancia
				valueV = float(tokens[6]) #potencial

				
				if(int(tokens[1]) < 0 and valueQ != 0 and valueV != 0):
					Q.append(valueQ)
					V.append(valueV)

				# c. reading the new line
				line = file.readline()
				tokens = line.split(',')

			# d. incrementing the cycle
			cycle = cycle + 1
			time = []

			#Test if the vector Q and V are not empty
			if(len(Q) > 3 and len(V) > 3 and any([t != Q[0] for t in Q]) ):
				# e. Differentiating dQ/dV
				plotx = []
				window_size= max([3, round(len(V)/50) if round(len(V)/50) % 2 != 0 else round(len(V)/50)+1])
				dVdQ, plotx = self.__differentiate__(V, Q, window_size)
				
				#f. plotting
				matplotlib.pyplot.plot(plotx, dVdQ,'-',label = 'original')
				V, Q, plotx, dVdQ = [], [], [], []

				# f. plot
				#if(abs(cycle) / 10 > cur_file):

				print(dest + '/' + plottitle + str(cur_file) + '.png')
				matplotlib.pyplot.legend(loc = 'upper right')

				cur_file = cur_file + 1
				matplotlib.pyplot.figure(cur_file)

				matplotlib.pyplot.title(plottitle)
				matplotlib.pyplot.xlabel(plotx_title)
				matplotlib.pyplot.ylabel(ploty_title)

		# 6 . Closing the opened file
		matplotlib.pyplot.show()
		print('5: |||||||||| 100%')
		file.close()

		# 7. Thats all folks :) ...
		print('6: |||||||||| 100%')





















	def plot(self,filename,dest,xcol,ycol,mode,plottitle,plotx,ploty,header):
		pb = myProgressBar('Plotting',['Opening File','Header Getting','Plot Type','Setting Labels and Information','Plot','Finishing'],40)

		# 1. Opening the file
		pb.start()
		file = fopen(filename,'r')
		pb.update(100)
		
		# 2. Ignoring the header
		if(header is True):
			file.readline()
		pb.update(100)

		# 3. Verifying the plot type
		if(COULUMBIC in [xcol,ycol]):
			self.__plotColumbic__(file,dest,7,plottitle,'Cycle Number','Coulombic Efficiency (%)')
			return(None)
			
		if(DVA in [xcol,ycol]):
			self.__plotDVA__(file,dest,plottitle,'Cycle Number','dQ/dV')
			return(None)
		pb.update(100)	

		# 4. Setting plot labels and retrieving the csv information
		matplotlib.pyplot.title(plottitle)
		pb.update(20)	
		matplotlib.pyplot.xlabel(plotx)
		pb.update(40)	
		matplotlib.pyplot.ylabel(ploty)
		pb.update(60)	
		
		information, xinformation, yinformation = [], [], []
		pb.update(80)	
		cycle, cur_file = 1, 1
		pb.update(100)	

		# 5. Plotting
		line = file.readline()
		matplotlib.interactive(True)
		matplotlib.pyplot.figure(cur_file)
		pb.update(20)

		if(xcol == 4):
			while(re.match('^$', line ) is None):
				# a. tokenizing line
				tokens = line.split(',')

				while(re.match('^$', line ) is None and cycle == abs(int(tokens[1]))):
					# b. storing the information
					value = float(tokens[ycol])

					if(mode*int(tokens[1]) > 0):
						information.append(value)
					elif(mode == FULL_CYCLE):
						information.append(value)

					# c. reading the new line
					line = file.readline()
					tokens = line.split(',')

				# d. incrementing the cycle
				cycle = cycle + 1
				time = []

				for i in range(1,len(information)+1):
					time.append(i)

				#spline(time,information,time)
				matplotlib.pyplot.plot(information,'-',label = 'Cycle ' + str(cycle-1))
				information = []

				# e. plotting
				if(abs(cycle) / 10 > cur_file):
					matplotlib.pyplot.legend(loc = 'upper right')

					cur_file = cur_file + 1
					matplotlib.pyplot.figure(cur_file)

					matplotlib.pyplot.title(plottitle)
					matplotlib.pyplot.xlabel(plotx)
					matplotlib.pyplot.ylabel(ploty)

			pb.update(80)	
			if(abs(cycle) / 10 == cur_file):
				matplotlib.pyplot.legend(loc = 'upper right')

		elif(ycol == 4):
			matplotlib.pyplot.xlabel(ploty)
			matplotlib.pyplot.ylabel(plotx)

			while(re.match('^$', line ) is None):
				# a. tokenizing line
				tokens = line.split(',')

				while(re.match('^$', line ) is None and cycle == abs(int(tokens[1]))):
					# b. storing the information
					value = float(tokens[xcol])

					if(mode*int(tokens[1]) > 0):
						information.append(value)
					elif(mode == FULL_CYCLE):
						information.append(value)

					# c. reading the new line
					line = file.readline()
					tokens = line.split(',')

				# d. incrementing the cycle
				cycle = cycle + 1
				time = []

				for i in range(1,len(information)+1):
					time.append(i)

				#spline(time,information,time)
				matplotlib.pyplot.plot(information,'-',label = 'Cycle ' + str(cycle-1))
				information = []

				# e. plotting
				if(abs(cycle) / 10 > cur_file):
					matplotlib.pyplot.legend(loc = 'upper right')

					cur_file = cur_file + 1
					matplotlib.pyplot.figure(cur_file)

					matplotlib.pyplot.title(plottitle)
					matplotlib.pyplot.xlabel(ploty)
					matplotlib.pyplot.ylabel(plotx)


			pb.update(80)	
			if(abs(cycle) / 10 == cur_file):
				matplotlib.pyplot.legend(loc = 'upper right')

		else:
			while(re.match('^$', line ) is None):
				# a. tokenizing line
				tokens = line.split(',')

				while(re.match('^$', line ) is None and cycle == abs(int(tokens[1]))):
					# b. storing the information
					xvalue = float(tokens[xcol])
					yvalue = float(tokens[ycol])

					if(mode*int(tokens[1]) > 0):
						xinformation.append(xvalue)
						yinformation.append(yvalue)
					elif(mode == FULL_CYCLE):
						xinformation.append(xvalue)
						yinformation.append(yvalue)

					# c. reading the new line
					line = file.readline()
					tokens = line.split(',')

				# d. incrementing the cycle
				cycle = cycle + 1

				#spline(time,information,time)
				matplotlib.pyplot.plot(xinformation,yinformation,'s',label = 'Cycle ' + str(cycle-1))
				xinformation, yinformation = [], []

				# e. plotting
				if(abs(cycle) / 10 > cur_file):
					matplotlib.pyplot.legend(loc = 'upper right')

					cur_file = cur_file + 1
					matplotlib.pyplot.figure(cur_file)

					matplotlib.pyplot.title(plottitle)
					matplotlib.pyplot.xlabel(plotx)
					matplotlib.pyplot.ylabel(ploty)

			pb.update(80)	
			if(abs(cycle) / 10 == cur_file):
				matplotlib.pyplot.legend(loc = 'upper right')

		# 6 . Closing the opened file
		pb.update(100)	
		matplotlib.pyplot.show()
		pb.update(50)	
		file.close()
		pb.update(100)	

		# 7. Thats all folks :) ...
