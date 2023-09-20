import streamlit as st
import os
from langchain.chat_models import ChatOpenAI
import tiktoken

from game_engine import game_engine, board_state_0
from utils import contributor_card, enric_info


# --- Configs ---

AVAILABLE_MODELS = [
        "openai gpt-3.5-turbo",
        "openai gpt-4",
    ]

DEFAULT_PROMPT1 = [
    """You are an expert gamer agent playing the 1vs1 snake game in a grid board. You can move up, down, left or right. 
You can eat food to grow. If you hit a wall or another snake, you die. The game ends when one of the snakes dies. You are compiting against another snake.""",
"""You are the snake1 which is the color green. Your opponent is the snake2 with color blue. This is the game board in emojis where heads are rounds, bodies are squares and food is an apple: 
{emojis_board}
and this is the board state in JSON, positions are (x, y), the game board size is 15 by 15, x goes from 0 to 14 left to right and y goes 0 to 14 up to down: {board_state_str}
The snake dir parameter is the first letter of the previous chosen direction of the snake, if you chose an opposite direction you will die as you will collide with your own body.
You have to shortly reason your next move in 1-3 lines and then always add one of the follwoing emojis: ⬆️ ⬇️ ⬅️ ➡️ to chose the direction of your next move.
Make sure to always add a space after the emoji and only use one emoji in your response which will be your final decision for the turn.""",
]

DEFAULT_PROMPT2 = [
    """You are an expert gamer agent playing the 1vs1 snake game in a grid board. You can move up, down, left or right. 
You can eat food to grow. If you hit a wall or another snake, you die. The game ends when one of the snakes dies. You are compiting against another snake.""",
"""You are the snake2 which is the color blue. Your opponent is the snake1 with color green. This is the game board in emojis where heads are rounds, bodies are squares and food is an apple: 
{emojis_board}
and this is the board state in JSON, positions are (x, y), the game board size is 15 by 15, x goes from 0 to 14 left to right and y goes 0 to 14 up to down: {board_state_str}
The snake dir parameter is the first letter of the previous chosen direction of the snake, if you chose an opposite direction you will die as you will collide with your own body.
You have to shortly reason your next move in 1-3 lines and then always add one of the follwoing emojis: ⬆️ ⬇️ ⬅️ ➡️ to chose the direction of your next move.
Make sure to always add a space after the emoji and only use one emoji in your response which will be your final decision for the turn.""",
]


