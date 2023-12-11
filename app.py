from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import random
from bson import ObjectId
from models import Player, Team
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb+srv://anhluunguyen:348project@cluster0.zvqt8r9.mongodb.net/?retryWrites=true&w=majority")
db = client["soccer_db"]
teams_collection = db["teams"]
players_collection = db["players"]

players_collection.create_index([('name', 1)])  # Index on the 'name' field
players_collection.create_index([('_id', 2)]) 


teams_collection.create_index([('name', 1)])   # Index on the 'name' field
teams_collection.create_index([('_id', 2)])


from Player import Player
from Team import Team
@app.route('/')
def index():
    players = players_collection.find()
    return render_template('index.html', players=players)

@app.route('/add_player', methods=['POST'])
def add_player():
    # Add a new player to the database
    # Extract player data from the form
    player_data = {
        'name': request.form['name'],
        'position': request.form['position'],
        'age': int(request.form['age']),
        'trophies': 0,
        'ballondor': 0,
        'team': None  # Add a null value for the team
    }

    # teams_data = list(teams_collection.find())
    # if teams_data:
    #     selected_team_data = random.choice(teams_data)
    #     player_data.team = Team(**selected_team_data) if selected_team_data else None

    # Insert player into the collection
    players_collection.insert_one(player_data)

    return redirect(url_for('index'))

@app.route('/simulate_career/<string:player_id>')
def simulate_career(player_id):
    player_data = players_collection.find_one({'_id': ObjectId(player_id)})

    if player_data:
        player = Player(**player_data)

        # Simulate random career data
        years_added = random.randint(1, 10)
        player.age += years_added

        # Assign player to a random team
        teams_data = list(teams_collection.find())
        if teams_data:
            selected_team_data = random.choice(teams_data)
            player.team = Team(**selected_team_data) if selected_team_data else None

        # Simulate other career logic...

        # Low chance of getting Ballon d'Or and trophies
        ballondor_chance = random.randint(1, 5)
        trophies_chance = random.randint(1, 2)

        if ballondor_chance == 1:
            player.ballondor += 1
            # if player.team:
            #     player.team.ballondor += 1

        if trophies_chance == 1:
            player.trophies += 1
            if player.team:
                with client.start_session() as session:
                    with session.start_transaction():
                        players_collection.update_one(
                            {'_id': ObjectId(player_id)},
                            {'$inc': {'trophies': 1}},
                            session=session
                        )
                        teams_collection.update_one(
                            {'_id': player.team._id},
                            {'$inc': {'trophies': 1}},
                            session=session
                        )
                # team_data = teams_collection.find_one({'_id': player.team._id})
                # if team_data:
                #     # Update the trophy count for the team
                #     new_trophy_count = team_data.get('trophies', 0) + 1
                #     teams_collection.update_one(
                #         {'_id': player.team._id},
                #         {'$set': {'trophies': new_trophy_count}}
                #     )
                    print(f"added 1 to {player.team.name}" )
        
        # Update player and team data in the collection
        players_collection.update_one(
            {'_id': ObjectId(player_id)},
            {
                '$set': {
                    'age': player.age,
                    'ballondor': player.ballondor,
                    'trophies': player.trophies,
                    'team': player.team.__dict__ if player.team else None  # Use None if player.team is None
                }
            }
        )

        # Redirect to a new page to display simulated career stats
        return redirect(url_for('career_stats', player_id=player_id))

    # Handle case where player is not found
    flash('Player not found', 'error')
    return redirect(url_for('index'))

@app.route('/player_stats/<string:player_id>')
def player_stats(player_id):
    # Fetch the player data from the database based on the player ID
    player_data = players_collection.find_one({'_id': ObjectId(player_id)})

    if player_data:
        # Render the player_stats.html template with the player's information
        return render_template('player_stats.html', player=player_data)

    # Handle case where player is not found
    flash('Player not found', 'error')
    return redirect(url_for('index'))


@app.route('/career_stats/<string:player_id>')
def career_stats(player_id):
    # Retrieve player data from the collection
    player_data = players_collection.find_one({'_id': ObjectId(player_id)})

    if player_data:
        player = Player(**player_data)

        # Fetch the team information
        print(player.team['_id'])
        # teamInfo = Team(player.team)
        # print(teamInfo._id)
        team_data = None
        # print(player.team._id)
        if player.team:
            team_data = teams_collection.find_one({'_id': player.team['_id']})


        return render_template('career_stats.html', player=player, team_data=team_data)

    # Handle case where player is not found
    flash('Player not found', 'error')
    return redirect(url_for('index'))

@app.route('/delete_player/<player_id>')
def delete_player(player_id):
    # Delete a player from the database
    player_id = ObjectId(player_id)
    players_collection.delete_one({'_id': player_id})
    return redirect(url_for('index'))

@app.route('/edit_player/<player_id>')
def edit_player(player_id):
    player = players_collection.find_one({'_id': ObjectId(player_id)})
    teams = list(teams_collection.find())

    if player:
        return render_template('edit.html', player=player, teams=teams)

    return redirect(url_for('index'))

@app.route('/update_player/<player_id>', methods=['POST'])
def update_player(player_id):
    player_id = ObjectId(player_id)
    try:
        # Retrieve player data from the form
        updated_player = {
            'name': request.form['name'],
            'position': request.form['position'],
            'age': int(request.form['age']),
            'trophies': int(request.form['trophies']),
            'ballondor': int(request.form['ballondor']),
            'team': request.form['team'],
        }


        # Update player data in the collection
        players_collection.update_one({'_id': ObjectId(player_id)}, {'$set': updated_player})

        # Redirect to the index page after updating
        return redirect(url_for('index'))

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    # Handle case where an error occurred
    return redirect(url_for('index'))




@app.route('/create_team_page')
def create_team_page():
    return render_template('create_team.html')


@app.route('/create_team', methods=['POST'])
def create_team():
    # Extract team data from the form
    team_data = {
        'name': request.form['name'],
        'country': request.form['country'],
        'trophies': int(request.form['trophies']),
    }

    # Insert team into the collection
    teams_collection.insert_one(team_data)

    # Redirect to the index page after creating the team
    return redirect(url_for('index'))

@app.route('/view_teams')
def view_teams():
    # Fetch all teams from the database
    teams = list(teams_collection.find())

    # Render the view_teams.html template with the list of teams
    return render_template('view_teams.html', teams=teams)

@app.route('/team_stats/<string:team_id>')
def team_stats(team_id):
    # Fetch the team data from the database based on the team ID
    team_data = teams_collection.find_one({'_id': ObjectId(team_id)})

    if team_data:
        # Render the team_stats.html template with the team's information
        return render_template('team_stats.html', team=team_data)

    # Handle case where team is not found
    flash('Team not found', 'error')
    return redirect(url_for('view_teams'))


if __name__ == '__main__':
    app.run(debug=True)