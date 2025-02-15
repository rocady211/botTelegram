from flask import jsonify
import requests
import random
from datetime import datetime
import time
from functools import lru_cache

API_KEY = "U6IOhB1gYGRidX6m14WHx4Mzu9pQHIBQas4nWYQs"
BASE_URL = "https://api.sportradar.com/soccer/trial/v4/en"

ligas_famosas = {
    "Premier League": { "id": "sr:competition:17", "famous_teams": [
        "MUN", "LIV", "CHE", "ARS", "MCI", "TOT"
    ]},
    "LaLiga": { "id": "sr:competition:8", "famous_teams": [
        "RMA", "BAR", "ATM", "SEV", "VAL"
    ]},
    "Serie A": { "id": "sr:competition:23", "famous_teams": [
        "JUV", "MIL", "INT", "NAP", "ROM"
    ]},
    "Bundesliga": { "id": "sr:competition:35", "famous_teams": [
        "BAY", "DOR", "RBL", "LEV", "S04"
    ]},
    "Ligue 1": { "id": "sr:competition:34", "famous_teams": [
        "PSG", "MAR", "LYO", "MON", "LIL"
    ]},
    "UEFA Champions League": { "id": "sr:competition:7", "famous_teams": [
        "RMA", "BAR", "BAY", "LIV", "MCI"
    ]},
    "FIFA World Cup": { "id": "sr:competition:16", "famous_teams": [
        "BRA", "ARG", "FRA", "GER", "ESP", "URU", "POR"
    ]},
    "Copa América": { "id": "sr:competition:133", "famous_teams": [
        "BRA", "ARG", "URU", "COL", "CHI", "ECU"
    ]},
    "Brasileirão Serie A": { "id": "sr:competition:325", "famous_teams": [
        "FLA", "PAL", "SAO", "COR", "CAM"
    ]},
    "Copa Libertadores": { "id": "sr:competition:384", "famous_teams": [
        "BOC", "RIV", "FLA", "PAL", "SAN",
        "GRE", "NAC", "PEN",
        "IND", "SAO"
    ]},
}


@lru_cache(maxsize=20)
def get_current_season(competition_id):
    url = f"{BASE_URL}/competitions/{competition_id}/seasons.json?api_key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["seasons"][-1]["id"] if "seasons" in data and data["seasons"] else None
    except Exception as e:
        print(f"Error obteniendo la temporada de {competition_id}: {e}")
        return None

def get_competitor_schedules(competitor_id):
    url = f"{BASE_URL}/competitors/{competitor_id}/schedules.json?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('schedules', [])
    else:
        print(response.text)
        return []

@lru_cache(maxsize=10)
def get_sport_event_summary(event_id):
    url = f"{BASE_URL}/sport_events/{event_id}/summary.json?api_key={API_KEY}"
    response = requests.get(url)
    print("url 1")
    print(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.text)
        return {}

def get_last_5_matches_statistics(competitor_id, abreviation):
    matches = get_competitor_schedules(competitor_id)
    last_5_matches = matches[:5]
    statistics = {
        f"goles_{abreviation}": [],
        f"tiros_{abreviation}": [],
        f"posesion_{abreviation}": [],
        f"ultimos_5_partidos_{abreviation}": [],
        f"es_local_{abreviation}": [],
        f"tiros_al_arco_{abreviation}": [],
        f"tiros_afuera_arco_{abreviation}": [],
        "proximo_partido_local_A": abreviation == "A"
    }

    for matchInfo in last_5_matches:
        time.sleep(3)
        match = matchInfo.get("sport_event", {})
        event_id = match.get('id')
        sport_event_status = matchInfo.get('sport_event_status', {})
        event_summary = get_sport_event_summary(event_id)
        event_statitics = event_summary.get("statistics", {}).get("totals", {}).get("competitors", [])
        if event_summary:
            home_team = event_statitics[0]
            away_team = event_statitics[1]
            home_score = sport_event_status.get("home_score", 0)
            away_score = sport_event_status.get("away_score", 0)
            home_shots = home_team.get('statistics', {}).get('shots_total', 0)
            away_shots = away_team.get('statistics', {}).get('shots_total', 0)
            home_shots_on_target = home_team.get('statistics', {}).get('shots_on_target', 0)
            away_shots_on_target = away_team.get('statistics', {}).get('shots_on_target', 0)
            home_shots_off_target = home_team.get('statistics', {}).get('shots_off_target', 0)
            away_shots_off_target = away_team.get('statistics', {}).get('shots_off_target', 0)
            home_possession = home_team.get('statistics', {}).get('ball_possession', 0)
            away_possession = away_team.get('statistics', {}).get('ball_possession', 0)
            is_home_game = 1 if home_team.get('id') == competitor_id else 0

            statistics["goles_" + abreviation].append(home_score if is_home_game else away_score)
            statistics["tiros_" + abreviation].append(home_shots if is_home_game else away_shots)
            statistics["tiros_al_arco_" + abreviation].append(home_shots_on_target if is_home_game else away_shots_on_target)
            statistics["tiros_afuera_arco_" + abreviation].append(home_shots_off_target if is_home_game else away_shots_off_target)
            statistics["posesion_" + abreviation].append(home_possession if is_home_game else away_possession)
            statistics["es_local_" + abreviation].append(is_home_game)
            statistics["ultimos_5_partidos_" + abreviation].append([home_score, away_score])

    return statistics

