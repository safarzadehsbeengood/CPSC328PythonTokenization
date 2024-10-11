# Author: Ryan Safarzadeh
# Input: a python file
# Output: Categories and Tokens -> dict<str: list<str>>
# ********************************************************
# Example usage: python3 tokenization.py [filepath]

# --------------------
# # Example comment
# def add(a, b):
#     result = a + b
#     return result
#
# print(add(5, 3))
# --------------------

import sys
from categories import DELIMITERS, OPERATORS, KEYWORDS

NEWLINE_OR_SPACE_OR_DELIMITER = {'\n', ' '}.union(DELIMITERS)   # the main separating characters for other token types

# a class for holding sets of tokens
class Tokens:
    keywords = set() 
    identifiers = set()
    operators = set()
    delimiters = set()
    literals = set()
    comments = set()
    
    # return a map for easy printing
    def asMap(self):
        return {
            "Keywords": self.keywords,
            "Identifiers": self.identifiers,
            "Operators": self.operators,
            "Delimiters": self.delimiters,
            "Literals": self.literals,
            "Comments": self.comments
        }
        
    # a print function
    def print(self):
        for label, tokens in self.asMap().items():
            print(f'> {label}:\n\t* {'\n\t* '.join(tokens)}')
            
    # return the token count
    def tokenCount(self):
        ct = 0
        for tokens in (self.asMap().values()):
            ct += len(tokens)
        return ct
    
masterTokens = Tokens()

def tokenize_line(s: str):
    """
    Parse the line and add the tokens to masterTokens

    Args:
        s (str): The line to be parsed and tokenized
    """
    def find_next(start: int, target):
        '''
        Returns the index of the first character found 
        in any character of target.
        '''
        pos = start
        while pos < len(s):
            if s[pos] in target:
                return pos
            pos += 1
        return None
        
    curr = 0

    while curr < len(s):
        # if we encounter a space, we can skip
        if s[curr] == ' ':
            # print("SPACE")
            curr += 1
            continue
        
        # if we encounter a pound, the rest of the line is a comment and we can ignore it
        if s[curr] == '#':
            masterTokens.comments.add("# " + s.split("#")[-1].strip())
            break
        
        # if we encounter a delimiter, we can just add it
        if s[curr] in DELIMITERS:
            masterTokens.delimiters.add(s[curr])
            curr += 1
        
        # if we encounter a numeric literal, find the next space or delimiter
        elif s[curr].isnumeric():
            # print("NUMBER LITERAL")
            # find the next newline, space, or delimiter
            next_char = find_next(curr, NEWLINE_OR_SPACE_OR_DELIMITER)
            if next_char is None:
                masterTokens.literals.add(s[curr:])
                curr = len(s)
            else:
                masterTokens.literals.add(s[curr:next_char])
                curr = next_char
            
        # if we encounter a string literal, find the next matching quote
        elif s[curr] == '"' or s[curr] == "'":
            # print("STRING LITERAL")
            next_quote = find_next(curr+1, ('"' if s[curr] == '"' else "'"))
            if next_quote is None:
                masterTokens.literals.add(s[curr:])
                curr = len(s)
            else:
                masterTokens.literals.add(s[curr:next_quote+1])
                curr = next_quote + 1
                
        # if we encounter an operator, we can just add it.
        elif s[curr] in OPERATORS:
            # print("OPERATOR")
            if s[curr:curr+1] in OPERATORS:
                masterTokens.operators.add(s[curr:curr+2])
                curr += 2
            else:
                masterTokens.operators.add(s[curr])
                curr += 1
        
        # for identifiers and keywords, we can check first if it's a keyword; if not, it's an identifier
        else:
            # print("KEYWORD OR IDENTIFIER")
            end_of_token = find_next(curr, NEWLINE_OR_SPACE_OR_DELIMITER)
            # special case for EOL
            if end_of_token is None:
                if s[curr:] in KEYWORDS:
                    masterTokens.keywords.add(s[curr:])
                else:
                    masterTokens.identifiers.add(s[curr:])
                curr = len(s)
                continue
            if s[curr:end_of_token] in KEYWORDS:
                masterTokens.keywords.add(s[curr:end_of_token])
            else:
                masterTokens.identifiers.add(s[curr:end_of_token])
            curr = end_of_token

# commandline parsing
if len(sys.argv) < 2 or len(sys.argv) > 2:
    print("[tokenization.py] -> Error: ")
    sys.exit("\tExample usage: python3 tokenize.py [filepath]")

# remove the inline comments from already formatted code
def clean_code(lines):
    res = [line.split("#")[0] for line in lines]
    return res

# file parsing
with open(sys.argv[1], 'r') as file:
    original_text = file.read()[:-1]
    print(f'\n{"◼︎" * 80}\t\t\n> {sys.argv[1]} Code: \n{"-"*60}\n{original_text}\n{"-"*60}\n')
    file.seek(0)
    # lines = [' '.join(line.strip().split()) for line in file.read().split('\n') if (line.strip() != '' and not line.strip()[0] == '#')]
    lines = []
    
    # get inline comments
    for line in file.readlines():
        if not line.strip() == '':
            if line.strip()[0] == "#":
                masterTokens.comments.add("# " + line.split("#")[-1].strip())
            else:
                lines.append(' '.join(line.strip().split()))
    print(f'> Cleaned code:\n{"-"*60}\n{'\n'.join(clean_code(lines))}\n{"-"*60}\n')
    
    # Tokenize the lines, avoid triple-quote comments
    i = 0
    while i < len(lines): 
        if lines[i] == '"""':
            comment = '"""'
            i += 1
            while lines[i] != '"""':
                comment += lines[i]
                i += 1
            masterTokens.comments.add(comment + '"""')
            i += 1
        tokenize_line(lines[i])
        i += 1
    masterTokens.print()
    print(f"Total: {masterTokens.tokenCount()}")
    
