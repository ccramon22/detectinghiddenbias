# pipeline.py
# PART 2

class Pipeline:
    def __init__(self):
        self.steps = []

    def add_step(self, func):  # add_step(func)
        if not callable(func):
            raise TypeError("step must be callable.")
        self.steps.append(func)
        return self

    def run(self, data):
        islist = isinstance(data, list)
        stream = iter(data) if islist else data
        for step in self.steps:
            stream = step(stream)
        return list(stream) if islist else stream

    def filelines(self, path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                yield line

# PART 3
#these are the defined transformations 
# 1) to lowercase
def to_lowercase(iterable):
    for s in iterable:
        yield s.lower().strip()

def remove_stopwords(stopwords):
    stop = set(stopwords)
    def step(iterable):
        for s in iterable:
            tokens = s.split() if isinstance(s, str) else s
            yield [t for t in tokens if t not in stop]
    return step

# 2) vectorize
class Vectorize:
    def __init__(self):
        self.vocab = {}
        self.next_id = 1
    def __call__(self, iterable):
        for item in iterable:
            tokens = item.split() if isinstance(item, str) else item
            ids = []
            for t in tokens:
                if t not in self.vocab:
                    self.vocab[t] = self.next_id
                    self.next_id += 1
                ids.append(self.vocab[t])
            yield ids

class punctuation_removal: #custom 
    def __init__(self):
        self.punct = set('.,!?;:"\'()[]{}<>/-_@#$%^&*~`|\\')

    def __call__(self, iterable):
        for s in iterable:
            text = " ".join(s) if isinstance(s, list) else s
            out = []
            for ch in text:
                out.append(" " if ch in self.punct else ch)
            yield "".join(out)

# PART 4
def pair_with_count(iterable):
    for tokens in iterable:
        toks = tokens.split() if isinstance(tokens, str) else tokens
        yield (toks, len(toks))

class SelectBranch:
    def __init__(self, index):
        self.index = index
    def __call__(self, iterable):
        for item in iterable:
            yield item[self.index]

from functools import reduce
class WordCountReducer:
    def __call__(self, iterable):
        all_tokens = (t for tokens in iterable for t in tokens)
        def reducer(acc, token):
            acc[token] = acc.get(token, 0) + 1
            return acc
        total = reduce(reducer, all_tokens, {})
        yield total