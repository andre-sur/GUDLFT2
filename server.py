import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

error_counter = defaultdict(int)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])

def showSummary():
    email = request.form['email']
    matching_clubs = [club for club in clubs if club['email'] == email]

    if not matching_clubs:
        flash("Email inexistant.")
        return redirect(url_for('index'))

    club = matching_clubs[0]
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)

    if foundClub and foundCompetition:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    else:
        flash("Club ou competition introuvable. Veuillez réessayer.")
        return render_template('welcome.html', club=foundClub, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)

    if not competition or not club:
        error_counter["club_ou_competition_introuvable"] += 1
        flash("Club ou competition introuvable.")
        return render_template('welcome.html', club=club, competitions=competitions)

    try:
        places_required = int(request.form['places'])
    except ValueError:
        error_counter["places_invalide"] += 1
        flash("Nombre de places invalide.")
        return render_template('welcome.html', club=club, competitions=competitions)

    if places_required > 12:
        error_counter["trop_de_places"] += 1
        flash("Maximum 12 places.")
        return render_template('welcome.html', club=club, competitions=competitions)

    club_points = int(club['points'])
    if places_required > club_points:
        error_counter["points_insuffisants"] += 1
        flash("Pas assez de points.")
        return render_template('welcome.html', club=club, competitions=competitions)

    available_places = int(competition['numberOfPlaces'])
    if places_required > available_places:
        error_counter["places_insuffisantes"] += 1
        flash("Pas assez de places.")
        return render_template('welcome.html', club=club, competitions=competitions)

    competition['numberOfPlaces'] = available_places - places_required
    club['points'] = club_points - places_required

    flash('Réservation confirmée.')
    return render_template('welcome.html', club=club, competitions=competitions)

# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route('/errors')
def showErrors():
    return render_template('errors.html', errors=error_counter)

@app.route('/points', methods=['GET'])
def showPoints():
    return render_template('points.html', clubs=clubs)

