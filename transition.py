# This program was written by Josh Mermelstein (JoshMermel{at}gmail{dot}com).
# Given two valid siteswaps of the same number of objects, it finds a
# transition between them.
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
    val = ord(t.value)
    if val >= ord('0') and val <= ord('9'):
        t.value = val - ord('0')
    elif val >= ord('a') and val <= ord('z'):
        t.value = val + 10 - ord('a')
    else:
        print 'error'
    return t

# Error handling rule for unrecognized characters
def t_error(t):
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
    for i in range(len(p[1])):
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
    print 'Error during parsing, please try again:',

# Build the parser
parser = yacc.yacc()

################################################################################
#                                     math                                     #
################################################################################

# todo: find a better way to do this?
def siteswap_type(siteswap):
    if type(siteswap[0][0]).__name__ == 'instance':
        return 'async'
    return 'sync'

### verification ###
# Expects siteswap to be a well formed siteswap
# Returns True if the siteswap is valid
def verify(siteswap):
    if siteswap_type(siteswap) == 'sync':
        return sync_verify(siteswap)
    return async_verify(siteswap)

# Expects siteswap to be a well formed async siteswap
# Returns True if the siteswap is valid
def async_verify(siteswap):
    # Check no x's appear
    for i in range(len(siteswap)):
        for j in range(len(siteswap[i])):
            if siteswap[i][j].cross == 'x':
                return False

    # Build the countdown list
    countdown = Counter()
    for i in range(len(siteswap)):
        for j in range(len(siteswap[i])):
            countdown[(siteswap[i][j].val+i) % len(siteswap)] += 1

    # Verify the countdown list is as expected
    for height, multiplicity in countdown.items():
        if multiplicity != len(siteswap[height]):
            return False
    return True

# Expects siteswap to be a well formed sync siteswap
# Returns True if the siteswap is valid
def sync_verify(siteswap):
    # Check that all numbers are even and that 0x doesn't appear
    for i in range(len(siteswap)):
        for j in range(len(siteswap[i])):
            for k in range(len(siteswap[i][j])):
                if siteswap[i][j][k].val % 2 != 0:
                    return False
                if siteswap[i][j][k] == Toss(0,'x'):
                    return False

    # Build the countdown list
    countdown = [Counter(), Counter()]
    for i in range(len(siteswap)):
        # all left hand throws
        for j in range(len(siteswap[i][0])):
            desitnation = siteswap[i][0][j].location(i, len(siteswap), False)
            side = 0 if desitnation.cross == 'l' else 1
            countdown[side][desitnation.val] += 1
        # all right hand throws
        for j in range(len(siteswap[i][1])):
            desitnation = siteswap[i][1][j].location(i, len(siteswap), True)
            side = 0 if desitnation.cross == 'l' else 1
            countdown[side][desitnation.val] += 1

    # Verify the countdown list is as expected
    # left side
    for height, multiplicity in countdown[0].items():
        if multiplicity != len(siteswap[height][0]):
            return False
    # right side
    for height, multiplicity in countdown[1].items():
        if multiplicity != len(siteswap[height][1]):
            return False
    return True

### counting number of objects ###
# Expects siteswap to be a valid siteswap
def get_num_balls(siteswap):
    if siteswap_type(siteswap) == 'sync':
        return sync_num_balls(siteswap)
    return async_num_balls(siteswap)

# Expects siteswap to be a valid async siteswap
def async_num_balls(siteswap):
    total = 0
    for i in range(len(siteswap)):
        for j in range(len(siteswap[i])):
            total += siteswap[i][j].val
    return total/len(siteswap)

# Expects siteswap to be a valid sync siteswap
def sync_num_balls(siteswap):
    total = 0
    for i in range(len(siteswap)):
        for j in range(len(siteswap[i][0])):
            total += siteswap[i][0][j].val
        for j in range(len(siteswap[i][1])):
            total += siteswap[i][1][j].val
    return total/(2*len(siteswap))

### extracting state ###
def get_state(siteswap):
    if siteswap_type(siteswap) == 'sync':
        return sync_get_state(siteswap)
    return async_get_state(siteswap)

