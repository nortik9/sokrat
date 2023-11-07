import os
import random
import flask

from flask import Flask, render_template, url_for, request, session, redirect
import sqlite3
import hashlib

app = Flask(__name__)

app.config['SECRET_KEY'] = '6323422092:AAGtEOJWhvjfW411obuNeIM1T_e0NP3dsNM'

menu = [
    {"name": "Главная", "url": "/"},
    {"name": "Авторизация", "url": "avto"},
    {"name": "Регистрация", "url": "reg"}
]

@app.route("/insert", methods=['POST'])
def insert():

    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()

    user_names = cursor.execute('''SELECT * FROM 'users' WHERE login = ?''', (request.form["log"],)).fetchone()
    menu = [
        {"name": "Главная", "url": "/"},
        {"name": "Авторизация", "url": "avto"},
        {"name": "Регистрация", "url": "reg"}
    ]

    if (request.form["log"] == '' or request.form["pass"] == ''):

        flask.flash('Для регистрации заполните все поля')
        return render_template('reg.html', title="Регистрация", menu=menu)

    else:

        if user_names !=None:
            flask.flash('Данный логин уже занят')
            return render_template('reg.html', title="Регистрация", menu=menu)
        else:
            if request.form["pass"]!=request.form["passtwo"]:
                flask.flash('Пароли не совпадают')
                return render_template('reg.html', title="Регистрация", menu=menu)
            else:
                hashas = hashlib.md5(request.form["pass"].encode())
                passw = hashas.hexdigest()


                cursor.execute('''INSERT INTO users('login', password) VALUES(?, ?)''', (request.form["log"],passw))
                connect.commit()

                user = cursor.execute('''SELECT * FROM 'users' WHERE login = ?''', (request.form["log"],)).fetchone()

                session['user_login'] =user[1]
                session['user_id'] = user[0]
                menu = [
                    {"name": "Главная", "url": "/"},
                    {"name": session['user_login'], "url": "profile"},

                ]

                hrefs = cursor.execute(
                    '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
                    (session['user_id'],)).fetchall()
                type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()

                return render_template('html/profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type)

@app.route("/check", methods=['POST'])
def check():
    connect = sqlite3.connect('bd.db')
    cursor = connect.cursor()
    baselink = request.base_url
    baselink = baselink[:-5]
    user = cursor.execute('''SELECT * FROM 'users' WHERE login = ?''', (request.form["log"],)).fetchone()
    hashas = hashlib.md5(request.form["pass"].encode())
    passw = hashas.hexdigest()
    menu = [
        {"name": "Главная", "url": "/"},
        {"name": "Авторизация", "url": "avto"},
        {"name": "Регистрация", "url": "reg"}
    ]
    if user!=None:
        if passw==user[2]:

            session['user_login'] = user[1]
            session['user_id'] = user[0]
            hrefs = cursor.execute('''SELECT * FROM 'links' WHERE user_id = ?''', (session['user_id'],)).fetchall()
            menu = [
                {"name": "Главная", "url": "/"},
                {"name": session['user_login'], "url": "profile"},
            ]
            if 'adres' in session and session['adres']!=None:
                if session['type']==2:
                    ad = session['adres']
                    href = cursor.execute(
                        '''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE links.id = ?''',
                        (session['idlink'],)).fetchone()


                    cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (href[5] + 1, href[0]))
                    connect.commit()

                    session['idlink'] = None
                    session['adid'] = None
                    session['type'] = None
                    session['adres']=None
                    session['user_login'] = None
                    session['user_id'] = None
                    return redirect(f"{ad}")
                else:
                    if session['adid']==session['user_id']:
                        ad = session['adres']
                        href = cursor.execute(
                            '''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE links.id = ?''',
                            (session['idlink'],)).fetchone()

                        cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (href[5] + 1, href[0]))
                        connect.commit()

                        session['idlink'] = None
                        session['adid'] = None
                        session['type'] = None
                        session['adres'] = None
                        session['user_login'] = None
                        session['user_id'] = None
                        connect.commit()
                        return redirect(f"{ad}")
                    else:
                        session['user_login']=None
                        session['user_id']=None
                        session['adid'] = None
                        session['type'] = None
                        session['adres'] = None
                        return render_template('html/error.html', title="Ссылка приватная и другого юзера")
            else:
                hrefs = cursor.execute(
                    '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
                    (session['user_id'],)).fetchall()
                type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()

                return render_template('html/profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type, baselink=baselink)
        else:

            flask.flash('Пароль не подходит')
            return render_template('html/login.html', title="Авторизация", menu=menu)
    else:

        flask.flash('такого аккаунта не существует')
        return render_template('html/login.html', title="Авторизация", menu=menu)

@app.route("/delete", methods=['POST'])
def delete():
    baselink = request.base_url
    baselink = baselink[:-6]
    connect = sqlite3.connect('bd.db')
    cursor = connect.cursor()
    cursor.execute('''DELETE FROM 'links' WHERE id = ?''', (request.form['idd'],))
    connect.commit()
    menu = [
        {"name": "Главная", "url": "/"},
        {"name": session['user_login'], "url": "profile"},

    ]
    hrefs = cursor.execute(
        '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
        (session['user_id'],)).fetchall()
    type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()

    return render_template('html/profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type, baselink=baselink)

@app.route("/short", methods=['POST'])
def short():
    baselink = request.base_url
    baselink=baselink[:-5]

    if 'user_login' in session and session['user_login'] !=None:
        menu = [
            {"name": "Главная", "url": "/"},
            {"name": session['user_login'], "url": "profile"},

        ]
    else:
        menu = [
            {"name": "Главная", "url": "/"},
            {"name": "Авторизация", "url": "avto"},
            {"name": "Регистрация", "url": "reg"}
        ]
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    if request.form['how']=='1':

        if ('user_id' in session and session['user_id']!=None):
            user_adress = hashlib.md5(request.form['href'].encode()).hexdigest()[:random.randint(8, 12)]

            cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['href'], user_adress, session['user_id'], request.form['how'],0))
            connect.commit()
            flask.flash(f'{user_adress}')
            return render_template('index.html', title="Главная", menu=menu, baselink=baselink)
        else:
            user_adress = hashlib.md5(request.form['href'].encode()).hexdigest()[:random.randint(8, 12)]
            cursor.execute('''INSERT INTO links('link', 'hreflink', 'link_type_id', 'count') VALUES(?, ?, ?, ?)''', (request.form['href'], user_adress, request.form['how'], 0))
            connect.commit()

            flask.flash(f'{user_adress}')
            return render_template('html/index.html', title="Главная", menu=menu, baselink=baselink)

    elif request.form['how']=='2':
        user_adress = hashlib.md5(request.form['href'].encode()).hexdigest()[:random.randint(8, 12)]
        cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['href'], user_adress, session['user_id'], request.form['how'], 0))
        connect.commit()
        flask.flash(f'{user_adress}')
        return render_template('index.html', title="Главная", menu=menu, baselink=baselink)
    else:
        user_adress = hashlib.md5(request.form['href'].encode()).hexdigest()[:random.randint(8, 12)]
        cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['href'], user_adress, session['user_id'], request.form['how'], 0))
        connect.commit()
        flask.flash(f'{user_adress}')
        return render_template('html/index.html', title="Главная", menu=menu, baselink=baselink)

