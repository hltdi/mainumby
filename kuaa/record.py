#   
#   Mainumby: sentences and how to parse and translate them.
#
########################################################################
#
#   This file is part of the HLTDI L^3 project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyright (C) 2016 HLTDI <gasser@indiana.edu>
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

# 2016.02.29
# -- Created.
# 2016.03
# -- Lots of additions and fixes.

import datetime

ZERO_TIME = datetime.timedelta() 

def get_time():
    return datetime.datetime.utcnow()

class Session:
    """A record of a single user's responses to a set of sentences."""

    id = 0

    def __init__(self, user=None, source=None, target=None):
        self.start = get_time()
        self.user = user
        # Source and target languages
        self.source = source
        self.target = target
        self.end = None
        self.running = True
        # List of SentRecord objects
        self.sentences = []
        self.id = Session.id
        Session.id += 1

    def __repr__(self):
        return "@{}".format(self.id)

    def length(self):
        """Length of the session as a time delta object."""
        if self.running:
            return ZERO_TIME
        else:
            return self.end - self.start

    def user_input(self, string):
        return self.target.ortho_clean(string)

    def quit(self):
        """Set the end time and stop running."""
        self.running = False
        self.end = get_time()

    def record(self, sentrecord, trans_dict):
        """Record feedback about a segment's or entire sentence's translation."""
        print("{} recording translation for sentence {}".format(self, sentrecord))
        segrecord = None
        if trans_dict.get("UTraOra"):
            translation = trans_dict.get("UTraOra")
            translation = self.target.ortho_clean(translation)
            print("Alternate sentence translation: {}".format(translation))
            sentrecord.record(translation)
        else:
            # It might be capitalized
            segment_key = trans_dict.get('seg').lower()
            segrecord = sentrecord.segments.get(segment_key)
            print("Segment to record: {}".format(segrecord))

            # There might be both segment and whole sentence translations.
            if trans_dict.get("UTraSeg"):
                translation = trans_dict.get("UTraSeg")
                translation = self.target.ortho_clean(translation)
                print("Alternate segment translation: {}".format(translation))
                segrecord.record(translation=translation)
            else:
                # If alternative is given, don't record any choices
                tra_choices = []
                for key, value in trans_dict.items():
                    if key.isdigit():
                        key = int(key)
                        tra_choices.append((key, value))
                print(" Choices: {}".format(segrecord.choices))
#                for k, v in  tra_choices:
#                    print("  Chosen for {}: {}".format(k, v))
#                    print("  Alternatives: {}".format(segrecord.choices[k]))
                segrecord.record(choices=tra_choices)

    def write_record(self):
        print("Record for {}".format(self))
        for sentence in self.sentences:
            sentence.write()

class SentRecord:
    """A record of a Sentence and a single user's response to it."""

    def __init__(self, sentence, session=None, user=None):
        # Also include analyses??
        self.session = session
        self.raw = sentence.raw
        self.tokens = sentence.tokens
        self.time = get_time()
        self.user = user
        # Add to parent Session
        session.sentences.append(self)
        # a dict of SegRecord objects, with token strings as keys
        self.segments = {}
        self.feedback = None

    def __repr__(self):
        session = "{}".format(self.session) if self.session else ""
        return "{}:{}".format(session, self.raw)

    def record(self, translation):
        """Record user's translation for the whole sentence."""
        feedback = Feedback(translation=translation)
        print("{} recording translation {}, feedback: {}".format(self, translation, feedback))
        self.feedback = feedback

    def write(self):
        print("Record for {}".format(self))
        if self.feedback:
            print("Feedback: {}".format(self.feedback))
        # Can there be feedback for segments *and* for whole sentence?
        for key, segment in self.segments.items():
            if segment.feedback:
                print("Tokens {}, segment {}".format(key, segment))
                print("  Feedback: {}".format(segment.feedback))

class SegRecord:
    """A record of a sentence segment and its translation by a user."""

    def __init__(self, solseg, sentence=None, session=None):
        # a SentRecord instance
        self.sentence = sentence
        self.session = session
        self.indices = solseg.indices
        self.translation = solseg.translation
        self.tokens = solseg.token_str
        # Add to parent SentRecord
        self.sentence.segments[self.tokens] = self
        # These get filled in during set_html() in SolSeg
        self.choices = {}
        self.feedback = None

    def __repr__(self):
        session =  "{}".format(self.session) if self.session else ""
        return "{}:{}".format(session, self.tokens)

    def record(self, choices=None, translation=None):
        print("{} recording translation {}, choices {}".format(self, translation, choices))
        if choices:
            self.feedback = Feedback(choices=choices)
            print(" Feedback: {}".format(self.feedback))
        elif translation:
            self.feedback = Feedback(translation=translation)
            print(" Feedback: {}".format(self.feedback))
        else:
            print("Something wrong: NO FEEDBACK TO RECORD")

class Feedback:
    """Feedback from a user about a segment or sentence and its translation."""

    def __init__(self, accept=True, choices=None, translation=None):
        """
        EITHER the user simply
        -- accepts the system's translation (accept=True) OR
        -- makes selection from the alternatives offered by the system
           (choices is a list of pos_index, choice pairs) OR
        -- provides an alternate translation (translation is not None).
        No backpointer to the SegRecord or SentRecord that this refers to.
        """
        self.accept = accept
        self.choices = choices
        self.translation = translation
        self.id = '@'
        if translation:
            self.id += "REJ:{}".format(translation)
        elif choices:
            choice_string = ','.join(["{}={}".format(pos, c) for pos, c in choices])
            self.id += "REJ:{}".format(choice_string)
        else:
            self.id += "ACC"

    def __repr__(self):
        return self.id

ACCEPT = Feedback()

