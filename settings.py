from os import environ


SESSION_CONFIGS = [
    dict(
        name='DM_Experiment_NC',
        display_name="NC",
        app_sequence=['experiment1'],
        num_demo_participants=4,
    ),
    dict(
        name='DM_Experiment_CT',
        display_name="CT",
        app_sequence=['experiment2'],
        num_demo_participants=2,
    ),
    dict(
        name='DM_Experiment_AF',
        display_name="AF",
        app_sequence=['experiment3'],
        num_demo_participants=2,
    ),
    dict(
        name='DM_Experiment_RT',
        display_name="RT",
        app_sequence=['experiment4'],
        num_demo_participants=2,
    ),
    dict(
        name='Public_Goods_Simple',
        display_name="Public Goods Simple",
        app_sequence=['public_goods_simple'],
        num_demo_participants=12,
    ),

]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Please select the game assigned to you
"""
OTREE_PRODUCTION=True

SECRET_KEY = '9658390416086'
INSTALLED_APPS = ['otree']
