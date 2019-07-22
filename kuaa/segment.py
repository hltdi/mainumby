#   
#   MDT/TGS
#
########################################################################
#
#   This file is part of the MDT project of the PLoGS metaproject
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyleft 2014, 2015, 2016, 2017, 2018, 2019;
#      HLTDI, PLoGS <gasser@indiana.edu>
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

# 2016.01.05
# -- Split off from sentence.py
# 2016.01.06
# -- Added SolSeg class for sentence solution segments with translations.
# 2016.01.18
# -- Fixed TreeTrans.build() so that multiple translations work with groups involving merging.
# 2016.01.26
# -- Fixed it so that groups can have multiple abstract nodes, for example, <por $num $n>, and
#    match concrete nodes in multiple other groups.
# 2016.02.01
# -- Cache added to TreeTrans to save feature and node merger information during build, preventing
#    repetition.
# 2016.03.02
# -- Lots of changes to how segments are displayed in GUI, especially including radio buttons for
#    choices.
# 2016.03.06
# -- GInsts create GNodes only for tokens that fail to get deleted by MorphoSyns. So there may be
#    gaps in GNode indices.
# 2016.03.08
# -- SolSeg.set_html() also creates a dict of choice alternatives.
# 2016.06.01
# -- GNodes now carry sets of features rather than a single feature. This solves a problem with
#    failure to match features in node merging in the case of an ambiguous analysis of the concrete node.
# 2016.06.15
# -- Finally fixed build() so it correctly applies to each combination of group translation for top-level
#    and subtree groups.
# 2016.06.16
# -- OK, I still wasn't quite finished.
# 2017.03
# -- Display for GInsts improved.
# 2017.04.24
# -- Got things to work with external tagger (not many changes).
# 2017.06.22
# -- Skip group item matching for punctuation nodes.
#    Character joining items in phrases and numerals is now ~ instead of _.
# 2017.07.13
# -- Fixed TNodes within subtrees (nodes corresponding words in TL that are not in TL).
#    For example, ዓረፍተ in ዓረፍተ ነገር when this is part of a subtree.
# 2018.02-03
# -- Lots of changes and fixes in SolSeg.
# 2018.10.30
# -- SuperSeg
# 2019.3.12
# -- Changed SolSeg to Segment.

import itertools, copy, re
from .cs import *
from .morphology.semiring import FSSet
# needed for a few static methods
from .entry import Group, Token, JoinToken
from .record import SegRecord
from .utils import *
from kuaa.morphology.utils import reduce_lists

class Seg:
    """Interface class for segments:
    Segment, resulting from matching a group and possibly one or more merged groups under it
    SuperSeg, resulting from joining two or more Segments.
    """

    # Maximum number of generated forms permitted, given a root and set of update features
    max_gen_forms = 4

    # colors to display segments in interface
    tt_colors = ['blue', 'sienna', 'green',
                 'purple', 'red', 'blue', 'sienna', 'green', 'purple', 'red', 'blue', 'sienna', 'green',
                 'purple', 'red', 'blue', 'sienna', 'green', 'purple', 'red', 'blue', 'sienna', 'green',
                 'purple', 'red', 'blue', 'sienna', 'green', 'purple', 'red', 'blue', 'sienna', 'green',
                 'purple', 'red', 'blue', 'sienna', 'green', 'purple', 'red', 'blue', 'sienna', 'green',
                 'purple', 'red', 'blue', 'sienna', 'green', 'purple', 'red', 'blue', 'sienna', 'green']

    tt_notrans_color = "Silver"

    special_re = re.compile("%[A-Z]+~")

    # Character indicating that tokens in translation string should be joined ("Carlos `-pe" -> "Carlos-pe")
    join_tok_char = "`"

    def __init__(self, segmentation):
        self.segmentation = segmentation
        self.sentence = segmentation.sentence
        self.source = segmentation.source
        self.target = segmentation.target
        self.segmentation = segmentation.sentence
        self.generated = False
        self.special = False
        # structure
        self.shead = None
        self.shead_index = -1
        self.thead = None
        self.scats = None
        self.depth = 1
        # source and target strings
        self.original_token_str = ''
        self.token_string = ''
        self.clean_trans = None
        # html
        self.html = []
        self.source_html = None
        # parentheses
#        self.has_paren = False
#        self.is_paren = False
        # punctuation
        self.is_punc = False
        self.record = None
        self.gname = None
#        self.merger_gnames = None
        self.indices = None

    def get_tokens(self):
        """Returns a set of all possible tokens for this segment."""
        toks = self.get_shead_tokens() or self.get_untrans_token() or [self.token_str]
        raw = self.get_shead_raw()
        if raw and raw not in toks:
            toks.append(raw)
        to_add = []
        for tok in toks:
            if '_' in tok:
                to_add.append(tok.split('_')[0])
        return set(toks + to_add)

    def get_untrans_token(self):
        """For untranslated segments, return the cleaned string."""
        return self.cleaned_trans and self.cleaned_trans[0][0]

    ## Head properties (used in joining Segments to form Supersegs)

    def get_shead_raw(self):
        """The raw token for the source head."""
        if self.shead and self.shead_index >= 0:
            return self.tokens[self.shead_index]

    def get_shead_tokens(self):
        if self.shead:
            return [(h[0] if isinstance(h, tuple) else h) for h in self.shead]

    def get_shead_roots(self):
        if self.shead:
            return [h[0] for h in self.shead if isinstance(h, tuple)]

    def get_shead_feats(self):
        if self.shead:
            return [h[1] for h in self.shead if isinstance(h, tuple)]

    def get_shead_pos(self):
        if self.shead:
            pos = set()
            for h, f, p in self.shead:
                if p:
                    pos.add(p)
                if f:
                    pos.add(f.get('pos'))
                elif '_' in h:
                    pos.add(h.split('_')[-1])
            return pos

    def get_thead_roots(self):
        if not self.generated:
            if self.thead:
                return [h[0] for h in self.thead]

    def get_thead_feats(self):
        if not self.generated:
            if self.thead:
                return [h[2] for h in self.thead]

    def get_thead_pos(self):
        if not self.generated:
            if self.thead:
                return [h[1] for h in self.thead]

    def generate(self, limit_forms=True, verbosity=0):
        raise NotImplementedError()

    def get_special(self, del_spec=False):
        """If Segment is special, return its category and the token as a tuple."""
        if self.special:
            if self.cleaned_trans:
                # Already translated
                token = self.get_shead_tokens()[0]
#                print("Translated special token {}, self {}".format(token, self))
                pre, x, form = token.partition('~')
            else:
                tok = self.get_untrans_token()
                pre, form = tok.split('~')
            if del_spec:
                pre = pre[1:]
            return pre, form
        return None, None

    # Matching Join and Group instances

    def has_child(self):
        print("Error: has_child not defined for {}".format(self))

    def match_join(self, join_elem, join_pos, verbosity=0):
        """Does this Segment match a pattern element in a Join? join_elem
        is either a FSSet or a string."""
        if verbosity:
            print("  Matching item {} with join elem {} and pos {}".format(self, join_elem, join_pos))
        if join_pos:
            # If there's a POS for the join, it must be matched (there must also be a translation)
            if self.translation and JoinToken.match_pos(join_pos, self.get_shead_pos()):
                return True
            else:
                return False
        if isinstance(join_elem, str):
            # Match special type, category, or explicit token
            if Token.spec_char in join_elem:
                # Match special type
                pre, tok = self.get_special()
                return pre == join_elem and tok
            elif Token.cat_char in join_elem:
                # Match a category
                # This should fail SOMETIMES when there's no translation
                # DISTINGUISH THESE CASES WITH A CODE LIKE $$
                return self.scats and join_elem in self.scats
            else:
                toks = self.get_tokens()
                if verbosity > 1:
                    print("    Tokens to match {}".format(toks))
                return any([join_elem == tok for tok in toks]) and toks
        elif not self.translation:
            # If group element has features, matching segment must have translation
            return False
        else:
            feats = self.get_shead_feats()
            # Match features
            if feats:
                for feat in feats:
                    u = join_elem.u(feat)
                    if u and u != 'fail':
                        return u
            return False
            
    def match_group_tok(self, group_tok, group_feats, verbosity=1):
        """Does this Seg match pattern elem and features from a Group?"""
        if verbosity:
            print(" Matching item {} with group token {}".format(self, group_tok))
        if '$' in group_tok:
#            print("{} matching group tok {}".format(self, group_tok))
#            print("scats {}".format(self.scats))
#            print("shead_feats {}".format(self.get_shead_feats()))
            # segment has to have a translation to match a category
            if not self.translation:
                return False
            if not self.scats or group_tok not in self.scats:
                return False
            elif self.get_shead_feats():
                return self.get_shead_feats()[0] or True
            else:
                return True
        elif Token.is_special(group_tok):
            if not self.special:
                return False
            pre = self.head_tok.prefix
#            pre, tok = self.get_special()
            if verbosity:
                print(" Special prefix {}; group token {}".format(pre, group_tok))
                # Prefix could be more specific than group token, for example, %ND and %N
#            if not pre or not pre.startswith(group_tok):
            if not pre.startswith(group_tok):
                return False
        else:
            toks = self.get_tokens()
#            if verbosity:
#                print(" Matching group token {} with segment tokens {}".format(group_tok, toks))
            if not any([group_tok == tok for tok in toks]) or isinstance(self, SuperSeg):
                # Explicit string in group can't match a SuperSeg
                return False
            if not group_feats:
                return True
            feats = self.get_shead_feats()
            if feats:
                for feat in feats:
                    if verbosity:
                        print(" Matching group features {} with segment features {}".format(group_feats.__repr__(), feat.__repr__()))
                    # strict feature forces True feature in group_feats to be explicit in feat
                    u = feat.u(group_feats, strict=True)
                    if u == 'fail':
                        return False
                    else:
                        return u
        return True

    def get_group_cands(self, all_groups=None, verbosity=0):
        """Get groups that could match this segment and surrounding segments.
        Returns a set to prevent duplicates."""
        tokens = self.get_tokens()
        all_groups = all_groups or self.source.groups
        if all_groups and tokens:
            groups = set()
            for token in tokens:
                groups1 = all_groups.get(token)
                if groups1:
                    groups1 = [(g, g.head_index) for g in groups1]
                    groups.update(groups1)
            if verbosity and groups:
                print("  Found candidates {} for {}".format(groups, self))
            return groups
            
    def generate(self, limit_forms=True, verbosity=0):
        """Generate surface forms for segment."""
        if verbosity:
            print("Generating segment {} with cleaned trans {} and raw token str {}".format(self, self.cleaned_trans, self.raw_token_str))
        generator = self.target.generate
