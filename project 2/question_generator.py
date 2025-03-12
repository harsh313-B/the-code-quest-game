import random
from typing import Dict, List, Optional
import json

class Question:
    def __init__(self, content: str, options: List[str], correct_answer: str, 
                 difficulty: int, category: str, explanation: str):
        self.content = content
        self.options = options
        self.correct_answer = correct_answer
        self.difficulty = difficulty
        self.category = category
        self.explanation = explanation
        self.code_snippet = None

class QuestionBank:
    def __init__(self):
        self.templates = {
            'python_basics': [
                {
                    'template': "What is the output of: print({value})?",
                    'options': lambda x: [str(x), str(x+1), str(x-1), f"'{x}'"],
                    'correct': lambda x: str(x),
                    'difficulty': 1
                },
                {
                    'template': "What is the data type of {value}?",
                    'options': lambda x: ['int', 'str', 'float', 'bool'],
                    'correct': lambda x: type(x).__name__,
                    'difficulty': 1
                }
            ],
            'data_structures': [
                {
                    'template': "What is the length of this list: [1, 2, ..., {value}]?",
                    'options': lambda x: [str(x), str(x+1), str(x-1), '0'],
                    'correct': lambda x: str(x),
                    'difficulty': 2
                },
                {
                    'template': "Which method adds an element to a list?",
                    'options': lambda x: ['append()', 'add()', 'insert()', 'extend()'],
                    'correct': lambda x: 'append()',
                    'difficulty': 1
                }
            ],
            'loops': [
                {
                    'template': "How many times will this loop run: for i in range({value})?",
                    'options': lambda x: [str(x), str(x-1), str(x+1), '0'],
                    'correct': lambda x: str(x),
                    'difficulty': 2
                }
            ],
            'functions': [
                {
                    'template': "What will be returned by: def func(): return {value}?",
                    'options': lambda x: [str(x), 'None', str(x+1), 'Error'],
                    'correct': lambda x: str(x),
                    'difficulty': 2
                }
            ],
            'algorithms': [
                {
                    'template': "What is the time complexity of a simple for loop iterating {value} times?",
                    'options': lambda x: ['O(n)', 'O(1)', 'O(n²)', 'O(log n)'],
                    'correct': lambda x: 'O(n)',
                    'difficulty': 3
                }
            ]
        }

    def get_question(self, level: int, topic: str = None) -> Optional[Question]:
        # Get questions for the specified topic or all topics
        templates = self.templates.get(topic, self.templates['python_basics'])
        
        # Filter templates by difficulty
        suitable_templates = [t for t in templates if t['difficulty'] <= level]
        
        if not suitable_templates:
            return None

        # Select a random template and generate question
        template = random.choice(suitable_templates)
        value = self._generate_value(level)
        return self._create_question_from_template(template, value, topic or 'python_basics')

    def _generate_value(self, level):
        # Generate appropriate values based on level
        if level <= 2:
            return random.randint(1, 10)
        elif level <= 4:
            return random.randint(10, 50)
        else:
            return random.randint(50, 100)

    def _create_question_from_template(self, template, value, topic):
        content = template['template'].format(value=value)
        options = template['options'](value)
        correct_answer = template['correct'](value)
        explanation = f"The correct answer is: {correct_answer}"
        return Question(content, options, correct_answer, 1, topic, explanation)

class QuestionManager:
    def __init__(self):
        self.question_bank = QuestionBank()
        self.answered_questions = set()

    def get_question(self, level: int, topic: str = None) -> Optional[Question]:
        # Get a question from the question bank
        question = self.question_bank.get_question(level, topic)
        
        # If no question is available, return None
        if not question:
            return None

        # Add to answered questions set
        question_key = (question.content, question.correct_answer)
        self.answered_questions.add(question_key)
        
        return question 