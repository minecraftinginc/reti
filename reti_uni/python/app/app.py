from flask import Flask, render_template, redirect, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@mysql/tech'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'reti'
db = SQLAlchemy(app)

class Utente(db.Model):
    __tablename__ = 'utente'

    USERNAME = db.Column(db.String(80), primary_key=True)
    NOME = db.Column(db.String(80))
    COGNOME = db.Column(db.String(80))
    MAIL = db.Column(db.String(255))
    PASSWORD = db.Column(db.String(255))
    DATA = db.Column(db.Date)
    RUOLO=db.Column(db.String(80))

class Film(db.Model):
    __tablename__ = 'film'

    COD_FILM = db.Column(db.Integer, primary_key=True)
    NOME_FILM = db.Column(db.String(80))
    DESCRIZIONE = db.Column(db.String(300))
    ANNO=db.Column(db.Integer)

class Categoria(db.Model):
    __tablename__ = 'categoria'

    ID_CATEGORIA = db.Column(db.Integer, primary_key=True)
    NOME_CATEGORIA = db.Column(db.String(80))

class CategorieDiFilm(db.Model):
    __tablename__ = 'categorie_di_film'

    ID_CATEGORIA = db.Column(db.Integer, db.ForeignKey('categoria.ID_CATEGORIA'), primary_key=True)
    COD_FILM = db.Column(db.Integer, db.ForeignKey('film.COD_FILM'), primary_key=True)

class Recensioni(db.Model):
    __tablename__ = 'recensioni'

    COD_FILM = db.Column(db.Integer, db.ForeignKey('film.COD_FILM'), primary_key=True)
    USERNAME = db.Column(db.String(80), db.ForeignKey('utente.USERNAME'), primary_key=True)
    VALUTAZIONE = db.Column(db.Float, db.CheckConstraint('VALUTAZIONE IN (0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5)'))

class Profilo(db.Model):
    __tablename__ = 'profilo'
    USERNAME = db.Column(db.String(80), primary_key=True)
    IMAGE = db.Column(db.String(250))

@app.route('/inserimento', methods=['POST'])
def inserimento():
    data = request.get_json()

    # Esempio: salvare i dati ricevuti dal frontend nel modo desiderato
    username = data.get('username')
    nome = data.get('nome')
    cognome = data.get('cognome')
    email = data.get('email')
    password = data.get('password')
    date = data.get('date')
    #ruolo =data.get('ruolo')
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

     # Creazione di un nuovo utente
    nuovo_utente = Utente(
        USERNAME=username,
        NOME=nome,
        COGNOME=cognome,
        MAIL=email,
        PASSWORD=hashed_password,
        DATA=date,
        RUOLO="UTENTE"
    )

    # Aggiunta dell'utente al database e commit delle modifiche
    try:    
        db.session.add(nuovo_utente)
        db.session.commit()
        return jsonify(success=True)
    except Exception as e:  # 'Exception' dovrebbe essere minuscolo
        return jsonify(success=False, error=str(e))  # Ritorno di un messaggio d'errore come risposta JSON

@app.route('/film', methods=['POST'])
def inserimento_film():
    data = request.get_json()
    cod_film=data.get('cod_film')
    nome_film = data.get('nome_film')
    descrizione = data.get('descrizione')

    # Creazione di un nuovo film
    nuovo_film = Film(COD_FILM=cod_film,NOME_FILM=nome_film, DESCRIZIONE=descrizione)

    try:
        # Aggiunta del film al database e commit delle modifiche
        db.session.add(nuovo_film)
        db.session.commit()
        return jsonify(success=True)
    except Exception as e:  # 'Exception' dovrebbe essere minuscolo
        return jsonify(success=False, error=str(e))  # Ritorno di un messaggio d'errore come risposta JSON

@app.route('/categoria', methods=['POST'])
def inserimento_categoria():
    data = request.get_json()
    id_cat=data.get('id_cat')
    nome_categoria = data.get('nome_categoria')

    # Creazione di una nuova categoria
    nuova_categoria = Categoria(ID_CATEGORIA=id_cat,NOME_CATEGORIA=nome_categoria)

    # Aggiunta della categoria al database e commit delle modifiche
    try:
        db.session.add(nuova_categoria)
        db.session.commit()
        return jsonify(success=True)
    except Exception as e:  # 'Exception' dovrebbe essere minuscolo
        return jsonify(success=False, error=str(e))  # Ritorno di un messaggio d'errore come risposta JSON

