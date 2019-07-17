#   Mainumby/Mit'mit'a: sentences and how to parse and translate them.
#
########################################################################
#
#   This file is part of the PLoGS meta-project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyleft 2014, 2015, 2016, 2017, 2018, 2019
#      HLTDI and PLoGS <gasser@indiana.edu>
#   
#   This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#   
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# =========================================================================

# 2014.04.15
# -- Created.
# 2014.04.19-20
# -- Group matching. GInst, GNode, and SNode classes.
# 2014.04.22
# -- Solution class.
# 2014.04.26-7
# -- Translation class and realization.
# 2014.04.28
# -- Variables for sentence analysis.
# 2014.04.29-30
# -- Fixed some constraints and initial variables values.
# 2014.05.01
# -- Handling source words that aren't "covered" (no group candidate matches them):
#    variables and source constraints.
# 2014.05.02
# -- Uncovered source words: target ordering constraints.
#    Introduced "chunks": target output units that are not connected.
# 2014.05.04-5
# -- New agreement variables and constraints.
# 2014.05.09
# -- Fixed output ordering so that order between nodes in merged groups
#    is right: all nodes in outer group before merged node must
#    precede all nodes in inner group, and all nodes in outer group
#    after merged node must follow all nodes in inner group.
# 2014.05.11
# -- Tree variables for unselected groups get removed from essential
#    variable list so the list of undetermined essential variables can
#    end up empty when it should be.
# 2014.05.15
# -- Fixed how group trees are worked out: using the snode->gnodes variables
#    rather than merger-related variables and tree variables.
# -- Search in group selection and output ordering.
# 2014.05.16
# -- Fixed a bug in how SL snodes with no corresponding TL snodes are
#    handled during node merging.
# 2014.05.18
# -- Target-language within-group agreement ("GIVES them a piece of HER/HIS mind").
# 2014.05.19
# -- all_sols argument to solve() and other methods that search finds all
#    solutions without querying user.
# -- Alignments is inferred from lexicon if not explicit.
# 2015.05.18
# -- Cache search and morphological analysis replaces form lookup in tokenize().
# 2015.05.20
# -- Generation now handled by morphology FSTs.
# 2015.06.10
# -- MorphoSyns applied in Sentence.tokenize().
# 2015.07.04
# -- Text class, including sentence tokenizer and splitter.
# 2015.07.05
# -- Fixed SNode - Group matching so it works for features added during
#    MorphoSyn matching, like +r (reflexive) in Spanish. Required adding
#    explicit negative features in groups.
#      se abrió matches abrir_v[+r] but not abrir_v[-r]
#      abrió matchs abrir_v[-r] but not abrir_v[+r]
# 2015.07.11
# -- Changed Text to Document (to agree with database class)
# 2015.07.17-25
# -- Translation class replaced by TreeTrans class, with instances
#    for each GInst
# 2015.07.28
# -- all_sols and all_trans options are separate. (Usually we'll want only
#    one solution but multiple translations?)
# 2015.07.29
# -- Segmentation of contractions; lowercasing of capitalized words.
#    Optional capitalization of first word in sentence translation.
# 2015.08.03
# -- Matching of "set items" in groups, like $$pro_3oj for 3p object pronouns
#    in Spanish. These don't result in "abstract" GNodes that must merge
#    with "concrete" GNodes. Rather they are concrete.
# 2015.08.06
# -- Sentence can create HTML for translated segments from solutions treetrans
#    objects.
# 2015.08.13
# -- TreeTrans objects aren't recreated for segments that already have one,
#    unless that one resulted from a merger.
# 2015.08.16
# -- Working on evaluator function for search states.
# 2015.09.24
# -- Changed evaluator function so it favors preferred analyses of cached words
#    (these have lower group indices).
# 2015.09.25
# -- For each key in the groups dict, only allow one to match (the entries are
#    ordered from most to least specific). Later allow exceptions to this. See
#    lexicalize().
# 2016.01.06
# -- Split off segment.py.
# 2016.01.11
# -- Added ?! to end-of-sentence characters.
# 2016.01.18
# -- Fixed TreeTrans.build() call so that multiple translations work with groups involving merging.
# 2016.02.23
# -- Sentence copy() can skip some features for one or more tokens.
# 2016.02.24
# -- No complicated figuring out what the max number of translations for nodes that aren't merged. Since similar group translations
#    were collapsed, it's just the number of group translations.
# 2016.03.01
# -- Adjusted which segments are created and how segments are displayed when corresponding source tokens are discontinuous
# 2016.05.03
# -- Fixed bug that prevented the same group (actually group head) from applying to different words.
# 2016.05.05
# -- Made the tokenizer more sophisticated (see RE in Document).
# 2016.06.15
# -- Fixed Solution.make_translations(), finally, so that it correctly calls build() on each top-level TreeTrans for each
#    combination of top-level and subgroup translation.
# 2016.06.30
# -- New constraint (and constraint type) added to Sentence, enforcing dependency by higher-level group with a cat node
#    and lower-level group that has a lexical node that merges with the cat node.
# 2016.07.25
# -- Another new constraint (and constraint type) added to Sentence, enforcing imcompatibility of groups with "merger loops".
#    Example: la casa en la cual dormimos -> <casa PP ART cual V> | <en N>
# 2017.03
# -- Lots of changes to make documents bilingual for training.
# 2017.03.23
# -- Fixed problems related to order of GInsts associated with a solution (value of 'groups' variable). The list from the
#    set needed to be sorted by index before TreeTrans.build().
# 2017.04.13
# -- Incorporated external tokenizer/tagger into Document class, replacing Document.tokenize(). Document.split(), and
#    Language.anal_word() in Sentence.
# 2017.04.24
# -- Got sentence initialization and solution to work with external tagger.
# 2018.07.09
# -- Roots in language exceptions.lex file cause morphological analysis to take precedence over POS tagger (cuarto_n, cuarto_a).
# 2019.03.21
# -- Docs can generate HTML for document-level GUI
# 2019.04.08
# -- Introduced ¶ for end of paragraph and titles.
# 2019.05.27
# -- Lexicalization always looks at simple (lexical) groups only.

import copy, re, random, itertools, os
from .ui import *
from .segment import *
from .record import SentRecord, Session
from .entry import Token
from .utils import remove_control_characters, firsttrue

class Document(list):
    """A list of of Sentences, split from a text string. If biling is True, this is a bilingual document,
    used for training; for all (or some?) source language sentences, there is a corresponding target
    language sentence."""

    id = 0

    start = ['¿', '¡']
    end = ['.', '?', '!']
    markers = [('\"', '\"'), ("(", ")"), ("{", "}")]
    wordsplit = ['—']

    mwe_sep = '~'

    ## regular expressions for matching tokens
    # adjoining punctuation (except .)
    # before: ([{¡¿"*'`«“‘-–—=
    # after: )]}!?":;*'»”’-–—=
    # within token: letters and digits, _-+.'@$^&=|/,~<>
    # within word: letters and digits, _-.'`&=|/~
    # beginning of token: letters and digits, -+#.@$~
    # end of token: letters and digits, -+#.$%/º
    # end of word: letters and digits, #./º
    # only digits
    number1_re = re.compile(r"([(\[{¡¿–—\"\'«“‘`*=]*)([\-+±$£€]?[\d]+[%¢°º]?)([)\]}!?\"\'»”’*\-–—,.:;]*)$")
    # digits with intermediate characters (.,=></), which must be followed by one or more digits
    number_re = re.compile(r"([(\[{¡¿–—\"\'«“‘`*=]*)([\-+±$£€]?[\d]+[\d,.=></+\-±/×÷≤≥]*[\d]+[%¢°º]?)([)\]}!?\"\'»”’*\-–—,.:;]*)$")
    # separated punctuation, including some that might be separated by error
    punc_re = re.compile(r"([\-–—&=.,:;\"+<>/?!%$¶]{1,3})$")
    # word of one character
    word1_re = re.compile(r"([(\[{¡¿\-–—\"\'«»“”‘`*=]*)(\w)([)\]}\"\'»”’*\-–—,:;=]*[?|.!]?)$")
    # word of more than one character: one beginning character, one end character, 0 or more within characters;
    # followed by possible punctuation and a possible footnote
    word_re = re.compile(r"([(\[{¡¿\-–—\"\'«»”“‘`*=]*)([\w#@~’][\w\-/:;+.'`’~&=\|]*[\w’/º#.])([)\]}\"\'»”’*\-–—,:;=.?!)\"\'»”’…¶]{0,3}\d*)$")
    word_lenient_re = re.compile(r"([(\[{¡¿\-–—\"\'«»”“‘`*=]*)([\w#@~’][\w\-/:;+.'`’~&=\|]*[\w’/º#.])([)\]}\"\'»”’*\-–—,:;=.?!)\"\'»”’…¶]*\d*)$")
    period_re = re.compile("([\w.\-/:;+.'`’~&=\|¶]+\.)([\d]*)$")
    start_re = re.compile('[\-–—¿¡\'\"«»“‘(\[]+$')
    poss_end_re = re.compile('[")\]}]{0,2}[?!][)"\]]{0,2}')
    # 0-2 pre-end characters (like ")"), 1 end character (.?!), 0-3 post-end characters (like ")" or footnote digits)
    end_re = re.compile('[\"\'”’»)\]}]{0,2}[.?!¶][.)»”’\'\"\]\-–—¶\d]{0,3}')

    def __init__(self, language=None, target=None, text='', target_text='', path='',
                 proc=True, session=None, biling=False, alternating=True,
                 reinitid=False, docid='', single=False):
        self.set_id(reinitid=reinitid, docid=docid)
        self.language = language
        self.target = target
        self.session = session
        if not text and path:
            text = Document.get_text_from_file(path)
        # Intermediate representations: list of word-like tokens and ints representing types
        self.tokens = []
        list.__init__(self)
        # Texts in two languages
        self.biling = biling
        if biling:
            if alternating:
                self.text, self.target_text = Document.biling_sep(text)
            else:
                self.target_text = target_text
                self.text = text
        else:
            self.text = text
            self.target_text = ''
        self.target_tokens = []
        self.target_sentences = []
        # Whether the input consists of a single "sentence", possibly without final punctuation
        self.single = single
        # A list of pairs of raw source-target sentences, the result of the user's interaction
        # with the system.
        self.output = []
        # Whether the document has been tokenized and split into sentences.
        self.processed = False
        # Whether sentences in the document have been initialized
        self.initialized = False
        # Markup for GUI
        self.html = ''
        self.html_list = ''
        if proc:
            self.process()
#        print("Created document with session {}".format(session))

    ## Processing monolingual and bilingual corpora which are already segmented by sentence.
    
    @staticmethod
    def proc_preseg(source, target, sentences, session=None, biling=False, sep="\t"):
        """sentences is a list of presegmented sentence strings (or pairs of sentences
        if biling is True). Creates a list of Document instances (or a pair of lists),
        each consisting of a single Sentence instance."""
        sents1 = []
        sents2 = []
        for sentence in sentences:
            if biling:
                s1, s2 = Document.doc2bisents(source, target, sentence, session=session)
                sents1.append(s1)
                sents2.append(s2)
            else:
                s = Document.doc2sent(source, target, sentence, session=session)
                sents1.append(s)
        if biling:
            return sents1, sents2
        return sents1

    @staticmethod
    def doc2sent(source, target, text, session=None):
        """Given a text and source and target languages, return a Sentence instance (or None if this is not possible)."""
        return Document(source, target, text, proc=True, session=session, single=True).to_sentence()

    @staticmethod
    def doc2bisents(source, target, text, session=None):
#        if text.count("\t") > 1:
#            print("{} has too many tabs".format(text))
        # There could be an extra tab following the target sentence.
        text1, text2 = text.split("\t")[:2]
        return Document.doc2sent(source, target, text1, session=session), \
          Document.doc2sent(target, None, text2, session=session)

    def to_sentence(self):
        """Return the single (or first) sentence in the Document if there is one."""
        if len(self) > 0:
            return self[0]

    ###
    
    def set_id(self, reinitid=False, docid=''):
        if docid:
            self.id = docid
        else:
            if reinitid:
                Sentence.id = 0
            self.id = Document.id
            Document.id += 1

    def __repr__(self):
        return "D[ {} ]D".format(self.id)

    @staticmethod
    def biling_sep(pairs, join=True, sep="\t"):
        """Separate a text with a pair of sentences on each line, separated by sep, into two lists
        of sentences. If join is True, join the sentences in each list by newlines."""
#        pairs = text.split("\n")
        s, t = pairs[::2], pairs[1::2]
        if join:
            s, t = '\n'.join(s), '\n'.join(t)
        return s, t

    @staticmethod
    def get_text_from_file(path):
        """Read in the text from a file."""
        try:
            with open(path, encoding='utf8') as file:
                return file.readlines()
        except IOError:
            print("¡Archivo no encontrado!")

    def preprocess(self):
        """Preprocess the document text.
        Remove Unicode control characters."""
        self.text = remove_control_characters(self.text)

    def process(self, reinit=True, verbosity=0):
        """Use tokenize and split to generate tokenized sentences,
        or use the off-the-shelf tokenizer and tagger to do this."""
        self.preprocess()
        self.process1(reinit=reinit, verbosity=verbosity)
        if self.biling:
            self.process1(target=True, reinit=reinit,verbosity=verbosity)
        self.processed = True

    def process1(self, target=False, reinit=False, verbosity=0):
        """Process either source or target sentences using either the off-the-shelf tagger
        or a special MDT one."""
        if target:
            language = self.target
            text = self.target_text
            target_language = None
            sentence_list = self.target_sentences
        else:
            language = self.language
            target_language = self.target
            sentence_list = self
            text = self.text
        if language.tagger and language.tagger.tokenize:
            tagger = language.tagger
            # tagger splits document into sentences
            sentences = tagger.get_sentences(text)
            for s in sentences:
                tokens = [t[0] for t in s]
#                analyses = [t[1] for t in s]
                analyses = [[t.lower(), a[1]] for t, a in zip(tokens, s)]
                sentence = Sentence(language=language,
                                    tokens=tokens, analyses=analyses,
                                    target=target_language, session=self.session)
                sentence_list.append(sentence)
        else:
            self.tokenize(target=target, verbosity=verbosity)
