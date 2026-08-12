import random
import tkinter as tk

from agent import SearchAgent

# ============================================================
# ENVIRONMENT
# ============================================================

class VisualGridHuntGame:
    """
    Grid environment for IT3012 Intelligent Agents Lab 02.

    The environment provides percepts to the agent and
    executes the action selected by the agent.
    """

    def __init__(
        self,
        width=10,
        height=10,
        num_food=10,
        num_opponents=0,
        custom_walls=None
    ):

        self.width = width
        self.height = height

        # Agent starts at bottom-left
        self.agent_pos = [0, 0]

        # Walls
        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7)
            }

        # ----------------------------------------------------
        # Food
        # ----------------------------------------------------

        self.food_positions = set()

        while len(self.food_positions) < num_food:

            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)

            position = (fx, fy)

            if (
                position != (0, 0)
                and position not in self.walls
            ):
                self.food_positions.add(position)

        # ----------------------------------------------------
        # Toxic traps
        # ----------------------------------------------------

        self.toxic_traps = set()

        num_traps = 3

        while len(self.toxic_traps) < num_traps:

            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)

            trap = (tx, ty)

            if (
                trap != (0, 0)
                and trap not in self.walls
                and trap not in self.food_positions
            ):
                self.toxic_traps.add(trap)

        # ----------------------------------------------------
        # Opponents
        # ----------------------------------------------------

        self.opponents = []

        while len(self.opponents) < num_opponents:

            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)

            opponent = [ox, oy]

            if (
                tuple(opponent) != (0, 0)
                and tuple(opponent) not in self.walls
                and tuple(opponent) not in self.food_positions
                and tuple(opponent) not in self.toxic_traps
            ):
                self.opponents.append(opponent)

        # ----------------------------------------------------
        # Game information
        # ----------------------------------------------------

        self.score = 0
        self.steps = 0
        self.collision = False

    # ========================================================
    # PERCEPTS
    # ========================================================

    def get_percept(self):
        """
        Return information available to the agent.

        The agent can sense:
        - Walls in four directions
        - Food at current location
        - Toxic trap at current location
        """

        x, y = self.agent_pos

        return {

            "wall_up": (
                y >= self.height - 1
                or (x, y + 1) in self.walls
            ),

            "wall_down": (
                y <= 0
                or (x, y - 1) in self.walls
            ),

            "wall_left": (
                x <= 0
                or (x - 1, y) in self.walls
            ),

            "wall_right": (
                x >= self.width - 1
                or (x + 1, y) in self.walls
            ),

            "food_here": (
                tuple(self.agent_pos)
                in self.food_positions
            ),

            "smells_toxin": (
                tuple(self.agent_pos)
                in self.toxic_traps
            ),
            "agent_pos": tuple(
                self.agent_pos
            ),

            "grid_size": (
                self.width, self.height
            ),

            "walls": list(
                self.walls
            ),
            
            "all_food": list(
                self.food_positions)
        }

    # ========================================================
    # EXECUTE ACTION
    # ========================================================

    def execute_action(self, action):

        self.steps += 1

        new_pos = list(self.agent_pos)

        # ----------------------------------------------------
        # Move
        # ----------------------------------------------------

        if action == "Up":
            new_pos[1] += 1

        elif action == "Down":
            new_pos[1] -= 1

        elif action == "Left":
            new_pos[0] -= 1

        elif action == "Right":
            new_pos[0] += 1

        # ----------------------------------------------------
        # Check boundary
        # ----------------------------------------------------

        if (
            new_pos[0] < 0
            or new_pos[0] >= self.width
            or new_pos[1] < 0
            or new_pos[1] >= self.height
        ):

            self.score -= 5

        # ----------------------------------------------------
        # Check wall
        # ----------------------------------------------------

        elif tuple(new_pos) in self.walls:

            self.score -= 5

        # ----------------------------------------------------
        # Valid movement
        # ----------------------------------------------------

        else:

            self.agent_pos = new_pos

        # Current position
        current_pos = tuple(self.agent_pos)

        # ----------------------------------------------------
        # Food
        # ----------------------------------------------------

        if current_pos in self.food_positions:

            self.food_positions.remove(current_pos)

            self.score += 20

        # ----------------------------------------------------
        # Toxic trap
        # ----------------------------------------------------

        if current_pos in self.toxic_traps:

            self.score -= 15

        # ----------------------------------------------------
        # Opponents
        # ----------------------------------------------------

        for opponent in self.opponents:

            move = random.choice(
                ["Up", "Down", "Left", "Right", "Stay"]
            )

            if (
                move == "Up"
                and opponent[1] < self.height - 1
            ):
                opponent[1] += 1

            elif (
                move == "Down"
                and opponent[1] > 0
            ):
                opponent[1] -= 1

            elif (
                move == "Left"
                and opponent[0] > 0
            ):
                opponent[0] -= 1

            elif (
                move == "Right"
                and opponent[0] < self.width - 1
            ):
                opponent[0] += 1

            # Collision
            if opponent == self.agent_pos:

                self.score -= 50

                self.collision = True

    # ========================================================
    # TERMINATION
    # ========================================================

    def is_done(self):

        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )


