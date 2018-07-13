from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from otree_redwood.models import DecisionGroup
from otree_redwood.utils import DiscreteEventEmitter
import csv, random, math
from jsonfield import JSONField


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
            'payoff_matrix': [
                [float(row['pi1(AGood)']), float(row['pi2(AGood)'])], [float(row['pi1(ABad)']), float(row['pi2(ABad)'])],
                [float(row['pi1(BGood)']), float(row['pi2(BGood)'])], [float(row['pi1(BBad)']), float(row['pi2(BBad)'])]
            ],
            'probability_matrix': [
                [float(row['p1(AA)']), float(row['p2(AA)'])], [float(row['p1(AB)']), float(row['p2(AB)'])],
                [float(row['p1(BA)']), float(row['p2(BA)'])], [float(row['p1(BB)']), float(row['p2(BB)'])]
            ],
            'displayed_subperiods': int(row['displayed_subperiods']),
            'subperiod_length': int(row['subperiod_length']),
            'rest_length_seconds': int(row['rest_length_seconds']),
            'seconds_per_tick': float(row['seconds_per_tick']),
            'num_signals': int(row['num_signals']),
            'display_average_a_graph': True if row['display_average_a_graph'] == 'TRUE' else False,
            'display_average_b_graph': True if row['display_average_b_graph'] == 'TRUE' else False,
            'display_average_ab_graph': True if row['display_average_ab_graph'] == 'TRUE' else False,
            'display_payoff_matrix': True if row['display_payoff_matrix'] == 'TRUE' else False,
            'display_score': True if row['display_score'] == 'TRUE' else False,
        })
    return rounds


class Constants(BaseConstants):
    name_in_url = 'imperfect_monitoring'
    players_per_group = 2
    num_rounds = 100


class Subsession(BaseSubsession):
    pass


class Group(DecisionGroup):
    subperiod_results = JSONField()

    def num_rounds(self):
        return len(parse_config(self.session.config['config_file']))
    
    def seconds_per_tick(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]['seconds_per_tick']

    def subperiod_length(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]['subperiod_length']

    def rest_length_seconds(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]['rest_length_seconds']

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

    def num_signals(self):
        return parse_config(self.session.config['config_file'])[self.round_number-1]['num_signals']
    
    def period_length(self):
        rest_length_seconds = self.rest_length_seconds()
        seconds_per_tick = self.seconds_per_tick()
        num_signals = self.num_signals()
        subperiod_length = self.subperiod_length()

        num_subperiods = math.ceil(num_signals / subperiod_length)

        return (num_signals * seconds_per_tick) + (num_subperiods * rest_length_seconds)
    
    def when_all_players_ready(self):
        super().when_all_players_ready()

        if not self.subperiod_results:
            self.subperiod_results = {}
            self.save(update_fields=['subperiod_results'])

        emitter = DiscreteEventEmitter(
            (self.seconds_per_tick() * self.subperiod_length()) + self.rest_length_seconds(),
            self.period_length(),
            self,
            self.subperiod_start,
            True)
        emitter.start()

    def subperiod_start(self, current_interval, intervals):
        self.refresh_from_db()
        msg = {}
        num_signals = min(self.num_signals() - current_interval * self.subperiod_length(), self.subperiod_length())

        for player in self.get_players():
            pcode = player.participant.code

            msg[pcode] = {
                'fixed_decision': self.group_decisions[pcode],
                'payoffs': self.calc_payoffs(player, num_signals, current_interval),
            }
        
        self.send('subperiod-start', msg)
    
    def calc_payoffs(self, player, num_signals, subperiod_num):
        payoff_matrix = parse_config(self.session.config['config_file'])[self.round_number-1]['payoff_matrix']
        probability_matrix = parse_config(self.session.config['config_file'])[self.round_number-1]['probability_matrix']

        pcode = player.participant.code
        my_decision = self.group_decisions[pcode]
        other_decision = [self.group_decisions[c] for c in self.group_decisions if c != pcode][0]

        payoffs = [e[player.id_in_group - 1] for e in payoff_matrix]
        probabilities = [e[player.id_in_group - 1] for e in probability_matrix]

        prob = ((my_decision * other_decision * probabilities[0]) +
                    (my_decision * (1 - other_decision) * probabilities[1]) +
                    ((1 - my_decision) * other_decision * probabilities[2]) +
                    ((1 - my_decision) * (1 - other_decision) * probabilities[3]))
        
        realized_payoffs = []
        for i in range(num_signals):
            if random.random() <= prob:
                if my_decision == 1:
                    realized_payoffs.append(payoffs[1])
                else:
                    realized_payoffs.append(payoffs[3])
                self.add_subperiod_result(pcode, 'B', subperiod_num)
            else:
                if my_decision == 1:
                    realized_payoffs.append(payoffs[0])
                else:
                    realized_payoffs.append(payoffs[2])
                self.add_subperiod_result(pcode, 'G', subperiod_num)
        
        player.payoff += sum(realized_payoffs)
        player.save()

        return realized_payoffs
    
    def add_subperiod_result(self, pcode, result, subperiod_num):
        subperiod_key = str(subperiod_num)

        if subperiod_key not in self.subperiod_results:
            self.subperiod_results[subperiod_key] = {}
        if pcode not in self.subperiod_results[subperiod_key]:
            self.subperiod_results[subperiod_key][pcode] = ''

        self.subperiod_results[subperiod_key][pcode] += result
        self.save(update_fields=['subperiod_results'])
    

class Player(BasePlayer):
    # store randomly generated initial decisions for each round
    # ensures that calling initial_decision twice in the same round gives the same result
    decisions_by_round = JSONField()

    def initial_decision(self):
        self.refresh_from_db()

        if not self.decisions_by_round:
            self.decisions_by_round = {}
        
        key = str(self.round_number)

        if key in self.decisions_by_round:
            return self.decisions_by_round[key]
        
        decision = random.choice([0, 1])
        self.decisions_by_round[key] = decision
        # self.save() doesn't save JSONFields, so this line manually saves decisions_by_round
        # see otree_redwood.models.Group.save for more info
        self.__class__._default_manager.filter(pk=self.pk).update(decisions_by_round=self.decisions_by_round)
        return decision