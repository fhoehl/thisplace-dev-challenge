import pytest

from challenge import solve_arithmetic_question
from challenge import solve_word_question
from challenge import solve_guess_number_question

@pytest.mark.parametrize('question, answer', [
    ('What is 5 minus 5?', 0),
    ('What is 5 plus 5?', 10),
    ('What is 5 times 2?', 10),
])
def test_solve_arithmetic_question(question, answer):
    assert solve_arithmetic_question(question) == answer


@pytest.mark.parametrize('question, answer', [
    ('What are the first 3 letters of the word "apple"?', 'app'),
    ('What are the last 3 letters of the word "apple"?', 'ple'),
    ('What are the last 4 letters of the word "tree"?', 'tree'),
    ('What are the first 4 letters of the word "tree"?', 'tree'),
])
def test_solve_word_question(question, answer):
    assert solve_word_question(question) == answer


@pytest.mark.parametrize('question, answer', [
    ('What are the first 5 letters of the word "tree"?', 'tree'),
])
def test_solve_word_question(question, answer):
    with pytest.raises(Exception):
        solve_word_question(question)


@pytest.mark.parametrize('secret', range(0, 10))
def test_solve_guess_number_question(secret):
    question = 'Quess the number'
    low, high = 0, 10
    print('secret', secret)

    for _ in range(0, 5):  # We have 4 try
        guess, low, high = solve_guess_number_question(
            question,
            low=low, high=high)

        if guess == secret:
            print('match', guess, secret)
            return
        elif guess > secret:
            question = 'My number is less than your guess.'
        else:
            question = 'My number is greater than your guess.'

    assert False