# ============================================================
# SIMPLE REFLEX AGENT
# ============================================================

class SimpleReflexAgent:
    """
    Simple Reflex Agent.

    Uses only the current percept.
    It does NOT remember previous states.
    """

    def sense_and_act(self, percept):

        # Rule 1:
        # IF toxin is detected
        # THEN move Down
        if percept["smells_toxin"]:

            if not percept["wall_down"]:
                return "Down"

            if not percept["wall_right"]:
                return "Right"

            if not percept["wall_left"]:
                return "Left"

            return "Up"

        # Rule 2:
        # IF food is here
        # THEN move Up
        elif percept["food_here"]:

            if not percept["wall_up"]:
                return "Up"

            if not percept["wall_right"]:
                return "Right"

            if not percept["wall_left"]:
                return "Left"

            return "Down"

        # Rule 3:
        # IF wall is ahead/up
        # THEN choose another available direction
        elif percept["wall_up"]:

            if not percept["wall_right"]:
                return "Right"

            if not percept["wall_left"]:
                return "Left"

            if not percept["wall_down"]:
                return "Down"

            return "Up"

        # Rule 4:
        # Otherwise continue Up
        else:

            return "Up"


# ============================================================
# MODEL-BASED AGENT
# ============================================================

class ModelBasedAgent:
    """
    Model-Based Agent.

    Maintains an internal state containing:
    - Current estimated position
    - Previously visited cells

    It uses its internal model together with
    current percepts to choose an action.
    """

    def __init__(self):

        self.position = (0, 0)

        self.visited_cells = {
            (0, 0)
        }

    # --------------------------------------------------------
    # Calculate next position
    # --------------------------------------------------------

    def next_position(self, action):

        x, y = self.position

        if action == "Up":
            return (x, y + 1)

        elif action == "Down":
            return (x, y - 1)

        elif action == "Left":
            return (x - 1, y)

        elif action == "Right":
            return (x + 1, y)

        return (x, y)

    # --------------------------------------------------------
    # Update internal model
    # --------------------------------------------------------

    def update_position(self, action, percept):

        # If movement is blocked, position does not change.
        if action == "Up" and percept["wall_up"]:
            return

        if action == "Down" and percept["wall_down"]:
            return

        if action == "Left" and percept["wall_left"]:
            return

        if action == "Right" and percept["wall_right"]:
            return

        self.position = self.next_position(action)

        self.visited_cells.add(self.position)

    # --------------------------------------------------------
    # Choose action
    # --------------------------------------------------------

    def sense_and_act(self, percept):

        # ----------------------------------------------------
        # Rule 1: Toxic trap
        # ----------------------------------------------------

        if percept["smells_toxin"]:

            candidates = [
                "Down",
                "Right",
                "Left",
                "Up"
            ]

        # ----------------------------------------------------
        # Rule 2: Food
        # ----------------------------------------------------

        elif percept["food_here"]:

            candidates = [
                "Up",
                "Right",
                "Left",
                "Down"
            ]

        # ----------------------------------------------------
        # Rule 3: No food/toxin
        # Prefer unvisited cells.
        # ----------------------------------------------------

        else:

            candidates = [
                "Up",
                "Right",
                "Left",
                "Down"
            ]

        # ----------------------------------------------------
        # Find valid unvisited direction
        # ----------------------------------------------------

        for action in candidates:

            blocked = False

            if action == "Up":
                blocked = percept["wall_up"]

            elif action == "Down":
                blocked = percept["wall_down"]

            elif action == "Left":
                blocked = percept["wall_left"]

            elif action == "Right":
                blocked = percept["wall_right"]

            if blocked:
                continue

            next_cell = self.next_position(action)

            if next_cell not in self.visited_cells:

                self.update_position(action, percept)

                return action

        # ----------------------------------------------------
        # If all available cells are visited,
        # choose any valid direction.
        # ----------------------------------------------------

        for action in candidates:

            blocked = False

            if action == "Up":
                blocked = percept["wall_up"]

            elif action == "Down":
                blocked = percept["wall_down"]

            elif action == "Left":
                blocked = percept["wall_left"]

            elif action == "Right":
                blocked = percept["wall_right"]

            if not blocked:

                self.update_position(action, percept)

                return action

        # No valid movement
        return "Up"


