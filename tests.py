import fuzzy

from core import Responder
from parse import is_this_for_me
from parse import parse


def test_fuzzy_as_text():
    corpus = ['Avoid Harm', 'Keep It Together']
    result = fuzzy.fuzzyfinder('avod', corpus)
    assert result == 'Avoid Harm'


def test_fuzzy_miss():
    corpus = ['Avoid Harm', 'Keep It Together']
    result = fuzzy.fuzzyfinder('xyz', corpus)
    assert result is None


def test_fuzzy_as_dict():
    corpus = [{'move': 'Avoid Harm'}, {'move': 'Keep It Together'}]
    result = fuzzy.fuzzyfinder('avod', corpus, accessor=lambda x: x['move'])
    assert result == {'move': 'Avoid Harm'}


def test_is_this_for_me():
    assert is_this_for_me('') == []
    assert is_this_for_me('a ') == ['apua']
    assert is_this_for_me('a apua') == ['apua']
    assert is_this_for_me('a jotain') == ['jotain']
    assert is_this_for_me('A Keep It Together') == 'keep it together'.split()


def test_parser():
    assert not parse('')
    assert not parse('foobar')
    assert not parse('a -2')
    assert not parse('a -')
    assert parse('a').action == 'apua'
    assert parse('a Keep It Together').move == 'keep it together'
    assert parse('a avoid -2').modifier == -2
    assert parse('a avoid + 2').modifier == 2
    assert parse('a avoid + 2').move == 'avoid'


def test_responder_setup(responder: Responder):
    username = next(iter(responder.characters))
    assert 'name' in responder.characters[username]
    assert 'move' in responder.basic_moves[0]
    assert all([type(move) is dict for move in responder.all_moves_by_user[username]])


def test_basic_responses(responder):
    username = next(iter(responder.characters))
    assert responder('Dummy', '') == None
    assert responder(username, '') == None
    assert responder(username, 'Hölynpöly') == None
    assert "Heitä kirjoittamalla" in responder(username, 'a')
    assert responder(username, 'a foobar') == "En löydä movea: foobar"
    

def test_throws(monkeypatch, responder):
    username = next(iter(responder.characters))
    monkeypatch.setattr(responder, 'throw_one', lambda: 4)
    assert responder(username, 'a avoid') == 'Dancy - Avoid Harm - 4 4 +1 = 9'
    assert responder(username, 'a avoid -2') == 'Dancy - Avoid Harm - 4 4 +1 -2 = 7'

def test_make_id():
    move_id = Responder.make_id(
        {'name': 'Character'},
        {'move': 'Move Name'},
    )
    assert move_id == 'character-move-name'
    
def  test_make_url(responder):
    move_url = Responder.make_url(
        {'name': 'Character'},
        {'move': 'Move Name'},
        +2,
    )
    assert move_url == '/throw/character/move-name/2'
