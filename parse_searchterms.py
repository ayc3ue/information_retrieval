# print("hello world")
import re
s = set()
with open('searchterms.txt') as f:
	line = f.readline()
	while (line):
		s.add((re.findall(r"[\w']+", line))[0])
		while(1):
			try:
				line = f.readline()
				break
			except Exception as e:
				pass
for item in s:
	print(item)