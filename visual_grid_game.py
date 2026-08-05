# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0,0]
        self.direction = "Up"  # Starting position (x, y)

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        self.toxic_traps = set()

        while len(self.toxic_traps) < 5:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)

            trap = (tx, ty)

            if (
                trap != (0, 0)
                and trap not in self.walls
                and trap not in self.food_positions
            ):
                self.toxic_traps.add(trap)

        # Generate adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self):

        x, y = self.agent_pos

        # Check cell ahead
        if self.direction == "Up":
            ahead = (x, y + 1)
        elif self.direction == "Down":
            ahead = (x, y - 1)
        elif self.direction == "Left":
            ahead = (x - 1, y)
        else:
            ahead = (x + 1, y)

        return {
            "wall_ahead": (
                ahead in self.walls or
                ahead[0] < 0 or
                ahead[0] >= self.width or
                ahead[1] < 0 or
                ahead[1] >= self.height
            ),

            "food_here": tuple(self.agent_pos) in self.food_positions,

            "smells_toxin": tuple(self.agent_pos) in self.toxic_traps
        }

    def execute_action(self, action: str):
        self.direction = action
        self.steps += 1
        new_pos = list(self.agent_pos)

        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.toxic_traps:
            self.score -= 15
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision
    
class SimpleReflexAgent:

    def sense_and_act(self, percept):

        if percept["food_here"]:
            return "Up"

        elif percept["wall_ahead"]:
            return "Left"

        else:
            return "Up"
        

class ModelBasedAgent:

    def __init__(self, width=12, height=12):
        self.visited_cells = set()
        self.position = (0, 0)
        self.last_action = None
        self.last_wall = False
        self.width = width
        self.height = height

    def update_position(self):
        """
        Update internal position based on the previous action.
        If the previous action hit a wall, the position does not change.
        """

        if self.last_action is None:
            return

        # If the previous action was blocked, stay at the same position
        if self.last_wall:
            return

        x, y = self.position

        if self.last_action == "Up":
            y += 1
        elif self.last_action == "Down":
            y -= 1
        elif self.last_action == "Left":
            x -= 1
        elif self.last_action == "Right":
            x += 1

        self.position = (x, y)

    def get_next_position(self, action):

        x, y = self.position

        if action == "Up":
            y += 1

        elif action == "Down":
            y -= 1

        elif action == "Left":
            x -= 1

        elif action == "Right":
            x += 1

        # Don't allow positions outside the grid
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None

        return (x, y)

    def sense_and_act(self, percept):

        # Update internal state from previous action
        self.update_position()

        # Remember current position
        self.visited_cells.add(self.position)

        # Store whether the current direction is blocked
        self.last_wall = percept["wall_ahead"]

        # Rule 1:
        # IF food is here THEN move forward
        if percept["food_here"]:
            action = "Up"

        # Rule 2:
        # IF toxin is detected THEN move right
        elif percept["smells_toxin"]:
            action = "Right"

        # Rule 3:
        # IF wall ahead THEN choose an unvisited alternative
        elif percept["wall_ahead"]:

            right_cell = self.get_next_position("Right")
            left_cell = self.get_next_position("Left")
            down_cell = self.get_next_position("Down")

            if right_cell is not None and right_cell not in self.visited_cells:
                action = "Right"

            elif left_cell is not None and left_cell not in self.visited_cells:
                action = "Left"

            elif down_cell is not None and down_cell not in self.visited_cells:
                action = "Down"

            else:
                action = "Left"

        # Rule 4:
        # IF no wall ahead THEN continue forward
        else:

            next_cell = self.get_next_position("Up")

            # If forward cell was already visited,
            # try another direction.
            if next_cell in self.visited_cells:

                right_cell = self.get_next_position("Right")
                left_cell = self.get_next_position("Left")
                down_cell = self.get_next_position("Down")

                if right_cell is not None and right_cell not in self.visited_cells:
                    action = "Right"

                elif left_cell is not None and left_cell not in self.visited_cells:
                    action = "Left"

                elif down_cell is not None and down_cell not in self.visited_cells:
                    action = "Down"

                else:
                    action = "Left"

            else:
                action = "Up"

        # Remember the selected action
        self.last_action = action

        return action
    
class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None, agent_type="model"):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls)
        if agent_type == "simple":
            self.agent = SimpleReflexAgent()
            agent_name = "Simple Reflex Agent"
        else:
            self.agent = ModelBasedAgent(self.env.width, self.env.height)
            agent_name = "Model-Based Agent"

        self.agent_name = agent_name

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(
            root,
            text=f"{self.agent_name} | Score: 0 | Steps: 0",
            font=("Arial", 14)
        )
        self.label.pack(pady=10)   

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

        for tx, ty in self.env.toxic_traps:
            x1 = tx * self.cell_size + self.cell_size * 0.2
            y1 = (self.env.height - 1 - ty) * self.cell_size + self.cell_size * 0.2

            self.canvas.create_rectangle(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="purple"
            )

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()

                action = self.agent.sense_and_act(percept)
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(
                    text=(
                        f"{self.agent_name} | "
                        f"Score: {self.env.score} | "
                        f"Steps: {self.env.steps} | "
                        f"Action: {action}"
                    )
                )
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()

    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0,
        agent_type="model"
    )

    root.mainloop()