#        special = '%' in self.raw_token_str or '~' in self.raw_token_str
        cleaned_trans = []
        for translation in self.cleaned_trans:
            output1 = []
            if verbosity:
                print("  Generating {}".format(translation))
            for item in translation:
                if verbosity:
                    print("   Generating {}".format(item))
                if Token.is_special(item):
                    spec_trans = self.source.translate_special(item)
                    if spec_trans:
                        output1.append(Seg.clean_spec(spec_trans)) 
                elif isinstance(item, list):
                    # We need to generate it
                    token, pos, feats = item
                    form = generator(token, feats, pos=pos)
                    # Include only first max_gen_forms forms
                    if limit_forms:
                        form = form[:Seg.max_gen_forms]
                    form = '|'.join(form)
#                    if verbosity:
#                        print("      Generated form {}".format(form))
                    output1.append(form)
                    generated = True
                else:
                    output1.append(item)
            cleaned_trans.append(output1)
            if verbosity:
                print("  Cleaned: {}".format(cleaned_trans))
        Seg.join_toks_in_strings(cleaned_trans)
        self.cleaned_trans = cleaned_trans
        self.generated = True

    ## Matching

    def has_child(self):
        return len(self.segments) > 1

    ## Web app

    def set_source_html(self, index):
#        if self.has_paren:
#            self.source_html = "<span class='fuente' style='color:{};'> {} </span>".format(self.color, self.pre_token_str)
#            self.source_html += "<span id=parenthetical> {} </span>".format(self.paren_token_str)
#            self.source_html += "<span class='fuente' style='color:{};'> {} </span>".format(self.color, self.post_token_str)
#        else:
        cap = index == 0 and self.sentence.capitalized
        tokstr = self.original_token_str
        if cap:
            tokstr = tokstr[0].upper() + tokstr[1:]
        self.source_html = "<span class='fuente' style='color:{};'> {} </span>".format(self.color, tokstr)

    def get_gui_source(self, paren_color='Silver'):
#        if self.has_paren:
#            return ["<span class='fuente' style='color:{};'> {} </span>".format(self.color, self.pre_token_str),
#                    "<span class='fuente' style='color:{};'> {} </span>".format(paren_color, self.paren_token_str),
#                    "<span class='fuente' style='color:{};'> {} </span>".format(self.color, self.post_token_str)]
#        else:
        return "<span class='fuente' style='color:{};'> {} </span>".format(self.color, self.token_str)

    def set_single_html(self, index, verbosity=0):
        """Set the HTML markup for this segment as a colored segment in source and dropdown menu
        in target, given its position in the sentence.
        """
        self.color = Seg.tt_notrans_color if (not self.translation and not self.special) else Seg.tt_colors[index]
        self.set_source_html(index)
        transhtml = "<div class='desplegable' ondrop='drop(event);' ondragover='allowDrop(event);'>"
        capitalized = False
        choice_list = self.record.choices if self.record else None
        # Final source segment output
        tokens = self.token_str
        orig_tokens = self.original_token_str
        trans_choice_index = 0
#        print("Setting HTML for segment {}: orig tokens {}, translation {}, tgroups {}".format(self, orig_tokens, self.cleaned_trans, self.tgroups))
        # T Group strings associated with each choice
        choice_tgroups = []
        # Currently selected translation
        trans1 = ''
        despleg = "despleg{}".format(index)
        boton = "boton{}".format(index)
        wrap = "wrap{}".format(index)
        if self.is_punc:
            trans = self.translation[0][0]
            trans1 = trans
            if '"' in trans:
                trans = trans.replace('"', '\"')
            transhtml += "<div class='despleg' id='{}' style='cursor:default'>".format(boton)
#             draggable='true' ondragstart='drag(event);'>".format(boton)
            transhtml += trans
            transhtml += "</div>"
            transhtml += '</div>'
            self.html = (tokens, self.color, transhtml, index, trans1, self.source_html)
            return
        # No dropdown if there's only 1 translation
        first_trans = True
        ntgroups = len(self.tgroups)
        multtrans = True
        for tindex, (t, tgroups) in enumerate(zip(self.cleaned_trans, self.tgroups)):
#            print("  tindex {}, t {}, tgroups {}".format(tindex, t, tgroups))
            # Create all combinations of word sequences
            tg_expanded = []
            if self.special:
                trans = t[0]
                tgcombs = [[(trans, '')]]
            else:
                for tt, tg in zip(t, tgroups):
#                    print("    tt {}, tg {}".format(tt, tg))
                    tg = Group.make_gpair_name(tg)
                    # Get rid of parentheses around optional elements
                    if '(' in tt:
                        tt = ['', tt[1:-1]]
                    else:
                        tt = tt.split('|')
                    # Add tg group string to each choice
                    tg_expanded.append([(ttt, tg) for ttt in tt])
                tgcombs = allcombs(tg_expanded)
            tgcombs.sort()
            tgforms = []
            tggroups = []
            for ttg in tgcombs:
                # "if tttg[0]" prevents '' from being treated as a token
                tgforms.append(' '.join([tttg[0] for tttg in ttg if tttg[0]]))
                tggroups.append("||".join([tttg[1] for tttg in ttg if tttg[0]]))
            ntggroups = len(tggroups)
            if (ntgroups == 1) and (ntggroups == 1):
                multtrans = False
            for tcindex, (tchoice, tcgroups) in enumerate(zip(tgforms, tggroups)):
                tchoice = tchoice.replace('_', ' ')
                alttchoice = tchoice.replace("'", "’")
                alttchoice = alttchoice.replace(" ", "&nbsp;")
                # ID for the current choice item
                choiceid = 'opcion{}.{}'.format(index, trans_choice_index)
                choice_tgroups.append(tcgroups)
                # The button itself
                if tindex == 0 and tcindex == 0:
                    trans1 = alttchoice
                    if not multtrans:
                        # Only translation; no dropdown menu
                        transhtml += "<div class='despleg' id='{}' ".format(boton)
                        transhtml += "style='background-color:{};cursor:grab' draggable='true' ondragstart='drag(event);'>{}</div>".format(self.color, alttchoice)
                    else:
                        # First translation of multiple translations; make dropdown menu
                        transhtml += '<div draggable="true" id="{}" ondragstart="drag(event);">'.format(wrap)
                        transhtml += '<div onclick="desplegar(' + "'{}')\"".format(despleg)
                        transhtml += " id='{}' class='despleg' style='background-color:{};cursor:context-menu'>{} ▾</div>".format(boton, self.color, alttchoice)
                else:
                    # Choice in menu under button
                    if trans_choice_index == 1:
                        # Start menu list
                        transhtml += "<div id='{}' class='contenido-desplegable'>".format(despleg)
                    transhtml += "<span class='opcion' id='{}' onclick='cambiarMeta(".format(choiceid)
                    transhtml += "\"{}\", \"{}\")'".format(boton, choiceid)
                    transhtml += ">{}</span><br/>".format(alttchoice)
                trans_choice_index += 1
        if not self.translation and not self.special:
            trans1 = orig_tokens
            # No translations suggested: button for translating as source
            multtrans = False
            transhtml += "<div class='despleg' id='{}'  style='cursor:grab' draggable='true' ondragstart='drag(event);'>".format(boton)
            transhtml += orig_tokens
            transhtml += "</div>"
        if multtrans:
            transhtml += '</div></div>'
        transhtml += '</div>'
        # Capitalize tokens if in first place
        if index==0:
            capitalized = False
            if ' ' in tokens:
                toks = []
                tok_list = tokens.split()
                for tok in tok_list:
                    if capitalized:
                        toks.append(tok)
                    elif self.source.is_punc(tok):
                        toks.append(tok)
                    else:
                        toks.append(tok.capitalize())
                        capitalized = True
                tokens = ' '.join(toks)
            else:
                tokens = tokens.capitalize()
        self.choice_tgroups = choice_tgroups
        if self.record:
            self.record.choice_tgroups = choice_tgroups
        self.html = (orig_tokens, self.color, transhtml, index, trans1, self.source_html)

    def set_html(self, index, verbosity=0):
        """Set the HTML markup for this segment, given its position in the sentence,
        Do postprocessing on phrases joined by '_' or special tokens (numerals).
        """
        # Combine translations where possible
        self.color = Seg.tt_notrans_color if not self.translation else Seg.tt_colors[index]
        self.set_source_html(index)
        transhtml = '<table>'
        capitalized = False
        choice_list = self.record.choices if self.record else None
        # Final source segment output
        tokens = self.token_str
        orig_tokens = self.original_token_str
        trans_choice_index = 0
        print("Setting HTML for segment {}: orig tokens {}, translation {}, tgroups {}".format(self, orig_tokens, self.cleaned_trans, self.tgroups))
        # T Group strings associated with each choice
        choice_tgroups = []
        if self.is_punc:
            trans = self.translation[0][0]
            if '"' in trans:
                trans = trans.replace('"', '\"')
            transhtml += "<tr><td class='transchoice'>"
            transhtml += '<br/><input type="radio" name="choice" id={} value="{}" checked>{}</td>'.format(trans, trans, trans)
            transhtml += '</tr>'
            transhtml += '</table>'
            self.html = (tokens, self.color, transhtml, index, self.source_html)
            return
        for tindex, (t, tgroups) in enumerate(zip(self.cleaned_trans, self.tgroups)):
            # Create all combinations of word sequences
            tg_expanded = []
            if self.special:
                trans = t[0]
                tgcombs = [[(trans, '')]]
            else:
                for tt, tg in zip(t, tgroups):
                    tg = Group.make_gpair_name(tg)
                    # Get rid of parentheses around optional elements
                    if '(' in tt:
                        tt = ['', tt[1:-1]]
                    else:
                        tt = tt.split('|')
                    # Add tg group string to each choice
                    tg_expanded.append([(ttt, tg) for ttt in tt])
                tgcombs = allcombs(tg_expanded)
            tgcombs.sort()
            tgforms = []
            tggroups = []
            for ttg in tgcombs:
                # "if tttg[0]" prevents '' from being treated as a token
                tgforms.append(' '.join([tttg[0] for tttg in ttg if tttg[0]]))
                tggroups.append("||".join([tttg[1] for tttg in ttg if tttg[0]]))
            # A single translation of the source segment
            transhtml += '<tr>'
            transhtml += "<td class='transchoice'>"
            html_choices = []
            for tcindex, (tchoice, tcgroups) in enumerate(zip(tgforms, tggroups)):
                tchoice = tchoice.replace('_', ' ')
                choice_tgroups.append(tcgroups)
