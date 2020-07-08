record_path = 'Record'
sys_path = 'System Files'
wordLists_path = 'Word lists'

acronym = {"Petit Livre Rouge": "PLR", "Trois Mille": "TM", "Le Français 1": "LF1", "Hyojun Nihongo": "HJNHG"}
findAcronym = {value: key for key, value in acronym.items()}

listNumber = {"zh-hk": {"Petit Livre Rouge": list(range(1,43)), "Trois Mille": list(range(1,32)), "Le Français 1": list(range(1,2)), "Hyojun Nihongo": list(range(1,2))}, "zh-cn": {"Petit Livre Rouge": list(range(1,43)), "Trois Mille": list(range(1,32)), "Le Français 1": list(range(1,2))}, "ja": {"Petit Livre Rouge": [3, 5, 11, 12, 13], "Le Français 1": list(range(1,2))}}
lang = ""
parameters = {}
instructions = {}
instructions_All = {}
availableBooks = []

tzs = ["Hawaii", "Alaska", "LosAngeles", "Arizona", "Mountain", "Chicago", "NewYork", "UTC", "London", "Paris", "Shanghai", "Singapore", "Perth", "Tokyo", "Seoul", "Sydney"]
tznames = ["US/Hawaii", "US/Alaska", "US/Pacific", "US/Arizona", "US/Mountain", "US/Central", "US/Eastern", "utc", "Europe/London", "Europe/Paris", "Asia/Shanghai", "Asia/Singapore", "Australia/Perth", "Asia/Tokyo", "Asia/Seoul", "Australia/Sydney"]
