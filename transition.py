# This program was written by Josh Mermelstein (JoshMermel{at}gmail{dot}com).
# Given two valid siteswaps of the same number of objects, it finds a
# transition between them.
#
# My thanks go out to Anschel Schaffer-Cohen and Professor Sam Guyer for
# advising me on using grammar based parsing.
#
# For information on usage, please consult the included readme.

import sys
from collections import Counter
import ply.lex as lex
import ply.yacc as yacc

from toss import Toss

################################################################################
#                                    lexing                                    #
################################################################################

tokens = (
   'X',
   'LPAREN',
   'COMMA',
   'RPAREN',
   'RBRACE',
   'LBRACE',
   'NUMBER',
   'STAR',
)

t_X       = r'x'
t_LPAREN  = r'\('
t_COMMA   = r'\,'
t_RPAREN  = r'\)'
t_LBRACE  = r'\['
t_RBRACE  = r'\]'
t_STAR  = r'\*'
def t_NUMBER(t):
    r'[0-9a-w]'
    val = ord(t.value);
    if val >= ord('0') and val <= ord('9'):
        t.value = val - ord('0');
    elif val >= ord('a') and val <= ord('z'):
        t.value = val + 10 - ord('a');
    else:
        print 'error'
    return t

# Error handling rule for unrecognized characters
def t_error(t):
    # print "Illegal character '%s'" % t.value[0]
    # Error message removed since p_error is called in this case anyway and
    # users don't need two errors.
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

################################################################################
#                                   parsing                                    #
################################################################################

# Rules for handling complete sequences (what we want from this parser)
def p_sequence_sync(p):
    '''sequence : sync_sequence_star'''
    p[0] = p[1]
def p_sequence_async(p):
    '''sequence : async_sequence'''
    p[0] = p[1]

# Rules for handling presence or lack of * in sync sequences
def p_sync_sequence_no_star(p):
    '''sync_sequence_star : sync_sequence'''
    p[0] = p[1]
def p_sync_sequence_star(p):
    '''sync_sequence_star :  sync_sequence STAR'''
    p[0] = p[1]
    for i in range(0, len(p[1])):
        p[0].append(p[1][i][::-1])

# Rules for handling sync sequences
def p_sync_sequence_base(p):
    '''sync_sequence : sync'''
    p[0] = [p[1]]
def p_sync_sequence_recursive(p):
    '''sync_sequence : sync_sequence sync'''
    p[0] = p[1]
    p[1].append(p[2])

# Rules for handling async sequences
def p_async_sequence_base(p):
    '''async_sequence : multi'''
    p[0] = [p[1]]
def p_async_sequence_recursive(p):
    '''async_sequence : async_sequence multi'''
    p[0] = p[1]
    p[0].append(p[2])

# Rules for handling sync throws
def p_sync(p):
    '''sync : LPAREN multi COMMA multi RPAREN'''
    p[0] = ([p[2],p[4]])

# Rules for handling multiplex throws
def p_multi_singleton(p):
    '''multi : throw'''
    p[0] = [p[1]]
def p_multi_full(p):
    '''multi : multi_begin RBRACE'''
    p[0] = p[1]
def p_multi_begin_base(p):
    '''multi_begin : LBRACE throw'''
    p[0] = [p[2]]
def p_multi_begin_recursive(p):
    '''multi_begin : multi_begin throw'''
    p[0] = p[1]+[p[2]]

# Rules for handling individual throws
def p_throw(p):
    '''throw : NUMBER'''
    p[0] = Toss(p[1], ' ')
def p_Xthrow(p):
    '''throw : NUMBER X'''
    p[0] = Toss(p[1], 'x')

# Error rule for syntax errors
def p_error(p):
    print 'Error during parsing, please try again'

# Build the parser
parser = yacc.yacc()

################################################################################
#                                     math                                     #
################################################################################

def siteswap_type(siteswap):
    if type(siteswap[0][0]).__name__ == 'instance':
        return 'async'
    return 'sync'

### verification ###
def verify(siteswap):
    if siteswap_type(siteswap) == 'sync':
        return sync_verify(siteswap)
    return async_verify(siteswap)