@app.route("/href/<hashref>")
def direct(hashref):
    connect = sqlite3.connect('bd.db')
    cursor = connect.cursor()
    href = cursor.execute('''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE hreflink = ?''', (hashref, ) ).fetchone()
    print(href)
    if href[4]==1:
        cursor.execute('''UPDATE links SET count = ? WHERE id=?''',(href[5]+1, href[0]))
        connect.commit()
        return redirect(f"{href[1]}")

    elif href[4]==2:
        if 'user_id' in session and session['user_id']!=None:
            cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (href[5] + 1, href[0]))
            connect.commit()
            return redirect(f"{href[1]}")

        else:
            session['adres'] = href[1]

            session['type'] = 2
            session['adid'] = href[3]
            session['idlink'] = href[0]
            menu = [
                # {"name": "Главная", "url": "/"},
                {"name": "Авторизация", "url": "avto"},
                {"name": "Регистрация", "url": "reg"}
            ]
            return render_template('html/login.html', title="Пройдите авторизацию для перехода", menu=menu)

    elif href[4]==3:
        if 'user_id' in session and session['user_id'] != None:
            if (href[3]==session['user_id']):
                cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (href[5] + 1, href[0]))
                connect.commit()
                return redirect(f"{href[1]}")
            else:
                return render_template('no.html', title="Ссылка приватная и другого юзера")
        else:
            session['adres'] = href[1]
            session['type'] = 3
            session['adid'] = href[3]
            session['idlink'] = href[0]
            menu = [
                # {"name": "Главная", "url": "/"},
                {"name": "Авторизация", "url": "avto"},
                {"name": "Регистрация", "url": "reg"}
            ]
            return render_template('html/login.html', title="Пройдите авторизацию для перехода", menu=menu)

