import os

from Help_funs import isInt, QuitException, quitOrInput
import Vars
from Vars import getInst, printInst, inpInst

def chooseYorNorA(A_allowed, current = None):
	"""
		choosesetYorN(current = None):
		Returns "Y" or "N", or "A" if A_allowed is True
		
		Parameters
		__________
		A_allowed: If True, input "A" is also allowed
		current: string "Y" or "N", or "A" if A_allowed is True; the current setting
	"""
	choose = ["Y", "N", "A"] if A_allowed else ["Y", "N"]
	if current is not None and current not in choose:
		raise Exception("In chooseYorNorA: Argument 'current' must be None or one of the allowed inputs.")
	inst = getInst("setYorNorA") if A_allowed else getInst("setYorN")
	user_input = input(inst + "\n").upper()
	while not user_input in choose:
		if current and user_input == "QUIT":
			return current
		user_input = input(inst + "\n").upper()
	return user_input

def chooseLanguage(current = None):
	"""
		chooseLanguage(current = None):
		Returns language code "zh-hk", "zh-cn", or "ja"
		
		Parameters
		__________
		current: string "zh-hk", "zh-cn", or "ja"
		The current language code
	"""
	langs = ["zh-hk", "zh-cn", "ja"]
	Vars.lang = input("\n" + Vars.instructions_All["chooseLanguage"] + "\n").lower()
	while not Vars.lang in langs:
		if current and Vars.lang.upper() == "QUIT":
			return current
		Vars.lang = input("\n" + Vars.instructions_All["chooseLanguage"] + "\n").lower()
	return Vars.lang

def chooseOneTimeZone(current = None): # Choose one time zone, returns one time zone
	"""
	   chooseOneTimeZone(current = None)
	   Chooses the time zone for one functionality (record, schedule, time), returns (1) string for time zone code and (2) bool for quitted or not
	   
	   Parameters
	   __________
	   current: string, must be in tznames below
	   The current time zone
	"""
	choose = ""
	print("\n" + "\n".join(["{0:>2}. {1}".format(str(index + 1), getInst("timeZone" + tz)) for index, tz in enumerate(Vars.tzs)])) # Print all possible time zones
	while (not isInt(choose)) or (not int(choose) in range(1, len(Vars.tzs) + 1)):
		if current and choose == "QUIT":
			return current, True # Do not change settings
		choose = inpInst("setTimeZone", rep=str(len(Vars.tzs))).upper()
	return Vars.tznames[int(choose) - 1], False

def chooseTimeZone(current): # Choose one time zone in the three options, returns all three time zones
	"""
		chooseTimeZone(current)
		Chooses all time zones
		
		Parameters
		__________
		current: the string composed of three time zone strings joined by " ** "
		The current time zones
	"""
	print("\n" + getInst("promptSetParameters"))
	print("1. {0}".format(getInst("paraTimeZoneRecord")))
	print("2. {0}".format(getInst("paraTimeZoneSchedule")))
	print("3. {0}".format(getInst("paraTimeZoneTime")))
	print("4. {0}".format(getInst("paraTimeZoneUnify")))
	choose = input().upper()
	while (not isInt(choose)) or (not int(choose) in range(1, 5)):
		if choose == "QUIT":
			return current
		choose = inpInst("chooseFromAbove", rep="4").upper()
	current = current.split(" ** ")
	choose = int(choose) - 1
	if choose in range(0,3):
		current[choose], quit = chooseOneTimeZone(current[choose])
	elif choose == 3: # If unify all time zones
		tz, quit = chooseOneTimeZone(current[0]) # current[0] is meaningless, but needed to enable the user to quit from chooseOneTimeZone()
		if quit: # If quitted
			return " ** ".join(current)
		else:
			return " ** ".join([tz] * 3)
	else:
		assert()
	return " ** ".join(current) # Record, Schedule, Time

def chooseRandom50Words(current):
	"""
		chooseRandom50Words(current = None):
		Returns the number of random words in the Random50Words mode.
		
		Parameters
		__________
		current: An integer, the current setting.
	"""
	print()
	num = inpInst("chooseRandom50Words")
	while not (isInt(num) and int(num) >= 1) :
		if num.upper() == "QUIT":
			return current
		print()
		if not isInt(num):
			num = inpInst("enterANumber")
		else: # int(num) >= 1
			num = inpInst("enterAPositiveNumber")
	return num
					
def setParameters():
	"""
		setParameters()
		Returns the system parameters set by user, or set by default if first time of use.
	"""
	par = os.path.join(Vars.sys_path, 'Parameters.txt')
	Vars.parameters = {}
	if not os.path.exists(par):
		print("\n" + Vars.instructions_All["greetings"])
		Vars.lang = chooseLanguage()
		Vars.availableBooks = list(Vars.listNumber[Vars.lang])
		Vars.instructions = getInstructionsLang(Vars.lang)
		timeZoneQuitted = True
		while timeZoneQuitted:
			timeZone, timeZoneQuitted = chooseOneTimeZone()
		Vars.parameters["AllForRandom50Words"] = "A"
		Vars.parameters["Language"] = Vars.lang
		Vars.parameters["Random"] = "A"
		Vars.parameters["Random50Words"] = "50"
		Vars.parameters["Record"] = "A"
		Vars.parameters["ShowComments"] = "Y"
		Vars.parameters["TimeZone"] = " ** ".join([timeZone] * 3)
		f = open(par, 'w')
		for para in sorted(Vars.parameters):
			f.write(para + ": " + Vars.parameters[para] + "\n")
		f.close()
	else:
		f = open(par)
		for s in f:
			s = s.split(": ")
			if len(s) == 1:
				s.append("")
			Vars.parameters[s[0]] = s[1].rstrip("\n")
		f.close()
		Vars.instructions = getInstructionsLang(Vars.parameters["Language"])
		Vars.availableBooks = list(Vars.listNumber[Vars.parameters["Language"]])
	return Vars.parameters

