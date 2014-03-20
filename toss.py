#val is the height of the throw, cross is a char
class Toss: 
    cross = ''
    def __init__(self, _val, _cross):
        self.val = _val
        self.cross = _cross
    #find the drop location of a toss at a given offset
    def location(self, offset, length, right):
        retval = ((self.val/2)+offset) % length
        if right and self.cross == 'x':
            return Toss(retval, 'l')
        elif right:
            return Toss(retval, 'r')
        elif not right and self.cross == 'x':
            return Toss(retval, 'r')
        else:
            return Toss(retval, 'l')
    def __repr__(self):
        if self.val >= 0 and self.val <= 9:
            num = chr(self.val + ord('0'))
        else:
            num = chr(self.val - 10 + ord('a'))
        if self.cross == ' ':
            return "%s" % (num)
        else:
            return "%s%s" % (num, self.cross)
    # this is meant to be used when finding transitions
    # Tosses are expected to have a 'l' or 'r' as their cross
    def __sub__(self, other):
        val = self.val-other.val
        cross = 0 if self.cross == other.cross else 1

        return Toss(val, ' ' if cross == val % 2 else 'x')
    def __eq__(self, other):
        return self.cross == other.cross and self.val == other.val
