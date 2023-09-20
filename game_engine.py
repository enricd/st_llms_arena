import streamlit as st 
from random import randint
from copy import deepcopy
import pandas as pd

from board_plot import board_plot
from agents import get_agent_action


# Look... this could be done better, using OOP and so, but I programmed this in 2-3 nights and it takes me double the
# time to program with classes and objects unless I copy the code from somewhere else. So, I'm sorry if this bothers you :).

# Configs
board_config = {
    "GRID_SIZE": 15,
    "SQUARE_SIZE": 35,
    "LINE_THICKNESS": 2,

    "BACKGROUND_COLOR": (30, 20, 20),
    "LINES_COLOR": (75, 40, 40),
    "SNAKE1_COLOR": (20, 200, 20),
    "SNAKE2_COLOR": (190, 120, 0),
    "FOOD_COLOR": (50, 50, 250),

    "MAX_TURNS": 100,
}

# Initial state
board_state_0 = {
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
    "food": [],
}


# --- Utils ---

def place_food(board_config, board_state):

    new_food_pos = (randint(0, board_config["GRID_SIZE"]-1), randint(0, board_config["GRID_SIZE"]-1))

    it = 0
    while (new_food_pos in board_state["snake1"]["body"] or new_food_pos in board_state["snake2"]["body"] or new_food_pos in board_state["food"]) and it <= 50:
        it += 1
        new_food_pos = (randint(0, board_config["GRID_SIZE"]-1), randint(0, board_config["GRID_SIZE"]-1))

    if it <= 50:
        return new_food_pos
    else:
        return None
    

def move_snake(board_state, snake):

    head = deepcopy(snake["body"][0])

    if snake["dir"] == "U":
        head = (head[0], head[1]-1)
    elif snake["dir"] == "D":
        head = (head[0], head[1]+1)
    elif snake["dir"] == "L":
        head = (head[0]-1, head[1])
    elif snake["dir"] == "R":
        head = (head[0]+1, head[1])

    snake["body"].insert(0, head)

    if head in board_state["food"]:
        board_state["food"].remove(head)
    else:
        snake["body"].pop()


DIR_TO_ARROW = {
    "U": "⬆️",
    "D": "⬇️",
    "L": "⬅️",
    "R": "➡️",
    None: "❌",
}
    

# --- Main function ---

