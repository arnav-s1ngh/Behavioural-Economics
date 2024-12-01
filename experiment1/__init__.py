from otree.api import *
import random

doc = """
Asymmetric Information Experiment with Multiple Utility Tables
"""


class C(BaseConstants):
    NAME_IN_URL = 'asymmetric_info'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    # Define the three different utility tables
    UTILITY_TABLES = [
        {
            'buyer_choices': ['Low', 'High'],
            'seller_choices': ['Accept', 'Reject'],
            'utilities': {
                ('Low', 'Accept'): {'buyer': 5, 'seller': 3},
                ('Low', 'Reject'): {'buyer': 0, 'seller': 0},
                ('High', 'Accept'): {'buyer': 2, 'seller': 6},
                ('High', 'Reject'): {'buyer': 0, 'seller': 0}
            }
        },
        {
            'buyer_choices': ['Low', 'High'],
            'seller_choices': ['Accept', 'Reject'],
            'utilities': {
                ('Low', 'Accept'): {'buyer': 4, 'seller': 4},
                ('Low', 'Reject'): {'buyer': 0, 'seller': 0},
                ('High', 'Accept'): {'buyer': 1, 'seller': 7},
                ('High', 'Reject'): {'buyer': 0, 'seller': 0}
            }
        },
        {
            'buyer_choices': ['Low', 'High'],
            'seller_choices': ['Accept', 'Reject'],
            'utilities': {
                ('Low', 'Accept'): {'buyer': 6, 'seller': 2},
                ('Low', 'Reject'): {'buyer': 0, 'seller': 0},
                ('High', 'Accept'): {'buyer': 3, 'seller': 5},
                ('High', 'Reject'): {'buyer': 0, 'seller': 0}
            }
        }
    ]


class Subsession(BaseSubsession):
    scenario = models.IntegerField()


def creating_session(subsession: Subsession):
    # Randomly select one of the three utility tables for the session
    subsession.scenario = random.randint(0, len(C.UTILITY_TABLES) - 1)

    # Create groups of 2 players
    subsession.group_randomly()

    # Explicitly set buyer and seller roles
    for group in subsession.get_groups():
        players = group.get_players()
        players[0].is_buyer = True
        players[1].is_buyer = False


class Group(BaseGroup):
    buyer_choice = models.StringField(
        choices=['Low', 'High'],
        doc="Choice made by the buyer"
    )
    seller_choice = models.StringField(
        choices=['Accept', 'Reject'],
        doc="Choice made by the seller"
    )

    buyer_payoff = models.CurrencyField()
    seller_payoff = models.CurrencyField()


class Player(BasePlayer):
    is_buyer = models.BooleanField(initial=False)


def set_payoffs(group: Group):
    # Get the current scenario's utility table
    scenario = group.subsession.scenario
    utility_table = C.UTILITY_TABLES[scenario]

    # Find buyer and seller
    buyer = [p for p in group.get_players() if p.is_buyer][0]
    seller = [p for p in group.get_players() if not p.is_buyer][0]

    # Calculate payoffs based on choices and current scenario
    payoff_key = (group.buyer_choice, group.seller_choice)

    if payoff_key in utility_table['utilities']:
        buyer.payoff = utility_table['utilities'][payoff_key]['buyer']
        seller.payoff = utility_table['utilities'][payoff_key]['seller']

        # Store group-level payoffs for reference
        group.buyer_payoff = buyer.payoff
        group.seller_payoff = seller.payoff
    else:
        # Fallback in case of unexpected choices
        buyer.payoff = 0
        seller.payoff = 0
        group.buyer_payoff = 0
        group.seller_payoff = 0


# Pages
class Introduction(Page):
    pass


class BuyerChoice(Page):
    form_model = 'group'
    form_fields = ['buyer_choice']
    @staticmethod
    def is_displayed(player: Player):
        return player.field_maybe_none('is_buyer') == True


class BuyerChoiceWaitPage(WaitPage):
    title_text = "Waiting for Buyer's Decision"
    body_text = "Waiting for the buyer to make a choice."

    @staticmethod
    def is_displayed(player):
        return not player.is_buyer



class SellerChoice(Page):
    form_model = 'group'
    form_fields = ['seller_choice']

    @staticmethod
    def is_displayed(player: Player):
        return player.field_maybe_none('is_buyer') == False

    def vars_for_template(self):
        # Check if buyer's choice is set
        buyer_choice = self.group.field_maybe_none('buyer_choice')

        # If buyer's choice is not set, return a flag for the template
        if buyer_choice is None:
            return {
                'waiting_for_buyer': True,
                'buyer_choice': None
            }

        return {
            'waiting_for_buyer': False,
            'buyer_choice': buyer_choice
        }

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs
    title_text = "Calculating Results"
    body_text = "Waiting for all players to make their decisions and calculating payoffs."


class Results(Page):
    @staticmethod
    def vars_for_template(player):
        # Retrieve the scenario details for display
        scenario = player.subsession.scenario
        return {
            'scenario_details': C.UTILITY_TABLES[scenario]
        }




# Modify the page_sequence to include the new WaitPage
page_sequence = [
    Introduction,
    BuyerChoice,
    BuyerChoiceWaitPage,
    SellerChoice,
    ResultsWaitPage,
    Results
]

page_sequence = [
    Introduction,
    BuyerChoice,
    SellerChoice,
    ResultsWaitPage,
    Results
]
