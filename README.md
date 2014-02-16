Juggle-Transition
=================

A python program for finding transitions between juggling patterns

Given two valid juggling sequences of the same number of balls,
Juggle-Transition finds a transition between them.  If either is async it will
find two transitions, one for starting the pattern on the left and the other
for starting it on the right.  The transitions are suitable to be animated by
jugglinglab.

To use it, you will need ply, a lex-yacc package for python.  http://www.dabeaz.com/ply/ply.html

Juggle-Transition supports the following siteswap features:
 - async sequences
 - sync sequences (including *)
 - multiplexing in either sequence

  
Juggle-Transition does not support the following jugglinglab features:
 - L and R to determine which hand starts and async siteswap
 - ! after a sync throw to remove the half pause beat
 - (p^n) to repeat a subsequence several times (that wouldn't even make sense here...)
 - Sequences with a mix of sync and async throws.
    - Note that Juggle-Transition will happily transition you between a sync
      pattern and an async pattern.  However it will not accept a pattern that
      includes both types of throws.

In general, I find find myself inexplicably driven to shorten functions.  I
have tried my best to make readability a priority in the program but I
appologize if I have made something more difficult to understand in my attempts
to make it more conscise.

To Do list for Juggle-Transition:
 - doccument data structures
 - have more helpful print messages
 - detect and intercept output where jugglinglab will derp
 - Modularize the input
   - take input and calls itself until a passed in list of boolean functions are all passed?
   - is ths possible in python?
 - transition_from_* using 'l' and 'r' is bad.  
    - Why did I even do that?
        
Longer term possible features:
 - find equivalent transitions to existing ones?
 - make transition length a user selectable parameter?



