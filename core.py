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
    
    def get_username_by_character_name(self, character_name):
        for username, character in self.characters.items():
            if character['name'].lower() == character_name.lower():
                return username
        return None

    def throw(self, character, move, situation_modifier):        
        first_throw = self.throw_one()
        second_throw = self.throw_one()
        try:
            attribute_modifier = character['attributes'][move['attribute']]
        except KeyError:
            attribute_modifier = 0
        
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
        return randint(1, 10)

    def get_html(self):
        return f'''
        <body class="bg-gradient-to-r from-green-800 to-green-500">
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
        moves_html = moves and self.html_moves(moves, character) or ''
        content = f'{attributes_html}{moves_html}'
        return f'<details class="p-4 m-4 bg-white bg-opacity-75"><summary>{title}</summary>{content}</details>'

    def html_attributes(self, character):
        attributes = character.get('attributes')
        if not attributes:
            return ''
        attribute_html = self.html_attribute_set(list(attributes.items())[:3])
        attribute_html += '<br/>'
        attribute_html += self.html_attribute_set(list(attributes.items())[3:])
        attribute_html = f'<div class="p-4">{attribute_html}</div>'
        return attribute_html

    def html_attribute_set(self, attributes):
        return '&nbsp;&nbsp;&nbsp;'.join([f'<span style="color: darkGreen; font-weight: 300;">{name}:</span> {value}' for name, value in attributes])

    def html_basic_moves(self):
        return self.html_moves(self.basic_moves)

    def html_moves(self, moves, character):
        return ''.join([self.html_move(move, character) for move in moves])

    def html_move(self, move, character):
        attribute = move.get("attribute")
        modifier = attribute and character['attributes'].get(attribute) or 0
        attribute_html = attribute and f' <span style="font-weight: 300">({attribute}: {modifier:+})</span>' or ''
        throw_html = attribute and self.throw_buttons_html(move, character) or ''
        title = f'<span style="color: darkGreen;"><b>{move["move"]}</b>{attribute_html} {throw_html}</span> '
        content = move.get("description", '').replace('\n', '<br/>')
        return f'<details class="p-4"><summary>{title}</summary><div class="p-4" style="font-weight: 300">{content}</div></details>'
    
    def throw_buttons_html(self, move, character):
        this_id = self.make_id(character, move)
        return f'<span id="{this_id}">' + ' '.join([
            f'<button hx-get="{self.make_url(character, move, modifier)}" hx-trigger="click" hx-target="#{this_id}" style="background-color: rgba(239, 246, 255); color: darkGreen; padding: -4px 16px; line-height: 1.2em; border-radius: 4px;">&nbsp;&nbsp;&nbsp;{modifier:+}&nbsp;&nbsp;&nbsp;</button>'
            for modifier in range(-4, 5)
        ]) + '</span>'

    def buttons(self, character, move_name):
        character = self.characters[self.get_username_by_character_name(character)]
        for move in character['moves']:
            if move['move'].lower() == move_name:
                return self.throw_buttons_html(move, character)
        return "Big problem"

    @staticmethod
    def make_id(character, move):
        move_id = f'{character["name"]}-{move["move"]}'.lower()
        move_id = '-'.join(move_id.split())
        return move_id

    @staticmethod
    def make_url(character, move, modifier):
        move_url = f'/throw/{character["name"]}/{move["move"]}/{modifier}'.lower()
        move_url = '-'.join(move_url.split())
        return move_url
