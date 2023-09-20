import cv2
import numpy as np
from time import time


def board_plot(board_config, board_state, is_display=False, save_dir=None):

    t0 = time()

    # Board config
    GRID_SIZE = board_config["GRID_SIZE"]
    SQUARE_SIZE = board_config["SQUARE_SIZE"]
    LINE_THICKNESS = board_config["LINE_THICKNESS"]

    BACKGROUND_COLOR = board_config["BACKGROUND_COLOR"]
    LINES_COLOR = board_config["LINES_COLOR"]
    SNAKE1_COLOR = board_config["SNAKE1_COLOR"]
    SNAKE2_COLOR = board_config["SNAKE2_COLOR"]
    FOOD_COLOR = board_config["FOOD_COLOR"]

    # Board state
    turn = board_state["turn"]
    snake1_body = board_state["snake1"]["body"]
    snake1_dir = board_state["snake1"]["dir"]
    snake2_body = board_state["snake2"]["body"]
    snake2_dir = board_state["snake2"]["dir"]
    food = board_state["food"]


    grid_thickness = GRID_SIZE * SQUARE_SIZE + (GRID_SIZE + 1) * LINE_THICKNESS

    # Create a white background image
    image = np.ones((grid_thickness, grid_thickness, 3), dtype=np.uint8) * BACKGROUND_COLOR
    image = image.astype(np.uint8)

    cv2.line(image, (0, 0), (0, grid_thickness), LINES_COLOR, thickness=LINE_THICKNESS)
    cv2.line(image, (0, 0), (grid_thickness, 0), LINES_COLOR, thickness=LINE_THICKNESS)

    for i in range(1, GRID_SIZE + 1):
        # vertical line
        v_start_point = (i * (SQUARE_SIZE + LINE_THICKNESS), 0)
        v_end_point = (i * (SQUARE_SIZE + LINE_THICKNESS), grid_thickness)
        cv2.line(image, v_start_point, v_end_point, LINES_COLOR, thickness=LINE_THICKNESS)

        # horizontal line
        h_start_point = (0, i * (SQUARE_SIZE + LINE_THICKNESS))
        h_end_point = (grid_thickness, i * (SQUARE_SIZE + LINE_THICKNESS))
        cv2.line(image, h_start_point, h_end_point, LINES_COLOR, thickness=LINE_THICKNESS)

    def draw_pos(target_pos, color, is_head=False, dir=None):
        square_top_left = (target_pos[0] * (SQUARE_SIZE + LINE_THICKNESS) + LINE_THICKNESS, target_pos[1] * (SQUARE_SIZE + LINE_THICKNESS) + LINE_THICKNESS)
        square_bottom_right = (square_top_left[0] + SQUARE_SIZE - LINE_THICKNESS, square_top_left[1] + SQUARE_SIZE - LINE_THICKNESS)
        cv2.rectangle(image, square_top_left, square_bottom_right, color, -1)
        
        # Draw the eyes in the head
        if is_head:
            radius = SQUARE_SIZE // 5

            if dir in ["U", "D"]:
                center1 = (square_top_left[0] + SQUARE_SIZE//4 - 1, square_top_left[1] + SQUARE_SIZE//2)
                center2 = (square_top_left[0] + 3 * SQUARE_SIZE//4, square_top_left[1] + SQUARE_SIZE//2)
                if dir == "U":
                    center1pupil = (center1[0], center1[1] - radius//2) 
                    center2pupil = (center2[0], center2[1] - radius//2)
                elif dir == "D": 
                    center1pupil = (center1[0], center1[1] + radius//2) 
                    center2pupil = (center2[0], center2[1] + radius//2)

            elif dir in ["R", "L"]:
                center1 = (square_top_left[0] + SQUARE_SIZE//2, square_top_left[1] + SQUARE_SIZE//4 - 1)
                center2 = (square_top_left[0] + SQUARE_SIZE//2, square_top_left[1] + 3 * SQUARE_SIZE//4)
                if dir == "R":
                    center1pupil = (center1[0] + radius//2, center1[1]) 
                    center2pupil = (center2[0] + radius//2, center2[1])
                elif dir == "L":
                    center1pupil = (center1[0] - radius//2, center1[1]) 
                    center2pupil = (center2[0] - radius//2, center2[1])

            cv2.circle(image, center1, radius, (200, 200, 200), -1)
            cv2.circle(image, center2, radius, (200, 200, 200), -1)
            cv2.circle(image, center1pupil, radius//2, (20, 20, 20), -1)
            cv2.circle(image, center2pupil, radius//2, (20, 20, 20), -1)

    for pos in snake1_body[1:]:
        draw_pos(pos, SNAKE1_COLOR, False, snake1_dir)
    draw_pos(snake1_body[0], SNAKE1_COLOR, True, snake1_dir)

    for pos in snake2_body[1:]:
        draw_pos(pos, SNAKE2_COLOR, False, snake2_dir)
    draw_pos(snake2_body[0], SNAKE2_COLOR, True, snake2_dir)

    for pos in food:
        draw_pos(pos, FOOD_COLOR)

    
    image = image.astype(np.uint8)

    #print("Time taken: {:.5f} seconds".format(time() - t0))
    # Display the image on your computer screen
    if is_display:
        cv2.imshow("Grid Image", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    if save_dir is not None:
        # Save the image as a PNG file
        cv2.imwrite(save_dir + f"{turn:03}_turn.png", image)

    else:
        return image



if __name__ == "__main__":

    # --- Test case ---

    # Configs
    board_config = {
        "GRID_SIZE": 15,
        "SQUARE_SIZE": 35,
        "LINE_THICKNESS": 2,

        "BACKGROUND_COLOR": (30, 20, 20),
        "LINES_COLOR": (75, 40, 40),
        "SNAKE1_COLOR": (20, 200, 20),
        "SNAKE2_COLOR": (190, 120, 0),
        "FOOD_COLOR": (20, 200, 250),

        "MAX_TURNS": 100,
    }

    # Initial state
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
        "food": [],
    }

    
    board_plot(board_config, board_state, is_display=True, save_dir="./")