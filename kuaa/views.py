# Ñe'ẽasa. Parsing and translation with minimal dependency grammars.
#
########################################################################
#
#   This file is part of the HLTDI L^3 project
#   for parsing, generation, translation, and computer-assisted
#   human translation.
#
#   Copyright (C) 2015, HLTDI <gasser@cs.indiana.edu>
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
#
# Created 2015.06.12

from flask import request, session, g, redirect, url_for, abort, render_template, flash
from kuaa import app, translate, load

GRN = None
SPA = None

def load_languages():
    global GRN, SPA
    SPA, GRN = load()

@app.route('/')
def index():
    return redirect(url_for('base'))

@app.route('/base', methods=['GET', 'POST'])
def base():
    if request.method == 'POST' and 'Cargar' in request.form:
        return render_template('tra.html')
    return render_template('base.html')

@app.route('/tra', methods=['GET', 'POST'])
def tra():
    if not SPA:
        load_languages()
    print("Idiomas cargados")
    if request.method == 'POST':
        form = request.form
        print("Form: {}".format(form))
        if form.get('otra'):
            return render_template('tra.html', translation=None, sentence=None, otra=False)
        elif form.get('sentence'):
            s = form['sentence']
            print("Sentence {}".format(s))
            t = translate(s, SPA, GRN)
            print("Translations {}".format(t))
            return render_template('tra.html', translation=t, sentence=s)
    return render_template('tra.html', translation=None, sentence=None, otra=False)