# Expects siteswap to be a valid async siteswap
# write_pos is the index we are handling in a given loop
# stuff before write_pos is all correct, stuff after is still being modified
def async_get_state(siteswap):
    state = Counter()
    to_place = async_num_balls(siteswap)
    write_pos = 0
    #sorry for the following loop, I swear it makes sense to me
    while to_place > 0:
        pos = write_pos % len(siteswap) # position in the siteswap
        for i in range(len(siteswap[pos])):
            state[write_pos+siteswap[pos][i].val] += 1
        state[write_pos] = len(siteswap[pos]) - state[write_pos]
        to_place -= state[write_pos]
        write_pos += 1

    ret = [[],[]]
    for num,multiplicity in state.items():
        if num < write_pos:
            for i in range(multiplicity):
                ret[num % 2].append(num)

    return ret

# Expects siteswap to be a valid sync siteswap
# write_pos indexes the front write position in ret
# write_pos/2 % len(siteswap) indexes the read position is siteswap.  The /2 is
# necessary because of the unwritten null beat after a sync throw.
def sync_get_state(siteswap):
    to_place = sync_num_balls(siteswap)
    state = [Counter(), Counter()]
    write_pos = 0
    #sorry for the following loop, I swear it makes sense to me
    while to_place > 0:
        pos = (write_pos/2) % len(siteswap) # read index in the siteswap
        #left half of a (,)
        for i in range(len(siteswap[pos][0])):
            side = 1 if siteswap[pos][0][i].cross == 'x' else 0
            state[side][write_pos + (siteswap[pos][0][i].val)] += 1
        #right half of a (,)
        for i in range(len(siteswap[pos][1])):
            side = 0 if siteswap[pos][1][i].cross == 'x' else 1
            state[side][write_pos + (siteswap[pos][1][i].val)] += 1
        state[0][write_pos] = len(siteswap[pos][0]) - state[0][write_pos]
        to_place -= state[0][write_pos]
        state[1][write_pos] = len(siteswap[pos][1]) - state[1][write_pos]
        to_place -= state[1][write_pos]
        write_pos += 2

    ret = [[],[]]
    for num,multiplicity in state[0].items():
        if num < write_pos:
            for i in range(multiplicity):
                ret[0].append(num)
    for num,multiplicity in state[1].items():
        if num < write_pos:
            for i in range(multiplicity):
                ret[1].append(num)

    return ret

# Expects an async siteswap
# switches which hand has the starting throw
def flip_state(state):
    return (state[1], state[0])

### detecting conflicts ###
# Returns true if and only if every positive element in state1 appears in
# state2 with at least the multiplicity
# Here, states are lists
def sub_no_conflict(state1, state2):
   check_from = 0
   for i in range(len(state1)):
       if state1[i] >= 0:
            try:
                # increment check_from so it starts looking after the most
                # recently found value
                check_from += state2[check_from:].index(state1[i])+1
            except ValueError:
                return False
    return True

# Checks that there is no conflict in the left or right halves of a state
# Here states are a pair of lists
def no_conflict(state1, state2):
    return (sub_no_conflict(state1[0], state2[0]) and 
            sub_no_conflict(state1[1], state2[1]))


# Determines which hand of an async drop state has the first throw
def first_throw(state):
    if state[0] == []:
        if state[1] == []:
            return 'left'
        if state[1][0] % 2 == 1:
            return 'left'
    if state[0][0] % 2 == 0:
        return 'left'
    return 'right'

# Determines which hand of an async drop state has the last throw
def last_throw(state):
    if max(state[0]) > max(state[1]):
        return 'left'
    return 'right'

### Building strings out of siteswaps for printing ###
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
# Expects A to be the drop state of a sync siteswap
# Expects B to a valid drop state
def transition_from_sync(A, B):
    # Shift A back in time by the necessary number of throws
    throws_needed = 0
    ret = []
    while not no_conflict(A, B):
        A = (map(lambda x: x-2 , A[0]), map(lambda x: x-2 , A[1]))
        throws_needed += 1
        ret.append([[],[]])
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
        for i in range(count):
            have.append(Toss(val,'l'))
        for i in range(-1 * count):
            want.append(Toss(val,'l'))
    for val,count in cA1.items():
        for i in range(count):
            have.append(Toss(val,'r'))
        for i in range(-1 * count):
            want.append(Toss(val,'r'))

    # Pair elements from have and want and insert them into ret at the
    # appropriate location
    for i in range(len(A[0])):
        temp = Toss(A[0][i], 'l')
        if temp in have:
            ret[A[0][i]/2 + throws_needed][0].append(want[counter_want] - temp)
            counter_want += 1
    for i in range(len(A[1])):
        temp = Toss(A[1][i], 'r')
        if temp in have:
            ret[A[1][i]/2 + throws_needed][1].append(want[counter_want] - temp)
            counter_want += 1

    # Put zeros in all empty spots
    for i in range(len(ret)):
        for j in range(len(ret[i])):
            if ret[i][j] == []:
                ret[i][j] = [Toss(0,' ')]

    print pretty_str_sync(ret)