#                print("  Choice {}: {} (groups: {})".format(trans_choice_index, tchoice, tcgroups))
                if tindex == 0 and tcindex == 0:
                    html_choices.append('<input type="radio" name="choice" id="{}" value="{}" checked>{}'.format(tchoice, tchoice, tchoice))
                else:
                    html_choices.append('<input type="radio" name="choice" id="{}" value="{}">{}'.format(tchoice, tchoice, tchoice))
                trans_choice_index += 1
            transhtml += "<br/>".join(html_choices)
            if len(tgcombs) > 1:
                transhtml += "<hr>"
            transhtml += "</td>"
#            if self.record:
#                choice_list.append(tchoice)
            transhtml += '</tr>'
        if self.translation and self.translation[0]:
            if verbosity:
                print("Translation {}, clean trans {}".format(self.translation, self.cleaned_trans))
            if self.cleaned_trans[0][0] != tokens:
                # Add other translation button
                # Button to translate as source language
                transhtml += '<tr><td class="source">'
                transhtml += '<input type="radio" name="choice" id="{}" value="{}">{}</td></tr>'.format(orig_tokens, orig_tokens, orig_tokens)
        else:
            # No translations suggested: checkbox for translating as source (only option)
            transhtml += '<tr><td class="source">'
            transhtml += '<input type="checkbox" name="choice" id="{}" value="{}" checked>{}</td></tr>'.format(orig_tokens, orig_tokens, orig_tokens)
        transhtml += '</table>'
        # Capitalize tokens if in first place        
        if index==0:
            capitalized = False
            if ' ' in tokens:
                toks = []
                tok_list = tokens.split()
                for tok in tok_list:
                    if capitalized:
                        toks.append(tok)
                    elif self.source.is_punc(tok):
                        toks.append(tok)
                    else:
                        toks.append(tok.capitalize())
                        capitalized = True
                tokens = ' '.join(toks)
            else:
                tokens = tokens.capitalize()
        self.choice_tgroups = choice_tgroups
        if self.record:
            self.record.choice_tgroups = choice_tgroups
        self.html = (orig_tokens, self.color, transhtml, index, self.source_html)
#        print("HTML for {}".format(self))
#        for h in self.html:
#            print(" {}".format(h))

    def unseg_tokens(self):
        """Rejoin tokens in original_token_str that were segmented when the Sentence was created."""
        toksegs = self.sentence.toksegs
        if toksegs:
            remove = []
            for triple in toksegs:
                tok, seg, index = triple
                if index in self.indices:
                    # The tokseg is in this Seg; join it
                    self.original_token_str = self.original_token_str.replace(' '.join(seg), tok)
                    remove.append(triple)
            for triple in remove:
                toksegs.remove(triple)

    @staticmethod
    def remove_spec_pre(string):
        """Remove special prefixes, for example, '%ND~'."""
        if '%' in string:
            string = ''.join(Seg.special_re.split(string))
        return string

    @staticmethod
    def clean_spec(string, specpre=True):
        """Remove special prefixes and connecting characters."""
        if specpre:
            string = Seg.remove_spec_pre(string)
        # prefix ~
        if string[0] == '~':
            string = string[1:]
        # connecting _ and ~
        string = string.replace('  ', ' ').replace('_', ' ').replace('~', ' ')
        return string

    @staticmethod
    def join_toks(string):
        """Join tokens as specified by the join character."""
        return string.replace(' ' + Seg.join_tok_char, '')

    @staticmethod
    def join_toks_in_strings(stringlists):
        """Join tokens in each item in list of strings."""
        for i, stringlist in enumerate(stringlists):
            for j, string in enumerate(stringlist):
                if Seg.join_tok_char in string:
                    stringlists[i][j] = Seg.join_toks(string)

class SuperSeg(Seg):
    """SuperSegment: joins Segment instances into larger units, either via a Join rule
    or a Group."""

    def __init__(self, segmentation, segments=None, features=None, name=None, join=None, verbosity=0):
#        print("Creating SuperSeg for {} with features {}".format(segments, features))
        Seg.__init__(self, segmentation)
        self.segments = segments
        self.name = name
        self.join = join
        # If join is a group, this is a list of features (or True if there are none), one for seach segment
        self.features = features
        self.order = list(range(len(segments)))
        self.head_seg = segments[join.head_index]
        self.head_tok = self.head_seg.head_tok
        # This has to happen before head attributes are set
        self.apply_changes(verbosity=verbosity)
        self.shead = self.head_seg.shead
        self.scats = self.head_seg.scats
        self.thead = self.head_seg.thead
        if self.head_seg.special:
            self.special = True
        ## Copy properties of sub-Segments
        self.record = self.segments[0].record
        raw_tokens = []
        token_str = []
        # Indices are those of sub-Segments.
        self.indices = reduce_lists([seg.indices for seg in segments])
        self.indices.sort()
        self.translation = []
        gname = []
#        self.merger_gnames = []
        self.cleaned_trans = []
        self.tgroups = []
        self.original_token_str = ' '.join([seg.original_token_str for seg in self.segments])
        # Rejoin source tokens segmented during Sentence creation
        self.unseg_tokens()
        for i in self.order:
            if i < 0:
                # This represents a target token with no corresponding source token
                continue
            segment = self.segments[i]
            if verbosity:
                print("Setting SuperSeg properties, segment {}, current ct {}".format(segment, self.cleaned_trans))
                print(" Segment cleaned_trans: {}, translation {}".format(segment.cleaned_trans, segment.translation))
            if self.cleaned_trans:
                if segment.cleaned_trans:
                    self.cleaned_trans = [ct1 + ct2 for ct1 in self.cleaned_trans for ct2 in segment.cleaned_trans]
            else:
                self.cleaned_trans = segment.cleaned_trans
#            print(" Segment {}, tgroups {}".format(segment, segment.tgroups))
            if self.tgroups:
                if segment.tgroups:
                    # Segment may have no translation (e.g., "de")
                    self.tgroups = [tg1 + tg2 for tg1 in self.tgroups for tg2 in segment.tgroups]
            else:
                self.tgroups = segment.tgroups
#            print("Segments {}, tgroups {}".format(i, self.tgroups))
            self.translation.append(segment.translation)
#            print("Superseg cleaned_trans: {}, translation {}".format(self.cleaned_trans, self.translation))
            raw_tokens.append(segment.raw_token_str)
            token_str.append(segment.token_str)
            gname.append(segment.gname or '')
#            if segment.merger_gnames:
#                self.merger_gnames.extend(segment.merger_gnames)
        self.gname = "++".join(gname)
        self.raw_token_str = ' '.join(raw_tokens)
        self.token_str = ' '.join(token_str)
        # calculate depth from depth of segment components
        self.depth = self.get_depth()

    def __repr__(self):
        if self.name:
            return self.name
        elif self.segments:
            return ">>" + "++".join([seg.token_str for seg in self.segments]) + "<<"
        else:
            return "SuperSeg"

    def get_depth(self):
        d = 1
        d += max([segment.depth for segment in self.segments])
        return d

    def apply_changes(self, verbosity=1):
        """Implement the changes to features and order specified in the Join or Group instance."""
#        print("Superseg {} applying changes".format(self))
        self.join.apply(self, verbosity=verbosity)

class Segment(Seg):
    """Sentence segmentation segment, realization of a Group, possibly merged with another. Displayed in GUI."""

    def __init__(self, segmentation, indices, translation, tokens, color=None, space_before=1,
                 treetrans=None, sfeats=None, tgroups=None,
                 head=None, tok=None, spec_indices=None, session=None, gname=None, is_punc=False):
#        print("Creating Segment for indices {}, translation {}, head {}, sfeats {}".format(indices, translation, head, sfeats))
        Seg.__init__(self, segmentation)
        if sfeats:
            sfeat_dict = sfeats[0]
            self.shead_index = 0
            self.shead = [(sfeat_dict.get('root'), sfeat_dict.get('features'), sfeat_dict.get('pos'))]
            self.scats = sfeat_dict.get('cats', set())
        else:
            self.shead_index = -1
            self.shead = None
            self.scats = None
        self.treetrans = treetrans
        self.indices = indices
        self.space_before = space_before
        # Token instance for the head if there is one
        self.head_tok = tok
        # Are there any alternatives among the translations?
        self.any_choices = any(['|' in t for t in translation])
        # For each translation alternative, separate words, each of which can have alternatives (separated by '|').
        # self.translation is a list of lists
        self.translation = [(t.split() if isinstance(t, str) else t) for t in translation]
        self.cleaned_trans = None
        self.tokens = tokens
#        # Pre-parenthetical, parenthetical, post-parenthetical portions
#        self.has_paren = has_paren
#        # Whether this an unattached segment within another segment
#        self.is_paren = is_paren
        self.token_str = ' '.join(tokens)
        self.raw_token_str = self.token_str[:]
#        # Later set this to the Segment instance that intervenes within this one
#        self.paren_seg = None
#        # Stuff to do when there's a parenthetical segment within the segment
#        if has_paren:
#            pre, paren, post = has_paren
#            self.paren_tokens = [p[0] for p in paren]
#            self.paren_indices = [p[1] for p in paren]
#            self.original_tokens = pre + post
#            self.pre_token_str = ' '.join(pre)
#            self.paren_token_str = ' '.join(self.paren_tokens)
#            # There could be special tokens in the parenthetical part
#            self.paren_token_str = Seg.clean_spec(self.paren_token_str)
#            self.post_token_str = ' '.join(post)
#        else:
        self.original_tokens = tokens
        self.original_token_str = ' '.join(self.original_tokens)
        # If there are special tokens in the source language, fix them here.