def get_info_last_5_match():
    respo = get_last_5_matches_statistics("sr:competitor:44", "A")

    return jsonify(respo)


def get_famous_matches(today):
    important_matches = {}

    for liga_name, liga_data in ligas_famosas.items():
        time.sleep(1)  
        competition_id = liga_data["id"]
        famous_teams = set(liga_data["famous_teams"])        
        season_id = get_current_season(competition_id)
        if not season_id:
            continue

        url = f"{BASE_URL}/seasons/{season_id}/schedules.json?api_key={API_KEY}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            matches = [
                match for match in data.get("schedules", [])
                if match.get("sport_event", {}).get("start_time", "").startswith(today) and
                any(team["abbreviation"] in famous_teams for team in match.get("sport_event", {}).get("competitors", []))
            ]

            if len(matches) > 2:
                matches = random.sample(matches, 2)
            important_matches[liga_name] = [
                {
                    "teams": [{
                        "name": match.get("sport_event", {})["competitors"][0]["name"],
                        "id": match.get("sport_event", {})["competitors"][0]["id"],
                    },
                    {
                        "name": match.get("sport_event", {})["competitors"][1]["name"],
                        "id": match.get("sport_event", {})["competitors"][1]["id"]
                    }
                    ],
                    "date": match.get("sport_event", {})["start_time"],
                }
                for match in matches
            ]
            time.sleep(3) 
        except requests.exceptions.RequestException as e:
            print(f"Error obteniendo partidos para {liga_name}: {e}")

    return jsonify(important_matches)


def get_famous_matches_with_statistics(today):
    important_matches = {}

    for liga_name, liga_data in ligas_famosas.items():
        competition_id = liga_data["id"]
        famous_teams = set(liga_data["famous_teams"])

        season_id = get_current_season(competition_id)
        if not season_id:
            continue

        url = f"{BASE_URL}/seasons/{season_id}/schedules.json?api_key={API_KEY}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            matches = [
                match for match in data.get("schedules", [])
                if match.get("sport_event", {}).get("start_time", "").startswith(today) and
                any(team["abbreviation"] in famous_teams for team in match.get("sport_event", {}).get("competitors", []))
            ]

            if len(matches) > 2:
                matches = random.sample(matches, 2)
            important_matches[liga_name] = [
                {
                    "teams": [{
                        "name": match.get("sport_event", {})["competitors"][0]["name"],
                        "id": match.get("sport_event", {})["competitors"][0]["id"],
                    },
                    {
                        "name": match.get("sport_event", {})["competitors"][1]["name"],
                        "id": match.get("sport_event", {})["competitors"][1]["id"]
                    }
                    ],
                    "event_id": match.get("sport_event", {}).get("id", 0),
                    "date": match.get("sport_event", {})["start_time"],
                    "statistics": {
                       **get_last_5_matches_statistics(match.get("sport_event", {})["competitors"][0]["id"], "A"),
                       **get_last_5_matches_statistics(match.get("sport_event", {})["competitors"][1]["id"], "B")
                    }
                }
                for match in matches
            ]
            time.sleep(3)
        except requests.exceptions.RequestException as e:
            print(f"Error obteniendo partidos para {liga_name}: {e}")

    return jsonify(important_matches)
