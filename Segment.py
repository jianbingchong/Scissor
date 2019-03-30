class Segment:
    def __init__(self, start, end, name=None):
        self.start = start
        self.end = end
        self.name = name

    @staticmethod
    def load_dict(d):
        if d == None:
            return None
        d = NoExcepionDict(d)
        s = Segment(d['start'], d['end'], d['name'])
        return s

    def to_dict(self):
        return copy.deepcopy(self.__dict__)

    def __repr__(self):
        return "Segment{}".format(self.__dict__)


class NoExcepionDict:
    def __init__(self, dictionary):
        if isinstance(dictionary, NoExcepionDict):
            self.dictionary = dictionary.dictionary
        else:
            self.dictionary = dictionary

    def __getitem__(self, key):
        d = self.dictionary
        return d[key] if key in d else None