def game_engine(board_config=board_config, 
                board_state_0=board_state_0, 
                llm1=None, 
                llm2=None, 
                prompt1=None,
                prompt2=None,
                board_imgs_space=None, 
                turn_counter=None,
                plots_space=None,
                agents_spaces=None
                ):

    board_state = deepcopy(board_state_0)

    game_history = []
    game_history.append({"board_state": deepcopy(board_state),
                         
                        "agent1_response": None,
                        "agent1_action": None,
                        "agent1_time": 0,
                        "agent1_completion_tokens": 0,
                        "agent1_cost": 0,

                        "agent2_response": None,
                        "agent2_action": None,
                        "agent2_time": 0,
                        "agent2_completion_tokens": 0,
                        "agent2_cost": 0,
                        })

    game_over = False
    turn = 0
    
    while not game_over and turn < board_config["MAX_TURNS"]:

        # Update turn
        turn += 1
        board_state["turn"] = turn

        # Place food
        if len(board_state["food"]) < 2:
            new_food_pos = place_food(board_config, board_state)
            if new_food_pos is not None:
                board_state["food"].append(new_food_pos)

        #print("board_state:", board_state)

        # Agents turn
        agent1_action, agent1_response, llm1_time, completion_tokens1, cost1 = get_agent_action(agent=1, llm=llm1, prompt=prompt1, board_config=board_config, board_state=board_state)
        agent2_action, agent2_response, llm2_time, completion_tokens2, cost2 = get_agent_action(agent=2, llm=llm2, prompt=prompt2, board_config=board_config, board_state=board_state)

        if agent1_action is not None:
            board_state["snake1"]["dir"] = agent1_action

        if agent2_action is not None:
            board_state["snake2"]["dir"] = agent2_action

        # Move snakes
        move_snake(board_state, board_state["snake1"])
        move_snake(board_state, board_state["snake2"])

        # Check if game is over
        if board_state["snake1"]["body"][0] in board_state["snake2"]["body"] or \
            board_state["snake1"]["body"][0] in board_state["snake1"]["body"][1:] or\
            board_state["snake1"]["body"][0][0] < 0 or board_state["snake1"]["body"][0][0] >= board_config["GRID_SIZE"] or\
            board_state["snake1"]["body"][0][1] < 0 or board_state["snake1"]["body"][0][1] >= board_config["GRID_SIZE"]:
            
            board_state["snake1"]["is_alive"] = False
            game_over = True
        
        if board_state["snake2"]["body"][0] in board_state["snake1"]["body"] or \
            board_state["snake2"]["body"][0] in board_state["snake2"]["body"][1:] or\
            board_state["snake2"]["body"][0][0] < 0 or board_state["snake2"]["body"][0][0] >= board_config["GRID_SIZE"] or\
            board_state["snake2"]["body"][0][1] < 0 or board_state["snake2"]["body"][0][1] >= board_config["GRID_SIZE"]:
            
            board_state["snake2"]["is_alive"] = False
            game_over = True

        # Update game history
        game_history.append({"board_state": deepcopy(board_state),
                             
                            "agent1_response": agent1_response,
                            "agent1_action": agent1_action,
                            "agent1_time": llm1_time,
                            "agent1_completion_tokens": completion_tokens1,
                            "agent1_cost": cost1,

                            "agent2_response": agent2_response,
                            "agent2_action": agent2_action,
                            "agent2_time": llm2_time,
                            "agent2_completion_tokens": completion_tokens2,
                            "agent2_cost": cost2,
                            })

        # Update latest messages in web layout
        container1 = agents_spaces[0].container()
        container2 = agents_spaces[1].container()
        
        with container1:
            st.markdown(f"<h4 style='text-align:center; background-color:green;'> Agent 1 Score: {len(board_state['snake1']['body'])} </h4>", unsafe_allow_html=True)
            st.write("")
            for i in range(min(2, len(game_history)-1)):
                st.success(f"**Turn {turn-i}:** " + game_history[-(i+1)]["agent1_response"], icon=DIR_TO_ARROW[game_history[-(i+1)]["agent1_action"]])

        with container2:
            st.markdown(f"<h4 style='text-align:center; background-color:blue;'> Agent 2 Score: {len(board_state['snake2']['body'])} </h4>", unsafe_allow_html=True)
            st.write("")
            for i in range(min(2, len(game_history)-1)):
                st.info(f"**Turn {turn-i}:** " + game_history[-(i+1)]["agent2_response"], icon=DIR_TO_ARROW[game_history[-(i+1)]["agent2_action"]])

        # Update board
        img_arr = board_plot(board_config, board_state, is_display=False, save_dir=None)

        # BGR to RGB and update new img in web layout
        turn_counter.markdown(f"<h3 style='text-align:center'> Turn {turn} </h3>", unsafe_allow_html=True)
        board_imgs_space.image(img_arr[:, :, (2, 1, 0)], use_column_width=True)

        # Update plots
        plots_container = plots_space.container()
        df = pd.DataFrame(game_history)

        with plots_container:
            st.write("")
            cols_plots = st.columns(3)
            with cols_plots[0]:
                st.write("##### Completion tokens")
                st.line_chart(df[["agent1_completion_tokens", "agent2_completion_tokens"]], color=["#12c914", "#0074ba"])
                st.info(f"Total completion tokens Agent 1: {df['agent1_completion_tokens'].sum()}")
                st.info(f"Total completion tokens Agent 2: {df['agent2_completion_tokens'].sum()}")
            with cols_plots[1]:
                st.write("##### Cost of input + completion tokens ($)")
                st.line_chart(df[["agent1_cost", "agent2_cost"]], color=["#12c914", "#0074ba"])
                st.info(f"Total cost Agent 1: {df['agent1_cost'].sum():.4f} $") 
                st.info(f"Total cost Agent 2: {df['agent2_cost'].sum():.4f} $")
            with cols_plots[2]:
                st.write("##### Response Time (s)")
                st.line_chart(df[["agent1_time", "agent2_time"]], color=["#12c914", "#0074ba"])
                st.info(f"Total time Agent 1: {df['agent1_time'].sum():.3f} s")
                st.info(f"Total time Agent 2: {df['agent2_time'].sum():.3f} s")


    # --- Winning rules ---

    winner = None
    if board_state["snake1"]["is_alive"] and not board_state["snake2"]["is_alive"]:
        winner = "Agent 1"
    elif board_state["snake2"]["is_alive"] and not board_state["snake1"]["is_alive"]:
        winner = "Agent 2"
    elif not board_state["snake1"]["is_alive"] and not board_state["snake2"]["is_alive"]:
        winner = "Draw"
    elif len(board_state["snake1"]["body"]) > len(board_state["snake2"]["body"]):
        winner = "Agent 1"
    elif len(board_state["snake2"]["body"]) > len(board_state["snake1"]["body"]):
        winner = "Agent 2"
    else:
        winner = "Draw"

    turn_counter.markdown(f"<h3 style='text-align:center'> Turn {turn} - WINNER: {winner} </h3>", unsafe_allow_html=True)
    
    st.toast(f"Game over! \nWinner: {winner}", icon="🟰" if winner=="Draw" else "🎉")
    if winner != "Draw":
        st.balloons()


if __name__ == "__main__":

    randint()