#            print("Tokens: {}".format(self.tokens))
            if reinit:
                Sentence.id = 0
            # Sentences are created here
            self.split(target=target)

    def tokenize(self, target=False, verbosity=0):
        """Split the text into word tokens, separating off punctuation except for
        abbreviations and numerals. Alternately use a language-specific tokenizer.
        If target is True, tokenize target-text."""
        # Later split at \n to get paragraphs.
        # Separate at whitespace.
        text = self.target_text if target else self.text
        tokens = self.target_tokens if target else self.tokens
        language = self.target if target else self.language
        # There might be whitespace before or after the text.
        text = text.strip()
        # Normalize different newline and CR characters.
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\n\n", "¶\n")
        if verbosity:
            print("Tokenizing text {}".format(text))
        # Split at new lines ...
        text_lines = text.split("\n")
#        print("Lines of text: {}".format(text_lines))
        text_tokens = []
        # ... then at spaces.
        for line in text_lines:
            text_tokens.extend(line.split())
        pre = ''
        suf = ''
        word = None
        for token in text_tokens:
            tok_subtype = 0
            word_tok = False
            number = False
            punctuation = False
            match = Document.punc_re.match(token)
            if match:
                tok_subtype = 1
                pre = ''; suf = ''; word = match.groups()[0]
            else:
                match = Document.number1_re.match(token)
                if match:
                    tok_subtype = 2
                else:
                    match = Document.number_re.match(token)
                    if match:
                        tok_subtype = 2
                    else:
                        match = Document.word1_re.match(token)
                        if match:
                            word_tok = True
                        else:
                            # Introduced new more lenient regex 2018.12.26 (replacing word_re)
                            match = Document.word_lenient_re.match(token)
                            if match:
                                word_tok = True
                            else:
                                print("Something wrong: {} fails to be an acceptable token; accepting it anyway".format(token))
                                word_tok = True
#                                if not input("Accept it anyway? "):
#                                    return
                if match:
                    pre, word, suf = match.groups()
                else:
                    pre, word, suf = None, token, None
                if pre:
                    tokens.append((pre, 0, 0))
                # Check to see if word ends in . (and opposition footnote digits) and is not an abbreviation
                if word_tok:
                    period_match = Document.period_re.match(word)
                    if period_match:
                        word1, suf1 = period_match.groups()
                        if word1 not in self.language.abbrevs:
                            word = word1[:-1]
                            suf = '.' + suf1 + suf
            tokens.append((word, 1, tok_subtype))
            if suf:
                tokens.append((suf, 2, 0))

    @staticmethod
    def is_sent_start(token):
        return token[0].isupper()

    @staticmethod
    def start_next(tokens):
        # Does a new sentence begin at the start of tokens?
        if not tokens:
            return False
        tok, typ, subtyp = tokens[0]
        if typ == 1:
            if Document.is_sent_start(tok):
                return True
        elif Document.start_re.match(tok):
            # sentence-inital punctuation
            if len(tokens) > 1 and Document.is_sent_start(tokens[1][0]):
                return True
        return False
            
    def split(self, target=False):
        """Split tokenized text into sentences. Used when there is no language-specific splitter.
        If target is true, split target_text."""
        tokens = self.target_tokens if target else self.tokens
        sentence_list = self.target_sentences if target else self
        language = self.target if target else self.language
        target_language = None if target else self.target
        current_sentence = []
        sentences = []
        ntokens = len(tokens)
        tokindex = 0
        token = ''
        toktype = 1
        raw_sentences = []
        raw_sentence = []
        raw_token = ''
        last_token_triple = ('', 1, -1)
        while tokindex < ntokens:
            token, toktype, toksubtype = tokens[tokindex]
#            print("token {}, toktype {}, toksubtype {}".format(token, toktype, toksubtype))
#            print("last token, type, subtype: {}".format(last_token_triple))
            if toktype in (0, 1):
                current_sentence.append((token, toktype, toksubtype))
                if last_token_triple[1] in (1, 2):
                    # New raw token
                    if raw_token:
                        raw_sentence.append(raw_token)
                    raw_token = token
                else:
                    raw_token += token
            # Punctuation: check whether this is a sentence end
            elif Document.end_re.match(token):
                if not current_sentence:
                    print("Something wrong: empty sentence: {}".format(tokens[:tokindex]))
                    return
                elif len(current_sentence) == 1 and current_sentence[0][2] == 2:
                    # Sentence consists only of a numeral following by this end-of-sentence punctuation; continue current sentence.
                    current_sentence.append((token, toktype, toksubtype))
                    raw_token += token
                else:
                    # End sentence
                    current_sentence.append((token, toktype, toksubtype))
                    sentences.append(current_sentence)
                    current_sentence = []
                    # Handle raw tokens/sentences
                    raw_token += token
                    raw_sentence.append(raw_token)
                    raw_sentences.append(raw_sentence)
                    raw_token = ''
                    raw_sentence = []
            elif Document.poss_end_re.match(token):
                if current_sentence and (tokindex == ntokens-1 or Document.start_next(tokens[tokindex:])):
                    # End sentence
                    current_sentence.append((token, toktype, toksubtype))
                    sentences.append(current_sentence)
                    current_sentence = []
                    # Handle raw tokens/sentences
                    raw_token += token
                    raw_sentence.append(raw_token)
                    raw_sentences.append(raw_sentence)
                    raw_token = ''
                    raw_sentence = []
                else:
                    current_sentence.append((token, toktype, toksubtype))
                    raw_token += token
            else:
                current_sentence.append((token, toktype, toksubtype))
                raw_token += token
            tokindex += 1
            last_token_triple = (token, toktype, toksubtype)
        if raw_token:
            raw_sentence.append(raw_token)
            raw_sentences.append(raw_sentence)
        if self.single and not sentences:
            current_sentence.append(('', 1, 0))
            sentences = [current_sentence]
        # Make Sentence objects for each list of tokens and types
        for sentence, rawsent in zip(sentences, raw_sentences):
#            print("Sentence: {}".format(sentence))
            sentence_list.append(Sentence(language=language,
                                          tokens=[t[0] for t in sentence],
                                          toktypes=[t[1] for t in sentence],
                                          original=' '.join(rawsent),
                                          target=target_language,
                                          session=self.session))

    def initialize(self, constrain_groups=True, verbose=False):
        """Initialize all the sentences in the document. If biling, initialize in both languges."""
        print("Iniciando oraciones en documento")
        print("  Oraciones fuente ...", end='')
        count = 0
        for sentence in self:
            count += 1
            if verbose:
                print("Iniciando oración fuente {}".format(sentence))
            elif count % 10 == 0:
                print("{}...".format(count), end='')
            sentence.initialize(constrain_groups=constrain_groups, terse=True)
        if not verbose:
            print()
            print("  Inició {} oraciones".format(count))
        if self.biling:
            print("  Oraciones meta ...", end='')
            count = 0
            for sentence in self.target_sentences:
                count += 1
                if verbose:
                    print("Iniciando oración meta {}".format(sentence))
                elif count % 10 == 0:
                    print("{}...".format(count), end='')
                sentence.initialize(constrain_groups=constrain_groups, terse=True)
            if not verbose:
                print()
                print("  Inició {} oraciones".format(count))
        self.initialized = True

    def get_sentence_pair(self, index):
        """Return a source/target sentence pair, given their index."""
        if self.biling:
            return self[index], self.target_sentences[index]

    ### GUI
    def set_html(self):
        """Generate HTML for sentence display in GUI."""
        html = "<div id='doc'>"
        html_list = []
        for index, sentence in enumerate(self):
            shtml = ""
            stext = sentence.original
            ident = "ora{}".format(index)
            shtml += "<div class='oradoc' id='{}' onclick='seleccionarOra(".format(ident)
            shtml += "\"{}\", {})'".format(ident, index)
            shtml += ">{}</div>".format(stext)
            html_list.append(shtml)
            html += shtml
        html += "</div>"
        self.html = html
        self.html_list = html_list

    def select_html(self, index, shtml):
        """Replace the indexed element in html_list with one for the selected and translated
        element."""
        html = "<div id='doc'>"
        html_list = self.html_list[:]
        html_list[index] = shtml
        html += "".join(html_list) + "</div>"
        return html
        
class Sentence:
    """A sentence is a list of words (or other lexical tokens) that gets assigned a set of variables
    and constraints that are run during parsing or translation. Starts either with raw, tokens generated
    by Document, or tokens already pre-tagged and pre-analyzed by an off-the-shelf tagger.
    2017.4.19: toktypes and toksubtypes seem no longer useful.
    tokens is just a list of tokens now."""

    id = 0
    word_width = 10
    name_chars = 25
    # colors to display sentence (TreeTrans) segments in interface
    tt_colors = ['red', 'blue', 'sienna', 'green', 'purple', 'red', 'blue', 'sienna', 'green', 'purple', 'red', 'blue', 'sienna', 'green', 'purple']

    def __init__(self, raw='', language=None, tokens=None, rawtokens=None, toks=None,
                 # the (restored) original string
                 original='',
                 toktypes=None, toksubtypes=None,
                 nodes=None, groups=None, target=None, init=False,
                 analyses=None, session=None, parent=None,
                 verbosity=0):
        self.set_id()
        # A list of string tokens, created by a Document object including this sentence
        # or None if the Sentence is created outside of Document
#        print("Creating sentence with tokens {}".format(tokens))
        if tokens:
            self.tokens = tokens
            self.raw = ' '.join(self.tokens)
            if not rawtokens:
                # Make a copy of tokens, so that lowercasing doesn't affect rawtokens later
                self.rawtokens = tokens[:]
            else:
                self.rawtokens = rawtokens
#            self.instantiate_tokens(tokens)
        else:
            self.raw = raw
            self.tokens = None
            self.rawtokens = None
        self.toks = toks
        self.toktypes = toktypes
        self.original = original
        # Token segmentations: (token, segmentation, token_index)
        self.toksegs = []
        # Set capitalization and final punctuation booleans
        if not self.original or self.original[0].isupper():
            self.capitalized = True
        else:
            self.capitalized = False
        if not self.original or self.original[-1].isupper():
            self.finalpunc = True
        else:
            self.finalpunc = False
#        print("New sentence; cap? {}".format(self.capitalized))
        # List of booleans, same length as self.tokens specifying whether the raw token was upper case
#        self.isupper = []
        # Source language: a language object
        self.language = language
        # External tagger if there is one
        self.tagger = language.tagger
        # Target language: a language object or None
        self.target = target
        # A list of tuples of analyzed words
        self.analyses = analyses or []
        # A list of SNode objects, one for each token
        self.nodes = nodes or []
        # A list of candidate groups (realized as GInst objects) found during lexicalization
        self.groups = groups or []
        # Control messages
        self.verbosity = verbosity
        # GNodes in GInsts
        self.gnodes = []
        # Indices of covered SNodes
        self.covered_indices = []
        # A list of constraints to run
        self.constraints = []
        # Root domain store for variables
        self.dstore = DStore(name="S{}".format(self.id))
        # A dict of sentence-level variables
        self.variables = {}
        # Modified copies of the sentence for cases of syntactic ambiguity; "alternate syntax"
        self.altsyns = []
        # MorphoSyns applied to sentence along with their start and end
        self.morphosyns = []
        # For Sentence copies, parent is the source of the copy
        self.parent = parent
        # Pairs of group instances that are incompatible because of merger loops.
        self.incompat_groups = []
        # Solver to find solutions
        self.solver = Solver(self.constraints, self.dstore,
                             evaluator=self.state_eval,
                             varselect=self.select_varval,
                             description='group selection', verbosity=verbosity)
        # Solutions found during parsing
        self.segmentations = []
        # Outputs from tree translation
        self.trans_outputs = []
        # Complete translations
        self.complete_trans = []
        # Session and associated SentRecord object; create if there is an active Session
        self.session = session
        if session and session.running:
            self.record = self.make_record(session)
        else:
            self.record = None
        if verbosity:
            print("Created Sentence object {}".format(self))
        if init:
            self.initialize()

    def set_id(self):
        self.id = Sentence.id
        Sentence.id += 1

    ## Display
    def __repr__(self):
        """Print name."""
        if self.tokens:
            short_name = ' '.join(self.tokens)
            if len(short_name) > Sentence.name_chars:
                short_name = short_name[:Sentence.name_chars] + '...'
            return 'S[ ({}) {} ]S'.format(self.id, short_name)
        elif self.raw:
            return 'S[ ({}) {} ]S'.format(self.id, self.raw)
        else:
            return 'S[ {} {} ]S'.format(self.language, self.id)

    def get_final_punc(self):
        """Return sentence-final punctuation as a string or empty string if there is none."""
        # Final token
        fintok = self.nodes[-1].token
        if self.language.is_punc(fintok):
            return fintok
        return ''

    def pretty(self):
        """Print sentence more or less as it originally appeared."""
        # Later combine ending punctuation with preceding word.
        return self.raw

    def display(self, show_all_sols=True, show_trans=True, word_width=0):
        """Show the sentence and one or more solutions in terminal."""
        s = "    "
        gap = word_width + 2
