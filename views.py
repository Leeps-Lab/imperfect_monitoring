from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, parse_config


class Decision(Page):

    def is_displayed(self):
        return self.round_number <= self.group.num_rounds()

    def vars_for_template(self):
        return {
            "payoff_matrix": parse_config(self.session.config['config_file'])[self.round_number-1]['payoff_matrix'],
            "probability_matrix": parse_config(self.session.config['config_file'])[self.round_number-1]['probability_matrix'],
        }


class Results(Page):
    pass


page_sequence = [
    Decision,
    Results,
]
