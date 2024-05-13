from time import sleep, time
import logging
from random import randint
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.callbacks import get_openai_callback


logging.basicConfig(level=logging.INFO)


# Available models list to be used in the app
AVAILABLE_MODELS = [
    "openai gpt-4o-2024-05-13 (GPT-4o)",
    "openai gpt-4-1106-preview (GPT-4 Turbo)",
    "openai gpt-3.5-turbo",
    "openai gpt-4",
]


# Default prompts for the initial layout 
DEFAULT_PROMPT1 = [
"""You are an expert gamer agent playing the 1vs1 snake game in a grid board. You can move up, down, left or right. 
You can eat food to grow. If you hit a wall or another snake, you die. The game ends when one of the snakes dies. You are compiting against another snake.""",

"""You are the snake1, which is the color green. Your opponent is the snake2 with color blue. This is the game board in emojis where heads are rounds, bodies are squares and food is an apple: 
{emojis_board}

and this is the board state in JSON, positions are in (x, y) format, the game board size is 15 by 15, x goes from 0 to 14 left to right and y goes 0 to 14 up to down: 
{board_state_str}

The snake dir parameter is the first letter of the previous chosen direction of the snake, if you chose an opposite direction you will die as you will collide with your own body.
You have to shortly reason your next move in 1-3 lines and then always add one of the following emojis: ⬆️, ⬇️, ⬅️, ➡️ (for <up>, <down>, <left> and <right>) to chose the direction of your next move.
Make sure to always add a space after the emoji and only use one emoji in your response which will be your final decision for the turn.""",
]

DEFAULT_PROMPT2 = [
"""You are an expert gamer agent playing the 1vs1 snake game in a grid board. You can move up, down, left or right. 
You can eat food to grow. If you hit a wall or another snake, you die. The game ends when one of the snakes dies. You are compiting against another snake.""",

"""You are the snake2, which is the color blue. Your opponent is the snake1 with color green. This is the game board in characters where heads are 'G' (green) and 'B' (blue), bodies are 'g' and 'b' and food is 'R'. Empty cells are marked with '_'. 
Every line starts also with its number which is at the same time the y coordinate for that line: 
Characters board:
{chars_board}

and this is the board state in JSON, positions are in (x, y) format, the game board size is 15 by 15, x goes from 0 to 14 left to right and y goes 0 to 14 up to down: 
{board_state_str}

The snake dir parameter is the first letter of the previous chosen direction of the snake, if you chose an opposite direction you will die as you will collide with your own body.
You have to shortly reason your next move in 1-3 lines and then always add one of the following emojis: ⬆️, ⬇️, ⬅️, ➡️ (for <up>, <down>, <left> and <right>) to chose the direction of your next move.
Make sure to always add a space after the emoji and only use one emoji in your response which will be your final decision for the turn.

Makt the following Chain of Thought in few words:
1. Locate yourself and your head in the chars map (the <B> char) and the (x, y) coordinates from the board state (the element 0 of the body list in snake2, the body parts are ordered from head to tail)
2. Locate the closest food
3. Chose the direction to move on cell closer to the food, check if you will die/lose there and if so chose another direction
4. Finally output the emoji for the direction you chose""",
]