#        if word_width == 1:
#            gap = 3
#        else:
#            gap = word_width
        for node in self.nodes:
            token = node.token
            if word_width == 1:
                token = token[0]
            elif len(token) >= word_width-1:
                token = token[:word_width-1] + '.'
            s += "{}".format(token).center(gap)
        print(s)
        segmentations = self.segmentations if show_all_sols else self.segmentations[:1]
        for segmentation in segmentations:
            print("SEGMENTATION {}".format(segmentation.index))
            segmentation.display(word_width=gap)

    ## Initializing and solving a Sentence, created from a string if not already initialized
    @staticmethod
    def solve_sentence(sourceL, targetL, sentence=None, text='', session=None,
                       max_sols=2, translate=True, verbosity=0):
        if not sentence:
            d = Document(language=sourceL, target=targetL, text=text, proc=True,
                         single=True, session=session)
            sentence = d[0]
        sentence.initialize(ambig=False, verbosity=verbosity)
        sentence.solve(all_sols=max_sols > 1, max_sols=max_sols, translate=translate, verbosity=verbosity)
        return sentence

    ## Bilingual sentence pairs and analyses

    @staticmethod
    def biling_anal(source_sent, target_sent, verbosity=0):
        sanal = source_sent.analyze(translate=True, verbosity=verbosity)
        tanal = target_sent.analyze(translate=False, verbosity=verbosity)
        return sanal, tanal

    @staticmethod
    def biling_anal1(source_sents, target_sents, index, verbosity=0):
        return Sentence.biling_anal(source_sents[index], target_sents[index],
                                    verbosity=verbosity)

    @staticmethod
    def bitext_anal(source_sents, target_sents, report_every=20, start=0, end=-1, verbosity=0):
        result = []
        if end < 0:
            end = len(source_sents)
        for i, (s, t) in enumerate(zip(source_sents[start:end], target_sents[start:end])):
            if not s or not t:
                print("Warning {} or {} is empty".format(s, t))
                break
            sanal, tanal = Sentence.biling_anal(s, t, verbosity=verbosity)
            result.append((sanal, tanal))
            if (i + 1) % report_every == 0:
                print("{} pares de oraciones procesados".format(i + 1))
        return result

    @staticmethod
    def write_pseudosegs(source, segpairs, filename, append=True):
        path = source.get_pseudoseg_file(filename)
        with open(path, 'a' if append else 'w', encoding='utf8') as file:
            for seg1, seg2 in segpairs:
                if seg1 and seg2:
                    # Ignore pairs with no segmentations
                    print(seg1.pseudosegs, file=file)
                    print(seg2.pseudosegs, file=file)
                    print(file=file)

    ## Copying, for alternate syntactic representations

    def copy(self, skip=None):
        """Make a copy of the sentence, assumed to happen following analysis but before node creation.
        For ambiguous morphosyntax. Return the copy so it can be used by MorphoSyn.apply().
        skip is None or a list of triples: (position, token, feats). For each triple, the copy excludes the feats
        in the analysis of token in position."""
        s = Sentence(raw=self.raw[:],
                     tokens=self.tokens[:], rawtokens=self.rawtokens[:],
                     # toktypes=self.toktypes[:], toksubtypes= self.toksubtypes[:],
                     language=self.language, target=self.target, parent=self,
                     toks=self.toks[:],
                     analyses=copy.deepcopy(self.analyses))
        if skip:
#            print("Skipping {} in copy of {}".format(skip, self))
            for position, token, anal in skip:
                tok_anal = s.analyses[position]
#                print("  Token {}, analyses: {}".format(tok_anal[0], tok_anal[1]))
                res_anals = []
                for a in tok_anal[1]:
                    if a['features'] != anal:
                        res_anals.append(a)
#                print("  Replacing anals with {}".format(res_anals))
                tok_anal[1] = res_anals
#        print("Copied {} as {}".format(self, s))
        self.altsyns.append(s)
        return s

    def make_record(self, session):
        """Create a SentRecord object to this sentence."""
        return SentRecord(self, session=session)

    def get_node_by_raw(self, index):
        """Get the SNode that has index among its raw_indices."""
        for n in self.nodes:
            if index in n.raw_indices:
                return n
        return None

    ## Initial processing
    
    def segment(self, token, tok_index, verbosity=0):
        """Segment token if possible, replacing it in self.tokens with segmentation.
        Note that this has nothing to do with the class Segmentation."""
        segmentation = self.language.segs.get(token)
        if segmentation:
            self.tokens[tok_index:tok_index+1] = segmentation
            # Also increase the toktypes list
            self.toktypes[tok_index:tok_index+1] = [self.toktypes[tok_index], 1]
            self.toksegs.append((token, segmentation, tok_index))

    def clean(self):
        """Apply the language-specific clean-up function to normalize orthography and punctuation."""
        for index, token in enumerate(self.tokens):
            changed = False
            for d, c in self.language.clean.items():
                if d in token:
                    token = token.replace(d, c)
                    changed = True
            if changed:
                self.tokens[index] = token

    def join_lex(self, verbosity=0):
        """Combine tokens into units for numerals and names."""
        # Join words in MWE phrases (stored in the tree self.language.mwe)
        if self.language.mwe:
            joined = Sentence.join_from_tree(self.tokens, self.language.mwe)
            self.tokens = joined
        tokens = []
        tok_position = 0
        spec_found = False
        # Handle numeral word sequences
        while tok_position < len(self.tokens):
            spec = self.language.find_special(self.tokens[tok_position:], tok_position)
            if spec:
                newtokens, prefix = spec
                spec_found = True
                prefix = "%{}~".format(prefix)
                tokens.append(prefix + '~'.join(newtokens))
                tok_position += len(newtokens)
            else:
                tokens.append(self.tokens[tok_position])
                tok_position += 1
        if spec_found:
            self.tokens = tokens
                
    @staticmethod
    def join_from_tree(tokens, tree, position=0, subtree=None, result=None, to_join=None, previous_end=None):
        """Return tokens list with any sub-sequence joined with _ if found in tree.
        Searches for longest sequence when there are multiple possibilities beginning with the same sequence
        of tokens, but may fail to find the longest sequence when sequences overlap, because it searches left-to-right only.
        For example, given the sequence,
          a b c d e f g
          and possible joined subsequences, {b, c} and {c, d, e, f}, it will return
          a b_c d e f g
          rather than the otherwise preferable
          a b c_d_e_f g
        """
        if position >= len(tokens):
            return result
        if subtree is None:
            subtree = tree
        if result is None:
            result = []
        if to_join is None:
            to_join = []
        next_token = tokens[position]
#        print("Result: {}, position: {}, next_token: {}, previous end: {}".format(result, position, next_token, previous_end))
        if next_token in subtree:
            new_subtree = subtree[next_token]
#            print(" In subtree, new subtree: {}".format(new_subtree))
            to_join.append(next_token)
            if '' in new_subtree:
                # End of subtree is one option
                new_token = Document.mwe_sep.join(to_join)
                if len(new_subtree) > 1:
                    # But there are other longer options
#                    print(" End of subtree one option but not only one")
                    previous_end = (result + [new_token], position+1)
                    return Sentence.join_from_tree(tokens, tree, position=position+1, subtree=new_subtree,
                                                   result=result, to_join=to_join, previous_end=previous_end)
                else:
                    result.append(new_token)
#                    print(" End of subtree; new token: {}, new result: {}".format(new_token, result))
                    return Sentence.join_from_tree(tokens, tree, position=position+1, result=result)
            else:
                # More tokens need to be found
                return Sentence.join_from_tree(tokens, tree, position=position+1, subtree=new_subtree,
                                               result=result, to_join=to_join, previous_end=previous_end)
        elif position == 0 and next_token[0].isupper() and next_token.lower() in subtree:
            next_token = next_token.lower()
            new_subtree = subtree[next_token]
            to_join.append(next_token)
            return Sentence.join_from_tree(tokens, tree, position=position+1, subtree=new_subtree,
                                           result=result, to_join=to_join, previous_end=previous_end)
        else:
            # Fail
            if previous_end:
                # Return to last end
                prev_result, prev_pos = previous_end
#                print(" Failing on subtree, using previous end {}, {}".format(prev_result, prev_pos))
                return Sentence.join_from_tree(tokens, tree, position=prev_pos, result=prev_result)
            else:
                # Return to beginning of to_join sequence + 1
                if to_join:
                    result.append(to_join[0])
                    position = position - len(to_join) + 1
                else:
                    result.append(next_token)
                    position = position+1
#                print(" Failing on subtree, return to position {}".format(position))
                return Sentence.join_from_tree(tokens, tree, position=position, result=result)
            
    def lowercase(self):
        """Make capitalized tokens lowercase.
        2016.05.08: only do this for the first word.
        2017.03.19: do it for all words but keep a record of raw capitalization in self.isupper.
        2018.02.15: do this only for the first word, unless a word is uppercase.
        Still need to figure out what to do for words that are capitalized by convention within
        sentences, for example, at the beginning of quotations.
        """
        first_word = True
        for index, token in enumerate(self.tokens):
#            print("Token {}".format(token))
#            tok = self.toks[index]
#            tokname = tok.name
            if Document.mwe_sep in token:
                # Don't change case in MWE
                first_word = False
                continue
            if first_word:
                first_char = token[0]
                if not self.language.is_punc(first_char):
                    if self.language.is_known(token.lower()):
#                        print("First token lower {}".format(token))
                        self.tokens[index] = token.lower()
#                        tok.name = tokname.lower()
                    # Otherwise this is a name, so keep it capitalized
#                    print("  Not really first word...")
                    first_word = False
            elif token.isupper():
                # Lowercase words other than the first one if they're all uppercase
                self.tokens[index] = token.lower()
#                tok.name = tokname.lower()

    def preprocess(self, verbosity=0):
        """Segment contractions, join numerals, lowercase first word, normalize orthography and punctuation.
        Must follow word tokenization.
        Segmentation can add to the number of tokens in the sentence."""
        self.join_lex()
        self.lowercase()
        # Examine tokens in reverse order because segment() might change the number
        for index, token in zip(range(len(self.tokens)-1, -1, -1), self.tokens[-1::-1]):
            self.segment(token, index)
        self.clean()

    def instantiate_tokens(self):
        """Create SentToken instances for Sentence tokens."""
        self.toks = []
        for token in self.tokens:
            prefix, name = Token.split_token(token)
            self.toks.append(SentToken(name, prefix, self, punc=self.language.is_punc(name)))

    def initialize(self, ambig=True, verbosity=0, terse=True):
        """Things to do before running constraint satisfaction."""
        if verbosity:
            print("Initializing {}".format(self))
        # Note: this can change the number of tokens because of morphological segmentation.
        self.tokenize(verbosity=verbosity, ambig=ambig, terse=terse)
        # Tokenization could result in altsyns
        self.nodify(verbosity=verbosity)
        self.lexicalize(verbosity=verbosity, terse=terse)
        for s in self.altsyns:
            s.nodify(verbosity=verbosity)
            s.lexicalize(verbosity=verbosity, terse=terse)
        anygroups=False
        for s in [self] + self.altsyns:
            if not s.groups:
                continue
            s.create_variables(verbosity=verbosity)
            s.create_constraints(verbosity=verbosity)
            anygroups=True
        if not anygroups:
#            if not terse:
#                print("Ningunos grupos encontrados para {}".format(self))
            return False
        else:
            return True

    def tokenize(self, ambig=True, verbosity=0, terse=True):
        """Segment the sentence string into tokens, analyze them morphologically,
        and create a SNode object for each.
        2015.06.07: Save the analyzed tokens as well as nodes.
        2015.06.10: Apply MorphoSyns before creating nodes.
        2015.06.11: If incl_del is True, create nodes for elements deleted by MorphoSyns.
        2015.07: Document normally does the tokenization, so only morphological
        analysis and morphosyn matching happen here.
        2015.07.29: Segmentation and lowercasing of first word.
        2015.10.17: Added copy() possibility when there is morphosyntactic ambiguity.
        ambig option determines whether this happens.
        2017.05: Added POS tagging, where this doesn't happen in Document
        """
        if verbosity:
            print("Tokenizing {}".format(self))
        if not self.nodes:
            # Don't do this if nodes have already been created.
            # Skip the next steps if tokenization and morphological analysis happened when the
            # sentence was created.
            if self.analyses:
                self.lowercase()
                self.instantiate_tokens()
            else:
                tagged = None
                # Split at spaces by default.
                if not self.tokens:
                    self.tokens = self.raw.split()
                # Lowercase capitalized words, segment contractions, join numerals and other fixed sequences.
                self.preprocess()
                self.instantiate_tokens()
                # Do morphological analysis (added 2015.06.07)
                # 2017.03.09: cleaning done in preprocess() so don't do it here.
                # 2017.04.21: do this only if it hasn't already happened in an external tagger
                # First tag the tokens if there's an external tagger and this hasn't happened
                if self.tagger and not self.tagger.tokenizer:
                    # Use the POS tagger here
                    tagged = self.tagger.tag(self.tokens)
                # Still need to figure out how to integrated tagged results and morphological analyses
                if not self.tagger or self.tagger.morph:
                    analyses = self.morph_anal()
#                    [[token, self.language.anal_word(token, clean=False)] for token in self.tokens]
#                    print("Analyzed {}: {}".format(self.tokens, analyses))
                    if self.tagger:
                        # Merge results of tagging and morphological analysis
                        self.analyses = self.merge_POS(tagged, analyses)
                    else:
                        self.analyses = analyses
#                        self.analyses = [[token, self.language.anal_word(token, clean=False)] for token in self.tokens]
                    # Then run MorphoSyns on analyses to collapse syntax into morphology where relevant for target
            if verbosity:
                print("Running Morphosyns for {} on {}".format(self.language, self))
