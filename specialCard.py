
"""
we have 3 types of special cards:
    1. balance_change
    2. move_to_field
    3. move_for_n_fields
    4. quiz
"""

import json
import random


class SpecialCard:

    # rule is dict from json 
    def __init__(self, rule):
        self.type = rule.get('type')
        self.info = rule.get('text_info')

        if self.type == 1:  # balance_change
            self.change_balance = rule.get('change_balance')
        elif self.type == 2:  # move_to_field
            self.move_to_id = rule.get('move_to_id')
        elif self.type == 3:  # move_for_n_fields
            self.move_for = rule.get('move_for')
            self.direction = rule.get('direction')
        elif self.type == 4:  # quiz
            self.question = rule.get('question')
            self.answers = rule.get('answers')
            self.correct_answer = rule.get('correct_answer')
            self.balance_add = rule.get('balance_add')
            self.balance_subtract = rule.get('balance_subtract')
        else:
            raise ValueError(f"Unknown card type: {self.type}")

    def get_card_info(self):
        if self.type == 1:  # balance_change
            info = {
                'type': self.type,
                'change_balance': self.change_balance,
                'text_info': self.info
            }
        elif self.type == 2:  # move_to_field
            info = {
                'type': self.type,
                'move_to_id': self.move_to_id,
                'text_info': self.info
            }
        elif self.type == 3:  # move_for_n_fields
            info = {
                'type': self.type,
                'move_for': self.move_for,
                'direction': self.direction,
                'text_info': self.info
            }
        elif self.type == 4:  # quiz
            answers = self.answers[:]
            random.shuffle(answers)
            correct_index = answers.index(self.correct_answer)
            info = {
                'type': self.type,
                'question': self.question,
                'answers': answers,
                'correct_answer': self.correct_answer,
                'correct_index': correct_index,
                'balance_add': self.balance_add,
                'balance_subtract': self.balance_subtract,
                'text_info': self.info
            }
        else:
            info = {'error': 'Unknown card type'}

        return json.dumps(info)

    def get_type(self):
        return self.type
    

    def __str__(self):
        return f"SpecialCard(type={self.type}, info={self.info})"