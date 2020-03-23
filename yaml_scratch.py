import sys
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

def strip_python_tags(s):
    result = []
    for line in s.splitlines():
        idx = line.find("!")
        if idx > -1:
            line = line[:idx]
        result.append(line)
    return '\n'.join(result)

class Kid(object):
    def __init__(self, name):
        self.name = name

class Person(object):
    population = 0
    def __init__(self, first, last):
        self.first = first        
        self.last = last
        self.kids = []
        self.kids['foo'] = Kid("Henry")
        # self.kids.append(Kid("Alice"))
        # self.kids.append(Kid("Sally"))
        self.population += 1

a = Person('first', 'last')

yaml = YAML()
yaml.encoding = None
yaml.typ = "safe"
yaml.register_class(Person)
yaml.register_class(Kid)
yaml.dump(a, sys.stdout, transform=strip_python_tags)