#            print("Toks: {}".format(self.toks))
            for mi, ms in enumerate(self.language.ms):
                # If ms applies and is "ambiguous", create a new copy of the sentence and add to altsyns
                # (this happens in MorphoSyn)
                if ms.apply(self, ambig=ambig, verbosity=verbosity, terse=terse):
                    scopy = self.altsyns[-1]
                    if verbosity or not terse:
                        print("{} copied sentence: {}".format(ms, scopy))
                    # Attempt to apply succeeding morphosyns to copy if there is one
                    for ms1 in self.language.ms[mi+1:]:
                        ms1.apply(scopy, ambig=ambig, verbosity=verbosity, terse=terse)

    def morph_anal(self):
        """Morphological analysis of the tokens in the sentence."""
        analyses = []
        for tok in self.toks:
            tokstring = tok.fullname
            if tok.special or tok.punc or not tokstring:
                # Don't bother to analyze it
                analyses.append([tokstring, [{'root': tokstring, 'features': ''}]])
            else:
                analyses.append([tokstring, self.language.anal_word(tokstring, clean=False)])
        return analyses

    def merge_POS(self, tagged, analyzed, verbosity=0):
        """Merge the output of an external tagger and the L3Morpho analyzer. Use the tagger to
        disambiguate analyses, preferring the analysis if there's only one."""
        if verbosity:
            print("Merging tagger and analyzer results for {}".format(self))
        results = []
        for (word, tag), (token, anals) in zip(tagged, analyzed):
            if verbosity:
                print("  word {}, tag {}, token {}, anals {}".format(word, tag, token, anals))
            results1 = []
            for aindex, anal in enumerate(anals):
                anal_pos = None
                features = anal.get('features')
                if features:
                    anal_pos = features.get('pos')
                if verbosity:
                    print("  tagger tag {}, analyzer tag {}".format(tag, anal_pos))
                if anal_pos and tag:
                    if anal_pos == tag or self.language.postag_match(tag, anal_pos):
                        if verbosity:
                            print("  tagger and analyzer agree on {} for {}".format(tag, anal))
                        results1.append(anal)
                    else:
                        if len(anals) == 1:
                            if verbosity:
                                print("  tagger and analyzer disagree on {}/{} for {}".format(tag, anal_pos, anal))
                                print("   only 1 analysis, so accepting it")
                            results1.append(anal)
                        elif aindex == 0:
                            if verbosity:
                                print("  tagger and analyzer disagree on {}/{} for {}".format(tag, anal_pos, anal))
                            root = anal.get('root')
                            if root in self.language.exceptions:
                                if verbosity:
                                    print("  root {} is in exceptions, so using morphology".format(root))
                                results1.append(anal)
                            else:
                                if verbosity:
                                    print("    rejecting {}".format(anal))
                        else:
                            if verbosity:
                                print("  rejecting non-preferred analysis {} by analyzer for {}".format(anal_pos, word))
                elif tag:
                    if verbosity:
                        print("  no features for {}, using tagger POS {}".format(word, tag))
                    anal['pos'] = tag
                    tag1 = tag.split('.')[0]
#                    print("Adding pos {} to anal {} root {} to {}".format(tag1, anal, anal.get('root'))
                    anal['root'] = anal['root'] + '_' + tag1
                    results1.append(anal)
                elif anal_pos:
                    if verbosity:
                        print("  no tagger tag, using analyzer POS {}".format(anal_pos))
                    results1.append(anal)
                else:
                    if verbosity:
                        print("  neither tagger nor analyzer provide tag for {}".format(word))
                    results1.append(anal)
            results.append([token, results1])
        return results

    def nodify(self, incl_del=False, verbosity=0):
        """Create nodes for sentence.
        2015.10.17: Split off from tokenize().
        2019.05.25: Added Token instances.
        """
        self.nodes = []
        index = 0
        del_indices = {}
        toktype = 1
        tokobjs = []
        for tokindex, (tokobj, rawtok, (token, anals)) in enumerate(zip(self.toks, self.tokens, self.analyses)):
            if self.toktypes:
                toktype = self.toktypes[tokindex]
            tokobjs.append(tokobj)
            if not incl_del and Token.del_token(token):
                # Ignore elements deleted by MorphoSyns
                if anals and 'target' in anals[0]:
                    target_index = tokindex + anals[0]['target']
                else:
                    # Find the next element that's not deleted; that's the target
                    dist = 1
                    for tok, an in self.analyses[tokindex + 1:]:
                        if not Token.del_token(tok):
                            break
                        else:
                            dist += 1
                    target_index = tokindex + dist
                if target_index in del_indices:
                    del_indices[target_index].append(tokindex)
                else:
                    del_indices[target_index] = [tokindex]
                continue
            if anals:
                # Multiple dicts: ambiguity; let node handle it
                # Get cats
                # FIX THIS LATER; ONLY ONE ANAL SHOULD BE POSSIBLE
                if not isinstance(anals, list):
                    anals = [anals]
                for anal in anals:
                    root = anal['root']   # there has to be one of these
                    cats = self.language.get_cats(root)
#                    print("Cats for {}: {}".format(root, cats))
                    if cats:
                        anal['cats'] = cats
                    features = anal['features']
                    pos = ''
                    if features:
                        if isinstance(features, FSSet):
                            pos = list(features)[0].get('pos')
                        elif isinstance(features, FeatStruct):
                            pos = features.get('pos')
                    if pos:
                        anal['pos'] = pos
                raw_indices = del_indices.get(tokindex, [])
                raw_indices.append(tokindex)
                self.nodes.append(SNode(token, index, anals, self, raw_indices, toks=tokobjs, tok=tokobj, rawtoken=rawtok, toktype=toktype))
                tokobjs = []
                index += 1
            else:
                # No analysis, just use the raw string
                # First check for categories
                cats = self.language.get_cats(token)
                if cats:
                    anals = [{'cats': cats}]
                elif token.istitle():
                    # If token is capitalized, it's a name.
                    anals = [{'cats': ['$nm']}]
                else:
                    anals = None
                self.nodes.append(SNode(token, index, anals, self, [tokindex], rawtoken=rawtok, tok=tokobj, toktype=toktype))
                tokobjs = []
                incorp_indices = []
                index += 1

    def split(self):
        """Split the raw sentence into words, separating off punctuation."""

    def add_anal_to_keys(self, anal, keys):
        """Add parts of an analyses to the set of keys for looking up groups."""
        root = anal.get('root')
        if root:
            if root not in keys:
                keys.add(root)
            if '|' in root:
                # An ambiguous root (ir|ser)
                psuf = ''
                r = root
                if '_' in root:
                    r, psuf = root.split('_')
                    psuf = '_' + psuf
                for rr in r.split('|'):
                    keys.add(rr + psuf)
        pos = anal.get('pos')
        if pos and '_' not in root:
            k = root + '_' + pos
            if k not in keys:
                keys.add(k)

    def lexicalize(self, verbosity=0, terse=True):
        """Find and instantiate all groups that are compatible with the tokens in the sentence."""
        if verbosity:
            print("Lexicalizing {}, terse={}".format(self, terse))
        if not self.nodes:
            print("Tokenization must precede lexicalization.")
            return
        candidates = []
        for index, node in enumerate(self.nodes):
            # Get keys into lexicon for this node
            keys = node.tok.get_keys(index)
#            keys = {node.token}
#            if node.rawtoken:
#                keys.add(node.rawtoken)
#            if index == 0:
#                # For first word in sentence, try both capitalized an uncapitalized versions.
#                keys.add(node.token.capitalize())
#            print("Keys for {}: {}".format(node, keys))
            # Add root key
            anals = node.analyses
            if anals:
                if not isinstance(anals, list):
                    # Is this still possible?
                    anals = [anals]
                for a in anals:
                    self.add_anal_to_keys(a, keys)
            # Look up candidate groups in lexicon
            # Use simple (lexical) groups
#            # Use group groupings specified in constrain_groups (False or a list of ints) or
#            # all groupings
#            groups2 = self.language.groups
            groups = self.language.groups[0]
#            groupgroups = [groups2[0]] if constrain_groups else groups2
#            print("Keys for group search {}".format(keys))
            for k in keys:
#                for groups in groupgroups:
                if k in groups:
                    # All the groups with key k
                    for group in groups[k]:
                        # Reject group if it doesn't have a translation in the target language
                        if self.target and not group.get_translations():
                            print("No translation for {}".format(group))
                            continue
                        candidates.append((node.index, k, group))
                        node.group_cands.append(group)
#        print("Candidates {}".format(candidates))
        # Now filter candidates to see if all words are present in the sentence.
        # For each group, save a list of sentence token indices that correspond
        # to the group's words
        matched_keys = []
        group_index = 0
        # Initially filtered
        filtered1 = []
        # Candidate groups with categories
        cat_groups = []
        # Rejected category groups
        rejected = []
        # Keep track of unambiguous groups associated with source ambiguous groups already included
        # so they can be avoided
        sambig_assocs = []
        for head_i, key, group in candidates:
            # Check whether there is already a match for this position, key, and group length
            # LATER HAVE A BETTER WAY OF CHOOSING A MATCH
            if verbosity > 1 or group.debug:
                print("Checking candidate {} with head {} and key {}".format(group, head_i, key))
            matched_key = (head_i, key, len(group.tokens), group.get_nfeatures)
            if matched_key in matched_keys:
                # Reject this match because there's already a comparable one
                if verbosity > 1 or group.debug:
                    print("{} rejected because {} already found".format(group, matched_key))
                continue
            # Matching snodes, along with root and unified features if any
            if verbosity > 1 or group.debug:
                print("Matching group {}".format(group))
            snodes = group.match_nodes(self.nodes, head_i, verbosity=verbosity)
            if not snodes:
                # This group is out
                if verbosity > 1 or group.debug:
                    print("Group {} failed to match".format(group))
                continue
            matched_keys.append(matched_key)
            if verbosity > 1 or group.debug:
                print('Group {} matches snodes {}'.format(group, snodes))
            # Find snodes that would be category nodes within this group
            cat_i = group.get_cat_indices()
            if cat_i:
                # Groups with category nodes
                cat_snodes = [snodes[i][0][0] for i in cat_i]
                cat_groups.append((group, cat_snodes))
            # All candidate groups
            filtered1.append((group, head_i, snodes))
            # If the new filtered group is source ambiguous (like ir|ser_v), add
            # associated unambiguous groups to sambig_assocs.
            if group.is_sambig():
                sambig_assocs1 = self.language.sambig_groups[group]
                sambig_assocs.extend(sambig_assocs1)
        if cat_groups:
            for cat_group, cat_snodes in cat_groups:
                for cat_snode in cat_snodes:
                    cat_match = firsttrue(lambda c: c[1] == cat_snode, filtered1)
                    if not cat_match:
                        rejected.append(cat_group)
                        break
        for (group, head_i, snodes) in filtered1:
            if group in rejected or group in sambig_assocs:
                # This group was rejected because there was no match for its category token(s)
                # or it was an unambigous associate of a source ambiguous group
                continue
            # Create a GInst object and GNodes for each surviving group
            self.groups.append(GInst(group, self, head_i, snodes, group_index))
            group_index += 1
        if not terse or verbosity:
            print("{} grupo(s) encontrado(s) para {}".format(len(self.groups), self))
            for g in self.groups:
                print("  {}".format(g))
        # Assign sentence-level indices to each GNode; store gnodes in list
        sent_index = 0
        for group in self.groups:
            for gnode in group.nodes:
                gnode.sent_index = sent_index
                self.gnodes.append(gnode)
                sent_index += 1
        # Number of GNodes
        self.ngnodes = sent_index
        # Record uncovered snodes
        covered = {}
        for gnode in self.gnodes:
            si = gnode.snode_indices
            for i in si:
                if i not in covered:
                    covered[i] = []
                covered[i].append(gnode.sent_index)
        for snode in self.nodes:
            gnodes = covered.get(snode.index, [])
            snode.gnodes = gnodes
            if gnodes:
                self.covered_indices.append(snode.index)
        self.get_group_dependencies()
        self.get_group_sindices()
        self.get_group_conflicts()
        self.get_incompat_groups()

    def get_group_sindices(self):
        """Set the possible snode indices for each GInst, grouping them according to whether
        they're lexical or category nodes."""
        for gnode in self.gnodes:
            ginst = gnode.ginst
            si = gnode.snode_indices
            if gnode.cat:
                ginst.sindices[1].extend(si)
            else:
                ginst.sindices[0].extend(si)

    def get_incompat_groups(self):
        """Find pairs of groups that are incompatible because of a "merger loop": one SNode with an associated
        cat GNode in group A and lex node in group B and another SNode with the reverse."""
        for i1, ginst1 in enumerate(self.groups[:-1]):
            lex_sn1, cat_sn1 = ginst1.sindices
            for ginst2 in self.groups[i1:]:
                lex_sn2, cat_sn2 = ginst2.sindices
                if any([ls1 in cat_sn2 for ls1 in lex_sn1]) and any([ls2 in cat_sn1 for ls2 in lex_sn2]):
                    self.incompat_groups.append((ginst1, ginst2))

    def get_group_conflicts(self):
        """Find group conflicts, lists of GInst indices, only one of which can be part of a segmentation."""
        s2g = {}
        for ginst in self.groups:
            slexi = ginst.sindices[0]
            gi = ginst.index
            for si in slexi:
                if si in s2g:
                    s2g[si].append(gi)
                else:
                    s2g[si] = [gi]
        self.group_conflicts = [g for g in s2g.values() if len(g) > 1]

    def get_group_dependencies(self):
        """After GInsts and GNodes are created, check to see which GInsts with cat nodes depend on
        other GInsts."""
        dependencies = {}
        for gnode1 in self.gnodes:
            if not gnode1.cat:
                continue
            # gnode1 is a cat node, so it has to have another gnode to merge with
            ginst1 = gnode1.ginst
            anal1 = gnode1.snode_anal
            sindices1 = gnode1.snode_indices
            for gnode2 in self.gnodes:
                if gnode2 == gnode1 or gnode2.cat:
                    continue
                anal2 = gnode2.snode_anal
                sindices2 = gnode2.snode_indices
                if any([(s2 in sindices1) for s2 in sindices2]) and \
                  any([(a2 in anal1) for a2 in anal2]):
                  # gnode1 and gnode2 have the same snode index, root, and features
                    ginst2 = gnode2.ginst
                    if ginst1 in dependencies:
                        dependencies[ginst1].append(ginst2)
                    else:
                        dependencies[ginst1] = [ginst2]
        # Convert the dependencies dict to a list of pairs, one for each ginst
        for ginst in self.groups:
            if ginst in dependencies:
                ginst.dependencies = {g.index for g in dependencies[ginst]}

    ## Solving: translation and potentially also parsing
    ## As of 2018.12, "solutions" are really initial "segmentations".

    def solve(self, translate=True, all_sols=False, all_trans=True, interactive=False,
              limit_trans=True, max_sols=0, verbosity=0, tracevar=None, terse=True):
        """Generate segmentations, for all analyses if all_sols is True and translations (if translate is True)."""
        if not terse:
            print("RESOLVIENDO oración principal {}".format(self))
        self.solve1(translate=translate, all_sols=all_sols, all_trans=all_trans, interactive=interactive,
                    limit_trans=limit_trans, max_sols=max_sols, verbosity=verbosity, tracevar=tracevar, terse=terse)
        if all_sols or (len(self.segmentations) < max_sols):
            for s in self.altsyns:
                if not terse:
                    print("RESOLVIENDO oración alternativa {}".format(s))
                s.solve1(translate=translate, all_sols=all_sols, all_trans=all_trans, interactive=interactive,
                         limit_trans=limit_trans, max_sols=max_sols, verbosity=verbosity, tracevar=tracevar,
                         terse=terse)
    
    def solve1(self, translate=True, all_sols=False, all_trans=True, interactive=False,
               limit_trans=True, max_sols=0, verbosity=0, tracevar=None, terse=True):
        """Generate segmentations and translations (if translate is true)."""
        if not self.groups:
            if not terse or verbosity:
                print("NINGUNOS GRUPOS encontrados para {}, así que NO HAY SEGMENTACIÓN POSIBLE".format(self))
            return
        if not terse or verbosity:
            print(" Resolviendo {}".format(self))
        ds = None
        generator = self.solver.generator(test_verbosity=verbosity, expand_verbosity=verbosity,
                                          tracevar=tracevar)
        try:
            proceed = True
            while proceed:
                succeeding_state = next(generator)
                ds = succeeding_state.dstore
                segmentation = self.create_segmentation(dstore=ds, verbosity=verbosity)
                if translate and self.target:
                    # Translating
                    translated = segmentation.translate(verbosity=verbosity, limit_trans=limit_trans,
                                                        all_trans=all_trans, interactive=interactive)
                    if not translated:
                        if not terse:
                            print("Translation failed; trying next segmentation!")
                        continue
                    else:
                        # Store the translation segmentation
                        self.segmentations.append(segmentation)
                else:
                    # Parsing; store the segmentation and display the parse
                    self.segmentations.append(segmentation)
                    if not terse:
                        self.display(show_all_sols=False)
                if max_sols and len(self.segmentations) >= max_sols:
                    proceed = False
                if all_sols:
                    continue
                if not interactive or not input('SEARCH FOR ANOTHER ANALYSIS? [yes/NO] '):
                    proceed = False
        except StopIteration:
            if verbosity:
                print('No more segmentations')
        if not self.segmentations:
            if not terse or verbosity:
                print("Last DS: {}".format(ds))
                print("NINGUNAS SEGMENTACIONES encontradas para {}".format(self))

    def translate(self, sol_index=-1, all_trans=False, limit_trans=True, verbosity=0):
        """Translate the segmentation with sol_index or all segmentations if index is negative."""
        segmentations = self.segmentations if sol_index < 0 else [self.segmentations[sol_index]]
        for segmentation in segmentations:
            segmentation.translate(all_trans=all_trans, limit_trans=limit_trans, verbosity=verbosity)

    ## Create IVars and (set) Vars with sentence DS as root DS

    def ivar(self, name, domain, ess=False):
        self.variables[name] = IVar(name, domain, rootDS=self.dstore,
                                    essential=ess)

    def svar(self, name, lower, upper, lower_card=0, upper_card=MAX,
             ess=False):
        self.variables[name] = Var(name, lower, upper, lower_card, upper_card,
                                  essential=ess, rootDS=self.dstore)

    def create_variables(self, verbosity=0):
        # All abstract (category) and instance (word or lexeme) gnodes
        catnodes = set()
        instnodes = set()
        for group in self.groups:
            for node in group.nodes:
                if node.cat:
                    catnodes.add(node.sent_index)
                else:
                    instnodes.add(node.sent_index)

        self.svar('groups', set(), set(range(len(self.groups))),
                  # At least 1, at most all groups
                  1, len(self.groups),
                  ess=True)
        self.svar('gnodes', set(), set(range(self.ngnodes)),
                  # At least size of smallest group, at most all
                  min([len(g.nodes) for g in self.groups]),
                  self.ngnodes)
        # covered snodes
        covered_snodes = {sn.index for sn in self.nodes if sn.gnodes}
        self.variables['snodes'] = DetVar('snodes', covered_snodes)
        # Category (abstract) nodes
        self.svar('catgnodes', set(), catnodes)
        # Position pairs
        pos_pairs = set()
        for group in self.groups:
            pos_pairs.update(group.pos_pairs())
        self.svar('gnode_pos', set(), pos_pairs)
        ## Create variables for SNodes, GInsts, and GNodes
        for snode in self.nodes:
            snode.create_variables()
        for ginst in self.groups:
            ginst.create_variables()
        for gnode in self.gnodes:
            gnode.create_variables()
        self.svar('covered_snodes', set(), covered_snodes, 1, len(covered_snodes), ess=True)

    def create_constraints(self, verbosity=0):
        if verbosity > 1:
            print("Creating constraints for {}".format(self))

        groupvar = self.variables['groups']

        # Covered nodes are the union of the snodes associated with all of the groups that succeed.
        self.constraints.append(UnionSelection(self.variables['covered_snodes'],
                                               groupvar,
                                               [g.variables['gnodes_pos'] for g in self.groups]))

        # Dependencies among GInsts
        gdeps = [g.variables['deps'] for g in self.groups]
        self.constraints.append(DependencySelection(selvar=groupvar, depvars=gdeps))
        # If there are inconsistent groups, create a NAND constraint for each pair
        for g1, g2 in self.incompat_groups:
            self.constraints.append(NAND(groupvar, g1.index, g2.index))
        # Relation among abstract, concrete, and all gnodes for each snode
        # For each of the covered snodes, the associated gnodes are the union of the cgnodes and agnodes
        snodes_union_sel = [DetVar("nU2", {2*pos, 2*pos+1}) for pos in range(len(self.nodes))]
