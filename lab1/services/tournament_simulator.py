import math
import random
from typing import Any, Dict

from django.db.models import QuerySet

from lab1.models import Team
from lab1.services.event_simulator import EventSimulator


class TournamentSimulator:
    def __init__(self, teams_queryset: QuerySet[Team]):
        team_count = teams_queryset.count()
        if team_count == 0:
            raise ValueError("There are no teams to participate in the tournament.")

        k = int(math.log2(team_count))
        if 2 ** k != team_count:
            k = k if 2 ** k < team_count else k - 1

        required_teams = 2 ** k
        if k > 6:
            required_teams = 2 ** 6

        if team_count > required_teams:
            self.teams = list(teams_queryset.order_by('-rating')[:required_teams])
        else:
            self.teams = list(teams_queryset)

        self.num_teams = len(self.teams)
        self.num_stages = int(math.log2(self.num_teams))

        if self.num_teams < 2 or (self.num_teams & (self.num_teams - 1)) != 0:
            raise ValueError("The number of teams must be a power of two (2, 4, 8, 16, 32, 64).")

        self.stages_history = []
        self.winner = None

    @staticmethod
    def _simulate_match(team1: Team, team2: Team) -> Team:
        prob_team1_wins = team1.get_win_probability_against(team2)
        if EventSimulator.simulate_simple_event(prob_team1_wins):
            return team1
        else:
            return team2

    def run_tournament(self):
        if self.num_teams < 2:
            raise ValueError("A minimum of 2 teams are required to host the tournament.")

        current_stage_teams = list(self.teams)

        self.stages_history.append({
            'stage_number': 0,
            'description': 'Tournament participants',
            'matches': [],
            'winners': [{'team': team, 'from_match': None} for team in current_stage_teams]
        })

        for stage in range(1, self.num_stages + 1):
            random.shuffle(current_stage_teams)

            next_stage_teams = []
            matches_in_stage = []

            for i in range(0, len(current_stage_teams), 2):
                team1 = current_stage_teams[i]
                team2 = current_stage_teams[i + 1]

                winner = self._simulate_match(team1, team2)
                next_stage_teams.append(winner)

                matches_in_stage.append({
                    'team1': team1,
                    'team2': team2,
                    'winner': winner,
                    'loser': team2 if winner == team1 else team1
                })

            self.stages_history.append({
                'stage_number': stage,
                'description': f'Stage {stage}',
                'matches': matches_in_stage,
                'winners': [{'team': team, 'from_match': match} for team, match in
                            zip(next_stage_teams, matches_in_stage)]
            })

            current_stage_teams = next_stage_teams

        self.winner = current_stage_teams[0]

    def get_tournament_result(self) -> Dict[str, Any]:
        if not self.winner:
            raise RuntimeError("The tournament has not been played yet. Call run_tournament() first.")

        return {
            'total_teams': self.num_teams,
            'total_stages': self.num_stages,
            'winner': self.winner,
            'stages_history': self.stages_history
        }