def sync_verify(siteswap):
    # Check that all numbers are even and that 0x doesn't appear
    for i in range (0, len(siteswap)):
        for j in range (0, len(siteswap[i])):
            for k in range (0, len(siteswap[i][j])):
                if siteswap[i][j][k].val % 2 != 0:
                    return False
                if siteswap[i][j][k] == Toss(0,'x'):
                    return False

    # Build the countdown list
    countdown = [[] for x in xrange(2)]
    for i in range (0, len(siteswap)):
        countdown[0].append(0)
        countdown[1].append(0)
    for i in range (0, len(siteswap)):
        for j in range (0, len(siteswap[i][0])):
            val1 = siteswap[i][0][j].location(i, len(siteswap), False)
            if(val1.cross == 'l'):
                countdown[0][val1.val] += 1
            else:
                countdown[1][val1.val] += 1
        for j in range (0, len(siteswap[i][1])):
            val2 = siteswap[i][1][j].location(i, len(siteswap), True)
            if(val2.cross == 'l'):
                countdown[0][val2.val] += 1
            else:
                countdown[1][val2.val] += 1

    # Verify the countdown list is as expected
    for i in range (0, len(countdown[0])):
        if countdown[0][i] != len(siteswap[i][0]):
            return False
        if countdown[1][i] != len(siteswap[i][1]):
            return False
    return True

def async_verify(siteswap):
    # Check no x's appear
    for i in range(0, len(siteswap)):
        for j in range (0, len(siteswap[i])):
            if siteswap[i][j].cross == 'x':
                return False

    # Build the countdown list
    countdown = [];
    for i in range (0, len(siteswap)):
        countdown.append(0);
    for i in range (0, len(siteswap)):
        for j in range (0, len(siteswap[i])):
            countdown[(siteswap[i][j].val+i) % len(siteswap)] += 1;

    # Verify the countdown list is as expected
    for i in range (0, len(countdown)):
        if countdown[i] != len(siteswap[i]):
            return False;
    return True;

### counting number of objects ###
def get_num_balls(siteswap):
    if siteswap_type(siteswap) == 'sync':
        return sync_num_balls(siteswap)
    return async_num_balls(siteswap)

def async_num_balls(siteswap):
    total = 0
    for i in range(0, len(siteswap)):
        for j in range(0, len(siteswap[i])):
            total += siteswap[i][j].val
    return total/len(siteswap)

def sync_num_balls(siteswap):
    total = 0
    for i in range(0, len(siteswap)):
        for j in range(0, len(siteswap[i][0])):
            total += siteswap[i][0][j].val
        for j in range(0, len(siteswap[i][1])):
            total += siteswap[i][1][j].val
    return total/(2*len(siteswap))

### extracting state ###
# These functions are frankly bad but appear to work.  They are at the top of
# my list for when I refactor stuff.
def get_state(siteswap):
    if siteswap_type(siteswap) == 'sync':
        return sync_get_state(siteswap)
    return async_get_state(siteswap)

def async_get_state(siteswap):
    state = Counter();
    num_balls = async_num_balls(siteswap)
    to_place = num_balls
    state_len = 0;
    #sorry for the following loop, I swear it makes sense to me
    while to_place > 0:
        pos = state_len % len(siteswap) # position in the siteswap
        for i in range (0, len(siteswap[pos])):
            state[state_len+siteswap[pos][i].val] += 1
        state[state_len] = len(siteswap[pos]) - state[state_len]
        to_place -= state[state_len]
        state_len += 1
        
    ret = [[],[]]
    for num,multiplicity in state.items():
        if num < state_len:
            for i in range (multiplicity):
                ret[num % 2].append(num)

    return ret

# confusingly, state_len indexes the write position in ret, not the read
# position in siteswap.  I forgot they were the same when first writing this
# and haven't refactored yet
def sync_get_state(siteswap):
    num_balls = sync_num_balls(siteswap)
    state = [Counter(), Counter()]
    to_place = num_balls
    state_len = 0;
    #sorry for the following loop, I swear it makes sense to me
    while to_place > 0:
        pos = (state_len/2) % len(siteswap) # index in the siteswap
        #left half of a (,)
        for i in range (0, len(siteswap[pos][0])):
            side = 1 if siteswap[pos][0][i].cross == 'x' else 0
            state[side][state_len + (siteswap[pos][0][i].val)] += 1
        #right half of a (,)
        for i in range (0, len(siteswap[pos][1])):
            side = 0 if siteswap[pos][1][i].cross == 'x' else 1
            state[side][state_len + (siteswap[pos][1][i].val)] += 1
        state[0][state_len] = len(siteswap[pos][0]) - state[0][state_len]
        to_place -= state[0][state_len]
        state[1][state_len] = len(siteswap[pos][1]) - state[1][state_len]
        to_place -= state[1][state_len]
        state_len += 2

    ret = [[],[]]
    for num,multiplicity in state[0].items():
        if num < state_len:
            for i in range (multiplicity):
                ret[0].append(num)
    for num,multiplicity in state[1].items():
        if num < state_len:
            for i in range (multiplicity):
                ret[1].append(num)

    return ret

