#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import re
from urllib.parse import urljoin

import requests

BASE_URL = 'http://dev-challenge.thisplace.com'

QUESTION_URL_RE = '\/question\/([0-9])\/([\w0-9]+)\/([\w0-9]+)'
ARITHMETIC_QUESTION_RE = 'What is ([0-9]+) (plus|minus|times) ([0-9]+)?'
WORD_QUESTION_RE = 'What are the (first|last) ([0-9]+) letters of the word \"(\w+)\"\?'
GUESS_NUMBER_RE = 'My number is (greater|less) than your guess.'

def solve_arithmetic_question(question):
    '''Solve an arithmetic type question.

    The supported opertor are 'plus', 'minus', and 'times'. We assume the
    given numbers to be positive integers. Throws an exception when no answer
    can be found.

    example: What is 1 plus 2? Answer 3

    '''

    match = re.search(ARITHMETIC_QUESTION_RE, question)

    if match:
        left_operand, operator, right_operand = match.groups()

        # We expect integers. A ValueError will be raised otherwise.
        left_operand = int(left_operand)
        right_operand = int(right_operand)

        if operator == 'plus':
            return left_operand + right_operand
        elif operator == 'minus':
            return left_operand - right_operand
        elif operator == 'times':
            return left_operand * right_operand
        else:
            raise Exception('Can’t answer the question. %s' % question)
    else:
        raise Exception('Can’t parse the question. %s' % question)

def solve_word_question(question):
    '''Solve a word type question.

    Answer with the nth first or last letter of a given word. Throws an
    exception when no answer can be found.

    example: What are the first 3 letters of the word apple?

    '''

    match = re.search(WORD_QUESTION_RE, question)

    if match:
        operator, number, word = match.groups()

        if int(number) <= len(word):
            if operator == 'first':
                return word[:int(number)]
            elif operator == 'last':
                return word[-int(number):]

        raise Exception('Can’t answer the question. %s' % question)
    else:
        raise Exception('Can’t parse the question. %s' % question)

def solve_guess_number_question(question, low=0, high=10):
    '''Solve a guess a number question. The number to guess is between [0-9]
    and we have 4 try. We use a Divide And Conquer strategy: use the middle
    value of the available range. Example:

    Let say the secret number is 6.

    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] answer 5, wrong answer, the number is greater
    [6, 7, 8, 9] answer 8, wrong answer, the number is lower
    [6, 7] answer 7, wrong answer, the number is lower
    [6] answer 6, correct answer.

    This strategy will always give us the right answer in less or exactly 4
    guesses.

    Throws an exception when no answer can be found.

    '''

    match = re.search(GUESS_NUMBER_RE, question)

    guess = int((high - low) / 2 + low)

    if match:
        relation, = match.groups()

        if relation == 'greater':
            low = guess
        elif relation == 'less':
            high = guess
        else:
            raise Exception('Can’t answer the question. %s' % question)

    guess = int((high - low) / 2 + low)

    return (guess, low, high)

def find_question_url(body):
    match = re.search(QUESTION_URL_RE, body)

    if match:
        url = match.group()
        return urljoin(BASE_URL, url)
    else:
        raise ValueError('Can’t find any URL.')

def answer_question(question_url):
    response = requests.get(question_url)

    print('----')
    print(response.text)

    if response.text.startswith('Arithmetic question'):
        answer = solve_arithmetic_question(response.text)
        answer_response = requests.post(question_url, data={'answer': answer})
        print('----> %s' % answer)
        return find_question_url(answer_response.text)
    elif response.text.startswith('Word question'):
        answer = solve_word_question(response.text)
        answer_response = requests.post(question_url, data={'answer': answer})
        print('----> %s' % answer)
        return find_question_url(answer_response.text)
    elif response.text.startswith('Guess a number question'):
        low, high = 0, 10
        hint = response.text

        for _ in range(0, 5):
            answer, low, high = solve_guess_number_question(
                hint,
                low=low,
                high=high)

            print('----> %s' % answer)
            answer_response = requests.post(question_url, data={'answer': answer})
            hint = answer_response.text

            print(answer_response.text)
            if answer_response.text.startswith('Correct!'):
                break

    return None

def solve(name):
    '''Solve the challenge.

    There are 5 questions. And 3 types of questions: arithmetic, word,
    guess the number. The questions are always in the same order: 2 arithmetic,
    2 word, and a final guess the number.

    '''

    # Initiate the challenge by calling hello with a name.
    response = requests.post(urljoin(BASE_URL, '/hello'), data={'name': name})

    try:
        # Get the URL of the first question
        question_url = find_question_url(response.text)

        for _ in range(0, 5):
            question_url = answer_question(question_url)

    except ValueError as error:
        print('I could not solve the challenge! 😭 %s' % error)

def main():
    """Main"""

    parser = argparse.ArgumentParser(
        description='Solve the This Place developer challenge'
    )

    parser.add_argument('name', help='Your name')
    args = parser.parse_args()
    solve(args.name)

if __name__ == '__main__':
    main()
