This code can be used if the location of the code injected into the process 
can be guessed to a certain extend. Assume the guessed address is "A" and the
maximum expected deviation from this address is "D". A nopslide with length
(D * 2) is sufficient to make sure that the nopslide will always cover the 
address A + D. This nopslide will start at an address in the range 
[A - D, A + D]. If the exploit returns to address A + D, the execution will 
start at offset "O" in the nopslide as shown in the following three examples:

Nopslide start| Address space ->                                 |   Execution
  address:    | A - D      A     A + D                           | start offset:
--------------+---|--------|-------|-----------------------------+--------------
B = (A - D)   |   [nopslidexxxxxxxx][code_____                   |  O = D * 2
B = (A +/- ?) |   |      [nopslidexxxxxxxx][code_____            |  O = ?
B = (A + D)   |   |        |       [nopslidexxxxxxxxx][code_____ |  O = 0
--------------'---'--------'-------'-----------------------------'--------------

In this example, if the exploit jumps to the hardcoded address (A + D), it will
always land in the nopslide. The base address "B" of the nopslide plus the 
offset "O" in the nopslide where execution starts are equal to the return 
address:
                            (B + O)  ==  (A + D)
Because A and D are known values, if O can be calculated then this can be used
to calucalte the base address "B" of the code.

The code that is executed immediately after the nopslide starts at address
(A + D) + (D * 2) - O, which is in the range [A + D, A + D * 3]. If this code is
also at least (D * 2) bytes long, it can write to the address A + D * 3 and 
always overwrite part of itself. Exactly which part of the code is overwritten
depends on the value of O. This means that O can determine what our code does,
which we can use to calculate the value of O.

In order to do so, a small piece of code (called the "patcher") of length "P" is
created after the nopslide followed by a second nopslide of length (D * 2) 
called the "count slide". This "patcher" overwrites a byte in the countslide at
address A + D * 3 + P, which is always inside the countslide, here's an example:

Address:      B               (B + D * 2)   (B + D * 2 + P)    (B + D * 4 + P)
              |                      |         |                      |
Code:         [nopslidexxxxxxxxxxxxx][patcher_][countslidexxxxxxxxxxx][code___
                    |                                 |
Address:    (A + D) = (B + O)         (A + D * 3 + P) = (B + D * 2 + P + O)
           (Start of execution)      (Address where countslide is "patched")

The count slide will consist entirely of one byte "INC ECX" instructions.
The patcher will overwrite one byte at the hardcoded address (A + D * 3 + P)
with a one byte "POP ECX" instruction. It then puts the hardcoded value 
(A + D * 3 + P + 1) on the stack after which the countslide is executed.

So, after the exploit makes code jump to the nopslide, the nopslide executes 
until it reaches the patcher. The patcher then modifies the countslide and saves
a value on the stack, after which the countslide is executed. The countslide 
increments ECX, which does nothing of importance, until it runs into the patched
"POP ECX", which pops the value saved by the patcher (A + D * 3 + P + 1) off the
stack into ECX. It then continues to increment ECX for every instruction 
executed. The number of "INC ECX" instructions it executes depends on "D" and 
"O" as follows:
           (B + D * 3 + P) - (B + D * 2 + P + O)  ==  D - O
So, taking into account the value to which ECX is set by the "POP ECX", after 
the countslide has completely been executed, the value in ECX will be:
           (A + D * 3 + P + 1) + (D * 2 - O) = A + D * 5 + P + 1 - O
And because (B + O)  ==  (A + D), this means the value in ECX is:
           (B + O) + D * 4 + P + 1 - O = B + D * 4 + P + 1
So, ECX now points to the address of the code that follows immediately after the
countslide, which means ECX == EIP.