# Expects an async siteswap; switches which hand has the starting throw
def flip_state(state):
    return (state[1], state[0])

### detecting conflicts ###

# Returns true if and only if every positive element in state1 appears in
# state2 with at least the multiplicity
# Here, states are lists
def sub_no_conflict(state1, state2):
   counterB = 0
   for i in range (0, len(state1)):
       if state1[i] >= 0:
           try:
               counterB += state2[counterB:].index(state1[i])
           except ValueError:
               return False
   return True

# Checks that there is no conflict in the left or right halves of a state
# Here states are a pair of lists
def no_conflict(state1, state2):
    return sub_no_conflict(state1[0], state2[0]) and sub_no_conflict(state1[1], state2[1])

# horrible temporary solution
def first_throw(state):
    if state[0] == []:
        if state[1] == []:
            return 'left'
        if state[1][0] % 2 == 1:
            return 'left'
    if state[0][0] % 2 == 0:
        return 'left'
    return 'right'


# horrible temporary solution
def last_throw(state):
    if max(state[0]) > max(state[1]):
        return 'left'
    return 'right'

### Converting siteswaps to strings for printing ###
def pretty_str_multi(siteswap):
    if len(siteswap) == 1:
        return str(siteswap[0])
    ret = '['
    for i in siteswap:
        ret += str(i)
    ret += ']'
    return ret

def pretty_str_async(siteswap):
    ret = ''
    for i in siteswap:
        ret += pretty_str_multi(i)
    return ret

def pretty_str_sync(siteswap):
    ret = ''
    for i in siteswap:
        temp = '(' + pretty_str_multi(i[0]) + ',' + pretty_str_multi(i[1]) + ')'
        ret += temp
    return ret

def pretty_str(siteswap):
    if siteswap_type(siteswap) == 'sync':
        return pretty_str_sync(siteswap)
    return pretty_str_async(siteswap)

### Finding transitions ###
def transition_from_sync(A, B):
    # Shift A back in time by the necessary number of throws
    throws_needed = 0
    ret = []
    while not no_conflict(A, B):
        A = (map(lambda x: x-2 , A[0]), map(lambda x: x-2 , A[1]))
        throws_needed += 1
        ret.append([[],[]])
    final_size = throws_needed
    counter_want = 0

    # Build lists of what you have that is unused and what you want to map into
    have = []
    want = []
    cA0 = Counter(A[0])
    cA1 = Counter(A[1])
    # positive count means have that many; negative count means want that many
    cA0.subtract(Counter(B[0]))
    cA1.subtract(Counter(B[1]))
    for val,count in cA0.items():
        for i in range (0, count):
            have.append(Toss(val,'l'))
        for i in range (0, -1 * count):
            want.append(Toss(val,'l'))
    for val,count in cA1.items():
        for i in range (0, count):
            have.append(Toss(val,'r'))
        for i in range (0, -1 * count):
            want.append(Toss(val,'r'))
   
    # Pair elements from have and want and insert them into ret at the appropriate location
    for i in range (0, len(A[0])):
        temp = Toss(A[0][i], 'l')
        if temp in have:
            ret[A[0][i]/2 + throws_needed][0].append(want[counter_want] - temp)
            counter_want += 1
    for i in range (0, len(A[1])):
        temp = Toss(A[1][i], 'r')
        if temp in have:
            ret[A[1][i]/2 + throws_needed][1].append(want[counter_want] - temp)
            counter_want += 1

    # Put zeros in all empty spots
    for i in range (0, len(ret)):
        for j in range (0, len(ret[i])):
            if ret[i][j] == []:
                ret[i][j] = [Toss(0,' ')]

    print pretty_str_sync(ret)