#        if '%' in self.token_str: # or '~' in self.token_str:
        if self.head_tok.special:
#            print("Handling special item {}, tokens {}, translation {}".format(self.token_str, tokens, translation))
            self.special = True
            # Create the source and target strings without special characters
            if translation:
                self.cleaned_trans = self.translation[:] #translation[:]
#                self.translation = [translation]
            else:
                spec_toks = [t for t in tokens if t[0] != '~']
                self.cleaned_trans = [spec_toks]
                tgroups = [spec_toks]
            self.token_str = Seg.clean_spec(self.token_str)
            self.original_token_str = Seg.clean_spec(self.original_token_str)
        if '~' in self.original_token_str:
            self.original_token_str = Seg.clean_spec(self.original_token_str)
        if '~' in self.token_str:
            self.token_str = Seg.clean_spec(self.token_str)
        if not self.cleaned_trans:
            self.cleaned_trans = self.translation[:]
#        print("cleaned {}, translation {}".format(self.cleaned_trans, self.translation))
        # Join tokens in cleaned translation if necessary
        if treetrans:
            thead_indices = [g.head_index for g in treetrans.tgroups]
#            print("thead indices {}, cleaned trans {}, translation {}".format(thead_indices, self.cleaned_trans, self.translation))
            self.thead = [o[i] for i, o in zip(thead_indices, self.translation)]
        else:
            self.thead = None
        self.color = color
        # Whether this segment is just punctuation
        self.is_punc = is_punc
        # Name of the group instantiated in this segment
        self.gname = gname
        # Triples for each merger with the segment
#        self.merger_gnames = merger_groups
        # Target-language groups
        self.tgroups = tgroups or [[""]] * (len(self.translation) or 1)
        # Target-language group strings, ordered by choices; gets set in set_html()
        self.choice_tgroups = None
        # The session associated with this segmentation segment
        self.session = session
        # Create a record for this segment if there's a session running and it's not punctuation
        if session and session.running and not self.source.is_punc(self.token_str):
            self.record = self.make_record(session, segmentation.sentence)
        else:
            self.record = None
#        print("Created {}, thead {}, translation {}, cleaned {}".format(self, self.thead, self.translation, self.cleaned_trans))

    def __repr__(self):
        """Print name."""
        return ">>{}<<".format(self.token_str)

    ## Record

    def make_record(self, session=None, sentence=None):
        """Create the SegRecord object for this Segment."""
        if sentence:
            return SegRecord(self, sentence=sentence.record, session=session)

    ## Matching

    def has_child(self):
        return len(self.tokens) > 1

class SNode:
    """Sentence token and its associated analyses and variables."""

    def __init__(self, index, analyses, sentence, raw_indices,
                 toks=None, tok=None, toktype=1): #, del_indices=None):
        # Raw form in sentence (possibly result of segmentation)
        self.token = tok.fullname
        # Token type (used to distinguish prefix from suffix punctuation.
        self.toktype = toktype
        # Original form of this node's token (may be capitalized)
#        self.rawtoken = rawtoken
        # Token objects
        self.toks = toks
        # Head Token object
        self.tok = tok
        # Position in sentence
        self.index = index
        # Positions in original sentence
        self.raw_indices = raw_indices
#        # Positions of deleted tokens
#        self.del_indices = del_indices or []
        # List of analyses
        if analyses and not isinstance(analyses, list):
            analyses = [analyses]
        if not analyses:
            analyses = [{'root': token}]
        self.analyses = analyses
        # Back pointer to sentence
        self.sentence = sentence
        # Raw sentence tokens associated with this SNode
#        print("Tokens {}".format(sentence.tokens))
#        print("Raw indices {}".format(self.raw_indices))
        self.raw_tokens = [sentence.tokens[i] for i in self.raw_indices]
        # Any deleted tokens to the left or right of the SNode token
        self.left_delete = None
        self.right_delete = None
        token_headi = self.raw_tokens.index(self.token)
        if token_headi != 0:
            self.left_delete = self.raw_tokens[:token_headi]
        if token_headi != len(self.raw_tokens) - 1:
            self.right_delete = self.raw_tokens[token_head1:]
        # We'll need these for multiple matchings
        self.cats = self.get_cats()
        # Indices of candidate gnodes for this snode found during lexicalization
        self.gnodes = None
        # Dict of variables specific to this SNode
        self.variables = {}
        ## Tokens in target language for this SNode
        self.translations = []
        ## Groups found during candidate search
        self.group_cands = []
#        print("Created SNode with tok {}, token {}, analyses {}".format(self.tok, self.token, self.analyses))

    def __repr__(self):
        """Print name."""
        return "*{}:{}".format(self.token, self.index)

    def get_analysis(self):
        """The single analysis for this node."""
        return self.analyses[0]

    def is_punc(self):
        """Is this node a punctuation node?"""
        return self.get_analysis().get('pos') == 'pnc'

    def is_unk(self):
        """Does this node have no analysis, no known category or POS?"""
#        if self.is_special():
#            return False
        if '~' in self.tok.name:
            # A special phrase (MWE) that bypasses POS tagging
            return False
        a = self.get_analysis()
        return not (a.get('pos') or a.get('cats') or a.get('features'))

    def is_special(self):
        """Is this 'special' (for example, a number)?"""
        return Token.is_special(self.token)

    ## Create IVars and (set) Vars with sentence DS as root DS

    def ivar(self, key, name, domain, ess=False):
        self.variables[key] = IVar(name, domain, rootDS=self.sentence.dstore,
                                   essential=ess)

    def svar(self, key, name, lower, upper, lower_card=0, upper_card=MAX,
             ess=False):
        self.variables[key] = Var(name, lower, upper, lower_card, upper_card,
                                  rootDS=self.sentence.dstore, essential=ess)

    def lvar(self, key, name, lower, upper, lower_card=0, upper_card=MAX,
             ess=False):
        self.variables[key] = LVar(name, lower, upper, lower_card, upper_card,
                                   rootDS=self.sentence.dstore, essential=ess)

    def create_variables(self, verbosity=0):
        if not self.gnodes:
            # Nothing matched this snode; all variables empty
            self.variables['gnodes'] = EMPTY
            self.variables['cgnodes'] = EMPTY
            self.variables['agnodes'] = EMPTY
#            self.variables['mgnodes'] = EMPTY
            self.variables['features'] = EMPTY
        else:
            # GNodes associated with this SNode: 0, 1, or 2
            upper = set(self.gnodes)
            self.svar('gnodes', "w{}->gn".format(self.index), set(),
                      upper,
                      0, 2, ess=True)
            # Concrete GNodes associated with this SNode: must be 1
            self.svar('cgnodes', "w{}->cgn".format(self.index), set(),
                      {gn.sent_index for gn in self.sentence.gnodes if not gn.cat},
                      1, 1)
            # Abstract GNodes associated with this SNode: 0 or 1
            self.svar('agnodes', "w{}->agn".format(self.index), set(),
                      {gn.sent_index for gn in self.sentence.gnodes if gn.cat},
                      0, 1)
            # Features
            features = self.get_features()
            if len(features) > 1:
                self.lvar('features', 'w{}f'.format(self.index),
                          [], features, 1, 1)
            else:
                # Only one choice so features are determined for this SNode
                self.variables['features'] = DetLVar('w{}f'.format(self.index), features)

    def get_cats(self):
        """The set of categories for the node's token, or None."""
        if not self.analyses:
            return None
        cats = set()
        for analysis in self.analyses:
            if 'cats' in analysis:
                cats.update(analysis['cats'])
        return cats

    def get_features(self):
        """The list of possible FeatStruct objects for the SNode."""
        features = []
        if self.analyses:
            for analysis in self.analyses:
                if 'features' in analysis:
                    features.append(analysis['features'])
                else:
                    features.append(FeatStruct({}))
        return features

    def neg_match(self, grp_specs, verbosity=0, debug=False):
        """Does this node match a negative group condition, with grp_spec either a FeatStruc
        or a category? Look through analyses until one *fails* to match."""
        for grp_spec in grp_specs:
#            print("Neg match: {}".format(grp_spec))
            matched = True
            # See if any analysis fails to match this grp_spec; if not succeed
            for analysis in self.analyses:
#                print(" {}".format(analysis))
                if isinstance(grp_spec, str):
                    sn_cats = analysis.get('cats', [])
                    if grp_spec in sn_cats or grp_spec == analysis.get('pos'):
                        # Matches, keep looking
                        continue
                    else:
                        matched = False
                        # Go to next grp_spec
                        break
                else:
                    sn_feats = analysis.get('features')
                    if sn_feats:
                        u_features = sn_feats.unify_FS(grp_spec, strict=True, verbose=verbosity>1)
                        if u_features != 'fail':
                            # Matches, keep looking
                            continue
                        else:
                            matched = False
                            # Go to next grp_spec
                            break
                    else:
                        matched = False
                        # Go to next grp_spec
                        break
#            print(" Matched: {}".format(matched))
            if matched:
                return True
        # None matched
        return False

    def match(self, grp_item, grp_feats, verbosity=0, debug=False):
        """Does this node match the group item (word, root, category) and
        any features associated with it?"""
        # If this is a punctuation node, it can't match a group item unless the item is also punctuation (not alphanum)
        if self.is_punc() and grp_item.isalnum():
            return False
        if verbosity > 1 or debug:
            print('   SNode {} with features {} trying to match item {} with features {}'.format(self, self.analyses, grp_item, grp_feats.__repr__()))
        # If item is a category, don't bother looking at token
        is_cat = Token.is_cat(grp_item)
        is_spec = Token.is_special(grp_item)
        if is_spec and self.tok.special:
#            Token.is_special(self.token):
            if verbosity > 1 or debug:
                print("Special entry {} for {}".format(grp_item, self.token))
            token_type = self.token.split('~')[0]
            if token_type.startswith(grp_item):
                # Special group item matches node token (grp_item could be shorter than token_type)
                return None
        # Check whether the group item is really a set item (starting with '$$'); if so, drop the first '$' before matching
        if is_cat and Token.is_set(grp_item):
            grp_item = grp_item[1:]
        # If group token is not cat and there are no group features, check for perfect match
        if not is_cat and not grp_feats:
            if self.tok.name == grp_item:
                if verbosity or debug:
                    print("    Matches trivially")
                return None
        # Go through analyses, checking cat, root, and features (if any group features)
        results = []
        # 2018.2.23: updated to exclude case where SNode has no analyses; it always does
        #  also nodes can match group category even if they don't have associated groups of their own
        for analysis in self.analyses:
            node_features = analysis.get('features')
            node_cats = analysis.get('cats', [])
            node_root = analysis.get('root', '')