def board_to_char(board_config, board_state, chars_type="emojis"):
    """
    Receives the board configuration, board state and the type of output (emojis or characters).
    Returns a string with the board in characters or emojis, depending on the chars_type parameter.
    """

    if chars_type == "emojis":
        CELL = "⬜"
        SNAKE1_HEAD = "🟢"
        SNAKE1 = "🟩"
        SNAKE2_HEAD = "🔵"
        SNAKE2 = "🟦"
        FOOD = "🍎"

    elif chars_type == "_GBR":
        CELL = " _"
        SNAKE1_HEAD = " G"
        SNAKE1 = " g"
        SNAKE2_HEAD = " B"
        SNAKE2 = " b"
        FOOD = " R"

    # Creating the board in characters
    chars_board_list = []

    for y in range(board_config["GRID_SIZE"]):
        line = []
        for x in range(board_config["GRID_SIZE"]):

            # Agent 1 (green snake)
            if (x, y) in board_state["snake1"]["body"]:
                if (x, y) == board_state["snake1"]["body"][0]:
                    line.append(SNAKE1_HEAD)
                else:
                    line.append(SNAKE1)

            # Agent 2 (blue snake)
            elif (x, y) in board_state["snake2"]["body"]:
                if (x, y) == board_state["snake2"]["body"][0]:
                    line.append(SNAKE2_HEAD)
                else:
                    line.append(SNAKE2)

            # Food
            elif (x, y) in board_state["food"]:
                line.append(FOOD)

            # Empty cell
            else:
                line.append(CELL)

        chars_board_list.append(line)

    # Transforming the board to a string with the line number at the beginning of each line
    chars_board = "\n".join([f"{i:02}" + "".join(line) for i, line in enumerate(chars_board_list)])

    return chars_board


def get_agent_action(agent, llm, prompt, board_config, board_state, is_test=False):
    """
    Receives the agent int number, the LLM langchain chat model, the prompt list with 2 strings (sys_msg, human_msg), the board configuration dictionary, the board state dictionary and a boolean to indicate if it is a test case.
    Returns the action of the agent (direction to move), the raw response message from the LLM, the time it took to get the response, the tokens used and the cost of the API call.
    """

    if not is_test:

        # Creating the prompt template from the user defined agent's prompts
        template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(prompt["sys_msg"]),
                HumanMessagePromptTemplate.from_template(prompt["human_msg"]),
            ]
        )

        # Creating the board state in the emojis_board and chars_board formats to have them ready for the prompt if the template uses them
        emojis_board = board_to_char(board_config, board_state)
        chars_board = board_to_char(board_config, board_state, chars_type="_GBR")
        board_state_str = str(board_state)

        messages = template.format_messages(emojis_board=emojis_board, chars_board=chars_board, board_state_str=board_state_str)

        logging.info(f"Agent {agent} \nMessages: {messages}")

        # OpenAI API call with the callback to get the response message but also the cost and tokens used in the callback
        t0 = time()
        with get_openai_callback() as cb:
            agent_response = llm(messages).content
        llm_time = time() - t0

        # Getting the direction from the LLM response and the arrow emoji in it
        if "⬆️" in agent_response:
            dir = "U"
        elif "⬇️" in agent_response:
            dir = "D"
        elif "⬅️" in agent_response:
            dir = "L"
        elif "➡️" in agent_response:
            dir = "R"
        else: 
            dir = None
        
        return (dir, agent_response, llm_time, cb.completion_tokens, cb.total_cost)

    # Test case without calling the LLM API, it will randomly return a direction
    else:
        
        sleep(0.5)
        if agent == 1:
            dir = "D" if randint(0, 1) == 0 else "R"
        
        elif agent == 2:
            dir = "U" if randint(0, 1) == 0 else "L"

        return (dir, "Test", 0.5, 0, 0)
        


if __name__ == "__main__":

    # --- Test case ---

    board_config = {
        "GRID_SIZE": 15,
        "SQUARE_SIZE": 35,
        "LINE_THICKNESS": 2,

        "BACKGROUND_COLOR": (30, 20, 20),
        "LINES_COLOR": (75, 40, 40),
        "SNAKE1_COLOR": (20, 200, 20),
        "SNAKE2_COLOR": (209, 31, 177),
        "FOOD_COLOR": (20, 200, 250)
    }

    board_state = {
        "turn": 0,
        "snake1": {
            "body": [(5, 2), (4, 2), (3, 2), (2, 2)],
            "dir": "R",
            "is_alive": True,
        },
        "snake2": {
            "body": [(9, 12), (10, 12), (11, 12), (12, 12)],
            "dir": "L",
            "is_alive": True,
        },
        "food": [(7, 7), (8, 1)],
    }

    print(board_to_char(board_config, board_state))
    print("")
    print(board_to_char(board_config, board_state, chars_type="_GBR"))