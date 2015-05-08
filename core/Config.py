from os.path import expanduser

class Config(object):
	"""docstring for Config"""
	def __init__(self):
		self.projectsRoot = expanduser("~/projects")
		self.defects4jRoot = expanduser("~/defects4j")
		self.resultsRoot = expanduser("~/results")
		self.z3Root = expanduser("~/nopol/z3-x64-debian-7.7/bin/")
		self.javaHome = expanduser("/usr/lib/jvm/java-1.7.0-openjdk-amd64/bin/")

conf = Config()