@app.route('/recensione', methods=['POST'])
def inserimento_recensione():
    data = request.get_json()

    cod_film = data.get('cod_film')
    username = data.get('username')
    valutazione = data.get('valutazione')
    valutazione = float(valutazione)

    user_exists = Utente.query.filter_by(USERNAME=username).first()
    film_exists = Film.query.filter_by(COD_FILM=cod_film).first()

    print(f"Codice film: {cod_film}")
    print(f"Username: {username}")
    print(f"Valutazione: {valutazione}")

    if user_exists and film_exists and 0.5 <= valutazione <= 5:
        nuova_recensione = Recensioni(COD_FILM=cod_film, USERNAME=username, VALUTAZIONE=valutazione)
        try:
            db.session.add(nuova_recensione)
            db.session.commit()
            return jsonify(success=True)
        except Exception as e:
            return jsonify(success=False, error=str(e))
    else:
        return jsonify(success=False, error="Condizioni non soddisfatte", cod_film=cod_film, username=username, valutazione=valutazione)
    
@app.route('/categoria_film', methods=['POST'])
def inserimento_categoria_film():
    data = request.get_json()

    id_categoria = data.get('id_categoria')
    cod_film = data.get('cod_film')

    # Creazione di una nuova categoria di film
    nuova_categoria_film = CategorieDiFilm(ID_CATEGORIA=id_categoria, COD_FILM=cod_film)
    if str(Categoria.query.filter_by(ID_CATEGORIA=id_categoria).first) and str(Film.query.filter_by(COD_FILM=cod_film).first):
    # Aggiunta della categoria di film al database e commit delle modifiche
        try:
            db.session.add(nuova_categoria_film)
            db.session.commit()
            return jsonify(success=True)
        except Exception as e:  # 'Exception' dovrebbe essere minuscolo
            return jsonify(success=False, error=str(e))  # Ritorno di un messaggio d'errore come risposta JSON
    else:
        return jsonify(success=False, error="Condizioni non soddisfatte")

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        username = data.get('name')
        password = data.get('password')
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            # Controlla se l'utente esiste nel database
        user = Utente.query.filter_by(USERNAME=username).first().USERNAME
        p = Utente.query.filter_by(USERNAME=username).first().PASSWORD
        if user==username and p==hashed_password:
            return jsonify({'user': user})
            #return render_template('nuovo.html', user=user)  # Passaggio di 'user' al template search.html
        else:
            # Se il login non è avvenuto con successo, potresti mostrare un messaggio di errore
            return jsonify(success=False, error="Condizioni non soddisfatte")
    except Exception as e:
        print(str(e))  # Stampare l'errore per debug
        return jsonify({'error': 'Si è verificato un errore interno'}), 500

@app.route('/search', methods=['GET'])
def search_movie():
    try:
        nome=request.args.get('nome')
        username=request.args.get('username')
        film=Film.query.filter_by(NOME_FILM=nome).first()
        film_trovato = Recensioni.query.filter_by(COD_FILM=film.COD_FILM).all()
        if not film_trovato:
            print('No reviews found for this film.')
            total_ratings = 0  # or any default value you want to set when no reviews are found
        else:
            total_ratings = sum(recensione.VALUTAZIONE for recensione in film_trovato)
        # Calcola la media delle valutazioni
        if len(film_trovato) > 0:
            average_ratings = total_ratings / len(film_trovato)
            #print(f'Average Ratings: {average_ratings}')  Stampiamo il valore di average_ratings
        else:
            average_ratings = 0

        #results = Film.query.filter(Film.NOME_FILM.like(f'%{nome}%')).all()
            # Se presente nel db allora presente anche nella cartella uploads
        if film:
            film_serialized = {'username':username,'COD_FILM': film.COD_FILM, 'NOME_FILM': film.NOME_FILM,'DESCRIZIONE': film.DESCRIZIONE, 'ANNO': film.ANNO, 'VALUTAZIONE': average_ratings}  # Converti l'oggetto in un dizionario
            return jsonify({'film': film_serialized})
            #return render_template('search.html', film=film)  # Passaggio di 'film' al template search.html
        else:
            return jsonify({'film non trovato'})
    except Exception as e:
        print(str(e))  # Stampare l'errore per debug
        response = {
            'error': 'Si è verificato un errore durante la media della valutazione',
            'nome': nome if 'nome' in locals() else None
        }
        return jsonify(response), 500

@app.route('/films', methods=['GET'])
def get_all_films():
    try:
        films = Film.query.all()  # Ottieni tutti i film dalla tabella

        # Serializza la lista dei film in un formato comprensibile per la risposta JSON
        serialized_films = [{
            'COD_FILM': film.COD_FILM,
            'NOME_FILM': film.NOME_FILM,
            'DESCRIZIONE': film.DESCRIZIONE,
            'ANNO': film.ANNO
        } for film in films]

        return jsonify({'films': serialized_films})  # Restituisci la lista di film in formato JSON
    except Exception as e:
        print(str(e))  # Stampa l'errore per il debug
        return jsonify({'error': 'Si è verificato un errore interno'}), 500

