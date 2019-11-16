from flask import Flask, request, Response, render_template, redirect, url_for
import requests
import itertools
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Regexp
import re

class WordForm(FlaskForm):
    # word_length = SelectField("Word Length:", choices=[(4,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9.)])
    avail_letters = StringField("Letters", validators= [
        Regexp(r'^[a-z]+$|.*[a-z]+.*|.*[.]+.*|^$', message="must provide a word or a pattern")
    ])
    pattern_symbol = '.'
    word_length = SelectField("Word Length", choices=[('0','-'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')])
    submit = SubmitField("Go")


csrf = CSRFProtect()
app = Flask(__name__)
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)

@app.route('/index')
def index():
    form = WordForm()
    return render_template("index.html", form=form)


@app.route('/words', methods=['POST','GET'])
def letters_2_words():

    form = WordForm()
    pattern_symbol = '.'
    
    if form.validate_on_submit():
        letters = form.avail_letters.data
        length = form.word_length.data
        if letters == '':
            letters = 'empty'
        if pattern_symbol in letters:
            if int(length) != len(letters):
                return "pattern length must matches input length"
    else:
        return render_template("index.html", form=form)

    return redirect(url_for('search_result',letters=letters, length=length))



@app.route('/search_result/<letters>/<length>')
def search_result(letters, length):

    
    with open('sowpods.txt') as f:
        good_words = set(x.strip().lower() for x in f.readlines())

    pattern_symbol = '.'

    if letters == 'empty':
        
        if length == '0':
            word_set = []
            for word in good_words:
                word_set.append([word,len(word)])
        else: 
            word_set = []
            requested_len = int(length)
            for word in good_words:
                if len(word) == requested_len:
                    word_set.append([word,len(word)])

    else:

        if length == '0':
            # word_set = set()
            word_set = []
            for l in range(3,len(letters)+1):
                for word in itertools.permutations(letters,l):
                    w = "".join(word)
                    if w in good_words:
                        word_set.append([w,len(w)])

        else:
            if pattern_symbol in letters:
                alphabet = ''.join(re.findall(r'[A-Za-z]', letters))
                position = letters.find(alphabet)
                requested_len = int(length)

                word_set = []
                # for word in itertools.permutations(alphabet,requested_len):
                #     w = "".join(word)
                #     if (w in good_words) and (w.find(alphabet) == position):
                #         word_set.append([w,len(w)])
                for word in good_words:
                    if (len(word) == requested_len):
                        if (word[position] == alphabet):
                            word_set.append([word, len(word)])
            else:
                word_set = []
                requested_len = int(length)
                for l in range(3,len(letters)+1):
                    for word in itertools.permutations(letters,requested_len):
                        w = "".join(word)
                        if w in good_words:
                            word_set.append([w,len(w)])
    


    return render_template('wordlist.html', wordlist=sorted(word_set, key=lambda x: (x[1],x[0])))


@app.route('/dic/<words>')
def xkcdproxy(words):
    x = requests.get(f'http://xkcd.com/{words}?key=5ff7a1a4-7728-4449-b0af-be34ad07ff6f/info.0.json')
    return jsonify(x.json())



@app.route('/proxy')
def proxy():
    result = requests.get(request.args['url'])
    resp = Response(result.text)
    resp.headers['Content-Type'] = 'application/json'
    return resp