#            node_pos = analysis.get('pos', '')
#            node_root_pos = node_root + '_' + node_pos if node_pos else None
            node_roots = None
            if verbosity > 1 or debug:
                print("    Trying to match analysis: {}/{}/{} against group {}".format(node_root, node_cats, node_features.__repr__(), grp_item))
            if '_' in node_root: # and not Seg.special_re.match(node_root):
                # Numbers and other special tokens also contain '_'
                node_roots = []
                # An ambiguous root in analysis, for example, ser|ir in Spa
                r, p = node_root.split('_')
                for rr in r.split('|'):
                    node_roots.append(rr + '_' + p)
            # Match group token
            if is_cat:
                if grp_item in node_cats:
#                    if node_root not in self.sentence.language.groups:
#                        if verbosity > 1 or debug:
#                            print("      Cat succeeds but there's no group for {}".format(grp_item, node_root))
#                        continue
#                    else:
                    if verbosity > 1 or debug:
                        print("      Succeeding for cat {} for node with root {}".format(grp_item, node_root))
                else:
                    # Fail because the group category item doesn't match the node categories
                    if verbosity > 1 or debug:
                        print("      Failing because group cat item doesn't match node cats")
                    continue
            else:
                # Not a category, has to match the root
                if node_roots:
                    if verbosity > 1 or debug:
                        print("      Checking node roots {}".format(node_roots))
                    m = firsttrue(lambda x: x == grp_item, node_roots)
                    if m:
                        node_root = m
                    elif grp_item != node_root:
                        continue
#                    else:
#                        continue
                elif grp_item != node_root:
                    continue
            if verbosity > 1 or debug:
                print("      Matched token")
            # Match features if there are any
            if node_features:
                if grp_feats:
                    # 2015.7.5: strict option added to force True feature in grp_features
                    # to be present in node_features, e.g., for Spanish reflexive
                    if verbosity > 1 or debug:
                        print("    Unifying n feats {} with g feats {}".format(node_features, grp_feats.__repr__()))
                    nfeattype = type(node_features)
                    if nfeattype == FSSet:
                        u_features = node_features.unify_FS(grp_feats, strict=True, verbose=verbosity>1)
                    else:
                        u_features = simple_unify(node_features, grp_feats, strict=True)
                    if u_features != 'fail':
                        # SUCCEED: matched token and features
                        results.append((node_root, u_features))
                else:
                    # SUCCEED: matched token and no group features to match
                    results.append((node_root, node_features))
            else:
                # SUCCEED: group has features but node doesn't
                results.append((grp_item, grp_feats))
        if results:
            if verbosity > 1 or debug:
                print("  Returning match results: {}".format(results))
            return results
        return False

class GInst:

    """Instantiation of a group; holds variables and GNode objects."""

    def __init__(self, group, sentence, head_index, snode_indices, index):
#        print("Creating GInst for group {} with head i {} and snode indices {}".format(group, head_index, snode_indices))
        # The Group object that this "instantiates"
        self.group = group
        self.sentence = sentence
        self.source = sentence.language
        self.target = sentence.target
        # Index of group within the sentence
        self.index = index
        # Index of SNode associated with group head
        self.head_index = head_index
#        self.head_pos = group.pos
        # List of GNodes
        self.nodes = []
        # Index of the GNode that is the head
        ghead_index = group.head_index
        for index, sntups in enumerate(snode_indices):
            # sntups is a list of snindex, match features, token, create? tuples
            deleted = False
            for snindex, match, token, create in sntups:
                if not create:
                    deleted = True
                    break
            if deleted:
                # If this is before where the head should be, decrement that index
                if index <= ghead_index:
                    ghead_index -= 1
                # Increment index so indices correspond to raw group tokens
                continue
            else:
                self.nodes.append(GNode(self, index, sntups))
        # The GNode that is the head of this GInst
        if ghead_index > len(self.nodes) - 1:
            print("Problem instantiating {} for {}; head index {}".format(group, self.nodes, ghead_index))
        self.ghead_index = ghead_index
        self.head = self.nodes[ghead_index]
        # Dict of variables specific to this group
        self.variables = {}
        # List of target language groups, gnodes, tnodes
        self.translations = []
        self.ngnodes = len(self.nodes)
        # Number of abstract nodes
        self.nanodes = len([n for n in self.nodes if n.cat])
        # Number of concrete nodes
        self.ncgnodes = self.ngnodes - self.nanodes
        # TreeTrans instance for this GInst; saved here to prevent multiple TreeTrans translations
        self.treetrans = None
        # Indices of GInsts that this GINst depends on; set in Sentence.lexicalize()
        self.dependencies = None
        # Possible snode indices for lexical and category nodes.
        self.sindices = [[], []]

    def __repr__(self):
        return '<<{}:{}>>'.format(self.group.name, self.group.id)

    def display(self, word_width=10, s2gnodes=None):
        """Show group in terminal."""
        s = '<{}>'.format(self.index).rjust(4)
        n_index = 0
        n = self.nodes[n_index]
        ngnodes = len(self.nodes)
        for gn_indices in s2gnodes:
            if n.sent_index in gn_indices:
                i = '*{}*' if n.head else "{}"
                s += i.format(n.index).center(word_width)
                n_index += 1
                if n_index >= ngnodes:
                    break
                else:
                    n = self.nodes[n_index]
            else:
                s += ' '*word_width
        print(s)

    def pos_pairs(self):
        """Return position constraint pairs for gnodes in the group."""
        gnode_pos = [gn.sent_index for gn in self.nodes]
        return set(itertools.combinations(gnode_pos, 2))

    def gnode_sent_index(self, index):
        """Convert gnode index to gnode sentence index."""
        return self.nodes[index].sent_index

    def get_agr(self):
        """Return agr constraints for group, converted to tuples."""
        result = []
        if self.group.agr:
            for a in copy.deepcopy(self.group.agr):
                feats = [tuple(pair) for pair in a[2:]]
                a[2:] = feats
                # Convert gnode positions to sentence positions
                a[0] = self.gnode_sent_index(a[0])
                a[1] = self.gnode_sent_index(a[1])
                result.append(tuple(a))
        return set(result)

    ## Create IVars and (set) Vars with sentence DS as root DS

    def ivar(self, key, name, domain, ess=False):
        self.variables[key] = IVar(name, domain, rootDS=self.sentence.dstore,
                                   essential=ess)

    def svar(self, key, name, lower, upper, lower_card=0, upper_card=MAX,
             ess=False):
        self.variables[key] = Var(name, lower, upper, lower_card, upper_card,
                                  rootDS=self.sentence.dstore,
                                  essential=ess)

    def create_variables(self, verbosity=0):
        ngroups = len(self.sentence.groups)
        nsnodes = len(self.sentence.nodes)
        cand_snodes = self.sindices[0] + self.sindices[1]
#            self.sentence.covered_indices
#        print("Creating variables for {}, # abs nodes {}".format(self, self.nanodes))
        if self.dependencies:
            self.variables['deps'] = DetVar('deps{}'.format(self.index), self.dependencies)
        else:
            self.variables['deps'] = EMPTY
        # GNode indices for this GInst (determined)
        self.variables['gnodes'] = DetVar('g{}->gnodes'.format(self.index), {gn.sent_index for gn in self.nodes})
        # Abstract GNode indices for GInst (determined)
        if self.nanodes:
            self.variables['agnodes'] = DetVar('g{}->agnodes'.format(self.index), {gn.sent_index for gn in self.nodes if gn.cat})
            # Concrete GNode indices for GInst (determined)
            self.variables['cgnodes'] = DetVar('g{}->cgnodes'.format(self.index), {gn.sent_index for gn in self.nodes if not gn.cat})
        else:
            self.variables['agnodes'] = EMPTY
            self.variables['cgnodes'] = self.variables['gnodes']
        # SNode positions of GNodes for this GInst
        self.svar('gnodes_pos', 'g{}->gnodes_pos'.format(self.index),
                  set(), set(cand_snodes), self.ngnodes, self.ngnodes)
        # SNode positions of abstract GNodes for this GInst
        if self.nanodes == 0:
            # No abstract nodes
            self.variables['agnodes_pos'] = EMPTY
            # SNode positions of concrete GNodes for this GInst
            self.variables['cgnodes_pos'] = self.variables['gnodes_pos']
        else:
            # Position for each abstract node in the group
            self.svar('agnodes_pos', 'g{}->agnodes_pos'.format(self.index),
                      set(), set(cand_snodes), self.nanodes, self.nanodes)
            # Position for each concrete node in the group
            self.svar('cgnodes_pos', 'g{}->cgnodes_pos'.format(self.index),
                      set(), set(cand_snodes), self.ncgnodes, self.ncgnodes)
        # Determined variable for within-source agreement constraints, gen: 0}
        agr = self.get_agr()
        if agr:
            self.variables['agr'] = DetVar('g{}agr'.format(self.index), agr)

    def set_translations(self, verbosity=0):
        """Find the translations of the group in the target language."""
        translations = self.group.get_translations()
        # Sort group translations by their translation frequency
        Group.sort_trans(translations)
        if verbosity:
            print("Setting translations for {}: {}".format(self, translations))
        # If alignments are missing, add default alignment
        for i, t in enumerate(translations):
            if len(t) == 1:
                translations[i] = [t[0], {}]
#                                    {'align': list(range(len(self.nodes)))}]
        ntokens = len(self.group.tokens)
        for tgroup, s2t_dict in translations:
            nttokens = len(tgroup.tokens)
            if verbosity > 1:
                print("   tgroup {}, s2t_dict {}".format(tgroup, s2t_dict))
            # If there's no explicit alignment, it's the obvious default
            if 'align' in s2t_dict:
                alignment = s2t_dict.get('align')
            else:
                alignment = list(range(ntokens))
                for ia, a in enumerate(alignment):
                    if a >= nttokens:
                        alignment[ia] = -1
            if isinstance(tgroup, str):
                # First find the target Group object
                tgroup = self.target.groupnames[tgroup]