#        print("SNodes union selection: {}".format(snodes_union_sel))
        node_apos_cpos_vars = []
        for node in self.nodes:
            node_apos_cpos_vars.extend([node.variables['cgnodes'], node.variables['agnodes']])
        snode_ac_union_constraint = ComplexUnionSelection(selvar=self.variables['covered_snodes'],
                                                          selvars=snodes_union_sel,
                                                          seqvars=node_apos_cpos_vars,
                                                          mainvars=[node.variables['gnodes'] for node in self.nodes])
        self.constraints.append(snode_ac_union_constraint)
        # Constraints involving groups with category (abstract) nodes
        # For each group that succeeds, the set of snodes ('gnodes_pos') is the union of the concrete and abstract nodes
        group_union_sel= [DetVar("gU2", {2*pos, 2*pos+1}) for pos in range(len(self.groups))]
        apos_cpos_vars = []
        for group in self.groups:
            apos_cpos_vars.extend([group.variables['agnodes_pos'], group.variables['cgnodes_pos']])
        group_ac_union_constraint = ComplexUnionSelection(selvar=groupvar,
                                                          selvars=group_union_sel,
                                                          seqvars=apos_cpos_vars,
                                                          mainvars=[group.variables['gnodes_pos'] for group in self.groups])
        self.constraints.append(group_ac_union_constraint)
        # The set of category (abstract) nodes used is the union of the category nodes of the groups used
        # ('agnodes' for each group)
        self.constraints.append(UnionSelection(self.variables['catgnodes'],
                                               groupvar,
                                               [g.variables['agnodes'] for g in self.groups]))
        # All snodes must have distinct category nodes ('agnodes' for each snode)
        self.constraints.extend(Disjoint([sn.variables['agnodes'] for sn in self.nodes]).constraints)
        # All position constraints for snodes
        # 'gnode_pos' specifies pairs of snode positional constraints; applied over 'snodes' for each gnode
        self.constraints.append(PrecedenceSelection(self.variables['gnode_pos'],
                                                    [gn.variables['snodes'] for gn in self.gnodes]))
        # Gnode position constraint pairs ('gnode_pos') are the gnode position pairs ('g*pos') for all groups used
        self.constraints.append(UnionSelection(self.variables['gnode_pos'],
                                               groupvar,
                                               [DetVar("g{}pos".format(g.index), g.pos_pairs()) for g in self.groups]))
        # Union selection on gnodes for each snode:
        #  the union of the snode indices ('snodes') associated with the gnodes of an snode is the snode's index
        #  ('sn*'). But this should only hold for covered snodes, so it's a complex selection constraint.
        gn2s = [gn.variables['snodes'] for gn in self.gnodes]
        s2gn = [s.variables['gnodes'] for s in self.nodes]
        snode_mainvars = [DetVar("sn{}".format(snode.index), {snode.index}) for snode in self.nodes]
        snode_gnode_union_constraint = ComplexUnionSelection(selvar=self.variables['covered_snodes'],
                                                             selvars=s2gn, seqvars=gn2s,
                                                             mainvars=snode_mainvars)
        self.constraints.append(snode_gnode_union_constraint)
        # Union of all gnodes used snodes is all gnodes used
        self.constraints.append(UnionSelection(self.variables['gnodes'], self.variables['snodes'], s2gn))
        # Union of all gnodes for groups used is all gnodes used
        self.constraints.append(UnionSelection(self.variables['gnodes'],
                                               groupvar,
                                               [g.variables['gnodes'] for g in self.groups]))
        # Union of all covered snodes for gnodes used is all snodes
        self.constraints.append(UnionSelection(self.variables['covered_snodes'], self.variables['gnodes'],
                                               [gn.variables['snodes'] for gn in self.gnodes]))
        # Complex union selection by groups on positions of all concrete gnodes in each selected group
        self.constraints.append(ComplexUnionSelection(selvar=groupvar,
                                                      selvars=[g.variables['cgnodes_pos'] for g in self.groups],
                                                      seqvars=[s.variables['cgnodes'] for s in self.nodes],
                                                      mainvars=[g.variables['cgnodes'] for g in self.groups]))
        # Complex union selection by groups on positions of all category gnodes in each selected group
        self.constraints.append(ComplexUnionSelection(selvar=groupvar,
                                                      selvars=[g.variables['agnodes_pos'] for g in self.groups],
                                                      seqvars=[s.variables['agnodes'] for s in self.nodes],
                                                      mainvars=[g.variables['agnodes'] for g in self.groups]))
        ## Agreement
        if any([g.variables.get('agr') for g in self.groups]):
            # If any groups have an 'agr' variable...
            self.constraints.append(ComplexAgrSelection(selvar=groupvar,
                                                        seqvars=[gn.variables['snodes'] for gn in self.gnodes],
                                                        featvars=[sn.variables['features'] for sn in self.nodes],
                                                        selvars=[g.variables.get('agr', EMPTY) for g in self.groups]))

    @staticmethod
    def update_tree(group_dict, group_i, tree, depth=0):
        """Update a tree (a set of snode indices) for the group with index group_i
        by searching for merged groups and their trees in group_dict."""
        if depth > 3:
            print("Infinite loop!")
            return
        if not group_dict[group_i][1]:
            # Nothing to merge for this group
            return
        else:
            for mgi in group_dict[group_i][1]:
                # Group indices for merger. Add the snode indices for each
                # merged group to the tree (set).
                tree.update(group_dict[mgi][0])
                if mgi == group_i:
                    print("Error in making tree, group_dict: {}".format(group_dict))
                    return
                Sentence.update_tree(group_dict, mgi, tree, depth=depth+1)

    ## Methods to constrain search

    def state_eval(self, dstore, var_value, par_val, verbosity=0):
        """Assign a score to the domain store based on how many snodes are covered and how large groups are.
        Changed 2015.09.24, adding second constraint and eliminating number of undetermined esssential variables.
        Changed 2016.07.13 to using groups and snodes to figure score, independent of the variable selected,
        only sn->gn variables if one is selected.
        Changed again massively 2018.02.20-22. Based on number of gnodes in determined (lower bound) groups greater than 1.
        Variables are independent in determining score: change in variable value is added or subtracted to
        previous (parent) score; that is, there are no interactions among the variables in determining the score.
        If parent value and variable/value are given, just update on the basis of the variable.
        2018.12.25: Added preference for groups with longer head names (e.g., mbo'ehára over mbo'e). Normalization
        factor (.04) is totally arbitary.
        """
        score = 0.0
        if par_val and var_value:
            if verbosity:
                print("Evaluating dstore {} from parent {} and var/val {}".format(dstore, par_val, var_value))
            # Don't calculate the whole score; just update the parent's score on the basis of the variable and value
            # (this is done for the ...a branch in distribution).
            score = par_val
            variable, value = var_value
            typ = Sentence.get_var_type(variable)
            if typ == 'groups':
                # Subtract the number of gnodes in the group that is the single member of the value set
                group = self.groups[list(value)[0]]
                score -= (group.ngnodes - 1) / 2.0
                # Prefer groups with longer heads
                head_length = len(group.head.gtoken)/25.0
                score -= head_length
            elif typ == 'covered_snodes':
                score -= 1
            elif typ == 'sn->gn':
                # sn->gn variable value selected represents a cat gnode that is to be merged with
                # a concrete node in another group
                if value:
                    score -= 0.5
            else:
                print("Something wrong: state eval variable {} is not of an acceptable type".format(variable))
            score = round(score, 4)
            if verbosity:
                print("  Score: {}".format(score))
            return score
        # Otherwise calculate the whole value, based on three types of variables
        # Essential undetermined variables
        undet = dstore.ess_undet
        gnodes = 0
        nnodes = len(self.nodes)
        if verbosity:
            print("Evaluating dstore {}; undet: {}, var/value {}, parent val {}".format(dstore, undet, var_value, par_val))
        ## $groups
        # lower bound of $groups variable for sentence
        gl = self.variables['groups'].get_lower(dstore)
        # Number of gnodes for each group in $groups lower bound
        gllengths = [self.groups[g].ngnodes for g in gl]
        glbonus = sum([max(0, n-1) for n in gllengths]) / 2.0
        ## $s2g variables for sentence nodes
        s2gl = [v.get_lower(dstore) for v in [node.variables.get('gnodes') for node in self.nodes]]
        s2glbonus = sum([(1 if len(s) == 2 else 0) for s in s2gl]) / 2.0
        # $covered_snodes
        cl = self.variables['covered_snodes'].get_lower(dstore)
        cslower = len(cl)
        csscore = nnodes - cslower
        if verbosity:
            print("  Uncovered nodes {}, groups {}, s2g {}".format(csscore, glbonus, s2glbonus))
        score = csscore - glbonus - s2glbonus
        # Tie breaker
        score += random.random() / 100.0
        score = round(score, 4)
        if verbosity:
            print("  Score: {}".format(score))
        return score

    @staticmethod
    def get_var_type(variable):
        name = variable.name
        if 'groups' in name:
            return 'groups'
        if '->gn' in name:
            return 'sn->gn'
        if 'covered' in name:
            return 'covered_snodes'
        return None

    def select_varval(self, undecvars, dstore):
        """Given a list of undecided essential variables and dstore, select
        a variable and two complementary values to distribute on."""