def changeParameters():
	"""
		changeParameters():
		Changes one system parameter.
	"""
	Vars.instructions["paraAllForRandom50Words"] = getInst("paraAllForRandom50Words", rep=Vars.parameters["Random50Words"])
	Vars.instructions["paraRandom50Words"] = getInst("paraRandom50Words", rep= Vars.parameters["Random50Words"])
	prompt = "\n" + getInst("promptSetParameters") + "\n" + "\n".join([str(index + 1) + ". " + getInst("para" + par) + "\n" for index, par in enumerate(sorted(Vars.parameters))])
	try:
		choose = quitOrInput(prompt).upper()
	except QuitException:
		return
	while not (isInt(choose) and int(choose) >= 1 and int(choose) <= len(Vars.parameters)):
		try:
			choose = quitOrInput(prompt).upper()
		except QuitException:
			return
	choose = sorted(Vars.parameters)[int(choose) - 1]
	if choose == "AllForRandom50Words":
		setChoose = chooseYorNorA(True, Vars.parameters["AllForRandom50Words"])
	elif choose == "Language":
		setChoose = chooseLanguage(Vars.parameters["Language"])
	elif choose == "Random":
		setChoose = chooseYorNorA(True, Vars.parameters["Random"])
	elif choose == "Random50Words":
		setChoose = chooseRandom50Words(Vars.parameters["Random50Words"])
	elif choose == "Record":
		setChoose = chooseYorNorA(True, Vars.parameters["Record"])
	elif choose == "ShowComments":
		setChoose = chooseYorNorA(False, Vars.parameters["ShowComments"])
	elif choose == "TimeZone":
		setChoose = chooseTimeZone(Vars.parameters["TimeZone"])
	else:
		assert()
	f = open(os.path.join(Vars.sys_path, 'Parameters.txt'))
	g = open(os.path.join(Vars.sys_path, 'Parameters 2.txt'), 'w')
	for s in f:
		if s.split(": ")[0] == choose:
			s = choose + ": " + setChoose + "\n"
		g.write(s)
	f.close()
	g.close()
	os.rename(os.path.join(Vars.sys_path, 'Parameters 2.txt'), os.path.join(Vars.sys_path, 'Parameters.txt'))
	Vars.parameters = setParameters()
	Vars.lang = Vars.parameters["Language"]
	Vars.instructions = getInstructionsLang(Vars.lang)
	printInst("changesSaved")
	return

def getAllInstructions():
	"""
		getAllInstructions()
		Returns the Vars.instructions needed to be shown before letting the user chooses system language
	"""
	Vars.instructions_All = {}
	f = open(os.path.join(Vars.sys_path, 'Instructions_all.txt'))
	for s in f:
		s = s.split(": ")
		if len(s) == 1:
			s.append("") # If instruction is empty (possible because it might be non-empty for some other languages)
		Vars.instructions_All[s[0]] = s[1].replace("RETURN", "\n").replace("SPACE", " ") # With '\n'
	f.close()
	return Vars.instructions_All

def getInstructionsLang(lang):
	"""
		getInstructionsLang(lang):
		Returns the Vars.instructions in the chosen language
		
		Paramters
		_________
		lang : string "zh-hk", "zh-cn", or "ja"
		Language code
	"""
	Vars.instructions = {}
	if lang == "zh-hk":
		f = open(os.path.join(Vars.sys_path, 'Instructions_hant.txt'))
	elif lang == "zh-cn":
		f = open(os.path.join(Vars.sys_path, 'Instructions_hans.txt'))
	elif lang == "ja":
		f = open(os.path.join(Vars.sys_path, 'Instructions_ja.txt'))
	else:
		assert()
	for s in f:
		s = s.split(": ")
		if len(s) == 1:
			s.append("") # If instruction is empty (possible because it might be non-empty for some other languages)
		Vars.instructions[s[0]] = s[1].replace("RETURN", "\n").replace("SPACE", " ") # With '\n'
	f.close()
	return Vars.instructions

def initialization():
	"""
		initialization()
		Initializes the program: set the parameters, defines global variable "Vars.lang", and makes "Record" directory
	"""
	Vars.instructions_All = getAllInstructions() # Top
	Vars.parameters = setParameters()
	Vars.lang = Vars.parameters["Language"]
	#Vars.instructions = getInstructionsLang(Vars.parameters["Language"])
	if not os.path.exists(Vars.record_path):
		os.makedirs(Vars.record_path)
	return
