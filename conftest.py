import pytest

from core import Responder


@pytest.fixture
def responder() -> Responder:
    return Responder()


@pytest.fixture
def character():
    return {'Player': {
        'name': 'Dancy',
        'attributes': {
            'Willpower': +3,
            'Reflexes': +1,
            'Fortitude': 0,
            'Violence': +5,
            'Perception': +3,
            'Soul': +3,
            'Coolness': +1,
            'Intuition': +1,
            'Reason': -1,
            'Charisma': -2,
        },
        'moves': [
            {
                'move': 'Divine Strength',
            },
            {
                'move': 'Enhanced Awareness',
                'attribute': 'Soul',
                'description':
                    "When you are at a location where the Illusion is weak, roll Soul. On a success you may have visions about the place and may be able to speak to animals and  entities tied to it."
                    "(15+) You can discern clear details."
                    "(10–14) You get some basic impressions."
                    "(−9) The Illusion tears. The veil to an alternate dimension is lifted temporarily, and the PC could be sucked into it or something may emerge out of it into our reality. The GM makes a move."
            },
        ],
    }}
