import os
import json
import re
import sys
import datetime
from core.Config import conf

reload(sys)  
sys.setdefaultencoding('Cp1252')

def repeat_to_length(string_to_expand, length):
   return (string_to_expand * ((length/len(string_to_expand))+1))[:length]

tools = ["NopolPC", "NopolC", "Ranking", "Brutpol", "Genprog", "Kali"]

root = conf.resultsRoot
resultsAll = {}
resultsAllPath = os.path.join(root, "results.json")
resultsMdPath = os.path.join(root, "results.md")
rankingAll = {}
for project in os.listdir(root):
	projectPath = os.path.join(root, project) 
	if os.path.isfile(projectPath):
		continue
	resultsProject = {}
	resultsProjectPath = os.path.join(projectPath, "results.json")
	rankingProjectPath = os.path.join(projectPath, "ranking.json")
	rankingBug = {}
	for bugId in os.listdir(projectPath):
		bugPath = os.path.join(projectPath, bugId) 
		if not bugId.isdigit() or os.path.isfile(bugPath):
			continue
		resultsBugPath = os.path.join(bugPath, "results.json")
		resultsBug = {}
		for tool in os.listdir(bugPath):
			toolPath = os.path.join(bugPath, tool)
			if os.path.isfile(toolPath):
				continue
			resultsToolPath = os.path.join(toolPath, "results.json")
			stderrToolPath = os.path.join(toolPath, "stderr.log")
			stdoutToolPath = os.path.join(toolPath, "stdout.log")
			if os.path.exists(resultsToolPath):
				with open(resultsToolPath) as data_file:
					data = json.load(data_file)
					if tool == "Ranking":
						rankingBug[bugId] = data
					else:
						resultsBug[tool] = data
			elif os.path.exists(stderrToolPath):
				with open(stderrToolPath) as data_file:
					data = data_file.read()
					if len(data) == 0:
						resultsBug[tool] = {
							"error": "EMPTY"
						}
						continue
				with open(stderrToolPath) as data_file:
					data = data_file.read()
					m = re.search("Job [0-9]+ KILLED", data)
					if m:
						resultsBug[tool] = {
							"error": "TIMEOUT"
						}
					elif len(data) == 0:
						resultsBug[tool] = {
							"error": "EMPTY"
						}
					else:
						resultsBug[tool] = {
							"error": "ERROR"
						}
		resultsProject[int(bugId)] = resultsBug
		resultsBugFile = open(resultsBugPath, "w")
		resultsBugFile.write(json.dumps(resultsBug, sort_keys=True))
		resultsBugFile.close()
	rankingAll[project] = rankingBug
	resultsAll[project] = resultsProject
	resultsProjectFile = open(resultsProjectPath, "w")
	resultsProjectFile.write(json.dumps(resultsProject, sort_keys=True))
	resultsProjectFile.close()
	rankingProjectFile = open(rankingProjectPath, "w")
	rankingProjectFile.write(json.dumps(rankingBug, sort_keys=True))
	rankingProjectFile.close()
resultsAllFile = open(resultsAllPath, "w")
resultsAllFile.write(json.dumps(resultsAll, sort_keys=True))
resultsAllFile.close()

count = {}
result = ""
body = ""
line = "BugId | "
for tool in tools:
	if tool == "Ranking":
		continue
	line += "%s | " % tool
result += "%sTotal\n----- | " % (line)
for tool in tools:
	if tool == "Ranking":
		continue
	result += "%s | " % repeat_to_length("-", len(tool)) 
