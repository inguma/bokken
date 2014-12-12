import re

def valid_text(start, end, doc):
    if not start or not end:
        return False
    if start.get_line_offset() > end.get_line_offset():
        (start, end) = (end, start) # swap
    text = doc.get_text(start, end, False)
    for char in text:
        if not re.match("\w", char):
            return False
    return True

def increment(index, incr):
    newindex = index.copy()
    newindex.set_line_offset(index.get_line_offset() + incr)
    return newindex

def find_word_bound(index, step, doc):
    condition = lambda x: not index.get_line_offset() == 0 if step < 0 else lambda x: not x.ends_line()
    while condition(index):
        newindex = increment(index, step)
        # newindex contains word?
        if not valid_text(newindex, index, doc):
            break
        # save new index
        index = newindex
    return index
