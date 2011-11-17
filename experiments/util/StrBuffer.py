import StringIO

class StrBuffer(StringIO.StringIO):
    def __init__(self):
        StringIO.StringIO.__init__(self)
        
    def writeln(self, str):
        self.write(str + '\n')