#        conflicts = self.get_group_varval(undecvars, dstore)
#        print("Group undet conflicts: {}".format(conflicts))
#        return self.get_s2g_varval(undecvars, dstore)
        # Use the 'groups' variable if there are group conflicts
        group_varval = self.get_group_varval(undecvars, dstore)
        if group_varval:
            return group_varval
        else:
            # Otherwwise use the 'covered_snodes' variable if it's undetermined
            snode_varval = self.get_snodes_varval(undecvars, dstore)
            if snode_varval:
                return snode_varval
        # Otherwise choose an snode->gnode variable
        return self.get_s2g_varval(undecvars, dstore)

    def get_snodes_varval(self, undecvars, dstore, verbosity=0):
        """Pick a undecided value for the 'covered_nodes' variable and its complement
        among undecided values. Prefer 'shared' snodes, those with potentially a lexical
        and a category gnode."""
        covered = self.variables['covered_snodes']
        if verbosity:
            covered.pprint(dstore=dstore, spaces=2)
        cundec = covered.get_undecided(dstore)
        if not cundec:
            return
        if verbosity:
            print("  Selecting from undecided snodes: {}".format(cundec))
        for sn in cundec:
            snode = self.nodes[sn]
            s2g = snode.variables['gnodes']
            s2gup = s2g.get_upper(dstore)
            gnodes = [self.gnodes[gn] for gn in s2gup]
            if verbosity:
                print("  Gnodes for {}: {}".format(sn, gnodes))
            if any([gn.cat for gn in gnodes]):
                # This possibly covered snode may be a shared node
                val = {sn}
                if verbosity:
                    print("  SELECTED snode {} with possible gnodes {}".format(sn, gnodes))
                return covered, val, cundec - val
        # No possible shared snodes found, just use the last one found
        val = {sn}
        if verbosity:
            print("  SELECTED random snode {}".format(sn))
        return covered, val, cundec - val
            
    def get_group_varval(self, undecvars, dstore):
        """Select a value for the $groups variable."""
        groups = self.variables['groups']
        gundec = groups.get_undecided(dstore)
        if not gundec or not self.group_conflicts:
            return
        conflicts = []
        # index of group and number of nodes
        biggest = (0, 0)
        for conflict in self.group_conflicts:
            # A list of conflicting group indices that are between
            # upper and lower bounds
            conflict1 = [g for g in conflict if g in gundec]
            # If there's more than one, add the list to conflicts
            if len(conflict1) > 1:
                conflicts.append(conflict1)
        if conflicts:
            for conflict in conflicts:
                for conflict1 in conflict:
                    group = self.groups[conflict1]
                    # 2018.7.10: Fixed this so it favors concrete over abstact tokens (nodes)
                    gn = group.ncgnodes + group.nanodes / 2.0
                    if gn > biggest[1]:
                        biggest = (conflict1, gn)
            val = {biggest[0]}
            # Return the $groups variable, the promising value, and
            # the remaining uncertain values with the promising value removed
            return groups, val, gundec - val
        return

    def get_s2g_varval(self, undecvars, dstore):
        """Given a set of undecided variables in a domain store, find a snode->gnode variable
        that has at last one value that is part of a group with more than one node and
        at least one other value that is part of a group with only one node. Use this
        to select variable and values in search (distribution).
        """
        variables = [node.variables.get('gnodes') for node in self.nodes]
        # Variable whose possible values are tuples of gnodes for individual groups
        gn_pos = self.variables['gnode_pos']
        if gn_pos:
            gn_pairs = gn_pos.get_upper(dstore=dstore)
            for var in variables:
                if var not in undecvars:
                    continue
                # gnode indices that are in pairs or not in pairs
                inpair = []
                notinpair = []
                varundec = var.get_undecided(dstore=dstore)
                for value in varundec:
                    if any([value in pair for pair in gn_pairs]):
                        inpair.append(value)
                    else:
                        notinpair.append(value)
                if inpair and notinpair:
                    prefval = inpair[0]
                    return var, {prefval}, varundec - {prefval}

    def create_segmentation(self, dstore=None, verbosity=0):
        """Assuming essential variables are determined in a domain store, make a Segmentation object.
        Adds segmentation to self.segmentations and also returns the segmentation."""
        dstore = dstore or self.dstore
        # Get the indices of the selected groups
        groups = self.variables['groups'].get_value(dstore=dstore)
        groupindices = list(groups)
        groupindices.sort()
        covered_snodes = self.variables['covered_snodes'].get_value(dstore=dstore)
        ginsts = [self.groups[g] for g in groupindices]
        s2gnodes = []
        # For each snode, find which gnodes are associated with it in this dstore. This becomes the value of
        # the s2gnodes field in the segmentation created.
        for node in self.nodes:
            if node.index in covered_snodes:
                gnodes = list(node.variables['gnodes'].get_value(dstore=dstore))
            else:
                gnodes = []
            s2gnodes.append(gnodes)
#        if verbosity:
#        print("groups for {}: {}".format(self, groups))
        ncovered = len(covered_snodes)
        nuncovered = len(self.nodes) - ncovered
        ngroups = len(ginsts)
        score = ngroups + nuncovered
#        print("  ginsts: {}".format(ginsts))
#          if verbosity:
        # Create trees for each group
        tree_attribs = {}
        for snindex, sg in enumerate(s2gnodes):
            for gn in sg:
                gnode = self.gnodes[gn]
                gn_group = gnode.ginst.index
                if gn_group not in tree_attribs:
                    tree_attribs[gn_group] = [[], []]
                tree_attribs[gn_group][0].append(snindex)
            if len(sg) == 2:
                # Record group merger when an snode is associated with two gnodes
                gn0, gn1 = self.gnodes[sg[0]], self.gnodes[sg[1]]
                group0, group1 = gn0.ginst.index, gn1.ginst.index
                if gn0.cat:
                    # Group for gnode0 is merged with group for gnode1
                    tree_attribs[group0][1].append(group1)
                else:
                    tree_attribs[group1][1].append(group0)
        for gindex, sn in tree_attribs.items():
            # First store the group's own tree as a set of sn indices and
            # the third element of sn
            sn.append(set(sn[0]))
            # Next check for mergers
            Sentence.update_tree(tree_attribs, gindex, sn[2])
        # Convert the dict to a list and sort by group indices
        trees = list(tree_attribs.items())
        trees.sort(key=lambda x: x[0])
        # Just keep the snode indices in each tree
        trees = [x[1][2] for x in trees]
        # Get the indices of the GNodes for each SNode
        segmentation = Segmentation(self, ginsts, s2gnodes, len(self.segmentations),
                                    trees=trees, dstore=dstore, session=self.session,
                                    score=score)
        print('FOUND SEGMENTATION {} for {}'.format(segmentation, self))
#        print("  score: # groups {}, # uncovered {}".format(ngroups, nuncovered))
        return segmentation

    def get_all_segmentations(self, translate=True, generate=True,
                              connect=False, html=False, verbosity=0):
        """After a sentence has been translated and segmented, collect all the
        segmentations, including those resulting from altsyn sentences."""
        segmentations = []
        if self.segmentations:
            segmentations.extend(self.segmentations)
        if self.altsyns:
            for sa in self.altsyns:
                if sa.segmentations:
                    segmentations.extend(sa.segmentations)
        if segmentations:
            Segmentation.rank(segmentations)
            if connect:
                # Match joins and further groups only for best segmentation
                segmentations = segmentations[:1]
            if translate:
                for seg in segmentations:
                    seg.get_segs(html=False, single=True)
                    if connect:
                        # Search for Segment matches with Join and Group instances
                        # and connect Segments if found
                        seg.connect(generate=False, verbosity=verbosity)
                    if generate:
                        # Realize target morphology
                        seg.generate()
                        if html:
                            # Generate the HTML for the GUI
                            seg.seg_html(single=True)
            for sindex, segmentation in enumerate(segmentations):
                print("SEGMENTACIÓN {}".format(sindex))
                for segment in segmentation.segments:
                    print("{}: {}".format(segment, segment.cleaned_trans))
            return segmentations

    ### Various ways of displaying translation outputs.
    
    def set_trans_outputs(self):
        """Combine the tree trans outputs from all segmentations, excluding repeated ones."""
        if not self.segmentations:
            return
        for segmentation in self.segmentations:
            t1 = segmentation.get_ttrans_outputs()
            for tt1 in t1:
                if tt1 not in self.trans_outputs:
                    self.trans_outputs.append(tt1)
        self.trans_outputs.sort()

    def get_complete_trans(self, capfirst=True):
        """Produce complete translations (list of lists of strings) from tree trans outputs for segmentations, filling
        in gaps with source words where necessary."""
        if self.complete_trans:
            return self.complete_trans
        trans = []
        for segmentation in self.segmentations:
            tt = segmentation.get_ttrans_outputs()
            tt_complete = []
            end_index = -1
            for indices, forms, x, y in tt:
                start, end = indices[0], indices[-1]
                if start > end_index+1:
                    # Some word(s) not translated; use source forms with # prefix
                    verbatim = [self.verbatim(n) for n in self.nodes[end_index+1:start]]
                    tt_complete.append([' '.join(verbatim)])
#                    tt_complete.append([self.verbatim(n) for n in self.nodes[end_index+1:start]])
                tt_complete.append(forms)
                end_index = end
            if end_index+1 < len(self.nodes):
                # Some word(s) not translated; use source forms with # prefix
                verbatim = [self.verbatim(n) for n in self.nodes[end_index+1:len(self.nodes)]]
                tt_complete.append([' '.join(verbatim)])
            if capfirst:
                # Capitalize first word
                tt_complete[0] = [Sentence.capitalize(w) for w in tt_complete[0]]
            trans.append(tt_complete)
        self.complete_trans = trans
        return trans

    def get_html(self, single=False):
        """Create HTML for a sentence with no segmentation."""
        tokens = ' '.join(self.tokens)
        tokens = Segment.clean_spec(tokens)
        if single:
            # Create button
            trans_html = "<div class='desplegable'>"
            trans_html += "<button class='btndesplegable'>"
            trans_html += tokens
            trans_html += "</button>"
            trans_html += '</div>'
            source_html = "<span style='color:Silver;'> {} </span>".format(tokens)
        else:
            trans_html = "<table>"
            trans_html += '<tr><td class="source">'
            trans_html += '<input type="radio" name="choice" id="{}" value="{}">{}</td></tr>'.format(tokens, tokens, tokens)
            trans_html += '</table>'
            source_html = "<span style='color:Silver;'> {} </span>".format(tokens)
        return [(self.raw, "Silver", trans_html, 0, tokens, source_html)]

    def verbatim(self, node):
        """Use the source token in the target complete translation."""
        # If token consists of only punctuation or digits, just return it
        token = node.token
        if token[0].isdigit() or token[0] in self.language.morphology.punctuation:
            return token
        else:
            return '#' + token

    @staticmethod
    def capitalize(token):
        if token[0] == '#':
            return '#' + token[1:].capitalize()
        elif '|' in token:
            return '|'.join([t.capitalize() for t in token.split('|')])
        return token.capitalize()

    ## Analyzing the sentence without creating segments
    def analyze(self, translate=True, verbosity=0):
        """Analyze the sentence without creating Segs (or TreeTrans instances).
        Match all Groups simultaneously, and do not apply any Joins.
        Useful for bitext corpus processing."""
        if verbosity:
            print("Analizando {}".format(self))
        self.initialize(ambig=False, constrain_groups=False, verbosity=verbosity)
        self.solve(all_sols=False, translate=False, verbosity=verbosity,
                   limit_trans=False)
        if self.segmentations:
            segmentation = self.segmentations[0]
            segmentation.make_pseudosegs(translate=translate, verbosity=verbosity)
            return segmentation

class Segmentation:
    
    """A non-conflicting set of groups for a sentence, at most one instance
    GNode for each sentence token, exactly one sentence token for each obligatory
    GNode in a selected group. Created when a complete variable assignment
    is found for a sentence."""

    # Maximum number of group translations permitted
    max_group_trans = 2

    def __init__(self, sentence, ginsts, s2gnodes, index, trees=None, dstore=None, session=None,
                 score=0, terse=True):
        self.sentence = sentence
        # Source language
        self.source = sentence.language
        # Target language
        self.target = sentence.target
        # List of sets of gnode indices
        self.s2gnodes = s2gnodes
        self.ginsts = ginsts
        self.trees = trees
        self.index = index
        # A list of pairs for each snode: (gnodes, features)
        self.gnodes_feats = []
##        # List of Translation objects; multiple translations are possible
##        # for a given segmentation because of multiple translations for groups
##        self.translations = []
        # A list of TreeTrans objects making up this segmentation
        self.ttrans = None
        self.ttrans_outputs = None
        # Variable domain store for segmentation state
        self.dstore = dstore
        # List of Segments, sentence segments with translations
        self.segments = []
        # Current session (need for creating SegRecord objects)
        self.session = session
        # Properties of selected groups, simpler than actual Segs
        self.pseudosegs = None
        # Score based on number of groups and sentences nodes covered (lower is better)
        self.score = score
        if not terse:
            print("SEGMENTACIÓN CREADA con dstore {} y ginsts {}".format(dstore, ginsts))

    def __repr__(self):
        return "|< {} >|({}.{})".format(self.sentence.raw, self.sentence.id, self.index)

    def display(self, word_width=10):
        """Show segmentation groups (GInsts) in terminal."""
        for g in self.ginsts:
            g.display(word_width=word_width, s2gnodes=self.s2gnodes)

    ## Ranking segmentations
    @staticmethod
    def rank(segmentations):
        segmentations.sort(key=lambda s: s.score)

    ## Creating translations

    
    def translate(self, verbosity=0, all_trans=False, interactive=False,
                  limit_trans=True):
        """Do everything you need to create the translation."""
        merged = self.merge_nodes(verbosity=verbosity)
        if not merged:
            return False
        for ginst in self.ginsts:
            if ginst.translations:
                if verbosity:
                    print("{} translations already set in other segmentation".format(ginst))
            else:
                ginst.set_translations(verbosity=verbosity)
        self.make_translations(verbosity=verbosity, all_trans=all_trans, interactive=interactive,
                               limit_trans=limit_trans)
        return True

    def merge_nodes(self, verbosity=0):
        """Merge the source features of cat and inst GNodes associated with each SNode.
        Return False if unification fails."""
        if verbosity:
            print("Merging target nodes for {}".format(self))
        for snode, gn_indices in zip(self.sentence.nodes, self.s2gnodes):
            feats_unified = None
            # gn_indices is either one or two ints indexing gnodes in self.gnodes
            gnodes = [self.sentence.gnodes[index] for index in gn_indices]
            if not gnodes:
                self.gnodes_feats.append((gnodes, None))
                continue