@app.route('/average', methods=['POST'])
def add_film_rating():
    try:
        # Recupera i dati inviati nella richiesta POST
        data = request.get_json()
        cod = data.get('cod_film')
        film_trovato = Recensioni.query.filter_by(COD_FILM=cod).all()
        if not film_trovato:
            print('No reviews found for this film.')
            total_ratings = 0  # or any default value you want to set when no reviews are found
        else:
            total_ratings = sum(recensione.VALUTAZIONE for recensione in film_trovato)
        # Calcola la media delle valutazioni
        if len(film_trovato) > 0:
            average_ratings = total_ratings / len(film_trovato)
            print(f'Average Ratings: {average_ratings}')  # Stampiamo il valore di average_ratings
        else:
            average_ratings = 0
        return jsonify({
            'average_ratings': average_ratings
        })

    except Exception as e:
        print(str(e))  # Stampa l'errore per il debug
        response = {
            'error': 'Si è verificato un errore durante la media della valutazione',
            'total_ratings': total_ratings if 'total_ratings' in locals() else None,
            'average_ratings': average_ratings if 'average_ratings' in locals() else None
        }
        return jsonify(response), 500
@app.route('/showuser', methods=['POST'])
def show_user():
    try:
        data = request.get_json()

        username = data.get('username')

        # Check if the user exists in the database
        user = Utente.query.filter_by(USERNAME=username).first()
        
        if user:
            
            # If the user exists, return the user's email
            return jsonify({'email': user.MAIL,'username':username,'name': user.NOME,'cognome':user.COGNOME,'data':user.DATA})
        else:
            return jsonify(success=False, error="User not found")

    except Exception as e:
        print(str(e))  # Consider logging the error instead
        response = {
            'error': 'Si è verificato un errore durante l invio dati utente',
        }
        return jsonify(response), 500

from flask import jsonify

@app.route('/imageprofile', methods=['POST'])
def upload_image():
    try:
        data = request.get_json()
        user = data.get('username')
        uploaded_file = data.get('imageFile')
        true = Utente.query.filter_by(USERNAME=user).first()

        # Cerca l'entry esistente
        existing_profile = Profilo.query.filter_by(USERNAME=user).first()

        if existing_profile:
            # Sovrascrivi i valori esistenti
            existing_profile.IMAGE = uploaded_file
            db.session.commit()
            return jsonify(success=True)
        elif true:
            # Salva l'immagine nel database
            profile = Profilo(USERNAME=user, IMAGE=uploaded_file)
            db.session.add(profile)
            db.session.commit()
            return jsonify(success=True)
        else:
            return jsonify(success=False, error="User not found")

    except Exception as e:
        print(str(e))  # Considera di registrare l'errore invece di stamparlo
        response = {
            'error': 'Si è verificato un errore durante l inserimento dell immagine nel database',
        }
        return jsonify(response), 500

@app.route('/checkimage', methods=['GET'])
def check_image():
    try:
        username = request.args.get('username')

        # Cerca l'utente nella tabella 'profilo'
        user_profile = Profilo.query.filter_by(USERNAME=username).first()

        if user_profile:
            # Se l'utente è presente, restituisci un oggetto JSON con success: true
            IMAGE=Profilo.query.filter_by(USERNAME=username).first().IMAGE
            return jsonify({'success': True, 'imagePresent': True, 'username': username, 'image': user_profile.IMAGE})
        else:
            # Se l'utente non è presente, restituisci un oggetto JSON con success: true e imagePresent: false
            return jsonify({'success': True, 'imagePresent': False, 'username': username})
    except Exception as e:
        print(str(e))  # Considera di registrare l'errore invece di stamparlo
        response = {
            'error': 'Si è verificato un errore durante l inserimento dell immagine nel database',
        }
        return jsonify(response), 500
    
@app.route('/categoriefilms', methods=['POST'])
def get_cat_films():
    try:
        data = request.get_json()
        categorie = data.get('categorie', [])

        if not categorie:
            return jsonify({'success': False, 'message': 'Nessuna categoria fornita'})

        # Ottieni i film che hanno TUTTE le categorie
        all_films = None
        for cat in categorie:
            categoria = Categoria.query.filter_by(NOME_CATEGORIA=cat).first()
            if categoria:
                id_categoria = categoria.ID_CATEGORIA
                categorie_di_film = CategorieDiFilm.query.filter_by(ID_CATEGORIA=id_categoria).all()
                cod_film_list = [c.COD_FILM for c in categorie_di_film]

                # Utilizza una query AND per selezionare i film che hanno TUTTE le categorie
                films = (Film.query
                         .filter(Film.COD_FILM.in_(cod_film_list))
                         .all() if cod_film_list else [])

                if all_films is None:
                    all_films = set(films)
                else:
                    all_films.intersection_update(set(films))

                if not all_films:
                    break  # Interrompi se non ci sono film con tutte le categorie cercate
            else:
                return jsonify({'success': False, 'message': f'Categoria non trovata: {cat}'})

        serialized_films = [{
            'cod_film': film.COD_FILM,
            'nome_film': film.NOME_FILM,
            'descrizione': film.DESCRIZIONE,
            'anno': film.ANNO
        } for film in all_films] if all_films else []

        return jsonify({'success': True, 'films': serialized_films})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1200)