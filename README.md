#Juggle-Transition

A python program for finding transitions between juggling patterns

Given two valid juggling sequences of the same number of balls,
Juggle-Transition finds a transition between them.  If either is async it will
find two transitions, one for starting the pattern on the left and the other
for starting it on the right.  The transitions are suitable to be animated by
jugglinglab.

## Usage

Juggle-Transition can be run with

    python transition.py

To use it, you will need ply, a lex-yacc package for python.  http://www.dabeaz.com/ply/ply.html

On first run it will need to generate parsing tables.  This should take at most a few seconds.

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

## Disorganized thoughts

In general, I find find myself inexplicably driven to shorten functions.  I
have tried my best to make readability a priority in the program but I
appologize if I have made something more difficult to understand in my attempts
to make it more conscise.

## Examples

### Async, Async
    python transition.py 
    Please enter the first pattern:
    4
    Please enter the second pattern:
    741

    To enter the second pattern on the left side, use
    45
    To enter the second pattern on the right side, use
    5


    python transition.py 
    Please enter the first pattern:
    741
    Please enter the second pattern:
    4

    To enter the second pattern on the left side, use
    34
    To enter the second pattern on the right side, use
    3

And in fact, (4^4)5(741^2)3 is valid (http://jugglinglab.sourceforge.net/siteswap.php?(4^4)5(741^2)3), as are the other three combinations

### Sync, Sync

    python transition.py 
    Please enter the first pattern:
    (4,4)
    Please enter the second pattern:
    (6x,2x)*

    (6,4)

    python transition.py 
    Please enter the first pattern:
    (6x,2x)*
    Please enter the second pattern:
    (4,4)

    (2,4)

And in fact ((4,4)^4)(6,4)((6x,2x)(2x,6x)^3)(2,4) is valid (http://jugglinglab.sourceforge.net/siteswap.php?((4,4)^4)(6,4)((6x,2x)(2x,6x)^3)(2,4))

### Async, Sync

    python transition.py 
    Please enter the first pattern:
    5
    Please enter the second pattern:
    (6x,4)*

    If your last cycle began on the left side, use
    83x43x
    If you last cycle began on the right side, use
    8x3x43x


    python transition.py 
    Please enter the first pattern:
    (6x,4)*
    Please enter the second pattern:
    5

    To enter the second pattern on the left side, use
    (8,5x)(4,5x)
    To enter the second pattern on the right side, use
    (7x,a)(7x,6)(2x,0)



##Data Structures

### Tosses
 - A toss contains an int and a char
 - We abuse them when finding transitions but this part of the documentation doesn't concern that
 - When the char is a space, it represents a throw whose height is the integer.
 - When the char is an 'x', it represents a throw whose height is the integer followed by an 'x'
 - for example
    - a 6x is represented by Toss(6, 'x')
    - A 4 is represented by a Toss(4, ' ')

### Siteswaps
 - To get a siteswap, call the parse() function on the string representation of a siteswap
 - A siteswap can take two types, sync and async
 - An async siteswap is a Toss list list.
    - Each internal toss list represents a multiplex throw
    - A non-multiplex throw is just a singleton list
    - for example:
        A 531 is represented by [[Toss(5, ' ')], [Toss(3, ' ')], [Toss(1, ' ')]]
        A 23[34] is represented by [[Toss(2, ' ')],[Toss(3, ' ')],[Toss(3, ' '), Toss(4, ' ')]]
 - A sync siteswap is a Toss list list list.
    - Each internal Toss list list represents a pair of throws and is required to be of length 2
    - Each Toss list within that has the same properties as an async siteswap
    - for example:
        - (6x,4)(4,6x) is represnted by [[[Toss(6 'x')], [Toss(4, ' ')]], [[Toss(4, ' ')], [Toss(6, 'x')]]]
        - ([44],[44])(0,4) is represented by [[[Toss(4, ' '), Toss(4, ' ')], [Toss(4, ' '), Toss(4, ' ')]], [[Toss(0, ' ')], [Toss(4, ' ')]]]

### States
 - A state is what results when you call get_state() on a siteswap.
 - A state is an int list list where the outer list is required to be of length 2
 - It represents the drop state of a siteswap
 - The first internal int list represents the beats on which balls will fall on the left and the second internal int list represents the beats on which a ball will fall on the right
    - The multiplicity with which a number repeats represents how many balls will fall on that beat
 - for example:
    - The state of a 3 ball ground state trick such as 3 or 531 is [[0, 2], [1]]
    - The state of 741 is [[0,2,4],[1]]
    - The state of 23[34] is [[0,2],[1,3]] \(4 ball ground state\)
    - The state of 3[34]2 is [[0,2],[1,1]]
    - The state of (4,4) is [[0,2],[0,2]]
    - The state of (6x,2x)(2x,6x) is [[0,4],[0,2]]
 - Async siteswaps have state with all even numbers on one side and all odd number on the other
 - Sync siteswaps have state with all even numbers on both sides

## To Do
 - improve siteswap_type()?
 - improve first_throw()?
 - consider shortening sync_verify() by consolidating similar code into a loop
    - pros: more concise, structure better matches async_verify
    - cons: possibly less readable
    - same question about sync_get_state()
 - have more helpful print messages
 - detect and intercept output where jugglinglab will derp
        
Longer term possible features:
 - find equivalent transitions to existing ones?
 - make transition length a user selectable parameter?



