from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, parse_config
import math


class Instructions(Page):

    def is_displayed(self):
        return self.round_number == 1
    
    def vars_for_template(self):
        return {
            'instructions_link': self.session.config['instructions_link'],
        }


class Decision(Page):

    def is_displayed(self):
        return self.round_number <= self.group.num_rounds()

    def vars_for_template(self):
        return {
            "payoff_matrix": parse_config(self.session.config['config_file'])[self.round_number-1]['payoff_matrix'],
            "probability_matrix": parse_config(self.session.config['config_file'])[self.round_number-1]['probability_matrix'],
        }


class Results(Page):

    def is_displayed(self):
        return self.round_number <= self.group.num_rounds()


def get_config_columns(group):
    num_signals = group.num_signals()
    subperiod_length = group.subperiod_length()
    num_subperiods = math.ceil(num_signals / subperiod_length)

    seconds_per_tick = group.seconds_per_tick()
    rest_length = group.rest_length_seconds()

    config = parse_config(group.session.config['config_file'])
    payoff_matrix = config[group.round_number - 1]['payoff_matrix']
    probability_matrix = config[group.round_number - 1]['probability_matrix']

    return [num_subperiods, seconds_per_tick, rest_length, payoff_matrix, probability_matrix]

def get_output_table_header(groups):
    return [
        'timestamp_of_start',
        'session_ID',
        'period_id',
        'pair_id',     
        'p1_code',
        'p2_code',
        'p1_action',
        'p2_action',
        'p1_countGood',
        'p2_countGood',
        'p1_periodResult',
        'p2_periodResult',
        'p1_avg_payoffs',
        'p2_avg_payoffs',
        'subperiod_length',
        'num_subperiods',
        'seconds_per_tick',
        'rest_length_seconds',
        'payoff_matrix(AGood, ABad, BGood, BBad)',
        'probability_matrix(AA, AB, BA, BB)'
    ]

def get_output_table(events):
    if not events:
        return []
    rows = []
    p1, p2 = events[0].group.get_players()
    p1_code = p1.participant.code
    p2_code = p2.participant.code
    group = events[0].group
    config_columns = get_config_columns(group)
    subperiod_num = 0
    for event in events:
        if event.channel == 'subperiod-start':
            p1_result = group.subperiod_results[str(subperiod_num)][p1_code]
            p2_result = group.subperiod_results[str(subperiod_num)][p2_code]
            p1_payoffs = event.value[p1_code]['payoffs']
            p2_payoffs = event.value[p2_code]['payoffs']
            rows.append([
                event.timestamp,
                group.session.code,
                group.subsession_id,
                group.id_in_subsession,
                p1_code,
                p2_code,
                event.value[p1_code]['fixed_decision'],
                event.value[p2_code]['fixed_decision'],
                p1_result.count('G'),
                p2_result.count('G'),
                p1_result,
                p2_result,
                sum(p1_payoffs) / len(p1_payoffs),
                sum(p2_payoffs) / len(p2_payoffs),
                len(p1_payoffs)
            ] + config_columns)
            subperiod_num += 1

    rows.append("")
            
    return rows


page_sequence = [
    Instructions,
    Decision,
    Results,
]