result += "-----\n"
for project in resultsAll:
	smallName = project[0]
	for bugId in resultsAll[project]:
		line = "[%s%d](#%s-%s)" % (smallName, bugId, project.lower(), bugId)
		line = "%s%s| " % (line, repeat_to_length(" ", 6 - len(line)))
		body += "# %s %s\n\n\n" % (project, bugId)
		lineCount = 0

		if str(bugId) in rankingAll[project]:
			if 'executedTest' in rankingAll[project][str(bugId)]:
				body += "Nb Executed tests: %d\n\n" % rankingAll[project][str(bugId)]['executedTest']
			if 'failedTest' in rankingAll[project][str(bugId)]:
				body += "Nb Failing tests: %d\n\n" % rankingAll[project][str(bugId)]['failedTest']
			if 'failedTestDetails' in rankingAll[project][str(bugId)]:
				for test in rankingAll[project][str(bugId)]['failedTestDetails']:
					body += ">\t%s#%s\n" % (test['class'], test['method'])

		body += "\n## Human Patch \n\n"
		path = os.path.join(conf.defects4jRoot, "framework/projects", project, "patches",  "%d.src.patch" % bugId)
		with open(path) as patchFile:
			content = patchFile.read()
			body += "```Java\n%s\n```\n\n" % (content)
		
		for tool in tools:
			if tool == "Ranking":
				continue
			if(tool in resultsAll[project][bugId]):
				if ('error' in resultsAll[project][bugId][tool]):
					line += "%s%s" % (resultsAll[project][bugId][tool]['error'], repeat_to_length(" ", len(tool) - len(resultsAll[project][bugId][tool]['error'])))
				elif ("patch" in resultsAll[project][bugId][tool] and resultsAll[project][bugId][tool]["patch"]):
					body += "## %s \n\n" % (tool)
					lineKey = "%s:%d" % (resultsAll[project][bugId][tool]['patchLocation']["className"], resultsAll[project][bugId][tool]['patchLocation']["line"])
					if str(bugId) in  rankingAll[project] and 'suspicious' in rankingAll[project][str(bugId)]:
						body += "%s (Suspicious rank: %d)\n" % (lineKey,  rankingAll[project][str(bugId)]['suspicious'][lineKey]['rank'])
					else:
						body += "%s\n" % (lineKey)
					body += "```Java\n%s\n```\n\n" % (resultsAll[project][bugId][tool]["patch"])
					body += "Nb Angelic value: %d\n\n" % resultsAll[project][bugId][tool]['nbAngelicValue']
					body += "Nb analyzed Statement: %d\n\n" % resultsAll[project][bugId][tool]['nbStatement']
					body += "Execution time: %s\n\n" % datetime.timedelta(milliseconds=resultsAll[project][bugId][tool]['executionTime'])
					body += "Grid5000 node: %s\n\n" % resultsAll[project][bugId][tool]['node']
					line += "Yes%s" % repeat_to_length(" ", len(tool) - 3)
					lineCount += 1
					if(not tool in count):
						count[tool] = 1
					else:
						count[tool] += 1
				elif ("operations" in resultsAll[project][bugId][tool] and len(resultsAll[project][bugId][tool]["operations"]) > 0):
					body += "## %s \n\n" % (tool)
					for operation in resultsAll[project][bugId][tool]["operations"]:
						lineKey = "%s:%d" % (operation['patchLocation']["className"], operation['patchLocation']["line"])
						if str(bugId) in  rankingAll[project] and 'suspicious' in rankingAll[project][str(bugId)]:
							body += "%s (Suspicious rank: %d)\n" % (lineKey,  rankingAll[project][str(bugId)]['suspicious'][lineKey]['rank'])
						else:
							body += "%s\n" % (lineKey)
						body += "```Java\n%s\n```\n\n" % (operation["patch"])
					body += "Execution time: %s\n\n" % datetime.timedelta(milliseconds=int(resultsAll[project][bugId][tool]['timeTotal']))
					# body += "Execution time: %sms\n\n" % resultsAll[project][bugId][tool]['timeTotal']
					body += "Grid5000 node : %s\n\n" % resultsAll[project][bugId][tool]['node']
					line += "Yes%s" % repeat_to_length(" ", len(tool) - 3)
					lineCount += 1
					if(not tool in count):
							count[tool] = 1
					else:
							count[tool] += 1
				else:
					line += "No%s" % repeat_to_length(" ", len(tool) - 2)
			else:
				line += "%s" % repeat_to_length(" ", len(tool))
			line += " | "
		result += "%s%d\n" % (line, lineCount)
	line = "Total | "
total = 0
for tool in tools:
	if tool == "Ranking":
		continue
	if(tool in count):
		total += count[tool]
		line += "%d%s" % (count[tool], repeat_to_length(" ", len(tool) - len(str(count[tool]))))
	else:
		line += "0%s" % repeat_to_length(" ", len(tool) - 1)
	line += " | "
result += "%s%d\n" % (line, total)
print "%s\n\n\n%s" % (result,body)

resultsAllFile = open(resultsMdPath, "w")
resultsAllFile.write("%s\n\n\n%s" % (result,body))
resultsAllFile.close()
