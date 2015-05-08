import os

from core.projects.LangProject import LangProject
from core.projects.MathProject import MathProject
from core.projects.ChartProject import ChartProject
from core.projects.TimeProject import TimeProject

from core.tools.Ranking import Ranking
from core.tools.NopolPC import NopolPC
from core.tools.NopolC import NopolC
from core.tools.Astor import Astor
from core.tools.Kali import Kali


root = os.path.join("results") 

for project in os.listdir(root):
	projectCl = MathProject()
	if project.lower() == "chart":
		projectCl = (ChartProject())
	elif project.lower() == "lang":
		projectCl = (LangProject())
	elif project.lower() == "math":
		projectCl = (MathProject())
	elif project.lower() == "time":
		projectCl = (TimeProject())
	else:
		continue
	projectPath = os.path.join(root, project) 
	if os.path.isfile(projectPath):
		continue
	for bugId in os.listdir(projectPath):
		bugPath = os.path.join(projectPath, bugId) 
		if os.path.isfile(bugPath):
			continue
		for tool in os.listdir(bugPath):
			toolPath = os.path.join(bugPath, tool)
			if os.path.isfile(toolPath):
				continue
			toolCl = NopolPC()
			if tool.lower() == "nopolpc":
				toolCl =  (NopolPC())
			elif tool.lower() == "ranking":
				toolCl =  (Ranking())    
			elif tool.lower() == "nopolc":
				toolCl =  (NopolC())
			elif tool.lower() == "genprog":
				toolCl =  (Astor())
			elif tool.lower() == "kali":
				toolCl =  (Kali())
			else: 
				continue
			logToolPath = os.path.join(toolPath, "stdout.log")
			if os.path.exists(logToolPath):
				with open(logToolPath) as data_file:
					log = data_file.read()
					toolCl.parseLog(log, projectCl, int(bugId))