const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

class Token {
    constructor(type, value) {
        this.type = type
        this.value = value
      }
}

const TT_ART = "ART"
const TT_NOUN = "NOUN"
const TT_VERB = "VERB"
const TT_ADJ = "ADJ"
const TT_COMMA = "COMMA"

const nouns = [
    'dog',
    'man',
    'cat',
    'woman',
    'robot',
    'dice',
    'town'
]

const verbs = [
    'bit',
    'kicked',
    'stroked',
    'goes'
]

const adjs = [
    'powerful',
    'beautiful',
    'furious',
    'furry'
]

const arts = [
    'a',
    'the',
    'to'
]

class Lexer {
    constructor (text){
        this.text = text
        this.pos = -1
        this.advance()
      }

    advance(){
        this.pos += 1
        this.current_char = this.pos<this.text.length? this.text[this.pos] : null
      }

    select_form(){
      let word = ''
        while ((this.current_char != null) && (LETTERS.split("").includes(this.current_char))){
            word += this.current_char
            this.advance()
          }
          if (nouns.includes(word)){
              return new Token(TT_NOUN, word)
          } else if (arts.includes(word)){
              return new Token(TT_ART, word)
          } else if (verbs.includes(word)){
              return new Token(TT_VERB, word)
          } else if (adjs.includes(word)){
              return new Token(TT_ADJ, word)
            }else{
              console.log(`undefined word ${word}`)
            }
          }

    generate_tokens(){
        let tokens = []
        while (this.current_char != null){
            if ([" ", "\t"].includes(this.current_char)){
                this.advance()
              } else if (this.current_char == ','){
                tokens.push(new Token(TT_COMMA, null))
                this.advance()
              } else if (LETTERS.split("").includes(this.current_char)){
                tokens.push(this.select_form())
              } else {
                console.log(`undefined letter ${this.current_char}`)
              }
          }
        return tokens
    }
}

class SubjectNode {
    constructor (art, adj, noun){
        this.art = art
        this.adj = adj
        this.noun = noun
      }
}

class VerbNode{
    constructor (verb){
        this.letters = verb
      }
}
class ObjectNode {
    constructor(art, adj, noun){
        this.art = art
        this.adj = adj
        this.noun = noun
      }
}
class SingleAdjNode{
     constructor(value){
        this.adj = value
      }
}

class AdjNode{
    constructor (adjectives){
        this.adjectives = adjectives
      }
}

class Parser{
    constructor(tokens){
        this.tokens = tokens
        this.pos = -1
        this.advance()
      }

      advance (){
        this.pos += 1
        this.current_tok = this.pos<this.tokens.length? this.tokens[this.pos] : null
      }

    sentence(){
        let subject = this.subj()
        let verb = this.verb()
        let object = this.obj()
        return [subject, verb, object]
      }

    subj(){
        if (this.current_tok.type != TT_ART){
            print("Grammar Error, expected art")
            return null
          }
        let art = this.current_tok.value
        this.advance()
        let whole = this.noun()
        return new SubjectNode(art, whole[0], whole[1])
      }

    adjective(){
        let adjectives = []
        if (this.current_tok.type != TT_ADJ){
            print("Grammar Error, expected adjective")
            return null
          }
        adjectives.push(new SingleAdjNode(this.current_tok.value))
        this.advance()
        while (this.current_tok.type == TT_COMMA){
            this.advance()
            adjectives.push(new SingleAdjNode(this.current_tok.value))
            this.advance()
          }
        return new AdjNode(adjectives)
      }

    noun(){
        let adjective = new AdjNode([])
        if (this.current_tok.type == TT_ADJ){
            adjective = this.adjective()
          }
        if (this.current_tok.type != TT_NOUN){
            console.log("Grammar Error, expected noun")
            return null
          }
        let noun = this.current_tok.value
        this.advance()
        return [adjective, noun]
      }

    verb(){
        if (this.current_tok.type != TT_VERB) {
            console.log("Grammar Error, expected verb")
            return null
          }
        let ret_verb = this.current_tok.value
        this.advance()
        return new VerbNode(ret_verb)
      }

    obj(){
        if (this.current_tok.type != TT_ART){
            console.log("Grammar Error, expected art")
            return null
          }
        let art = this.current_tok.value
        this.advance()
        let whole = this.noun()
        return new ObjectNode(art, whole[0], whole[1])
      }

    parse(){
        let sentence = this.sentence()
        return sentence
      }
}
class codeGen{
    constructor(nodes){
        this.nodes = nodes
        this.generated = {}
      }

    generate_code(){
        for (let i = 0; i<this.nodes.length; i++){
            this.visit(this.nodes[i])
          }
        let string = ''
        if (this.generated['object_adjs']){
            string = `${this.generated['object_art']} ${this.generated['object_adjs']} ${this.generated['object_noun']}, `
        }else{
            string = `${this.generated['object_art']} ${this.generated['object_noun']}, `
        }
        if (this.generated['subject_adjs']){
            string += `${this.generated['subject_art']} ${this.generated['subject_adjs']} ${this.generated['subject_noun']} `
        }else{
            string += `${this.generated['subject_art']} ${this.generated['subject_noun']} `
          }
        string += `${this.generated['verb']}`
        return string
      }

    visit(node, parent=null){
        let toCall = `visit_${node.constructor.name}`
        let args = [node, parent]
        if (!args[1]){
          args.pop()
        }
        args = args.filter(x => x)
        this[toCall](...args)
    }
    visit_SubjectNode(node){
        this.generated["subject_art"] = node.art
        this.visit(node.adj, 'subject')
        this.generated["subject_noun"] = node.noun
      }

    visit_VerbNode(node){
        this.generated["verb"] = node.letters
      }

    visit_AdjNode(node, parent){
        this.generated[`${parent}_adjs`] = []
        for (let i=0; i<node.adjectives.length; i++){
            this.visit(node.adjectives[i], parent)
          }
        let adjectives = this.generated[`${parent}_adjs`].slice()
        this.generated[`${parent}_adjs`] = adjectives.join(", ")
      }

    visit_SingleAdjNode(node, parent){
        this.generated[`${parent}_adjs`].push(node.adj)
      }

    visit_ObjectNode(node){
        this.generated["object_art"] = node.art
        this.visit(node.adj, 'object')
        this.generated["object_noun"] = node.noun
      }
}
const run = (text) => {
    let lexer = new Lexer(text)
    let tokens = lexer.generate_tokens()
    let parser = new Parser(tokens)
    let ast = parser.parse()
    let generator = new codeGen(ast)
    let result = generator.generate_code()
    return result
}
console.log(run("the furious robot kicked the beautiful town"))
