import re
import os
import json
import datetime
import collections
from core.tools.Nopol import Nopol
from core.Config import conf
from math import sqrt

class Ranking(Nopol):
    """docstring for Ranking"""
    def __init__(self):
        super(Ranking, self).__init__("Ranking")

    def run(self, project, id):
        log = self.runNopol(project, id, mode="ranking")
        slittedLog = log.split('/******** Tests *********/')
        if(len(slittedLog) > 1):
            print slittedLog[1]
            self.parseLog(slittedLog[1], project, id)

    def parseLog(self, log, project, id):
        suspiciousStatements = {}
        rank = 0
        reg = re.compile('([0-9a-zA-Z\-_\.\$]+):([0-9]+) -> ([0-9\.]+) \(ep: ([0-9]+), ef: ([0-9]+), np: ([0-9]+), nf: ([0-9]+)\)')
        m = reg.findall(log)
        for i in m:
            rank += 1
            ep = int(i[3])
            ef = int(i[4])
            np = int(i[5])
            nf = int(i[6])
            suspiciousStatements[i[0]+":"+i[1]] = {
                "class": i[0],
                "line": int(i[1]),
                "ep": ep,
                "ef": ef,
                "np": np,
                "nf": nf,
                "rank": {
                    "ochiai": rank
                },
                "metrics": {
                    "gzoltar": float(i[2]),
                    "ochiai": (ef)/sqrt((ef+ep)*(ef+nf)),
                    "tarantula": (ef/float(ef+nf))/float((ef/float(ef+nf))+(ep/float(ep+np))),
                    "ample": abs((ef/float(ef+nf)) - (ep/float(ep+np)))
                }
            }
        rank = 0
        suspiciousStatementsAmple = collections.OrderedDict(sorted(suspiciousStatements.items(), key=lambda t: t[1]['metrics']['ample'], reverse=True))
        for i in suspiciousStatementsAmple:
            rank += 1
            suspiciousStatementsAmple[i]['rank']['ample'] = rank
        rank = 0
        suspiciousStatementsTarantula = collections.OrderedDict(sorted(suspiciousStatements.items(), key=lambda t: t[1]['metrics']['tarantula'], reverse=True))
        for i in suspiciousStatementsTarantula:
            rank += 1
            suspiciousStatementsTarantula[i]['rank']['tarantula'] = rank
        executedTest = None
        successfulTest = None
        failedTest = None
        failedTestDetails = []
        m = re.search('Executed tests:   ([0-9]+)', log)
        if m:
            executedTest = int(m.group(1))
        m = re.search('Successful tests: ([0-9]+)', log)
        if m:
            successfulTest = int(m.group(1))
        m = re.search('Failed tests:     ([0-9]+)', log)
        if m:
            failedTest = int(m.group(1))
        m = re.search('Executed tests:   ([0-9]+)', log)
        if m:
            executedTest = int(m.group(1))

        reg = re.compile('([0-9a-zA-Z\.\-_\$]+)#([^\n]+)')
        m = reg.findall(log)
        for i in m:
            cl = i[0]
            md = i[1]
            failedTestDetails.append({
                'class': cl,
                'method': md
            })
        results = {
            'executedTest': executedTest,
            'successfulTest': successfulTest,
            'failedTest': failedTest,
            'failedTestDetails': failedTestDetails,
            'suspicious': suspiciousStatements,
            'node': self.getHostname(),
            'date': datetime.datetime.now().isoformat()
        }
        path = os.path.join(project.logPath, str(id), self.name, "results.json")
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        file = open(path, "w")
        file.write(json.dumps(results, indent=4, sort_keys=True))
        file.close()