#            print("snode {}, gn_indices {}, gnodes {}".format(snode, gn_indices, gnodes))
            merging = len(gnodes) > 1
            if not merging:
                # Not really a merged node
                features = []
                gnode = gnodes[0]
                snode_indices = gnode.snode_indices
                snode_index = snode_indices.index(snode.index)
                snode_anal = gnode.snode_anal[snode_index]
                if snode_anal and snode_anal[0] and snode_anal[0][1]:
                    features = [a[1] for a in snode_anal]
                if verbosity:
                    print("  Not a merge node, anal {}, using preferred from {}".format(snode_anal, features))
                # Use the first (preferred) analysis.
                if features:
                    feature = features[0]
                    feats_unified = FSSet(feature)
            else:
                # A genuine merge node
                features = []
                for gnode in gnodes:
                    snode_indices = gnode.snode_indices
                    snode_index = snode_indices.index(snode.index)
                    snode_anal = gnode.snode_anal[snode_index]
                    if verbosity:
                        print("   Merge nodes for gnode {}: snode_anal {}".format(gnode, snode_anal))
                    # It could be a list of anals, only None if there aren't any.
                    if snode_anal and snode_anal[0] and snode_anal[0][1]:
                        if verbosity:
                            print("   Appending snode_anals for gnode {}: {}".format(gnode, [a[1] for a in snode_anal]))
                        features.extend([a[1] for a in snode_anal])
                # Could this fail?? YES, currently it can
                if verbosity:
                    print("  Unification result for {}: snode {}, gn_indices {} features {}".format(self, snode, gn_indices, features))
#            if len(features) > 1 and verbosity:
#                print("More than one feature to unify {}".features)
                if verbosity:
                    print("  Unifying fss in merge node {}".format(features))
                feats_unified = FSSet.unify_all([FSSet(feats) for feats in features])
#            if feats_unified:
#                print("  Unified feats {}".format(feats_unified))
#            if verbosity and len(features) > 1:
#                print("Features now {}".format())
            if merging and not feats_unified:
                print("SOMETHING WRONG: unification failed for {}!".format(features))
                return False
            if verbosity:
                s = "  Unification result for {}: snode {}, gn_indices {} features {} feats unified {}"
                print(s.format(self, snode, gn_indices, features, feats_unified))
            self.gnodes_feats.append((gnodes, feats_unified))
        return True

    def make_translations(self, verbosity=0, display=True, all_trans=False, interactive=False,
                          limit_trans=True):
        """Create a TreeTrans object for each GInst and tree. build() each top TreeTrans and
        realize translation. Whew."""
        if verbosity:
            print("Making translations for {} with ginsts {}".format(self, self.ginsts))
            for g in self.ginsts:
                for t in g.translations:
                    print("  {}".format(t))
        # Create TreeTrans instances here
        abs_gnode_dict = {}
        # A single gnode_dict for all treetranss
        gnode_dict = {}
        treetranss = []
        ttindex = 0
        for tree, ginst in zip(self.trees, self.ginsts):
#            print("Translating {} / {}".format(tree, ginst))
            if ginst.treetrans and ginst.treetrans.top and ginst.treetrans.segmentation == self:
                # There's a treetrans already and it's not the result of a merger,
                # so just use it rather than creating a new one.
                print("Not recreating treetrans for {}".format(ginst))
                treetranss.append(ginst.treetrans)
            else:
#                print("Making translations for tree {} and ginst {}".format(tree, ginst))
                # Figure the various features for the next TreeTrans instance.
                is_top = not any([(tree < other_tree) for other_tree in self.trees])
                group_attribs = []
                any_anode = False
                # This is the first place we can limit the number of translations allowed
                ginsttrans = ginst.translations
#                print("ginst translations: {}".format(ginsttrans))
                if limit_trans:
                    ginsttrans = ginsttrans[:Segmentation.max_group_trans]
                for tgroup, tgnodes, tnodes in ginsttrans:
#                    print(" Forming group_attribs: tgroup {}, tgnodes {}, tnodes {}".format(tgroup, tgnodes, tnodes))
                    for tgnode, tokens, feats, agrs, t_index in tgnodes:
                        if tgnode.cat:
                            any_anode = True
                            if tgnode in abs_gnode_dict:
                                abs_gnode_dict[tgnode].append((tgroup, tokens, feats, agrs, t_index))
                            else:
                                abs_gnode_dict[tgnode] = [(tgroup, tokens, feats, agrs, t_index)]
                        elif tgnode in gnode_dict:
                            gnode_dict[tgnode].append((tgroup, tokens, feats, agrs, t_index))
                        else:
                            gnode_dict[tgnode] = [(tgroup, tokens, feats, agrs, t_index)]
                    group_attribs.append((tgroup, tnodes, tgroup.agr, tgnodes))

                treetrans = TreeTrans(self, tree=tree.copy(),
                                      ginst=ginst, # attribs=ginst.translations,
                                      gnode_dict=gnode_dict, abs_gnode_dict=abs_gnode_dict,
                                      group_attribs=group_attribs,
                                      any_anode=any_anode,
                                      index=ttindex, top=is_top)
                treetranss.append(treetrans)
                ttindex += 1
#        print("Gnode dict: {}".format(gnode_dict))
        self.treetranss = treetranss

        # Add subTTs to TTs (actually only have to do this for top TTs)
        for index, tt1 in enumerate(treetranss[:-1]):
            tree1 = tt1.tree
            for tt2 in treetranss[index:]:
                tree2 = tt2.tree
                if tree1 < tree2:
                    tt2.subTTs.append(tt1)
                elif tree2 < tree1:
                    tt1.subTTs.append(tt2)

        # Build TTs
        for tt in treetranss:
            if tt.outputs:
                print("TreeTrans {} already processed".format(tt))
                tt.display_all()
            elif tt.top:
                # Translation groups and associated tnodes for this tree (top level)
                tt.all_tgroups.append(list(zip(tt.tgroups, tt.tnodes)))
                for stt in tt.subTTs:
                    tt.all_tgroups.append(list(zip(stt.tgroups, stt.tnodes)))
                # Find all combinations of the target groups involved in this TT (at any level)
                tgroup_combs = allcombs(tt.all_tgroups)
                if verbosity:
                    print(" TT group combs")
                    for tgc in tgroup_combs:
                        print("  {}".format(tgc))
                for tgroup_comb in tgroup_combs:
#                    print("tgroup_comb {}".format(tgroup_comb))
                    tgroups = [t[0] for t in tgroup_comb]
                    tnodes = [t[1] for t in tgroup_comb]
                    tt.build(tg_groups=tgroups, tg_tnodes=tnodes, verbosity=verbosity)
                    # Used to be generate_words()
                    tt.do_agreements(limit_forms=limit_trans)
                    tt.make_order_pairs(verbosity=verbosity)
                    tt.create_variables()
                    tt.create_constraints()
                    tt.realize(all_trans=all_trans, interactive=interactive)
                    if all_trans:
                        continue
                    if not interactive or not input('SEARCH FOR ANOTHER TRANSLATION FOR {}? [yes/NO] '.format(tt)):
                        break

    def get_ttrans_outputs(self):
        """Return a list of (treetrans, snode_indices, (thindex, ttoken, tcats))
        for the segmentation's tree translations. These are needed for the creation of Segment instances."""
        if not self.ttrans_outputs:
            self.ttrans_outputs = []
            last_indices = [-1]
            for tt in self.treetranss:
                if not tt.output_strings:
                    continue
                indices = tt.snode_indices
                thead = tt.ginst.head
                thindex = thead.index
                tfeats = thead.snode_anal
                ttoken = tfeats[0] or [thead.token]
                tsnode = tt.snodes[thindex]
                ttok = tsnode.tok
                tcats = tsnode.cats
#                print("TT {}, ttok {}".format(tt, ttok))
#                print("TT {}: head {}, index {}, feats {}, cats {}".format(tt, thead, thindex, tfeats, tcats))
                # WHY [0]??
                head = (thindex, ttoken, tcats, ttok)
                raw_indices = []
                for index in indices:
                    node = self.sentence.nodes[index]
                    raw1 = node.raw_indices
                    raw_indices.extend(raw1)
                raw_indices.sort()
                self.ttrans_outputs.append([tt, raw_indices, head])
                last_indices = raw_indices
        return self.ttrans_outputs

    def get_untrans_segs(self, src_tokens, end_index, gname=None,
#                         merger_groups=None,
                         indices_covered=None,
                         src_feats=None, src_toks=None, is_paren=False):
        '''Set one or more segments for a sequence of untranslatable tokens. Ignore indices that are already
         covered by translated segments.'''
        stok_groups = []
        sfeat_groups = []
        stoks = []
        stokheads = []
        sfeatures = []
        index = end_index + 1
        included_tokens = []
        newsegs = []
        if not src_toks:
            src_toks = [None] * len(src_tokens)
        for stoken, stok, sfeats in zip(src_tokens, src_toks, src_feats):
#            print("stoken {}, stok {}, sfeats {}".format(stoken, stok, sfeats))
            if not stoken:
                # empty sentence final token
                continue
            if Token.del_token(stoken):
#                print("Deleted token {}".format(stoken))
                stoks.append(stoken)
                sfeatures.append(sfeats)
                included_tokens.append(stoken)
            elif index in indices_covered:
                if stoks:
                    stok_groups.append(stoks)
                    sfeat_groups.append(sfeatures)
                    stokheads.append(stok)
                    stoks = []
                    sfeatures = []
            else:
                # Special token or punctuation; it should have its own segment
                stoks.append(stoken)
                sfeatures.append(sfeats)
                included_tokens.append(stoken)
                if stoks:
                    stok_groups.append(stoks)
                    sfeat_groups.append(sfeatures)
                    stokheads.append(stok)
                    stoks = []
                    sfeatures = []
            index += 1
        if stoks:
            stok_groups.append(stoks)
            sfeat_groups.append(sfeatures)
            stokheads.append(stok)
        i0 = end_index+1
        for stok_group, sfeat_group, stokhead in zip(stok_groups, sfeat_groups, stokheads):
#            print("stok_group {}".format(stok_group))
            is_punc = len(stok_group) == 1 and self.source.is_punc(stok_group[0])
            if is_punc:
                # Convert punctuation in source to punctuation in target if there is a mapping.
                translation = [self.target.punc_postproc(stok_group[0])]
            else:
                translation = []
            start = i0
            end = i0+len(stok_group)-1
            indices = list(range(start, end+1))
            node_toktype = [self.sentence.get_node_by_raw(i).toktype for i in range(start, end+1)][0]
            space_before = 1
            if node_toktype == 2:
                space_before = 0
#            print("Node type for untranslated Segment: {}".format(node_toktype))
            seg = Segment(self, indices, translation, stok_group, session=self.session,
                          gname=None, sfeats=sfeat_group[0], tok=stokhead,
                          space_before=space_before,
#                          merger_groups=None,
                          is_punc=is_punc, is_paren=is_paren)
            print("Segmento (no traducido) {}->{}: {}={} ({})".format(start, end, stok_group, seg.translation, seg.head_tok))
            self.segments.append(seg)
            newsegs.append(seg)
            i0 += len(stok_group)
        return newsegs

    def get_segs(self, html=True, single=False):
        """Set the segments (instances of Segment) for the segmentation, including their translations.
        THIS IS MESSY BECAUSE OF THE POSSIBILITY OF PARENTHETICALS AND GAPS.
        """
        tt = self.get_ttrans_outputs()
        end_index = -1
        max_index = -1
        sentence = self.sentence
        tokens = [a[0] for a in sentence.analyses]
#            sentence.tokens
        indices_covered = []
        # Token lists for parenthetical segments
        parentheticals = []
        # Segments containing parentheticals
        has_parens = []
        for treetrans, raw_indices, thead in tt:
            forms = treetrans.output_strings
#            print("Forms for segment: {}".format(forms))
            gname = treetrans.ginst.group.name
#            merger_groups = treetrans.get_merger_groups()
            tgroups = treetrans.ordered_tgroups
            late = False
            start, end = raw_indices[0], raw_indices[-1]
            if start > max_index+1:
                # there's a gap between the farthest segment to the right and this one; make one or more untranslated segments
                src_tokens = tokens[end_index+1:start]
                src_nodes = [sentence.get_node_by_raw(index) for index in range(end_index+1, start)]
                src_feats = [(s.analyses if s else None) for s in src_nodes]
                src_toks = [s.tok for s in src_nodes]
                self.get_untrans_segs(src_tokens, end_index, gname=gname,
#                                      merger_groups=merger_groups,
                                      src_feats=src_feats, src_toks=src_toks, indices_covered=indices_covered)
            if start < max_index:
                # There's a gap between the portions of the segment; this is a parenthetical segment within an outer one
                late = True
            # There may be gaps in the source tokens for a group; fill these with (...tokens...)
            src_tokens = []
            parenthetical = []
            pre_paren = []
            post_paren = []
            paren_record = []
            for tokindex in range(start, end+1):
                token = tokens[tokindex]
                if tokindex in raw_indices:
                    # A token in the group
                    # First check whether there is a parenthetical before this
                    if parenthetical:
                        post_paren.append(token)
                    else:
                        pre_paren.append(token)
                else:
                    parenthetical.append(token)
                    paren_record.append((token, tokindex))
            if parenthetical:
                parentheticals.append(paren_record)
                src_tokens = pre_paren + parenthetical + post_paren
            else:
                src_tokens = pre_paren
