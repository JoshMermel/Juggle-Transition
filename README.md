Juggle-Transition
=================

A python program for finding transitions between juggling patterns

Juggle-Transition supports the following siteswap features:
 - async sequences
 - sync sequences (including *)
 - multiplexing in either sequence

  
Juggle-Transition does not support the following jugglinglab features:
 - L and R to determine which hand starts and async siteswap
 - ! after a sync throw to remove the half pause beat
 - (p^n) to repeat a subsequence several times (that wouldn't even make sense here...)
 - Sequences with a mix of sync and async throws.
  
Note that Juggle-Transition will happily transition you between a sync pattern and an async pattern.  However it will not accept a pattern that includes both types of throws.

To Do list for Juggle-Transition:
 - Make better function for detecting the type of a siteswap
 - refactor the verification functions, especially sync_verify
   - replace countdown lists with countdown counters?
 - refactor get_state functions using counters instead of lists to hold intermediate values?
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