def transition_from_async(A, B):
    # Shift A back in time by the necessary number of throws
    throws_needed = 0
    ret = []
    while not no_conflict(A, B):
        A = (map(lambda x: x-1 , A[0]), map(lambda x: x-1 , A[1]))
        throws_needed += 1
        ret.append([])
    # If the lenght of the transition is more than the length of A, make sure
    # that left/right alignment is OK.
    if first_throw(B) == last_throw(A) and max(max(A[0]), max(A[1])) == -1:
        A = (map(lambda x: x-1 , A[0]), map(lambda x: x-1 , A[1]))
        throws_needed += 1
        ret.append([])
        print 'hi'

    final_size = throws_needed
    counter_want = 0

    # Build lists of what you have that is unused and what you want to map into
    have = []
    want = []
    cA0 = Counter(A[0])
    cA1 = Counter(A[1])
    # positive count means have that many; negative count means want that many
    cA0.subtract(Counter(B[0]))
    cA1.subtract(Counter(B[1]))
    for val,count in cA0.items():
        for i in range (0, count):
            have.append(Toss(val,'l'))
        for i in range (0, -1 * count):
            want.append(Toss(val,'l'))
    for val,count in cA1.items():
        for i in range (0, count):
            have.append(Toss(val,'r'))
        for i in range (0, -1 * count):
            want.append(Toss(val,'r'))

    # Pair elements from have and want and insert them into ret at the appropriate location
    for i in range (0, len(A[0])):
        temp = Toss(A[0][i], 'l')
        if temp in have:
            ret[A[0][i]+throws_needed].append(want[counter_want] - temp)
            counter_want += 1
    for i in range (0, len(A[1])):
        temp = Toss(A[1][i], 'r')
        if temp in have:
            ret[A[1][i]+throws_needed].append(want[counter_want] - temp)
            counter_want += 1

    # Put zeros in all empty spots
    for i in range (0, len(ret)):
        if ret[i] == []:
            ret[i] = [Toss(0,' ')]

    print pretty_str_async(ret)

def get_transition(state1, state2, type1, type2):
    print '\n',
    if type1 == 'async' and type2 == 'async':
        print 'To enter the second pattern on the left side, use'
        transition_from_async(state1,state2)
        print 'To enter the second pattern on the right side, use'
        transition_from_async(state1,flip_state(state2))
    elif type1 == 'async' and type2 == 'sync':
        print 'If your last cycle began on the left side, use'
        transition_from_async(state1, state2)
        print 'If you last cycle began on the right side, use'
        transition_from_async(flip_state(state1), state2)
    elif type1 == 'sync' and type2 == 'async':
        print 'To enter the second pattern on the left side, use'
        transition_from_sync(state1,state2)
        print 'To enter the second pattern on the right side, use'
        transition_from_sync(state1,flip_state(state2))
    else: #sync->sync
        transition_from_sync(state1, state2)

################################################################################
#                                     main                                     #
################################################################################

# Get first siteswap
try:
    input1 = raw_input('please enter the first pattern:\n')
except EOFError:
    sys.exit(1)
siteswap1 = parser.parse(input1)
while siteswap1 == None or not verify(siteswap1):
    message = 'invalid pattern, try again: \n'
    if siteswap1 == None:
        message = ''
    try:
        input1 = raw_input(message)
    except EOFError:
        sys.exit(1)
    siteswap1 = parser.parse(input1)
state1 = get_state(siteswap1)
type1 = siteswap_type(siteswap1)

# Get second siteswap
try:
    input2 = raw_input('please enter the second pattern:\n')
except EOFError:
    sys.exit(1)
siteswap2 = parser.parse(input2)
while siteswap2 == None or \
      not verify(siteswap2) or \
      get_num_balls(siteswap1) != get_num_balls(siteswap2):
    if siteswap2 == None:
       message = ''
    elif not verify(siteswap2):
        message = 'invalid pattern, try again\n'
    else:
        message = 'patterns must have the same number of balls\n'
    try:
        input2 = raw_input(message)
    except EOFError:
        sys.exit(1)
    siteswap2 = parser.parse(input2)
state2 = get_state(siteswap2)
type2 = siteswap_type(siteswap2)

# Print their transitions
get_transition(state1, state2, type1, type2)