def main():

    st.set_page_config(
        page_title="LLMs Arena", 
        page_icon="🕹️", 
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "About": """This is an app for the Streamlit LLMs Hackathon from Sep 23 developed by Enric Domingo.
                        Code: https://github.com/enricd/"""
        }
        )
    

    # --- Title ---

    st.markdown("<h1 style='text-align: center;'><span style='background-color: #12c914'>🤖🕹️</span> <em>The LLMs Arena</em> <span style='background-color: #0074ba'>🎮🤖</span></h1>", unsafe_allow_html=True)

    st.divider()


    # --- Sidebar ---

    with st.sidebar:

        # TODO: add st.expander with instructions

        openai_api_key = "" #os.getenv("OPENAI_API_KEY") if os.getenv("OPENAI_API_KEY") is not None else ""  # only for development environment, otherwise it should return None
        user_api_key = st.text_input("Introduce your OpenAI API Key (https://platform.openai.com/)", value=openai_api_key, type="password")
        if user_api_key != "":
            openai_api_key = user_api_key

        llm1_temp = st.slider("LLM-1 temperature", min_value=0.0, max_value=1.0, value=0.5, step=0.05)
        llm2_temp = st.slider("LLM-2 temperature", min_value=0.0, max_value=1.0, value=0.5, step=0.05)

        st.divider()

        st.write("### 👨‍💻 Developed by:")
        st.markdown(contributor_card(
            **enric_info,
            ), 
            unsafe_allow_html=True)


    # --- User inputs ---

    with st.expander("### Instructions:"):
        st.write("- The following variables are available for the prompt: `{emojis_board}`, `{board_state_str}`")
        st.write("- Example `{emojis_board}`:")
        st.text("""
        00⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
        01⬜⬜⬜⬜⬜⬜⬜⬜🍎⬜⬜⬜⬜⬜⬜
        02⬜⬜🟩🟩🟩🟢⬜⬜⬜⬜⬜⬜⬜⬜⬜
        03⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
        04⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
        05⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
        06⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
        07⬜⬜⬜⬜⬜⬜⬜🍎⬜⬜⬜⬜⬜⬜⬜
        08⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
        09⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
        10⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
        11⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
        12⬜⬜⬜⬜⬜⬜⬜⬜⬜🔵🟦🟦🟦⬜⬜
        13⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
        14⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜""")
        st.write("- Example `{board_state_str}`: ")
        st.write(str(board_state_0))
        st.write("- There is a couple of default prompt examples that you can modify.")
        st.write("- The agent has always to output one of the following emojis: ⬆️ ⬇️ ⬅️ ➡️ to chose the direction of the next move.")
        st.write("- The agent can make a few lines (recommended 1-3) of reasoning before deciding the next move with an arrow emoji. ")
        st.write("- The game ends when one of the snakes dies by hitting a wall or another snake or after 100 turns.")
        st.write("- The game is played in a 15x15 grid board. x is the horizontal axis and goes from 0 to 14 left to right. y is the vertical axis and goes from 0 to 14 up to down.")


    if openai_api_key == "" or openai_api_key is None or "sk-" not in openai_api_key:
        st.write("#")
        st.warning("⬅️ Please introduce your OpenAI API Key to continue...")

    else:
        cols0 = st.columns([3, 1, 3])

        with cols0[0]:
            model1 = st.selectbox("Select the LLM-1", options=AVAILABLE_MODELS, index=0)
            encoding1 = tiktoken.encoding_for_model(model1.split(" ")[1])
            llm1 = ChatOpenAI(temperature=llm1_temp, openai_api_key=openai_api_key, model_name=model1.split(" ")[1])

            with st.expander("Prompt for the Agent-1"):
                prompt1 = {
                    "sys_msg": st.text_area("System Message (opt.)", value=DEFAULT_PROMPT1[0], height=120, key="prompt1_sys_msg"),
                    "human_msg": st.text_area("Human Message", value=DEFAULT_PROMPT1[1], height=120, key="prompt1_human_msg"),
                }

                st.write(f"Input tokens: `{len(encoding1.encode(prompt1['human_msg'] + prompt1['sys_msg']))}` + variables tokens (800 aprox.)")


        with cols0[1]:
            st.markdown("<h1 style='text-align:center'> - vs - </h1>", unsafe_allow_html=True)

        with cols0[2]:
            model2 = st.selectbox("Select the LLM-2", options=AVAILABLE_MODELS, index=0)
            encoding2 = tiktoken.encoding_for_model(model2.split(" ")[1])
            llm2 = ChatOpenAI(temperature=llm2_temp, openai_api_key=openai_api_key, model_name=model2.split(" ")[1])

            with st.expander("Prompt for the Agent-2"):
                prompt2 = {
                    "sys_msg": st.text_area("System Message (opt.)", value=DEFAULT_PROMPT2[0], height=120, key="prompt2_sys_msg"),
                    "human_msg": st.text_area("Human Message", value=DEFAULT_PROMPT2[1], height=120, key="prompt2_human_msg"),
                }

                st.write(f"Input tokens: `{len(encoding2.encode(prompt2['human_msg'] + prompt2['sys_msg']))}` + variables tokens (800 aprox.)")


    # --- Game display ---

    st.write("##")

    cols1 = st.columns([5, 2, 2, 5])

    with cols1[1]:
        if openai_api_key == "" or openai_api_key is None or "sk-" not in openai_api_key:
            is_start = False
            st.write("#")

        else:
            is_start = st.button("▶️ Play!", type="primary", use_container_width=True)
            if is_start:
                with cols1[2]:
                    is_stop = st.button("⏹️ Stop", type="secondary", use_container_width=True)
                    if is_stop:
                        is_start = False

    cols2 = st.columns([4, 1, 4, 1, 4])

    with cols2[0]:
        agent1_space = st.empty()

    with cols2[2]:
        turn_counter = st.markdown("<h3 style='text-align:center'> Turn 0 </h3>", unsafe_allow_html=True)
        board_imgs_space = st.image("./000_turn.png", use_column_width=True)

    with cols2[4]:
        agent2_space = st.empty()

    plots_space = st.empty()

    if is_start:
        game_engine(llm1=llm1, 
                    llm2=llm2, 
                    prompt1=prompt1,
                    prompt2=prompt2,
                    board_imgs_space=board_imgs_space, 
                    turn_counter=turn_counter,
                    plots_space=plots_space,
                    agents_spaces=[agent1_space, agent2_space]
                    )



if __name__ == "__main__":

    main()