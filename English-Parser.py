from string import ascii_letters

LETTERS = ascii_letters

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f'[{self.type}:{self.value}]' if self.value else f'{self.type}'

TT_ART = "ART"
TT_NOUN = "NOUN"
TT_VERB = "VERB"
TT_ADJ = "ADJ"
TT_COMMA = "COMMA"

nouns = [
    'dog',
    'man',
    'cat',
    'woman',
    'robot',
    'dice',
    'town'
]

verbs = [
    'bit',
    'kicked',
    'stroked',
    'goes'
]

adjs = [
    'powerful',
    'beautiful',
    'furious',
    'furry'
]

arts = [
    'a',
    'the',
    'to'
]

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.advance()

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos<len(self.text) else None

    def select_form(self):
        word = ''
        while (self.current_char != None) and (self.current_char in LETTERS):
            word += self.current_char
            self.advance()
        if word in nouns:
            return Token(TT_NOUN, word)
        elif word in arts:
            return Token(TT_ART, word)
        elif word in verbs:
            return Token(TT_VERB, word)
        elif word in adjs:
            return Token(TT_ADJ, word)
        else:
            print(f"undefined word {word}")

    def generate_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, None))
                self.advance()
            elif self.current_char in LETTERS:
                tokens.append(self.select_form())
            else:
                print(f"undefined letter {self.current_char}")

        return tokens

class SubjectNode:
    def __init__(self, art, adj, noun):
        self.art = art
        self.adj = adj
        self.noun = noun

    def __repr__(self):
        return f"Subject: [Art: {self.art}, Adjective: {self.adj}, Noun: {self.noun}]" if self.adj else f"Subject: [Art: {self.art}, Noun: {self.noun}]"

class VerbNode:
    def __init__(self, verb):
        self.letters = verb

    def __repr__(self):
        return f"Verb: [{self.letters}]"

class ObjectNode:
    def __init__(self, art, adj, noun):
        self.art = art
        self.adj = adj
        self.noun = noun

    def __repr__(self):
        return f"Object: [Art: {self.art}, Adjective: {self.adj}, Noun: {self.noun}]" if self.adj else f"Object: [Art: {self.art}, Noun: {self.noun}]"

class SingleAdjNode:
    def __init__(self, value):
        self.adj = value

    def __repr__(self):
        return f"{self.adj}"

class AdjNode:
    def __init__(self, adjectives):
        self.adjs = adjectives

    def __repr__(self):
        return f"[{', '.join([str(x) for x in self.adjs])}]" if len(self.adjs)>1 else f"{self.adjs}"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = -1
        self.advance()

    def advance(self):
        self.pos += 1
        self.current_tok = self.tokens[self.pos] if self.pos<len(self.tokens) else None

    def sentence(self):
        subject = self.subj()
        verb = self.verb()
        object = self.obj()
        return [subject, verb, object]

    def subj(self):
        if self.current_tok.type != TT_ART:
            print("Grammar Error, expected art")
            return None
        art = self.current_tok.value
        self.advance()
        adjective, noun = self.noun()
        return SubjectNode(art, adjective, noun)

    def adjective(self):
        adjectives = []
        if self.current_tok.type != TT_ADJ:
            print("Grammar Error, expected adjective")
            return None
        adjectives.append(SingleAdjNode(self.current_tok.value))
        self.advance()
        while self.current_tok.type == TT_COMMA:
            self.advance()
            adjectives.append(SingleAdjNode(self.current_tok.value))
            self.advance()
        return AdjNode(adjectives)

    def noun(self):
        adjective = AdjNode([])
        if self.current_tok.type == TT_ADJ:
            adjective = self.adjective()
        if self.current_tok.type != TT_NOUN:
            print("Grammar Error, expected noun")
            return None
        noun = self.current_tok.value
        self.advance()
        return adjective, noun

    def verb(self):
        if self.current_tok.type != TT_VERB:
            print("Grammar Error, expected verb")
            return None
        ret_verb = self.current_tok.value
        self.advance()
        return VerbNode(ret_verb)

    def obj(self):
        if self.current_tok.type != TT_ART:
            print("Grammar Error, expected art")
            return None
        art = self.current_tok.value
        self.advance()
        adjective, noun = self.noun()
        return ObjectNode(art, adjective, noun)

    def parse(self):
        sentence = self.sentence()
        return sentence

class codeGen:
    def __init__(self, nodes):
        self.nodes = nodes
        self.generated = {}

    def generate_code(self):
        for node in self.nodes:
            self.visit(node)
        if self.generated['object_adjs']:
            string = f"{self.generated['object_art']} {self.generated['object_adjs']} {self.generated['object_noun']}, "
        else:
            string = f"{self.generated['object_art']} {self.generated['object_noun']}, "
        if self.generated['subject_adjs']:
            string += f"{self.generated['subject_art']} {self.generated['subject_adjs']} {self.generated['subject_noun']} "
        else:
            string += f"{self.generated['subject_art']} {self.generated['subject_noun']} "
        string += f"{self.generated['verb']}"
        return string

    def visit(self, node, parent=None):
        toCall = f"visit_{type(node).__name__}"
        args = [node, parent if parent else None]
        args = [x for x in args if x]
        if hasattr(self, toCall):
            getattr(self, toCall)(*args)
        else:
            raise Exception(f"Undefined method {toCall}")

    def visit_SubjectNode(self, node):
        self.generated["subject_art"] = node.art
        self.visit(node.adj, 'subject')
        self.generated["subject_noun"] = node.noun

    def visit_VerbNode(self, node):
        self.generated["verb"] = node.letters

    def visit_AdjNode(self, node, parent):
        self.generated[f"{parent}_adjs"] = []
        for adj in node.adjs:
            self.visit(adj, parent)
        adjs = [x for x in self.generated[f"{parent}_adjs"]]
        self.generated[f"{parent}_adjs"] = ", ".join(adjs)

    def visit_SingleAdjNode(self, node, parent):
        self.generated[f"{parent}_adjs"].append(node.adj)

    def visit_ObjectNode(self, node):
        self.generated["object_art"] = node.art
        self.visit(node.adj, 'object')
        self.generated["object_noun"] = node.noun

def run(text):
    lexer = Lexer(text)
    tokens = lexer.generate_tokens()
    parser = Parser(tokens)
    ast = parser.parse()
    generator = codeGen(ast)
    result = generator.generate_code()
    return result

print(run("the furious robot kicked the beautiful town"))
