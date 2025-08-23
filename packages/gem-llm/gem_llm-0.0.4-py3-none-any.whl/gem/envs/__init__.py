# Copyright 2025 AxonRL Team. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import reasoning_gym as rg

from gem.envs.registration import register

# Register games from our implementation of TextArena and beyond.
# GuessTheNumber
register(
    "game:GuessTheNumber-v0",
    "gem.envs.game_env.guess_the_number:GuessTheNumberEnv",
    min_number=1,
    max_number=20,
    max_turns=10,
)
register(
    "game:GuessTheNumber-v0-hard-no-max-turn",
    "gem.envs.game_env.guess_the_number:GuessTheNumberEnv",
    min_number=1,
    max_number=50,
    max_turns=50,
)
register(
    "game:GuessTheNumber-v0-hard",
    "gem.envs.game_env.guess_the_number:GuessTheNumberEnv",
    min_number=1,
    max_number=50,
    max_turns=7,
)
register(
    "game:GuessTheNumber-v0-easy",
    "gem.envs.game_env.guess_the_number:GuessTheNumberEnv",
    min_number=1,
    max_number=10,
    max_turns=4,
)
register(
    "game:GuessTheNumber-v0-random",
    "gem.envs.game_env.guess_the_number:GuessTheNumberEnv",
    min_number=None,
    max_number=None,
    max_turns=None,
)
# Mastermind
register(
    "game:Mastermind-v0",
    "gem.envs.game_env.mastermind:MastermindEnv",
    code_length=4,
    num_numbers=6,
    max_turns=20,
    duplicate_numbers=False,
)
register(
    "game:Mastermind-v0-hard",
    "gem.envs.game_env.mastermind:MastermindEnv",
    code_length=4,
    num_numbers=8,
    max_turns=30,
    duplicate_numbers=False,
)
register(
    "game:Mastermind-v0-random",
    "gem.envs.game_env.mastermind:MastermindEnv",
    code_length=None,
    num_numbers=None,
    max_turns=50,
    duplicate_numbers=False,
)
register(
    "game:Mastermind-v0-easy",
    "gem.envs.game_env.mastermind:MastermindEnv",
    code_length=2,
    num_numbers=6,
    max_turns=6,
    duplicate_numbers=False,
)
# Minesweeper
register(
    "game:Minesweeper-v0",
    "gem.envs.game_env.minesweeper:MinesweeperEnv",
    rows=8,
    cols=8,
    num_mines=10,
    max_turns=100,
)
register(
    "game:Minesweeper-v0-very-easy",
    "gem.envs.game_env.minesweeper:MinesweeperEnv",
    rows=3,
    cols=3,
    num_mines=1,
    max_turns=10,
)
register(
    "game:Minesweeper-v0-easy",
    "gem.envs.game_env.minesweeper:MinesweeperEnv",
    rows=5,
    cols=5,
    num_mines=3,
    max_turns=10,
)
register(
    "game:Minesweeper-v0-hard",
    "gem.envs.game_env.minesweeper:MinesweeperEnv",
    rows=12,
    cols=12,
    num_mines=30,
    max_turns=100,
)
register(
    "game:Minesweeper-v0-random",
    "gem.envs.game_env.minesweeper:MinesweeperEnv",
    rows=None,
    cols=None,
    num_mines=None,
    max_turns=None,
)
# Wordle
register(
    "game:Wordle-v0",
    "gem.envs.game_env.wordle:WordleEnv",
    word_length=5,
    only_real_words=True,
    max_turns=15,
)
register(
    "game:Wordle-v0-easy",
    "gem.envs.game_env.wordle:WordleEnv",
    word_length=3,
    only_real_words=True,
    max_turns=15,
)
register(
    "game:FifteenPuzzle-v0",
    "gem.envs.game_env.fifteen_puzzle:FifteenPuzzleEnv",
    num_rows=3,
    max_turns=20,
)
register(
    "game:FifteenPuzzle-v0-easy",
    "gem.envs.game_env.fifteen_puzzle:FifteenPuzzleEnv",
    num_rows=2,
    max_turns=10,
)
register(
    "game:FifteenPuzzle-v0-hard",
    "gem.envs.game_env.fifteen_puzzle:FifteenPuzzleEnv",
    num_rows=4,
    max_turns=50,
)

register(
    "game:Hangman-v0",
    "gem.envs.game_env.hangman:HangmanEnv",
    word_length=5,
    hardcore=False,
    max_turns=15,
)
register(
    "game:Hangman-v0-easy",
    "gem.envs.game_env.hangman:HangmanEnv",
    word_length=3,
    hardcore=False,
    max_turns=15,
)
register(
    "game:Hangman-v0-hard",
    "gem.envs.game_env.hangman:HangmanEnv",
    word_length=7,
    hardcore=False,
    max_turns=20,
)
register(
    "game:Sudoku-v0-easy",
    "gem.envs.game_env.sudoku:SudokuEnv",
    clues=10,
    max_turns=15,
    scale=4,
)
register(
    "game:Sudoku-v0-easy-v2",
    "gem.envs.game_env.sudoku:SudokuEnv",
    clues=10,
    max_turns=15,
    scale=4,
    invalid_action_reward_type="v2",
)
register(
    "game:Sudoku-v0",
    "gem.envs.game_env.sudoku:SudokuEnv",
    clues=50,
    max_turns=50,
    scale=9,
)
register(
    "game:TowerofHanoi-v0-easy",
    "gem.envs.game_env.tower_of_hanoi:TowerofHanoiEnv",
    num_disks=3,
    max_turns=10,
)
register(
    "game:TowerofHanoi-v0",
    "gem.envs.game_env.tower_of_hanoi:TowerofHanoiEnv",
    num_disks=4,
    max_turns=20,
)
register(
    "game:TowerofHanoi-v0-hard",
    "gem.envs.game_env.tower_of_hanoi:TowerofHanoiEnv",
    num_disks=5,
    max_turns=50,
)

