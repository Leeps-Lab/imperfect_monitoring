from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from otree_redwood.models import DecisionGroup
import csv


author = 'Your name here'

doc = """
Your app description
"""

def parse_config(config_file):
    with open('imperfect_monitoring/configs/' + config_file) as f:
        rows = list(csv.DictReader(f))

    rounds = []
    for row in rows:
        rounds.append({
            'displayed_subperiods': int(row['displayed_subperiods']),
            'subperiod_length': int(row['subperiod_length']),
            'rest_length': int(row['rest_length']),
            'seconds_per_tick': float(row['seconds_per_tick']),
            'display_average_a_graph': True if row['display_average_a_graph'] == 'TRUE' else False,
            'display_average_b_graph': True if row['display_average_b_graph'] == 'TRUE' else False,
            'display_average_ab_graph': True if row['display_average_ab_graph'] == 'TRUE' else False,
            'display_payoff_matrix': True if row['display_payoff_matrix'] == 'TRUE' else False,
            'display_score': True if row['display_score'] == 'TRUE' else False,
            'num_subperiods': 0 if row['num_subperiods'] == 'RANDOM' else int(row['num_subperiods']),
            'payoff_matrix': [
                [float(row['pi1(AGood)']), float(row['pi2(AGood)'])], [float(row['pi1(ABad)']), float(row['pi2(ABad)'])],
                [float(row['pi1(BGood)']), float(row['pi2(BGood)'])], [float(row['pi1(BBad)']), float(row['pi2(BBad)'])]
            ],
            'probability_matrix': [
                [float(row['p1(AA)']), float(row['p2(AA)'])], [float(row['p1(AB)']), float(row['p2(AB)'])],
                [float(row['p1(BA)']), float(row['p2(BA)'])], [float(row['p1(BB)']), float(row['p2(BB)'])]
            ],
        })
    return rounds

class Constants(BaseConstants):
    name_in_url = 'imperfect_monitoring'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(DecisionGroup):
    def num_rounds(self):
        return len(parse_config(self.session.config['config_file']))

    def subperiod_length(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]['subperiod_length']

    def rest_length(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]['rest_length']

    def displayed_subperiods(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]['displayed_subperiods']

    def display_average_a_graph(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]['display_average_a_graph']

    def display_average_b_graph(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]['display_average_b_graph']

    def display_average_ab_graph(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]['display_average_ab_graph']

    def display_payoff_matrix(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]['display_payoff_matrix']

    def display_score(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]['display_score']

    def number_subperiods(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]['num_subperiods']


class Player(BasePlayer):
    def initial_decisision(self):
        return 0