#            print("TGroup: {}, alignment {}".format(tgroup, alignment))
            # Make any TNodes (for target words not corresponding to any source words)
            tnodes = []
            # Target group has more nodes than source group.
            # Indices of groups that are not empty:
            full_t_indices = set(alignment)
            empty_t_indices = set(range(nttokens)) - full_t_indices
            if empty_t_indices:
#                print(" Extra target nodes, empty {}, full {}".format(empty_t_indices, full_t_indices))
                for i in empty_t_indices:
                    empty_t_token = tgroup.tokens[i]
                    empty_t_feats = tgroup.features[i] if tgroup.features else None
                    tnodes.append(TNode(empty_t_token, empty_t_feats, tgroup, i, self))
            # Deal with individual gnodes in the group
            gnodes = []
            tokens = tgroup.tokens
            features = tgroup.features
            # Go through source group nodes, finding alignments and agreement constraints
            # with target group nodes
            for gnode in self.nodes:
                gn_index = gnode.index
                gn_token = gnode.token
                # Align gnodes with target tokens and features
                targ_index = alignment[gn_index]
                if targ_index < 0:
#                    print("No targ item for gnode {}".format(gnode))
                    # This means there's no target language token for this GNode.
                    continue
#                print(" tgroup {}, gnode {}, gn_index {}, gn token {}, targ index {}".format(tgroup, gnode, gn_index, gn_token, targ_index))
                agrs = None
                if s2t_dict.get('agr'):
                    agr = s2t_dict['agr'][gn_index]
                    if agr:
                        tindex, stagr = agr
                        targ_index = tindex
#                        print(" s2t_dict agrs {}, tindex {}, stagr {}".format(agrs, tindex, stagr))
                        agrs = stagr
                if gnode.special:
                    spec_trans = self.source.translate_special(gn_token)
                    token = spec_trans
                else:
                    token = tokens[targ_index]
                feats = features[targ_index] if features else None
                gnodes.append((gnode, token, feats, agrs, targ_index))
            self.translations.append((tgroup, gnodes, tnodes))

class GNode:

    """Representation of a single node (word, position) within a GInst object."""

    def __init__(self, ginst, index, snodes):
        self.ginst = ginst
        self.index = index
        self.sentence = ginst.sentence
        self.snode_indices = [s[0] for s in snodes]
        self.snode_anal = [s[1] for s in snodes]
        self.snode_tokens = [s[2] for s in snodes]
        # Whether this is the head of the group
        self.head = index == ginst.group.head_index
        # Group word, etc. associated with this node
        gtoken = ginst.group.tokens[index]
        self.gtoken = gtoken
        # If this is a set node, use the sentence token instead of the cat name
        if Token.is_set(gtoken):
            self.token = self.sentence.nodes[snodes[0][0]].token
        else:
            self.token = gtoken
        if len(self.snode_tokens) == 1 and Token.is_special(self.snode_tokens[0]):
            self.token = self.snode_tokens[0]
#        print("Creating GNode for {} with indices {}, stokens {} and token {}".format(ginst, self.snode_indices, self.snode_tokens, self.token))
        # Whether the associated token is abstract (a category)
        self.cat = Token.is_cat(self.token)
        # Whether the associated token is special (for example, a numeral).
        self.special = Token.is_special(self.token)
        # Features associated with this group node
        groupfeats = ginst.group.features
        if groupfeats:
            self.features = groupfeats[index]
        else:
            self.features = None
        self.variables = {}

    def __repr__(self):
        return "{}|{}".format(self.ginst, self.token)

    ## Create IVars and (set) Vars with sentence DS as root DS

    def ivar(self, key, name, domain, ess=False):
        self.variables[key] = IVar(name, domain, rootDS=self.sentence.dstore,
                                   essential=ess)

    def svar(self, key, name, lower, upper, lower_card=0, upper_card=MAX,
             ess=False):
        self.variables[key] = Var(name, lower, upper, lower_card, upper_card,
                                  rootDS=self.sentence.dstore,
                                  essential=ess)

    def create_variables(self, verbosity=0):
        nsnodes = len(self.sentence.nodes)
        # SNode index for this GNode
        self.ivar('snodes', "gn{}->w".format(self.sent_index), set(self.snode_indices))

class TNode:

    """Representation of a node within a target language group that doesn't
    have a corresponding node in the source language group that it's the
    translation of."""

    def __init__(self, token, features, group, index, ginst):
        self.token = token
        self.features = features
        self.group = group
#        self.sentence = ginst.sentence
        self.index = index
        self.ginst = ginst
#        print(" Creating TNode for {}, features {}, group {}, index {}".format(token, features, group, index))

#    def generate(self, limit_forms=True, verbosity=0):
#        """Generate forms for the TNode."""
##        print("Generating form for target token {} and features {}".format(self.token, self.features))
#        if Entry.is_lexeme(self.token):
#            return self.sentence.target.generate(self.token, self.features)
#        else:
#            return [self.token]

    def __repr__(self):
        return "~{}|{}".format(self.ginst, self.token)

class TreeTrans:
    """Translation of a tree: a group or two or more groups joined by merged nodes."""

    def __init__(self, segmentation, tree=None, ginst=None,
                 abs_gnode_dict=None, gnode_dict=None, group_attribs=None,
                 # Whether the tree has any abstract nodes (to merge with concrete nodes)
                 any_anode=False, index=0, top=False, verbosity=0):
        # The segmentation generating this translation
        self.segmentation = segmentation
        self.source = segmentation.source
        self.target = segmentation.target
        self.sentence = segmentation.sentence
        # Dict keeping information about each gnode; this dict is shared across different TreeTrans instances
        self.abs_gnode_dict = abs_gnode_dict
        self.gnode_dict = gnode_dict
        # A set of sentence node indices
        self.tree = tree
        # Target position indices
        self.ttree = set()
        # TTs contained within this TT
        self.subTTs = []
        # Whether this is the top of a tree
        self.top = top
        # All target groups for nodes within this TT
        self.all_tgroups = []
        # Tgroups in output order for each translation
        self.ordered_tgroups = []
        # Merged group indices
        self.mergers = []
        snode_indices = list(tree)
        snode_indices.sort()
        self.snode_indices = snode_indices
        self.snodes = [self.sentence.nodes[i] for i in snode_indices]
        self.sol_gnodes_feats = [segmentation.gnodes_feats[i] for i in snode_indices]
        # The GInst at the top of the tree
        self.ginst = ginst
        # Save this TreeTrans in the GInst
        ginst.treetrans = self
        self.index = index
        self.any_anode = any_anode
        self.group_attribs = group_attribs or []
        # Translation groups
        self.tgroups = [g[0] for g in group_attribs]
        # TNodes
        self.tnodes = [g[1] for g in group_attribs]
        # Root domain store for variables
        self.dstore = DStore(name="TT{}".format(self.index))
        # Order variables for each node, tree variables for groups
        self.variables = {}
        # pairs of node indices representing order constraints
        self.order_pairs = []
        # Order and disjunction constraints
        self.constraints = []
        # Create the solver for ordering elements within the TreeTrans
        self.solver = Solver(self.constraints, self.dstore, description='target tree realization',
                             verbosity=verbosity)
        # These are produced in self.build(); each only applies to the latest translation
        self.node_features = None
        self.group_nodes = None
        self.agreements = None
        self.nodes = []
        # Accumulate the nodes found in build()
        self.all_nodes = []
        # Final outputs; different ones have alternate word orders
        self.outputs = []
        # Strings representing outputs
        self.output_strings = []
        # Cache for node mergers
        self.cache = {}
        if verbosity:
            print("Created TreeTrans {}".format(self))
            print("  Gnode dict: {}".format(self.gnode_dict))
            print("  Indices: {}, tgroups {}, tnodes {}".format(self.tree, self.tgroups, self.tnodes))
            print("  Sol gnodes feats: {}".format(self.sol_gnodes_feats))

    def __repr__(self):
        return "{{{}}}->".format(self.ginst)

##    def get_merger_groups(self):
##        """A list of triples for each merger: gnode index within top-level group,
##        index of concrete gnode within its group, name of group for concrete node."""
##        groups = []
##        for index, gnodes in enumerate([s[0] for s in self.sol_gnodes_feats]):
##            # A single gnode means no merger
##            if len(gnodes) == 1:
##                continue
##            # A merger, find the concrete gnode
##            concgn = gnodes[0]
##            if gnodes[0].cat:
##                concgn = gnodes[1]
##            groups.append((index, concgn.index, concgn.ginst.group.name))
##        return groups

##    def get_merger_roots(self):
##        """A list of triples for each merger: gnode index within top-level group,
##        index of concrete gnode within its group, group head (root) for concrete node."""
##        roots = []
##        for index, gnodes in enumerate([s[0] for s in self.sol_gnodes_feats]):
##            # A single gnode means no merger
##            if len(gnodes) == 1:
##                continue
##            # A merger, find the concrete gnode
##            concgn = gnodes[0]
##            if gnodes[0].cat:
##                concgn = gnodes[1]
##            roots.append((index, concgn.index, concgn.ginst.group.head))
##        return roots
        
    def display(self, index):
        print("{}  {}".format(self, self.output_strings[index]))

    def display_all(self):
        for index in range(len(self.outputs)):
            self.display(index)

    @staticmethod
    def output_string(output):
        """Create an output string from a list."""
#        print("Creating output string for {}".format(output))
        out = []
        # False if there is a (root, pos, feats) tuple because generation
        # is delayed
        generated = True
        for word_list in output:
            if len(word_list) == 1:
                wl0 = word_list[0]
                out.append(wl0)
                if isinstance(wl0, list):
                    generated = False
            else:
                out.append('|'.join(word_list))
        if generated:
            out = ' '.join(out)
        return out

