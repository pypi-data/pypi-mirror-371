#!/usr/bin/python

'''
LIBrary for YARE (Yet Another Regular Expression) pattern matching


CONTENTS

    • 0. Installation
    • 1. Usage
    • 2. Simple Patterns
    • 3. Charset Patterns
    • 4. Compound Patterns
    • 5. History

0. INSTALLATION

If for instance your Linux belongs to the Debian family, type:

    $ sudo apt install pipx

Then type:

    $ pipx install libyare
    $ pipx ensurepath

Now you can get this help by typing:

    $ libyare -h

...and you can check the libyare version by typing:

    $ libyare -V

1. USAGE

LIBYARE  implements  YARE  (Yet Another Regular Expression). YARE is a
regular  expression format aimed to be more readable (even at the cost
of  being  less  powerful)  than  standard regular expressions. It can
accept  simple  patterns  (standard  Unix shell patterns) and compound
patterns  (obtained  by  combining together simple patterns by logical
operators and parenthesis).

In  order  to  use  libyare  in  your  PyPI  project,  link it in your
pyproject.toml file:

    ...
    [project]
    ...
    dependencies = ["libyare", ...]
    ...

Then in your program you can write:

    ...
    from libyare import *
    ...
    if yarecsmatch(string, pattern): # case-sensitive match
        ...
    if yarecimatch(string, pattern): # case-insensitive match
        ...
    if yarecmmatch(string, pattern): # case-multiple match
        ...
    if yareosmatch(string, pattern): # system-depending match
        ...

A YARE pattern can be:

    • a simple pattern:
        • '*' matches everything
        • '?' matches any single character
        • '[seq]' matches any single character in seq
        • '[!seq]' matches any single character not in seq
    • a charset pattern:
        • made by a '=' char followed by a one-char simple pattern
    • a  compound  pattern,  made  by  combining  simple  and  charset
      patterns by:
        • not logical operator '^' 
        • and logical operator '&'
        • or logical operator ','
        • and ')' parenthesis '(' and ')'

2. SIMPLE PATTERNS

Some examples of simple patterns:

    • pattern '*' matches any string
    • pattern 'abc*' matches any string starting with 'abc'
    • pattern '*abc' matches any string ending with 'abc'
    • pattern '*abc*' matches any string containing 'abc'
    • pattern '?' matches any single character
    • pattern '[az]' matches 'a' or 'z'
    • pattern '[!az]' matches any single character except 'a' or 'z'
    • pattern '[a-z]' matches any single character between 'a' and 'z'
    • pattern '[!a-z]' matches any single char not between 'a' and 'z'
    • pattern  '[a-z0-9_]' matches any single char between 'a' and 'z'
      or between '0' and '9' or equal to '_'
    • pattern '[!a-z0-9_]' matches any single char not between 'a' and
      'z' and not between '0' and '9' and not equal to '_'

If  a  metacharacter  must  belong to a simple pattern then it must be
quoted by '[' and ']', more exactly:

    • '*' '?' '[' '^' '&' ',' '(' and ')' must always be quoted
    • '!'  and  '-' if not between '[' and ']' have no special meaning
      and don't need to be quoted
    • '=' needs to be quoted only if in first position
    • ']'  only  can not be quoted, but you should not need it because
      an  unmatched  ']'  has  no  special meaning and doesn't raise a
      syntax error, while unmatched '[' '(' and ')' do

Examples:

    • pattern  '[(]*[)]'  matches  any  string  starting  with '(' and
      ending with ')'
    • pattern  '[[]*]' matches any string starting with '[' and ending
      with ']'
    • patterns  '[=]*='  and  '[=]*[=]'  match any string starting and
      ending with '='

You can quote metacharacter '!' too, but not immediately after '['.

    • pattern '[?!]' matches '?' and '!' only
    • pattern '[!?]' matches any character except '?'

You can quote metacharacter '-' too, a '-' after '[' or before ']' has
no special meaning:

    • patterns '[-pr]' and '[pr-]' matches '-' 'p' and 'r'
    • pattern '[p-r]' matches 'p' 'q' and 'r'

'-' stands for itself even after a character interval:

    • pattern '[p-rx]' matches 'p' 'q' 'r' and 'x'
    • pattern '[p-r-x]' matches 'p' 'q' 'r' '-' and 'x'
    • pattern '[p-rx-z]' matches 'p' 'q' 'r' 'x' 'y' and 'z'
    • pattern '[p-r-x-z]' matches 'p' 'q' 'r' '-' 'x' 'y' and 'z'

Descending character intervals do not work:

    • pattern '[z-z]' is accepted and is equivalent to '[z]'
    • pattern '[z-a]' is accepted but it does not match anything

Curly  brackets '{' and '}' are not metacharacters and have no special
meaning.

They  are  only  two differences between patterns defined by fnmatch()
and  fnmatchcase()  functions  in  Python3 fnmatch module and patterns
accepted by YARE:

    • unmatched  '['  (as  in pattern 'abc[def') is allowed by fnmatch
      but is rejected by YARE as a syntax error
    • null pattern '' is allowed by fnmatch but is rejected by YARE as
      a  syntax  error  (see  later  for  a workaround to match a null
      string by a not null pattern)

Match of simple patterns can be:

    • case-sensitive, by yarecsmatch() function
    • case-insensitive, by yarecimatch() function
    • case-multiple, by yarecmmatch() function
    • system-dependent, by yareosmatch() function

Case-multiple  match  is case-sensitive for simple patterns containing
at least one lowercase letter, case-insensitive for the others:

    • with yarecmmatch(), pattern 'RAM,*.db' matches 'ram' or 'RAM' or
      'Ram' or 'xy.db' but not 'xy.Db'

System-dependent  match  is  case-insensitive  if the current platform
requires it, else is case-sensitive:

    • with  yareosmatch(),  pattern  '*.jpg'  matches  'xy.JPG'  under
      MS-Windows but not under Linux

3. CHARSET PATTERNS

A  charset pattern is made by a '=' char followed by a one-char simple
pattern.  It  matches  all  strings  where each char matches the given
simple pattern:

    • pattern  '=[0-9]' matches the null string and any string made up
      of only digits (it is a shortcut for '^*[!0-9]*')
    • pattern '=[!0-9]' matches the null string and any string made up
      of only non-digit chars (it is a shortcut for '^*[0-9]*')
    
Charset match is always case-sensitive.

4. COMPOUND PATTERNS

In the following examples, p and q are two simple or charset patterns.

A  compound pattern is built aggregating simple or charset patterns by
logic operators and parenthesis:

    • pattern '^p' matches any string not matching p
    • pattern 'p&q' matches any string matching both p and q
    • pattern 'p,q' matches any string matching p or q or both

Examples:

    • pattern  '*.jpg,*.mp4'  matches any string ending with '.jpg' or
      with '.mp4'
    • pattern '^*' does not match anything
    • pattern '?*' matches any string of one or more characters, so...
    • ...pattern '^?*' matches the null string and nothing else

Two '^' characters cancel each other out:

    • patterns '^^p' and 'p' are equivalent

Precedence is of course '^' > '&' > ',':

    • pattern   '=[a-zA-Z0-9_]&^[0-9]*'  matches  all  correct  Python
      identifier

Precedence  can  be forced by parenthesis '(' and ')', so for instance
the De Morgan's laws tell us that:

    • patterns '^p&^q' and '^(p,q)' are equivalent
    • patterns '^p,^q' and '^(p&q)' are equivalent

5. HISTORY

    • 1.1.0 (Production/Stable)
        • compatible with version 1.0.0
        • added: charset patterns
        • added: case-multiple match by yarecmmatch() function

    • 1.0.0 (Production/Stable)
        • incompatible with previous versions
        • simplified redefined and optimized

    • 0.4.3 (Experimental/Deprecated)
        • updated: documentation

    • 0.4.2 (Experimental/Deprecated)
        • updated: documentation

    • 0.4.1 (Experimental/Deprecated)
        • first version published on pypi.org
'''

