
import json
from collections import Counter, defaultdict

def analyze_stats():
    with open('game_stats.json', 'r') as f:
        data = json.load(f)

    games = data.get('games', [])
    total_games = len(games)
    
    if total_games == 0:
        print("No games found.")
        return

    mafia_wins = 0
    town_wins = 0
    total_turns = 0

    player_stats = defaultdict(lambda: {'games_played': 0, 'wins': 0, 'mafia_games': 0, 'mafia_wins': 0, 'town_games': 0, 'town_wins': 0, 'survived': 0})
    
    for game in games:
        if game.get('winner') == 'Mafia':
            mafia_wins += 1
        else:
            town_wins += 1
        
        total_turns += game.get('turns', 0)
        
        # Determine winner for this game to check individual player wins
        game_winner = game.get('winner')

        for player in game.get('players', []):
            name = player.get('name')
            role = player.get('role')
            survived = player.get('survived')
            
            stats = player_stats[name]
            stats['games_played'] += 1
            if survived:
                stats['survived'] += 1
            
            is_mafia = role == 'Mafia'
            if is_mafia:
                stats['mafia_games'] += 1
                if game_winner == 'Mafia':
                    stats['mafia_wins'] += 1
                    stats['wins'] += 1
            else:
                stats['town_games'] += 1
                if game_winner == 'Town':
                    stats['town_wins'] += 1
                    stats['wins'] += 1

    print(f"Total Games: {total_games}")
    print(f"Mafia Wins: {mafia_wins} ({mafia_wins/total_games*100:.1f}%)")
    print(f"Town Wins: {town_wins} ({town_wins/total_games*100:.1f}%)")
    print(f"Average Turns: {total_turns/total_games:.1f}")
    
    print("\nPlayer Stats (Name | GP | Win% | Surv% | Mafia Win% | Town Win%):")
    sorted_players = sorted(player_stats.items(), key=lambda item: (item[1]['wins']/item[1]['games_played']), reverse=True)
    
    for name, stats in sorted_players:
        gp = stats['games_played']
        win_rate = (stats['wins'] / gp) * 100
        surv_rate = (stats['survived'] / gp) * 100
        
        mafia_wr = 0.0
        if stats['mafia_games'] > 0:
            mafia_wr = (stats['mafia_wins'] / stats['mafia_games']) * 100
            
        town_wr = 0.0
        if stats['town_games'] > 0:
            town_wr = (stats['town_wins'] / stats['town_games']) * 100
            
        print(f"{name:<10} | {gp:<2} | {win_rate:>5.1f}% | {surv_rate:>5.1f}% | {mafia_wr:>9.1f}% ({stats['mafia_games']}) | {town_wr:>8.1f}% ({stats['town_games']})")

if __name__ == "__main__":
    analyze_stats()
