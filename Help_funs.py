import unidecode

class QuitException(Exception):
	pass

def quitOrInput(prompt=None):
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

def unique_everseen(seq, key=lambda x:x):
	seen = set()
	seen_add = seen.add
	return [x for x in seq if not (key(x) in seen or seen_add(key(x)))]

def comp_answers(inp, word):
	return unidecode.unidecode(inp).lower() == unidecode.unidecode(word).lower()

def shuffle_if_random(l, rand):
	return random.sample(l, len(l)) if rand else l

def comp_conj_answers(inp, words):
	return any([comp_answers(inp, form) for form in words])