#    def get_abs_conc(self, gnodes, tg_groups, verbosity=0):
#        """If there are no gnodes, return None, None.
#        If there are two gnodes, then return the concrete, then the abstract one.
#        Otherwise return the single node and None."""
#        print("gnodes {}".format(gnodes))
#        if not gnodes:
#            return None, None
#        gna, gnc = None, None
#        if verbosity:
#            if len(gnodes) > 1:
#                print("  multiple gnodes: {}".format(gnodes))
#        if gnodes[0] in self.abs_gnode_dict and len(gnodes) > 1:
#            gna = self.abs_gnode_dict[gnodes[0]]
#            gnc = self.gnode_dict[gnodes[1]]
#        elif len(gnodes) > 1 and gnodes[1] in self.abs_gnode_dict:
#            gna = self.abs_gnode_dict[gnodes[1]]
#            gnc = self.gnode_dict[gnodes[0]]
#        else:
#            gnc = gnodes[0]
#        if gna:
#            if verbosity > 1:
#                print("   gna: {}".format(gna))
#                print("   gnc: {}".format(gnc))
#                if len(gna) > 1:
#                    print("   multiple translations for abstract node: {}".format(gna))
#            gna1 = firsttrue(lambda x: x[0] in tg_groups, gna)
#            if verbosity:
#                print("   abstract gnode tuple: {}".format(gna1))
#            gnc1 = firsttrue(lambda x: x[0] in tg_groups, gnc)
#            if verbosity:
#                print("   concrete gnode tuple: {}".format(gnc1))
#                print("   merging nodes: concrete {}, abstract {}".format(gnc1, gna1))
#            return gnc1, gna1
#        if gnc:
#            if verbosity > 1 and len(gnc) > 1:
#                print("   multiple translations for concrete node: {}".format(gnc))
#        return gnc, gna

    def make_cache_key(self, concrete_gn_tuple, abstract_gn_tuple, verbosity=0):
        """Make the key for the cache of gnode info."""
        cache_key = None
#        print("Getting cache key for {} and {}".format(concrete_gn_tuple, abstract_gn_tuple))
        if abstract_gn_tuple:
            cache_key = ((concrete_gn_tuple[0], concrete_gn_tuple[-1]), (abstract_gn_tuple[0], abstract_gn_tuple[-1]))
        else:
            cache_key = concrete_gn_tuple[0], concrete_gn_tuple[-1]
        return cache_key

    def get_cached(self, concrete_gn_tuple, abstract_gn_tuple, cache_key=None, verbosity=0):
        """Get gnode information if already cached."""
        if not cache_key:
            cache_key = self.make_cache_key(concrete_gn_tuple, abstract_gn_tuple, verbosity=verbosity)
        if cache_key in self.cache:
            # merged nodes found in local cache
            cached = self.cache[cache_key]
            if verbosity > 1:
                print("   result already in cache: {}".format(cached))
            return cached
        return None

    def record_ind_feats(self, token='', tnode_index=-1, t_indices=None, targ_feats=None,
                         snode=None, node_index_map=None, verbosity=0):
        node_index_map[snode.index] = tnode_index
        if not t_indices:
            t_indices = []
        if not token:
            token = snode.token
        self.node_features.append([token, targ_feats, t_indices])
        if t_indices:
            feat_index = len(self.node_features) if token else []
            for t_index in t_indices:
                self.group_nodes[t_index] = [token, targ_feats, feat_index]

    def cache_gnodes(self, cache_key=None, token="", tnode_index=-1, t_indices=None, tg_merger_groups=None, targ_feats=None):
        self.cache[cache_key] = (token, tnode_index, t_indices, tg_merger_groups, targ_feats)
            
    def merge_agr_feats(self, agrs, targ_feats, features, verbosity=0):
        """Cause features in features to agree with targ_features for pairs agrs,
        returning targ_features.
        """
        if not targ_feats:
            targ_feats = FeatStruct({})
        if agrs:
            # Use an (unfrozen) copy of target features
            targ_feats = targ_feats.copy(True)
            if verbosity:
                print("  Causing sfeats {} to agree with tfeats {}".format(features, targ_feats.__repr__()))
            if features:
                targ_feats = features.agree_FSS(targ_feats, agrs)
            if verbosity:
                print("   Now: {} to agree with tfeats {}".format(features, targ_feats.__repr__()))
        return targ_feats

##    def make_merger_groups(self, tgroups, gnodes, tnode_index, verbosity=0):
##        """Record target merger groups and their target node index in mergers."""
##        tg_merger_groups = list(zip(tgroups, gnodes))
##        # Sort the groups with concrete first, abstract next
##        tg_merger_groups.sort(key=lambda x: x[1].cat)
##        tg_merger_groups = [x[0] for x in tg_merger_groups]
##        if verbosity:
##            print("   creating merger {} for tnode index {}".format(tg_merger_groups, tnode_index))
##        self.mergers.append((tnode_index, tg_merger_groups))
##        return tg_merger_groups    

    def build(self, tg_groups=None, tg_tnodes=None, verbosity=0):
        """Unify translation features for merged nodes, map agr features from source to target,
        generate surface target forms from resulting roots and features.
        tg_groups is a combination of target groups.
        2019.5.27: Changed to reflect the disappearance of merge nodes.
        """
        if verbosity:
            print('BUILDING {} with tgroups {} and tnodes {}'.format(self, tg_groups, tg_tnodes))
            print("  SNodes: {}".format(self.snodes))
        tnode_index = 0
        # Dictionary mapping source node indices to initial target node indices
        node_index_map = {}
        self.agreements, self.group_nodes = {}, {}
        self.node_features = []
        # reinitialize mergers
        self.mergers = []
        # Find the top-level tgroup
        top_group_attribs = list(itertools.filterfalse(lambda x: x[0] not in tg_groups, self.group_attribs))[0]
        if verbosity:
            print('Top group attribs: {}'.format(top_group_attribs))
        for snode, (gnodes, features) in zip(self.snodes, self.sol_gnodes_feats):
            if verbosity:
                fstring = "   snode {}, gnodes {}, features {}, tnode index {}"
                print(fstring.format(snode, gnodes, features.__repr__(), tnode_index))
            cache_key, token, targ_feats, agrs = None, None, None, None
            t_indices = []
            # Get the concrete and abstract gnodes if they exist
#            if merge:
#                gnode, gna1 = self.get_abs_conc(gnodes, tg_groups, verbosity=verbosity)
#            else:
            gnode = gnodes[0]
            gna1 = None
            if not gnode:
                # snode is not covered by any group
                self.record_ind_feats(tnode_index=tnode_index, snode=snode, node_index_map=node_index_map)
                tnode_index += 1
            else:
                # all other cases, there are one or more target translation groups
##                if gna1:
##                    # there are two nodes to be merged
##                    # There are two gnodes for this snode, one concrete, one abstract;
##                    # gna and gnc are lists of tuples for different translations
##                    if verbosity:
##                        print("   merging nodes: concrete {}, abstract {}".format(gnode, gna1))
##                    cache_key = self.make_cache_key(gnode, gna1)
##                    cached = self.get_cached(gnode, gna1, cache_key=cache_key, verbosity=verbosity)
##                    if cached:
##                        # merged nodes found in local cache
##                        tok, tn_i, t_i, tg, t_feats = cached
##                        self.mergers.append((tn_i, tg))
##                        if verbosity > 1:
##                            print("   mergers for {}: {}".format(self, self.mergers))
##                        self.record_ind_feats(token=tok, tnode_index=tn_i, t_indices=t_i, 
##                                              targ_feats=t_feats, snode=snode, node_index_map=node_index_map)
##                    else:
##                        # merged nodes not found in cache
##                        tgroups, tokens, targ_feats, agrs, t_index = zip(gna1, gnode)
##                        # Concrete node token
##                        token = tokens[1]
##                        # Unify target features of abstract and concrete nodes
##                        targ_feats = FeatStruct.unify_all(targ_feats)
##                        if targ_feats == 'fail':
##                            print("Merged target features fail to unify")
##                            return False
##                        # merge the agreements
##                        agrs = TreeTrans.merge_agrs(agrs)
##                        # record the target groups and their indices
##                        t_indices.extend([(tgroups[0], t_index[0]), (tgroups[1], t_index[1])])
##                        ## Record target merger groups and their target node index in mergers
##                        tg_merger_groups = self.make_merger_groups(tgroups, gnodes, tnode_index, verbosity=verbosity)
##                        # Make target and source features agree as required
##                        targ_feats = self.merge_agr_feats(agrs, targ_feats, features, verbosity=verbosity)
##                        self.record_ind_feats(token=token, tnode_index=tnode_index, t_indices=t_indices,
##                                              targ_feats=targ_feats, snode=snode, node_index_map=node_index_map)
##                        self.cache_gnodes(cache_key=cache_key, token=token, tnode_index=tnode_index, t_indices=t_indices,
##                                          tg_merger_groups=tg_merger_groups, targ_feats=targ_feats)
##                    
##                else:
                # only one gnode in list, no merger
                if verbosity > 1:
                    print("   single node to generate: {}".format(gnode))
                if gnode not in self.gnode_dict:
                    if verbosity > 1:
                        print("   not in gnode dict, skipping")
                    continue
                # translating single gnode
                gnode_tuple_list = self.gnode_dict[gnode]
                gnode_tuple = firsttrue(lambda x: x[0] in tg_groups, gnode_tuple_list)
                if verbosity > 1:
                    print("   gnode_tuple: {}, list {}".format(gnode_tuple, gnode_tuple_list))
                if not gnode_tuple:
                    print("Something wrong")
                cache_key = self.make_cache_key(gnode_tuple, None)
                cached = self.get_cached(gnode_tuple, None, cache_key=cache_key, verbosity=verbosity)
                if cached:
                    # translation already in local cache
                    tok, tn_i, t_i, x, t_feats = cached
                    self.record_ind_feats(token=tok, tnode_index=tn_i, t_indices=t_i,
                                          targ_feats=t_feats, snode=snode, node_index_map=node_index_map)
                else:
                    # translation not in local cache
                    tgroup, token, targ_feats, agrs, t_index = gnode_tuple
                    if len(tgroup.tokens) > 1:
                        t_indices.append((tgroup, t_index))
                    else:
                        t_indices = [(tgroup, 0)]