@app.route("/logout", methods=['POST'])
def logout():
    session['user_login']=None
    session['user_id'] = None
    return render_template('html/index.html', title="Главная", menu=menu)

@app.route("/updatehref", methods=['POST'])
def updatehref():

    baselink = request.base_url
    baselink = baselink[:-10]

    connect = sqlite3.connect('bd.db')
    cursor = connect.cursor()
    name = cursor.execute('''SELECT * FROM 'links' WHERE hreflink = ? ''', (request.form["hreflink"],)).fetchone()

    menu = [
        {"name": "Главная", "url": "/"},
        {"name": session['user_login'], "url": "profile"},

    ]

    if (name !=None):
        if (name[3]==session['user_id']):
            if (request.form["types"]!='0'):
                cursor.execute('''UPDATE links SET link_type_id = ? WHERE id = ?''', (request.form["types"],request.form["idlink"]))
                connect.commit()
                flask.flash('Все успешно изменено')
                hrefs = cursor.execute('''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',(session['user_id'],)).fetchall()
                type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()

                return render_template('html/profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type, baselink=baselink)
            else:
                flask.flash('???')
                hrefs = cursor.execute('''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',(session['user_id'],)).fetchall()
                type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
                return render_template('html/profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type, baselink=baselink)
        else:
            flask.flash(f'Имя {request.form["hreflink"]} уже занято')
            hrefs = cursor.execute(
                '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
                (session['user_id'],)).fetchall()
            type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
            return render_template('html/profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type, baselink=baselink)

    else:
        if (request.form["types"]!='0'):
            cursor.execute('''UPDATE links SET hreflink = ?, link_type_id = ? WHERE id = ?''',(request.form["hreflink"], request.form["types"], request.form["idlink"]))
            connect.commit()
            flask.flash('Все успешно изменено')
            hrefs = cursor.execute(
                '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
                (session['user_id'],)).fetchall()
            type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
            return render_template('html/profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type, baselink=baselink)
        else:
            cursor.execute('''UPDATE links SET hreflink = ? WHERE id = ?''',(request.form["hreflink"], request.form["idlink"]))
            connect.commit()
            flask.flash('Все успешно изменено')
            hrefs = cursor.execute(
                '''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',
                (session['user_id'],)).fetchall()
            type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
            return render_template('html/profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type, baselink=baselink)

@app.route("/")
def index():
    if 'user_login' in session and session['user_login'] !=None:
        menu = [
            {"name": "Главная", "url": "/"},
            {"name": session['user_login'], "url": "profile"},

        ]
    else:
        menu = [
            {"name": "Главная", "url": "/"},
            {"name": "Авторизация", "url": "avto"},
            {"name": "Регистрация", "url": "reg"}
        ]
    return render_template('html/index.html', title="Главная", menu=menu)

@app.route("/reg")
def reg():
    return render_template('html/registration.html', title="Регистрация", menu=menu)

@app.route("/avto")
def avto():
    return render_template('html/login.html', title="Авторизация", menu=menu)

@app.route("/profile")
def profile():
    baselink = request.base_url

    if 'user_login' in session and session['user_login']!=None:
        menu = [
            {"name": "Главная", "url": "/"},
            {"name": session['user_login'], "url": "profile"},

        ]
    else:
        menu = [
            {"name": "Главная", "url": "/"},
            {"name": "Авторизация", "url": "avto"},
            {"name": "Регистрация", "url": "reg"}
        ]
        return render_template('html/index.html', title="Главная", menu=menu)

    connect = sqlite3.connect('bd.db')
    cursor = connect.cursor()
    baselink = baselink[:-7]
    hrefs = cursor.execute('''SELECT * FROM 'links' INNER JOIN links_types ON links_types.id = links.link_type_id  WHERE user_id = ?''',(session['user_id'],)).fetchall()
    type = cursor.execute('''SELECT * FROM 'links_types' ''').fetchall()
    print(hrefs)
    return render_template('html/profile.html', title="Профиль", menu=menu, hrefs=hrefs, type=type, baselink=baselink)

if __name__ =="__main__":
    app.run(debug=True)