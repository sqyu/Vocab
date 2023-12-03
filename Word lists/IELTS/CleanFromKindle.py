import re
import pyperclip

def POS(s):
	try:
		return re.compile("^[a-z]+[.]").match(s).group(0)
	except:
		return ""

def one_list():
	ss = ""
	sss = input("")
	while sss != "":
		ss = ss + "\n" + sss
		sss = input("")
	res = []
	for s in ss.split("\n"):
		try:
			if not "[" in s:
				continue
			s = s.split("\n")[0].replace(" ", "").replace("*", "").replace(u"…", u"⋯")
			word, IPA_meaning = s.split("[")
			IPA, meaning = IPA_meaning.split("]")
			meanings = meaning.split(u"；")
			last_POS = ""
			for i, meaning in enumerate(meanings):
				this_POS = POS(meaning)
				if this_POS:
					last_POS = this_POS
					meanings[i] = meanings[i].replace(this_POS, this_POS+" ")
				else:
					meanings[i] = last_POS + " " + meaning
			meanings = " %% ".join(meanings)
			res.append(word + " ** [" + IPA + "] ** " + meanings)
		except Exception as e:
			print("Error occurred in "+s+":\n"+str(e))
	print("\n".join(res))
	if res:
		pyperclip.copy("\n".join(res))

if __name__ == '__main__':
	while True:
		one_list()