# Expects A to be the drop state of an async siteswap and B to be a drop state.
# is_B_sync is a boolean that is true if B is sync.
def transition_from_async(A, B, is_B_sync):
    # Shift A back in time by the necessary number of throws
    throws_needed = 0
    ret = []
    while not no_conflict(A, B):
        A = (map(lambda x: x-1 , A[0]), map(lambda x: x-1 , A[1]))
        throws_needed += 1
        ret.append([])
    # If the lenght of the transition is more than the length of A, make sure
    # that left/right alignment is OK.

    if first_throw(B) == last_throw(A) and all(x < 0 for x in A[0]+A[1]) and not is_B_sync:
        A = (map(lambda x: x-1 , A[0]), map(lambda x: x-1 , A[1]))
        throws_needed += 1
        ret.append([])       
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
        for i in range(count):
            have.append(Toss(val,'l'))
        for i in range(-1 * count):
            want.append(Toss(val,'l'))
    for val,count in cA1.items():
        for i in range(count):
            have.append(Toss(val,'r'))
        for i in range(-1 * count):
            want.append(Toss(val,'r'))

    # Pair elements from have and want and insert them into ret at the
    # appropriate location
    for i in range(len(A[0])):
        temp = Toss(A[0][i], 'l')
        if temp in have:
            ret[A[0][i]+throws_needed].append(want[counter_want] - temp)
            counter_want += 1
    for i in range(len(A[1])):
        temp = Toss(A[1][i], 'r')
        if temp in have:
            ret[A[1][i]+throws_needed].append(want[counter_want] - temp)
            counter_want += 1

    # Put zeros in all empty spots
    for i in range(len(ret)):
        if ret[i] == []:
            ret[i] = [Toss(0,' ')]

    print pretty_str_async(ret)

# Expects state1 and state 2 to be valid drop states
# Expects type1 and type2 to be the types associtated with state1 and state2
def get_transition(state1, state2, type1, type2):
    print '\n',
    if type1 == 'async' and type2 == 'async':
        print 'To enter the second pattern on the left side, use'
        transition_from_async(state1,state2, False)
        print 'To enter the second pattern on the right side, use'
        transition_from_async(state1,flip_state(state2), False)
    elif type1 == 'async' and type2 == 'sync':
        print 'If your last cycle began on the left side, use'
        transition_from_async(state1, state2, True)
        print 'If you last cycle began on the right side, use'
        transition_from_async(flip_state(state1), state2, True)
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

def not_none(i):
    return i != None

def same_num_balls(input1):
    return lambda x : get_num_balls(x) == get_num_balls(input1)

# Takes a message to print, a list of functions to test input against, and a
# parallel list of messages to print for each test if it is failed.  Returns a
# siteswap
def get_input(message, testlist, errorlist):
    try:
        user_input = raw_input(message)
    except EOFError:
        sys.exit(1)
    siteswap = parser.parse(user_input)
    for i in range(len(testlist)):
        if not testlist[i](siteswap):
            print errorlist[i]
            return get_input('', testlist, errorlist)
    return siteswap

testlist = [not_none, verify]
errorlist = ['','Invalid pattern, please try again:']

# get the first pattern
siteswap1 = get_input('Please enter the first pattern:\n',testlist, errorlist)
state1 = get_state(siteswap1)
type1 = siteswap_type(siteswap1)

#get the second pattern
testlist.append(same_num_balls(siteswap1))
errorlist.append('Patterns must have the same number of balls:')
siteswap2 = get_input('Please enter the second pattern:\n',testlist, errorlist)
state2 = get_state(siteswap2)
type2 = siteswap_type(siteswap2)

# Print their transitions
get_transition(state1, state2, type1, type2)