# ============================================================
# GUI
# ============================================================

class GridGameGUI:

    def __init__(
        self,
        root,
        width=10,
        height=10,
        num_food=12,
        num_opponents=0,
        walls=None,
        agent_type="model"
    ):

        self.root = root

        self.root.title(
            "IT3012 - Intelligent Agent Grid Hunt"
        )

        # ----------------------------------------------------
        # Environment
        # ----------------------------------------------------

        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls
        )

        # ----------------------------------------------------
        # Select agent
        # ----------------------------------------------------

        if agent_type == "simple":

            self.agent = SimpleReflexAgent()

            self.agent_name = (
                "Simple Reflex Agent"
            )

        elif agent_type == "model":

            self.agent = ModelBasedAgent()

            self.agent_name = (
                "Model-Based Agent"
            )

        elif agent_type == "search":

            self.agent = SearchAgent()

            self.agent_name = (
                "Search Agent"
            )
        # ----------------------------------------------------
        # Canvas size
        # ----------------------------------------------------

        max_canvas_dim = 600

        self.cell_size = max(
            20,
            min(
                max_canvas_dim // self.env.width,
                max_canvas_dim // self.env.height
            )
        )

        canvas_width = (
            self.env.width * self.cell_size
        )

        canvas_height = (
            self.env.height * self.cell_size
        )

        self.canvas = tk.Canvas(
            root,
            width=canvas_width,
            height=canvas_height,
            bg="white"
        )

        self.canvas.pack()

        # ----------------------------------------------------
        # Information label
        # ----------------------------------------------------

        self.label = tk.Label(
            root,
            text=(
                f"{self.agent_name} | "
                f"Score: 0 | Steps: 0"
            ),
            font=("Arial", 14)
        )

        self.label.pack(pady=10)

        # ----------------------------------------------------
        # Start button
        # ----------------------------------------------------

        self.btn = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop,
            font=("Arial", 12)
        )

        self.btn.pack(pady=5)

        self.draw_grid()

    # ========================================================
    # DRAW GRID
    # ========================================================

    def draw_grid(self):

        self.canvas.delete("all")

        # ----------------------------------------------------
        # Grid and walls
        # ----------------------------------------------------

        for x in range(self.env.width):

            for y in range(self.env.height):

                x1 = (
                    x * self.cell_size
                )

                y1 = (
                    (self.env.height - 1 - y)
                    * self.cell_size
                )

                x2 = (
                    x1 + self.cell_size
                )

                y2 = (
                    y1 + self.cell_size
                )

                if (x, y) in self.env.walls:

                    color = "#64748b"

                else:

                    color = "#f1f5f9"

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                    outline="#cbd5e1"
                )

        # ----------------------------------------------------
        # Food
        # ----------------------------------------------------

        for fx, fy in self.env.food_positions:

            offset = self.cell_size * 0.25

            x1 = (
                fx * self.cell_size
                + offset
            )

            y1 = (
                (self.env.height - 1 - fy)
                * self.cell_size
                + offset
            )

            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.5,
                fill="#f59e0b",
                outline="#d97706"
            )

        # ----------------------------------------------------
        # Toxic traps
        # ----------------------------------------------------

        for tx, ty in self.env.toxic_traps:

            offset = self.cell_size * 0.3

            x1 = (
                tx * self.cell_size
                + offset
            )

            y1 = (
                (self.env.height - 1 - ty)
                * self.cell_size
                + offset
            )

            self.canvas.create_polygon(
                x1 + self.cell_size * 0.2,
                y1,
                x1,
                y1 + self.cell_size * 0.4,
                x1 + self.cell_size * 0.4,
                y1 + self.cell_size * 0.4,
                fill="#9333ea",
                outline="#6b21a8"
            )

        # ----------------------------------------------------
        # Opponents
        # ----------------------------------------------------

        for ox, oy in self.env.opponents:

            offset = self.cell_size * 0.2

            x1 = (
                ox * self.cell_size
                + offset
            )

            y1 = (
                (self.env.height - 1 - oy)
                * self.cell_size
                + offset
            )

            self.canvas.create_rectangle(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="#990000",
                outline="#7a0000"
            )

        # ----------------------------------------------------
        # Agent
        # ----------------------------------------------------

        ax, ay = self.env.agent_pos

        offset = self.cell_size * 0.15

        x1 = (
            ax * self.cell_size
            + offset
        )

        y1 = (
            (self.env.height - 1 - ay)
            * self.cell_size
            + offset
        )

        self.canvas.create_oval(
            x1,
            y1,
            x1 + self.cell_size * 0.7,
            y1 + self.cell_size * 0.7,
            fill="#000066",
            outline="#1e3a8a"
        )

    # ========================================================
    # RUN SIMULATION
    # ========================================================

    def run_loop(self):

        self.btn.config(
            state="disabled"
        )

        def step():

            if not self.env.is_done():

                # --------------------------------------------
                # 1. Agent receives percept
                # --------------------------------------------

                percept = self.env.get_percept()

                # --------------------------------------------
                # 2. Agent chooses action
                # --------------------------------------------

                action = self.agent.sense_and_act(
                    percept
                )

                # --------------------------------------------
                # 3. Environment executes action
                # --------------------------------------------

                self.env.execute_action(
                    action
                )

                # --------------------------------------------
                # 4. Redraw environment
                # --------------------------------------------

                self.draw_grid()

                # --------------------------------------------
                # 5. Update information
                # --------------------------------------------

                self.label.config(
                    text=(
                        f"{self.agent_name} | "
                        f"Score: {self.env.score} | "
                        f"Steps: {self.env.steps} | "
                        f"Action: {action}"
                    )
                )

                self.root.after(
                    250,
                    step
                )

            else:

                if self.env.collision:

                    end_text = (
                        "Collision! Game Over! "
                        f"Final Score: {self.env.score}"
                    )

                elif len(self.env.food_positions) == 0:

                    end_text = (
                        "All food collected! "
                        f"Final Score: {self.env.score}"
                    )

                else:

                    end_text = (
                        "Step limit reached! "
                        f"Final Score: {self.env.score}"
                    )

                self.label.config(
                    text=end_text
                )

                self.btn.config(
                    state="normal"
                )

        step()


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = GridGameGUI(
        root,
        width=10,
        height=10,
        num_food=15,
        num_opponents=0,
        agent_type="search"
    )

    root.mainloop()