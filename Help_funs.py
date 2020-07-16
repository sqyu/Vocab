class QuitException(Exception):
	pass

def quitOrInput(prompt):
	if prompt:
		print(prompt)
	s = input()
	if s.upper() == "EXIT":
		quit()
	elif s.upper() == "QUIT":
		raise QuitException
	else:
		return s
		
def isInt(s):
	"""
		isInt(s):
		Returns True if s can be converted to int, or False otherwise
		
		Parameters
		__________
		s: string
	"""
	try:
		int(s)
		return True
	except ValueError:
		return False
		
def sortDate(dateList):
	"""
		sortDate(dateList):
		Sorts the dates in dateList.
		
		dateList: list of strings
		A list of dates in the format "(M)M/(D)D"
	"""
	for index1 in range(0, len(dateList)):
		for index2 in range(0, len(dateList)):
			d1 = dateList[index1].split("/")
			d2 = dateList[index2].split("/")
			if (int(d2[0]) > int(d1[0])) or (int(d1[0]) == int(d2[0]) and int(d2[1]) > int(d1[1])):
				d = dateList[index1]
				dateList[index1] = dateList[index2]
				dateList[index2] = d
	return dateList
