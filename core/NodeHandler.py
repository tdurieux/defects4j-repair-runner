import os
import time
import subprocess

class NodeHandler(object):
	"""docstring for NodeHandler"""
	def __init__(self, tasks):
		self.maxNode = 50
		self.tasks = tasks
		self.running = 0

	def run(self):
		while(len(self.tasks) > 0):
			self.getRunning()
			print len(self.tasks), self.running >= self.maxNode
			if self.running < self.maxNode:
				task = self.tasks.pop()
				filename = task.project.name.lower() + '_' + str(task.id)
				stdoutlog =  os.path.join(task.project.logPath, str(task.id), task.tool.name, 'stdout.log')
				stderrlog =  os.path.join(task.project.logPath, str(task.id), task.tool.name, 'stderr.log')

				if not os.path.exists(os.path.dirname(stdoutlog)):
					os.makedirs(os.path.dirname(stdoutlog))

				if not os.path.exists(os.path.dirname(stderrlog)):
					os.makedirs(os.path.dirname(stderrlog))

				cmd = 'rm ' + stdoutlog + ';'
				cmd += 'rm ' + stderrlog + ';'
				path = os.path.join('python ' + os.path.dirname(__file__),'../defect4j-node.py') + ' -p ' + task.project.name + ' -t ' + task.tool.name + ' -i ' + str(task.id)

				# cmd += path
				cmd += 'oarsub -l nodes=1,walltime=' + task.project.maxExecution +' -O ' + stdoutlog + ' -E ' + stderrlog + ' "' + path + '"'
				print cmd
				subprocess.call(cmd, shell=True)
				self.running += 1
			else:
				time.sleep( 5 )
				self.getRunning()
		while(True):
			self.getRunning()
			print str(self.running) + " tasks run"
			if self.running > 0:
				time.sleep( 5 )
			else:
				break

	def getRunning(self):
		cmd = 'oarstat -u | grep `whoami` | wc -l'
		output = subprocess.check_output(cmd,shell=True)
		self.running = int(output)
