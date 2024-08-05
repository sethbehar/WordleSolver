from playwright.sync_api import sync_playwright
from time import sleep

def get_words():
    with open('words.txt', 'r') as file:
        words = [line.strip() for line in file]
    return words    

def find_best_word(words, words_guessed, feedback):
    words_without_guesses = [word.lower() for word in words if word.lower() not in [w.lower() for w in words_guessed]]
    absent_letters = set()
    correct_letters = ['', '', '', '', '']
    present_letters = {}

    # Process each piece of feedback
    for arr in feedback:
        if len(arr) == 3:
            position_info, letter, status = arr
            letter = letter.lower().strip()
            status = status.lower()

            if status == 'absent':
                # Only add to absent if not listed as correct or present elsewhere
                if all(letter != correct_letters[i] for i in range(len(correct_letters))) and letter not in present_letters:
                    absent_letters.add(letter)
            elif status == 'present in another position':
                if letter not in present_letters:
                    present_letters[letter] = []
                present_letters[letter].append(int(position_info) - 1)
            elif status == 'correct':
                correct_letters[int(position_info) - 1] = letter

    # Filter potential words
    for word in words_without_guesses:
        if all((c == '' or word[i] == c) for i, c in enumerate(correct_letters)):
            if not any(char in absent_letters for char in word):
                # Ensure present letters appear in the word, but not in the "correct" spots
                if all(word.count(letter) > 0 and all(word[index] != letter for index in indices)
                       for letter, indices in present_letters.items()):
                    return word

    return None

def input_guess(page, row, guess):
    page.get_by_label(f"Row {row + 1}").get_by_label("1st letter, empty").click()
    page.keyboard.type(guess)
    page.keyboard.press("Enter")
    page.wait_for_timeout(1000)
    sleep(1)
    tile_selector = 'div.Tile-module_tile__UWEHN'
    tiles = page.locator(tile_selector)
    feedback = []

    for i in range(tiles.count()):
        tile = tiles.nth(i)
        aria_label = tile.get_attribute('aria-label')
        temp_arr = aria_label[11:].split(", ")
        if len(temp_arr) == 2:
            feedback.append([aria_label[0], temp_arr[0], temp_arr[1]])

    return feedback

def play_wordle(page, words):
    words_guessed = []
    feedback = []
    for row in range(6):
        guess = find_best_word(words, words_guessed, feedback)
        words_guessed.append(guess)
        feedback = input_guess(page, row, guess)
        sleep(2)


def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.nytimes.com/games/wordle/index.html")
    page.get_by_test_id("Play").click()
    page.get_by_label("Close").click()
    words = get_words()
    play_wordle(page, words)
    page.wait_for_timeout(50000)  
    browser.close()

with sync_playwright() as playwright:
    run(playwright)