#            print("Creating Segment with parenthetical {}, source tokens {}, head {}".format(parenthetical, src_tokens, thead))
            src_nodes = [sentence.get_node_by_raw(index) for index in range(start, end+1)]
            src_feats = [(s.analyses if s else None) for s in src_nodes]
#            print("  src nodes {}; src feats {}".format(src_nodes, src_feats))
            seg = Segment(self, raw_indices, forms, src_tokens, treetrans=treetrans,
                          session=self.session, gname=gname, sfeats=src_feats[0],
                          tgroups=tgroups, head=thead, tok=thead[-1],
#                          merger_groups=merger_groups
                          has_paren=[pre_paren, paren_record, post_paren] if parenthetical else None,
                          is_paren=late)
            if parenthetical:
                has_parens.append(seg)
            if late:
                pindices = seg.indices
#                print("Looking for enclosing segment for parenthetical {} with tokens {} and indices {}".format(seg, ptokens, pindices))
                for hp in has_parens:
                    hp_pindices = hp.paren_indices
                    if pindices == hp_pindices:
#                        print(" Found matching enclosing segment {}".format(hp))
                        hp.paren_seg = seg
            print("Segmento (traducido) {}->{}: {}={} ({}); {}".format(start, end, src_tokens, seg.translation, seg.head_tok, seg.cleaned_trans))
            self.segments.append(seg)
            indices_covered.extend(raw_indices)
#            print(" Indices covered: {}".format(indices_covered))
            max_index = max(max_index, end)
            end_index = end
        if max_index+1 < len(tokens):
            # Some word(s) at end not translated; use source forms
            src_tokens = tokens[max_index+1:len(tokens)]
            src_nodes = [sentence.get_node_by_raw(index) for index in range(max_index+1, len(tokens))]
            src_feats = [(s.analyses if s else None) for s in src_nodes]
            src_toks = [s.tok for s in src_nodes]
            self.get_untrans_segs(src_tokens, max_index, gname=gname,
#                                  merger_groups=merger_groups,
                                  src_feats=src_feats, src_toks=src_toks, indices_covered=indices_covered)
        # Check whether untranslated parentheticals have gotten segments
        for parenthetical in parentheticals:
            ptokens = [p[0] for p in parenthetical]
            pindices = [p[1] for p in parenthetical]
#            print("Checking parenthetical: {}, {}".format(ptokens, pindices))
            found = False
            i = 0
            while not found and i < len(self.segments):
                segment = self.segments[i]
                if segment.tokens == ptokens and segment.indices == pindices:
#                    print(" Segmento {} ya creado".format(segment))
                    found = True
                i += 1
            if not found:
#                print(" Creating untranslated segment")
                newsegs = self.get_untrans_segs(ptokens, pindices[0]-1, indices_covered=indices_covered,
                                                is_paren=True)
                # hopefully only one of these
                if newsegs and len(newsegs) > 0:
                    newseg = newsegs[0]
                    pindices = newseg.indices
                    for hp in has_parens:
                        if pindices == hp.paren_indices:
#                            print(" Found matching enclosing segment for untrans segment {}".format(newseg))
                            hp.paren_seg = newseg
        # Sort the segments by start indices in case they're not in order (because of parentheticals)
        self.segments.sort(key=lambda s: s.indices[0])
        if html:
            self.seg_html(single=single)

    def seg_html(self, single=False):
        """Set the HTML for each of the segments in this segmentation."""
        for i, segment in enumerate(self.segments):
            if single:
                segment.set_single_html(i)
            else:
                segment.set_html(i)

    def get_gui_segments(self, single=False):
        """These may differ from Segments because of intervening segments within outer segments."""
        segments = []
        enclosings = []
        parens = []
        for segment in self.segments:
            if segment.has_paren:
                paren_seg = segment.paren_seg
                if single:
                    tokens, color, html, index, trans1, src_html = segment.html
                    ptokens, pcolor, phtml, pindex, trans1, psrc = paren_seg.html
                else:
                    tokens, color, html, index, src_html = segment.html
                    ptokens, pcolor, phtml, pindex, psrc = paren_seg.html
                gui_src = segment.get_gui_source(pcolor)
                preseg = tokens, color, html, index, gui_src[0]
                parenseg = ptokens, pcolor, phtml, pindex, gui_src[1]
                postseg = tokens, color, html, index, gui_src[2]
#                print("Adding gui segments for {}".format(gui_src))
                segments.extend([preseg, parenseg, postseg])
            elif not segment.is_paren:
                segments.append(segment.html)
#        if single:
#            for i, s in enumerate(segments):
#                print("Initial trans for seg {}: {}".format(i, s[4]))
        return segments

    ## Pseudosegs: simpler alternative to Segs

    def make_pseudosegs(self, translate=True, verbosity=0):
        """Create pseudoseg list from ginsts."""
        if verbosity:
            print(" Creando pseudosegmentos para {}".format(self))
        self.pseudosegs = []
        for ginst in self.ginsts:
            name = ginst.group.name
#            gh = ginst.head
#            tok = gh.token
#            feats = gh.features
            if translate:
                ginst.set_translations()
                transgroups = {t[0] for t in ginst.translations}
#                transprops = [(g.head, g.features[g.head_index] if g.features else None) for g in transgroups]
                transprops = [g.name for g in transgroups]
#                ps = tok, feats, transprops
                ps = name, transprops
            else:
#                ps = tok, feats
                ps = name
            self.pseudosegs.append(ps)

    ## Generation, joining, group matching following initial segmentation

    def connect(self, iters=15, generate=True, only1=False, verbosity=1):
        """Iteratively match Join and Group instances where possible, create supersegs for
        matches, and optionally finish by generateing morphological surface forms for
        final segments."""
        iteration = 0
        matched = True
        all_matches = []
        nsegments = len([s for s in self.segments if not s.is_punc])
        while matched and iteration < iters and nsegments > 1:
            print("BUSCANDO COINCIDENCIAS CON JOINS Y GROUPS, ITERACIÓN {}".format(iteration))
            print(" Segmentos: {}".format(self.segments))
            matches = self.match_joins(verbosity=0)
            matches.extend(self.match_groups(make_super=False, resolve=False, verbosity=verbosity))
#            matches = join_matches + group_matches
            if matches:
                print(" Encontró coincidencias {}".format(matches))
                if len(matches) > 1:
                    Match.resolve(matches, verbosity=verbosity)
                    print(" Resueltas a {}".format(matches))
                if only1:
                    match = matches[0]
                    self.match2superseg(match, verbosity=verbosity)
                    all_matches.append(match)
                else:
                    self.matches2supersegs(matches, verbosity=verbosity)
                    all_matches.extend(matches)
            else:
                matched = False
            iteration += 1
            nsegments = len([s for s in self.segments if not s.is_punc])
        if generate:
            self.generate(limit_forms=True, verbosity=verbosity)
        return all_matches

    def join(self, iters=6, joingroupings=None, makesuper=True, generate=False, verbosity=1):
        """Iteratively match Join instances where possible, create supersegs for matches,
        and optionally finish by generating morphological surface forms for final segments."""
        iteration = 0
        matched = True
        all_matches = []
        while matched and iteration < iters:
#            if verbosity:
            print("MATCHING JOINS IN GROUPINGS {}, ITERATION {}".format(joingroupings, iteration))
            print(" Segments: {}".format(self.segments))
            matches = self.match_joins(joingroupings=joingroupings, verbosity=0)
            if matches:
                print(" Found matches {}".format(matches))
                if len(matches) > 1:
                    Match.resolve(matches)
                    print(" Resolved to {}".format(matches))
                all_matches.extend(matches)
                if makesuper:
                    self.matches2supersegs(matches, verbosity=verbosity)
            else:
                print(" Ningunas coincidencias encontradas")
                matched = False
            iteration += 1
        if generate:
            self.generate(limit_forms=True, verbosity=verbosity)
        return all_matches
    
    def match_joins(self, joingroupings=None, verbosity=0):
        """Try to match the sequence of Segments in this segmentation with the patterns
        in all the Join instances, taking Join instances one at a time in order."""
        matches = []
        segments = self.segments
        sollength = len(segments)
        segstart = 0
        source_join_groupings = self.source.join_groupings
        if joingroupings:
            # This should be None or a list of ints
            joingroupings = [source_join_groupings[index] for index in joingroupings]
        else:
            joingroupings = source_join_groupings
        for joingroup in joingroupings:
            if verbosity:
                print(" Match joins in grouping {}".format(joingroup))
            for join in joingroup:
                if verbosity > 1:
                    print("Matching {}".format(join))
                tokens = join.tokens
                patlength = len(tokens)
                endgap = sollength - patlength
                segstart = 0
                matches1 = []
                while segstart < sollength - 1 and endgap - segstart >= 0:
                    match1 = join.match(segments, segstart, verbosity=verbosity)
                    if match1:
                        if verbosity > 1:
                            print("  Matched at {}".format(segstart))
                        # Check the conditions on the join
                        match2 = join.match_conds(segments, segstart, verbosity=verbosity)
                        if match2:
                            if verbosity > 1:
                                print("  Matched conds")
#                            matches1.append((join, match1))
                            matches1.append(Match(join, match1))
                            # Don't look for more matches from this position; move forward
                            # by the length of the join - 1 (because we're moving forward
                            # anyway at the end of this loop)
                            segstart += patlength - 1
                    # Move forward
                    segstart += 1
                if matches1:
                    matches.extend(matches1)
        if matches and verbosity:
            print(" Found join matches {}".format(matches))
        return matches

    def match_groups(self, groupsid=1, make_super=True, resolve=True, verbosity=1):
        """Get candidate matches of groups with segmentation Segs and match them,
        returning matches as Match instances.
        """
#        print("MATCHING GROUPS {}".format(groupsid))
#        print(" Segments: {}".format(self.segments))
        cands = self.get_group_cands(groupsid=groupsid, verbosity=verbosity)
        matches = self.match_group_cands(cands, resolve=resolve, verbosity=verbosity)
        if make_super:
            self.matches2supersegs(matches, verbosity=verbosity)
        return matches

    def get_group_cands(self, groupsid=1, groups=None, verbosity=1):
        """Find candidate Group matches with segmentation Segs."""
        if verbosity:
            print("{} finding group candidates".format(self))
        groups = groups or self.source.groups[groupsid]
        cands = []
        sol_length = len(self.segments)
        for index, segment in enumerate(self.segments):
            cands1 = segment.get_group_cands(all_groups=groups, verbosity=verbosity)
            for cand1 in cands1:
                group, head_index = cand1
                start = index-head_index
                end = start + len(group.tokens)
                if end <= sol_length:
                    indices = range(start, end)
                    # Reject candidates that are too long for the sentence
                    cands.append((index, indices, cand1))
        return cands

    def match_group_cands(self, candidates, resolve=True, verbosity=0):
        """Match group candidates along with indices against segments in the Segmentation,
        filtering out shorter ones that overlap with longer ones,
        returning matches as tuples: (group, [position, segment, features])."""
        matches = []
        segments = self.segments
        for segindex, segindices, (group, head_index) in candidates:
            matches1 = group.match_segments(segments, segindex - head_index, verbosity=verbosity)
            if matches1:
                matches.append(matches1)
        if matches:
            if verbosity:
                print(" Found group matches {}".format(matches))
            if resolve:
                Match.resolve(matches)
                if verbosity:
                    print(" Resolved to {}".format(matches))
        elif verbosity:
            print(" No matches found")
        return matches

    def matches2supersegs(self, matches, verbosity=0):
        """Given a list of matches of a Join or Group instances, create new Superseg instances."""
        # First sort the matches from last to first, to prevent indices from changing before
        # a new Superseg is introduced.
        if len(matches) > 1:
            Match.sort_by_position(matches)
        for match in matches:
            self.match2superseg(match, verbosity=verbosity)

    def match2superseg(self, match, verbosity=0):
        """Given a match of a Join or Group instance, create a new SuperSeg instance."""
        if isinstance(match, Match):
            join, seglist = match.entry, match.matched
        else:
            join, seglist = match
        segs = [s[1] for s in seglist]
        positions = [s[0] for s in seglist]
        features = [s[2] for s in seglist]
        superseg = SuperSeg(self, segs, features=features, join=join, verbosity=verbosity)
#        if verbosity:
        print("CREANDO SUPERSEG PARA {} Y {} en posiciones {}".format(segs, join, positions))
#        print("...reemplazando segmento {} a segmento {}".format(self.segments[positions[0]], self.segments[positions[-1]+1]))
#            print("CREATING SUPERSEG FOR {} AND {} in positions {}".format(segs, join, positions))
#            print("...replacing segment {} to segment {}".format(self.segments[positions[0]], self.segments[positions[-1]+1]))
        # replace the joined segments in the segmentation with the superseg
        self.segments[positions[0]:positions[-1]+1] = [superseg]

    def generate(self, limit_forms=True, verbosity=0):
        """Generate forms within segmentation segments."""
        for segment in self.segments:
            segment.generate(limit_forms=limit_forms, verbosity=verbosity)

    def process(self, generate=False, verbosity=0):
        """Repeatedly try matching and applying Join instances and the Group instances from
        Join and Group groupings, until there are no more, then optionally do morphological
        generation."""
        njoins = len(self.source.join_groupings)
        ngroups2 = len(self.source.groups)
        j = 0
        g = 1
        while j < njoins or g < ngroups2:
            if j < njoins:
                self.join(joingroupings=None, verbosity=verbosity)
                j += 1
            if g < ngroups2:
                self.match_groups(groupsid=g, verbosity=verbosity)
                g += 1
        if generate:
            self.generate(limit_forms=True)

    ## Final translation
    def get_translation(self):
        return [s.cleaned_trans for s in self.segments]