#                    print("tgroup {}, token {}, targ_feats {}, t_indices {}".format(tgroup, token, targ_feats, t_indices))
                    # Make target and source features agree as required
                    targ_feats = self.merge_agr_feats(agrs, targ_feats, features, verbosity=verbosity)
                    self.record_ind_feats(token=token, tnode_index=tnode_index, t_indices=t_indices,
                                          targ_feats=targ_feats, snode=snode, node_index_map=node_index_map)
                    self.cache_gnodes(cache_key=cache_key, token=token, tnode_index=tnode_index,
                                      t_indices=t_indices, targ_feats=targ_feats)
                        
                tnode_index += 1
        
        # Make indices for tgroup trees
        for src_index in self.tree:
            if src_index in node_index_map:
                self.ttree.add(node_index_map[src_index])
        # Add TNode elements
        tgnode_elements = []
        tginst, tnodes, agr, tgnodes = top_group_attribs
        if agr:
            self.agreements[tginst] = agr
            if verbosity > 1:
                print(" build(): tginst {} agr {}, agreements {}".format(tginst, agr, self.agreements))
        subtnodes = tg_tnodes[1] if len(tg_tnodes) > 1 else []
        # Incorporate TNodes into nodes and features of this TTrans
        self.add_tnodes(tnodes, subtnodes, tginst)
        return True

    def add_tnodes(self, tnodes, subtnodes, tginst):
        """Incorporate TNodes into nodes and features of TTrans."""
#        print("Adding tnodes {}".format(tnodes))
        for tnode in tnodes:
            features = tnode.features or FeatStruct({})
            src_index = len(self.node_features)
            self.ttree.add(src_index)
            index = [(tginst, tnode.index)]
            feat_index = len(self.node_features)
            self.node_features.append([tnode.token, features, index])
            self.group_nodes[index[0]] = [tnode.token, features, feat_index]
        # TNodes in subTTs
        for tnode in subtnodes:
            features = tnode.features or FeatStruct({})
            src_index = len(self.node_features)
            self.ttree.add(src_index)
            index = [(tnode.group, tnode.index)]
            feat_index = len(self.node_features)
            self.node_features.append([tnode.token, features, index])

    @staticmethod
    def get_root_POS(token):
        """Token may be something like guata_, guata_v, Ty_q_v."""
        if Token.is_special(token) or '_' not in token:
            return token, None
        root, x, pos = token.rpartition("_")
        if pos not in ['v', 'a', 'n']: # other POS categories possible?
            # the '_' is part of the word itself
            return token, None
        return root, pos

##    @staticmethod
##    def merge_agrs(agr_list):
##        """Merge agr dicts in agr_list into a single agr dict."""
##        result = {}
##        for agr in agr_list:
##            if not agr:
##                continue
##            for k, v in agr:
##                if k in result:
##                    if result[k] != v:
##                        print("Warning: agrs in {} failed to merge; {} and {} don't match".format(agr_list, result[k], v))
##                        return 'fail'
##                    else:
##                        continue
##                else:
##                    result[k] = v
##        return result

    def do_agreements(self, limit_forms=True, verbosity=0):
        """Do intra-group agreement constraints."""
        # Reinitialize nodes
#        print("Generating words in {}, features {}".format(self, self.node_features))
        self.nodes = []
        for group, agr_constraints in self.agreements.items():
#            print("Group {}, agr constraints {}".format(group, agr_constraints))
            for agr_constraint in agr_constraints:
                i1, i2 = agr_constraint[0], agr_constraint[1]
                feature_pairs = agr_constraint[2:]
                # Find the sentence nodes for the agreeing group nodes in the group_nodes dict
                agr_node1 = self.group_nodes[(group, i1)]
                agr_node2 = self.group_nodes[(group, i2)]
#                print("Found node1 {} and node2 {} for constraint {}".format(agr_node1, agr_node2, feature_pairs))
                agr_feats1, agr_feats2 = agr_node1[1], agr_node2[1]
                feat_index1, feat_index2 = agr_node1[2], agr_node2[2]
                # FSSets agr_feats1 and agr_feats2 have to be unfrozen before then can be made to agree
                if isinstance(agr_feats1, FeatStruct):
                    agr_feats1 = FSSet(agr_feats1)
                if isinstance(agr_feats2, FeatStruct):
                    agr_feats2 = FSSet(agr_feats2)
                agr_feats1 = agr_feats1.unfreeze(cast=False)
                agr_feats2 = agr_feats2.unfreeze(cast=False)
                af1, af2 = FSSet.mutual_agree(agr_feats1, agr_feats2, feature_pairs)
                # Replace the frozen FSSets with the modified unfrozen ones
#                print("Modified FSSets: {}, {}".format(af1, af2))
                agr_node1[1], agr_node2[1] = af1, af2
                self.node_features[feat_index1][1] = af1
                self.node_features[feat_index2][1] = af2
#        print("Nodes and features for generation: {}, {}".format(self.nodes, self.node_features))
        for token, features, index in self.node_features:
            root, pos = TreeTrans.get_root_POS(token)
            if verbosity:
                print("  Token {}, features {}, index {}, root {}, pos {}".format(token, features.__repr__(), index, root, pos))
            output = [token]
            if not pos:
                if self.target.postsyll:
                    token = self.target.syll_postproc(token)
                    output = [token]
            else:
                output = [[root, pos, features]]
            self.nodes.append([output, index])
            if verbosity:
                print("Target node {}: {}".format(index, output))

    def make_order_pairs(self, verbosity=0):
        """Convert group/index pairs to integer (index) order pairs.
        Constrain order in merged groups."""
        # Reinitialize order pairs
        self.order_pairs.clear()
        if verbosity:
            print("ORDERING pairs for {}".format(self))
            print(" mergers {}, nodes {}".format(self.mergers, self.nodes))
        tgroup_dict = {}
        for index, (forms, constraints) in enumerate(self.nodes):
#            print("Order pairs for node {} with forms {} and constraints {}".format(index, forms, constraints))
#            print("Constraints {} for tdict {}".format(index, constraints))
            for tgroup, tg_index in constraints:
                if tgroup not in tgroup_dict:
                    tgroup_dict[tgroup] = []
                tgroup_dict[tgroup].append((index, tg_index))
#        print("tgroup_dict {}".format(tgroup_dict))
        for pairs in tgroup_dict.values():
            for pairpair in itertools.combinations(pairs, 2):
                pairpair = list(pairpair)
                # Sort by the target index
                pairpair.sort(key=lambda x: x[1])
                self.order_pairs.append([x[0] for x in pairpair])
        # Order nodes within merged groups
        for node, (inner, outer) in self.mergers:
            if verbosity:
                print("  Merger: tnode index {}, inner group {}, outer group {}".format(node, inner, outer))
            # node is sentence node index; inner and outer are groups
            # Indices (input, tgroup) in inner and outer groups
            inner_nodes = tgroup_dict[inner]
            outer_nodes = tgroup_dict[outer]
            # Get the tgroup index for the merge node
            merge_tg_i = dict(outer_nodes)[node]
            # Get input indices for outer group's units before and after the merged node
            prec_outer = [n for n, i in outer_nodes if i < merge_tg_i]
            foll_outer = [n for n, i in outer_nodes if i > merge_tg_i]
            if prec_outer or foll_outer:
                # Get input indices for inner group nodes other than the merge node
                other_inner = [n for n, i in inner_nodes if n != node]
                # Each outer group node before the merge node must precede all inner group nodes,
                # and each outer group node after the merge node must follow all inner group nodes.
                # Add order pair constraints (using input indices) for these constraints.
                for o in prec_outer:
                    for i in other_inner:
                        self.order_pairs.append([o, i])
                for o in foll_outer:
                    for i in other_inner:
                        self.order_pairs.append([i, o])
        if verbosity:
            print('  Order pairs: {}'.format(self.order_pairs))

    def svar(self, name, lower, upper, lower_card=0, upper_card=MAX, ess=True):
        return Var(name, lower, upper, lower_card, upper_card,
                   essential=ess, rootDS=self.dstore)

    def create_variables(self, verbosity=0):
        """Create an order IVar for each translation node and variables for each group tree."""
        # Reinitialize variables
        self.variables.clear()
        nnodes = len(self.nodes)
#        print("Creating variables: nnodes {}, order pairs {}".format(nnodes, self.order_pairs))
        self.variables['order_pairs'] = DetVar("order_pairs", set([tuple(positions) for positions in self.order_pairs]))
        self.variables['order'] = [IVar("o{}".format(i), set(range(nnodes)), rootDS=self.dstore, essential=True) for i in range(nnodes)]

    def create_constraints(self, verbosity=0):
        """Make order and disjunction constraints."""
        # Reinitialize constraints
        self.constraints.clear()
        if verbosity:
            print("Creating constraints for {}".format(self))
        ## Order constraints
        order_vars = self.variables['order']
        self.constraints.append(PrecedenceSelection(self.variables['order_pairs'], order_vars))
        self.constraints.append(Order(order_vars))

    def realize(self, verbosity=0, display=False, all_trans=False, interactive=False):
        """Run constraint satisfaction on the order and disjunction constraints,
        and convert variable values to sentence positions."""
#        print("Realizing {}".format(self))
        generator = self.solver.generator(test_verbosity=verbosity, expand_verbosity=verbosity)
        try:
            proceed = True
            while proceed:
                # Run solver to find positions (values of 'order' variables)
                succeeding_state = next(generator)
                order_vars = self.variables['order']
                positions = [list(v.get_value(dstore=succeeding_state.dstore))[0] for v in order_vars]
#                print("nodes {}, positions {}, order_vars {}".format(self.nodes, positions, order_vars))
                # list of (form, position) pairs; sort by position
                node_group_pos = list(zip(self.nodes, positions))
                node_group_pos.sort(key=lambda x: x[1])
                node_pos = [n[0] for n in node_group_pos]
                self.all_nodes.append(node_pos)
                # Groups and gnode indices in output order
                group_pos = [n[1] for n in node_pos]
                self.ordered_tgroups.append(group_pos)
                # just the form
                output = [n[0] for n in node_pos]
                self.outputs.append(output)
                output_string = output
                output_string = TreeTrans.output_string(output)
                self.output_strings.append(output_string)
                if display:
                    self.display(len(self.outputs)-1)
                if verbosity:
                    print('FOUND REALIZATION {}'.format(self.outputs[-1]))
                if all_trans:
                    continue
                if not interactive or not input('SEARCH FOR ANOTHER REALIZATION FOR TRANSLATION {}? [yes/NO] '.format(self)):
                    proceed = False
        except StopIteration:
            if verbosity:
                print('No more realizations for translation')