__version__ = '1.1.0'

from fnmatch import fnmatch, fnmatchcase
from re import error as ReError

__all__ = ['yarecsmatch', 'yarecimatch', 'yarecmmatch', 'yareosmatch'] # exported functions
NOT, AND, OR, LEFT, RIGHT, PATTERN = '^&,()*' # tokens: operators and patterns
CHARSET = '=' # prefix of charset patterns
RANK_NOT, RANK_AND, RANK_OR, RANK_LEFT, RANK_RIGHT = [3, 2, 1, 0, 0] # operator priorities
RANK = {NOT: RANK_NOT, AND: RANK_AND, OR: RANK_OR, LEFT: RANK_LEFT, RIGHT: RANK_RIGHT}
OPERATORS = frozenset(RANK.keys()) # YARE metacharacters
AFTER = {NOT:     frozenset([PATTERN, NOT, LEFT]), # token sequence check
         AND:     frozenset([PATTERN, NOT, LEFT]),
         OR:      frozenset([PATTERN, NOT, LEFT]), 
         LEFT:    frozenset([PATTERN, NOT, LEFT]),
         RIGHT:   frozenset([OR, AND, RIGHT]),
         PATTERN: frozenset([OR, AND, RIGHT])}
NOT_IN_SIMPLE, IN_SIMPLE, IN_BRAKES = [0, 1, 2] # status values for scanner()
scanned = {} # cache for results of scanner()

