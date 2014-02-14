Juggle-Transition
=================

A python program for finding transitions between juggling patterns

This software has been tested but not extensively.  I belive that it works in all cases but don't have proof of that.

update: there is at least one bug:
When asked to transition between 3 and 00555, the program says:

To enter the second pattern on the left side, use 5x5x5x
To enter the second pattern on the right side, use 663

The second is correct.  The first is incorrect in an interesting way.


Given two valid juggling sequences of the same number of balls, Juggle-Transition finds a transition between them.  If either is async it will find two transitions, one for starting the pattern on the left and the other for starting it on the right.  The transitions are suitable to be animated by jugglinglab.

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
    - Note that Juggle-Transition will happily transition you between a sync pattern and an async pattern.  However it will not accept a pattern that includes both types of throws.

To Do list for Juggle-Transition:
 - Make better function for detecting the type of a siteswap
 - refactor the verification functions, especially sync_verify
   - replace countdown lists with countdown counters?
 - Modularize the input
   - take input and calls itself until a passed in list of boolean functions are all passed?
   - is ths possible in python?
 - Improve the search function
   - Binary search instead?
   - http://stackoverflow.com/questions/364621/python-get-position-in-list ?
 - transition_from_* using 'l' and 'r' is bad.  
    - Why did I even do that?
        
Longer term possible features:
 - find equivelant transitions to existing ones?
 - make transition length a user selectable parameter?



