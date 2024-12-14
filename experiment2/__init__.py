from otree.api import *
import random

doc = """
Asymmetric Information Experiment with Multiple Utility Tables
"""

class C(BaseConstants):
    NAME_IN_URL = 'CT'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3
    tab_key = random.randint(0, 2)

    # Define the three different utility tables
    UTILITY_TABLES = [
        {
            'table_color': "Red",
            'buyer_choices': ['R1', 'R2', 'R3'],
            'seller_choices': ['C1', 'C2'],
            'utilities': {
                ('R1', 'C1'): {'buyer': 400, 'seller': 200},
                ('R1', 'C2'): {'buyer': 350, 'seller': 0},
                ('R2', 'C1'): {'buyer': 150, 'seller': 450},
                ('R2', 'C2'): {'buyer': 350, 'seller': 0},
                ('R3', 'C1'): {'buyer': 0, 'seller': 600},
                ('R3', 'C2'): {'buyer': 350, 'seller': 0},

            }
        },
        {
            'table_color': "Blue",
            'buyer_choices': ['R1', 'R2', 'R3'],
            'seller_choices': ['C1', 'C2'],
            'utilities': {
                ('R1', 'C1'): {'buyer': 1000, 'seller': 200},
                ('R1', 'C2'): {'buyer': 350, 'seller': 500},
                ('R2', 'C1'): {'buyer': 750, 'seller': 450},
                ('R2', 'C2'): {'buyer': 350, 'seller': 500},
                ('R3', 'C1'): {'buyer': 600, 'seller': 600},
                ('R3', 'C2'): {'buyer': 350, 'seller': 500},

            }
        },
        {
            'table_color': "White",
            'buyer_choices': ['R1', 'R2', 'R3'],
            'seller_choices': ['C1', 'C2'],
            'utilities': {
                ('R1', 'C1'): {'buyer': 700, 'seller': 200},
                ('R1', 'C2'): {'buyer': 350, 'seller': 250},
                ('R2', 'C1'): {'buyer': 450, 'seller': 450},
                ('R2', 'C2'): {'buyer': 350, 'seller': 250},
                ('R3', 'C1'): {'buyer': 300, 'seller': 600},
                ('R3', 'C2'): {'buyer': 350, 'seller': 250},

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
        choices=['R1', 'R2', 'R3'],
        doc="Choice made by the buyer"
    )
    seller_choice=models.StringField(
        choices=['C1','C2'],
        doc="Choice made by the seller"
    )
    table_color = models.StringField(
        choices=['Red', 'White', 'Blue'],
        doc="Choice made by the seller"
    )
    buyer_payoff = models.CurrencyField()
    seller_payoff = models.CurrencyField()
    message_table_color1 = models.StringField(
        blank=True,
        doc="The table colors the seller decides to send to the buyer",
    )
    message_table_color2 = models.StringField(
        blank=True,
        doc="The table colors the seller decides to send to the buyer",
    )
    message_table_color3 = models.StringField(
        blank=True,
        doc="The table colors the seller decides to send to the buyer",
    )


class Player(BasePlayer):
    is_buyer = models.BooleanField(initial=False)


def set_payoffs(group: Group):
    # Get the current scenario's utility table
    scenario = group.subsession.scenario

    utility_table = C.UTILITY_TABLES[C.tab_key]

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

    def vars_for_template(self):
        return {
            'seller_message_color1': self.group.field_maybe_none('message_table_color1'),
            'seller_message_color2': self.group.field_maybe_none('message_table_color2'),
            'seller_message_color3': self.group.field_maybe_none('message_table_color3'),
        }


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
        asymmetric_info=C.tab_key
        if asymmetric_info==0:
            asymmetric_info="Red"
        if asymmetric_info==1:
            asymmetric_info="Blue"
        if asymmetric_info==2:
            asymmetric_info="White"

        # If buyer's choice is not set, return a flag for the template
        if buyer_choice is None:
            return {
                'waiting_for_buyer': True,
                'buyer_choice': None,
                'asymmetric_info': asymmetric_info

            }

        return {
            'waiting_for_buyer': False,
            'buyer_choice': buyer_choice,
            'asymmetric_info':asymmetric_info
        }

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs
    title_text = "Calculating Results"
    body_text = "Waiting for all players to make their decisions and calculating payoffs."

class Results(Page):
    @staticmethod
    def vars_for_template(player):
        # Retrieve the scenario details for display
        return {
            'scenario_details': C.UTILITY_TABLES[C.tab_key]
        }

class SenderChoiceWaitPage(WaitPage):
    title_text = "Waiting for Seller's Message"
    body_text = "Keep on reloading this page till you receive the Seller's Message ."

    @staticmethod
    def is_displayed(player):
        return player.is_buyer

class BuyerSendDataPage(Page):
    form_model = 'group'
    form_fields = ['message_table_color1','message_table_color2','message_table_color3']
    @staticmethod
    def is_displayed(player: Player):
        return not player.is_buyer

    def vars_for_template(self):
        asymmetric_info = C.tab_key
        if asymmetric_info == 0:
            asymmetric_info = "Red"
        if asymmetric_info == 1:
            asymmetric_info = "Blue"
        if asymmetric_info == 2:
            asymmetric_info = "White"
        return {
            'available_colors': ['Red', 'Blue', 'White'],  # All available table colors
            'asymmetric_info': asymmetric_info
        }




# Modify the page_sequence to include the new WaitPage
page_sequence = [
    Introduction,
    BuyerSendDataPage,
    SenderChoiceWaitPage,
    BuyerChoice,
    BuyerChoiceWaitPage,
    SellerChoice,
    ResultsWaitPage,
    Results
]