def scanner(pattern):
    '''translate pattern into a list of tokens, checking the correct token sequence,
each token will be either a one-character operator (OR, AND, NOT, LEFT or RIGHT) or a simple PATTERN'''
    try:
        return scanned[pattern]
    except KeyError:
        tokens = []
        status = NOT_IN_SIMPLE
        allowed = LEFT
        for char in LEFT + pattern + RIGHT:
            if status == NOT_IN_SIMPLE:
                tokens.append(char)
                if char in OPERATORS: # char is an operator
                    if char not in allowed:
                        raise IndexError
                    allowed = AFTER[char]
                else: # char starts a simple pattern
                    if PATTERN not in allowed:
                        raise IndexError
                    allowed = AFTER[PATTERN]
                    status = IN_BRAKES if char == '[' else IN_SIMPLE
            elif status == IN_SIMPLE:
                if char in OPERATORS: # char is an operator, simple pattern ends
                    if char not in allowed:
                        raise IndexError
                    allowed = AFTER[char]
                    tokens.append(char)
                    status = NOT_IN_SIMPLE
                else: # simple pattern continues
                    tokens[-1] += char
                    if char == '[':
                        status = IN_BRAKES
            else: # status == IN_BRAKES, hence between '[' and ']'
                tokens[-1] += char
                if char == ']':
                    status = IN_SIMPLE
        if status == IN_BRAKES:
            raise IndexError # unmatched '[' is not allowed
        scanned[pattern] = tokens
        return tokens

def charset_match(string, charset):
    'charset low-level match'
    if not charset.endswith(']'):
        raise IndexError
    if charset.startswith('=[!'):
        return not fnmatchcase(string, f'*[{charset[3:]}*')
    elif charset.startswith('=['):
        return not fnmatchcase(string, f'*[!{charset[2:]}*')
    else:
        raise IndexError

def csmatch(string, pattern):
    'case-sensitive low-level match'
    if pattern.startswith(CHARSET):
        return charset_match(string, pattern)
    else:
        return fnmatchcase(string, pattern)

def cimatch(string, pattern):
    'case-insensitive low-level match'
    if pattern.startswith(CHARSET):
        return charset_match(string, pattern)
    else:
        return fnmatchcase(string.upper(), pattern.upper())

def cmmatch(string, pattern):
    'case-multiple low-level match'
    if pattern.startswith(CHARSET):
        return charset_match(string, pattern)
    elif pattern == pattern.upper():
        return fnmatchcase(string.upper(), pattern.upper())
    else:
        return fnmatchcase(string, pattern)

def osmatch(string, pattern):
    'case-platform low-level match'
    if pattern.startswith(CHARSET):
        return charset_match(string, pattern)
    else:
        return fnmatch(string, pattern)

def yarecsmatch(string, pattern):
    'YARE case-sensitive match'
    return yarematch(string, pattern, match=csmatch)

def yarecimatch(string, pattern):
    'YARE case-insensitive match'
    return yarematch(string, pattern, match=cimatch)

def yarecmmatch(string, pattern):
    'YARE case-multiple match'
    return yarematch(string, pattern, match=cmmatch)

def yareosmatch(string, pattern):
    'YARE system-dependent match'
    return yarematch(string, pattern, match=osmatch)

def yarematch(string, pattern, match=None):
    "YARE match main function, it uses the Dijkstra's 'two-stacks' (aka 'shunting-yard') algorithm"
    
    def apply(operator):
        'apply operator (OR AND or NOT) on stack of values'
        if operator == OR:
            one = values[-2]
            two = values.pop()
            values[-1] = ((True if one is True else False if one is False else match(string, one)) or
                          (True if two is True else False if two is False else match(string, two)))
        elif operator == AND:
            one = values[-2]
            two = values.pop()
            values[-1] = ((True if one is True else False if one is False else match(string, one)) and
                          (True if two is True else False if two is False else match(string, two)))
        else: # operator == NOT
            one = values[-1]
            values[-1] = False if one is True else True if one is False else not match(string, one)

    operators = [] # stack of operators, each operator can be OR AND NOT or LEFT
    values = [] # stack of values, each value is either str (simple pattern yet to be matched) or bool (simple pattern already matched)
    try:
        for token in scanner(pattern):
            if token == OR:
                while operators and RANK[operators[-1]] >= RANK_OR:
                    apply(operators.pop())
                operators.append(OR)
            elif token == AND:
                while operators and RANK[operators[-1]] >= RANK_AND:
                    apply(operators.pop())
                operators.append(AND)
            elif token == NOT:
                while operators and RANK[operators[-1]] > RANK_NOT:
                    apply(operators.pop())
                operators.append(NOT)
            elif token == LEFT:
                operators.append(LEFT)
            elif token == RIGHT:
                while operators and operators[-1] != LEFT:
                    apply(operators.pop())
                operators.pop()
            else: # token is a simple pattern
                values.append(token)
        if operators or len(values) != 1:
            raise IndexError
        one = values[0]
        return True if one is True else False if one is False else match(string, one)
    except (IndexError, ReError):
        raise SyntaxError(f'Syntax error in YARE pattern {pattern!r}')

