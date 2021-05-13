from pathlib import Path
from random import randint

import yaml

import fuzzy

from parse import parse


class Responder:
    
    def __init__(self):
        data = yaml.load(
            Path(__file__).with_name('data.yaml').read_text(),
            Loader=yaml.SafeLoader,
        )
        self.characters = data['characters']
        self.basic_moves = data['Basic moves']
        self.all_moves_by_user = {}
        for username, values in self.characters.items():
            character_moves = values.get('moves', [])
            character_moves.extend(self.basic_moves)
            self.all_moves_by_user[username] = character_moves

    def __call__(self, username, message):
        # if username not in self.characters:
        #     return f'En tiedä kuka on {username}'

        action = parse(message)

        if not action:
            return

        if action.action == 'apua':
            return (
              'Heitä kirjoittamalla esim. "a Avoid Harm".\n'
              'Botti käyttää hahmosi attribuutteja heitossa.\n'
              'Riittää kun kirjoitat sinne päin, "a avoid" luultavasti riittää.\n'
              'Lisää loppuun väliaikaiset säädöt, esim. "a engage -2".'
            )

        elif action.action == 'move':
            character = self.characters[username]
            all_moves = self.all_moves_by_user[username]
            move = self.get_move(action.move, all_moves)
            if not move:
                return f'En löydä movea: {action.move}'
            return self.throw(character, move, action.modifier)
            
        else:
            print('Something wrong with action:', action.__dict__)
            return 'Hämmennys'
    
    def throw(self, character, move, situation_modifier):        
        first_throw = self.throw_one()
        second_throw = self.throw_one()
        try:
            attribute_modifier = character['attributes'][move['attribute']]
        except KeyError as e:
            print('Character data missing', character, move, e)
            return 'Ei onnistu, jotain hässäkkää hahmon tiedoissa'
        
        result = first_throw + second_throw + attribute_modifier + situation_modifier

        reply = f'{character["name"]} - {move["move"]} - {first_throw} {second_throw}'

        if attribute_modifier != 0:
            reply += f' {"+" if attribute_modifier > 0 else ""}{attribute_modifier}'

        if situation_modifier:
            reply += f' {"+" if situation_modifier > 0 else ""}{situation_modifier}'

        reply += f' = {result}'

        return reply

    def get_move(self, move_name, all_moves):
        return fuzzy.fuzzyfinder(move_name, all_moves, accessor=lambda x: x['move'])

    @staticmethod
    def throw_one():
        return randint(1, 12)

    def get_html(self):
        return f'''
        <body class="text-sm text-gray-900 bg-gradient-to-r from-green-400 to-blue-500">
        {self.html_characters()}
        </body>'''

    def html_characters(self):
        return ''.join([
            self.html_character(character) for character in self.characters.values()
        ])

    def html_character(self, character):
        title = character["name"]
        attributes_html = self.html_attributes(character)
        moves = character.get('moves')
        moves_html = moves and self.html_moves(moves) or ''
        content = f'{attributes_html}{moves_html}'
        return f'<details class="p-4 m-4 bg-white"><summary>{title}</summary>{content}</details>'

    def html_attributes(self, character):
        attributes = character.get('attributes')
        if not attributes:
            return ''
        attribute_html = '&nbsp;&nbsp;&nbsp;'.join([f'⊛ {name}: {value}' for name, value in list(attributes.items())[:3]])
        attribute_html += '<br/>'
        attribute_html += '&nbsp;&nbsp;&nbsp;'.join([f'⊛ {name}: {value}' for name, value in list(attributes.items())[3:]])
        attribute_html = f'<div class="p-4">{attribute_html}</div>'
        return attribute_html

    def html_basic_moves(self):
        return self.html_moves(self.basic_moves)

    def html_moves(self, moves):
        return ''.join([self.html_move(move) for move in moves])

    def html_move(self, move):
        attribute = move.get("attribute")
        attribute_html = attribute and f' ({attribute})' or ''
        title = f'{move["move"]}{attribute_html}'
        content = move.get("description", '').replace('\n', '<br/>')
        return f'<details class="p-4"><summary>{title}</summary><div class="p-4">{content}</div></details>'
    
