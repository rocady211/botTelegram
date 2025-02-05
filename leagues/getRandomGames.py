import random
from .utils import ligas_famosas


rangeOfLeagues = len(ligas_famosas)


def generateAndValidateNumbersAleatoryInArray(array):
    random_number = random.randint(0, len(ligas_famosas) - 1)
    if(random_number in array):
        return generateAndValidateNumbersAleatoryInArray(array)
    else:
        return random_number


def getRandomsGames(numberGamesToSelect, dayGamesPerLeague, countSelected=0, randomNumbersGenerated=None, items=None):
    if randomNumbersGenerated is None:
        randomNumbersGenerated = []
    if items is None:
        items = []
    print('llega',dayGamesPerLeague)

    randomLeagueNumber = generateAndValidateNumbersAleatoryInArray(randomNumbersGenerated)
    randomNumbersGenerated.append(randomLeagueNumber)

    randomLeague = list(ligas_famosas.keys())[randomLeagueNumber]

    league_games = dayGamesPerLeague.get(randomLeague, [])
    longToRandomLeague = len(league_games)

    if numberGamesToSelect == countSelected or len(randomNumbersGenerated) >= rangeOfLeagues:
        return items

    if longToRandomLeague == 0:
        return getRandomsGames(numberGamesToSelect, dayGamesPerLeague, countSelected, randomNumbersGenerated, items)

    elif longToRandomLeague == 1:
        items.append(league_games[0])
        return getRandomsGames(numberGamesToSelect, dayGamesPerLeague, countSelected + 1, randomNumbersGenerated, items)

    else:
        randomNumberBinary = random.randint(0, longToRandomLeague - 1)  
        items.append(league_games[randomNumberBinary])
        return getRandomsGames(numberGamesToSelect, dayGamesPerLeague, countSelected + 1, randomNumbersGenerated, items)