# Register math dataset environments

register(
    "math:ASDiv2K",
    "gem.envs.math_env:MathEnv",
    dataset_name="axon-rl/ASDIV-2k",
    question_key="problem",
    answer_key="answer",
)

register(
    "math:GSM8K",
    "gem.envs.math_env:MathEnv",
    dataset_name="axon-rl/GSM-8k",
    question_key="problem",
    answer_key="answer",
)

register(
    "math:Math12K",
    "gem.envs.math_env:MathEnv",
    dataset_name="axon-rl/MATH-12k",
    question_key="problem",
    answer_key="answer",
)

register(
    "math:Math8K-3to5",
    "gem.envs.math_env:MathEnv",
    dataset_name="axon-rl/MATH-lvl3to5-8k",
    question_key="problem",
    answer_key="answer",
)

register(
    "math:Orz57K",
    "gem.envs.math_env:MathEnv",
    dataset_name="axon-rl/ORZ-57k",
    question_key="problem",
    answer_key="answer",
)

register(
    "math:DeepScaleR40K",
    "gem.envs.math_env:MathEnv",
    dataset_name="axon-rl/DeepScaleR-40K",
    question_key="problem",
    answer_key="answer",
)


# Register code dataset environments

register(
    "code:CodeContest",
    "gem.envs.code_env:CodeEnv",
    dataset_name="axon-rl/CodeContest",
    split="train",
    question_key="problem",
    test_key="tests",
)

register(
    "code:Taco8k",
    "gem.envs.code_env:CodeEnv",
    dataset_name="axon-rl/TACO-8k",
    split="train",
    question_key="problem",
    test_key="tests",
)

register(
    "code:PrimeIntellect15k",
    "gem.envs.code_env:CodeEnv",
    dataset_name="axon-rl/PrimeIntellect-15k",
    split="train",
    question_key="problem",
    test_key="tests",
)

# Register qa dataset environments

for i in [0, 1, 2, 3, 5]:
    register(
        f"logic:RuleTaker-d{i}",
        "gem.envs.qa_env:QaEnv",
        dataset_name=f"axon-rl/RuleTaker-d{i}-70k",
        split="train",
        extract_boxed=True,
        question_key="question",
        answer_key="answer",
    )

register(
    "qa:NaturalQuestions",
    "gem.envs.qa_env:QaEnv",
    dataset_name="axon-rl/NaturalQuestions",
    split="train",
    question_key="problem",
    answer_key="answer",
)

register(
    "qa:HotpotQA",
    "gem.envs.qa_env:QaEnv",
    dataset_name="axon-rl/HotpotQA",
    split="train",
    question_key="problem",
    answer_key="answer",
)

# Register datasets from ReasoningGym

for name in rg.factory.DATASETS.keys():
    register(
        f"rg:{name}",
        "gem.envs.reasoning_gym:ReasoningGymEnv",
        name=name,
        size=500,
        seed=42,
    )

# Register evaluation datasets

## MATH500
register(
    "eval:MATH500",
    "gem.envs.math_env:MathEnv",
    dataset_name="axon-rl/math-eval",
    split="math",
    question_key="problem",
    answer_key="answer",
)

## AMC
register(
    "eval:AMC",
    "gem.envs.math_env:MathEnv",
    dataset_name="axon-rl/math-eval",
    split="amc",
    question_key="problem",
    answer_key="answer",
)

## OlympiadBench
register(
    "eval:OlympiadBench",
    "gem.envs.math_env:MathEnv",
    dataset_name="axon-rl/math-eval",
    split="olympiad_bench",
    question_key="problem",
    answer_key="answer",
)

## Minerva
register(
    "eval:Minerva",
    "gem.envs.math_env:MathEnv",
    dataset_name="axon-rl/math-eval",
    split="minerva",
    question_key="problem",
    answer_key="answer",
)

## AIME24
register(
    "eval:AIME24",
    "gem.envs.math_env:MathEnv",
    dataset_name="axon-rl/math-eval",
    split="aime24",
    question_key="problem",
    answer_key="answer",
)

## The test split of deepmind/code_contests, with merged test cases.
register(
    "eval:CodeContest",
    "gem.envs.code_env:CodeEnv",
    dataset_name="axon-rl/CodeContest",
    split="test",
    question_key="problem",
    test_key="tests",
)

## QaOpen
register(
    "eval:QaOpen",
    "gem.envs.qa_env:QaEnv",
    dataset_name="google-research-datasets/nq_open",
    split="validation",
    question_key="question",
    answer_key="answer",
)

## The test split used in DeepResearcher, 512 questions per data_source
#   data_source: 2wiki, popqa, tq, hotpotqa, Bamboogle, nq, musique
data_names = [
    ("2wiki", "2Wiki"),
    ("popqa", "PopQA"),
    ("tq", "TriviaQA"),
    ("hotpotqa", "HotpotQA"),
    ("bamboogle", "Bamboogle"),
    ("nq", "NaturalQuestions"),
    ("musique", "Musique"),
]
for name, env_name in data_names:
    register(
        f"eval:{env_name}",
        "gem.envs.qa_env:QaEnv",
        dataset_name=f"axon-rl/search-eval",
        split=name,
        question_key="question",
        answer_key="answer",
    )
