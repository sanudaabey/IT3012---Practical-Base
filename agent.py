from collections import deque
import heapq
import math


class SearchAgent:

    def __init__(self):
        self.plan = []
        self.active_algo = "AStar"

    def manhattan_distance(self, pos, goal):
        x1, y1 = pos
        x2, y2 = goal

        return abs(x1 - x2) + abs(y1 - y2)

    def euclidean_distance(self, pos, goal):
        x1, y1 = pos
        x2, y2 = goal

        return math.sqrt(
            (x1 - x2) ** 2 +
            (y1 - y2) ** 2
        )

    def get_neighbors(self, position, grid_size, walls):
        x, y = position
        width, height = grid_size

        possible_moves = [
            ("Up", (x, y + 1)),
            ("Down", (x, y - 1)),
            ("Left", (x - 1, y)),
            ("Right", (x + 1, y))
        ]

        neighbors = []

        for action, next_pos in possible_moves:
            nx, ny = next_pos

            if (
                0 <= nx < width
                and 0 <= ny < height
                and next_pos not in walls
            ):
                neighbors.append((action, next_pos))

        return neighbors

    def reconstruct_path(self, parent, start, goal):
        actions = []
        current = goal

        while current != start:
            previous, action = parent[current]
            actions.append(action)
            current = previous

        actions.reverse()
        return actions

    def bfs_search(self, start, goal, grid_size, walls):
        queue = deque([start])
        reached = {start}
        parent = {}

        while queue:
            current = queue.popleft()

            if current == goal:
                return self.reconstruct_path(
                    parent,
                    start,
                    goal
                )

            for action, next_pos in self.get_neighbors(
                current,
                grid_size,
                walls
            ):
                if next_pos not in reached:
                    reached.add(next_pos)
                    parent[next_pos] = (current, action)
                    queue.append(next_pos)

        return []

    def dfs_search(self, start, goal, grid_size, walls):
        stack = [start]
        reached = {start}
        parent = {}

        while stack:
            current = stack.pop()

            if current == goal:
                return self.reconstruct_path(
                    parent,
                    start,
                    goal
                )

            for action, next_pos in self.get_neighbors(
                current,
                grid_size,
                walls
            ):
                if next_pos not in reached:
                    reached.add(next_pos)
                    parent[next_pos] = (current, action)
                    stack.append(next_pos)

        return []

    def ucs_search(self, start, goal, grid_size, walls):
        frontier = []
        heapq.heappush(frontier, (0, start))

        reached = {start: 0}
        parent = {}

        while frontier:
            cost, current = heapq.heappop(frontier)

            if current == goal:
                return self.reconstruct_path(
                    parent,
                    start,
                    goal
                )

            if cost > reached[current]:
                continue

            for action, next_pos in self.get_neighbors(
                current,
                grid_size,
                walls
            ):
                new_cost = cost + 1

                if (
                    next_pos not in reached
                    or new_cost < reached[next_pos]
                ):
                    reached[next_pos] = new_cost
                    parent[next_pos] = (current, action)

                    heapq.heappush(
                        frontier,
                        (new_cost, next_pos)
                    )

        return []

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type="manhattan"
    ):
        frontier = []

        if heuristic_type == "manhattan":
            h_cost = self.manhattan_distance(
                start_pos,
                goal_pos
            )
        else:
            h_cost = self.euclidean_distance(
                start_pos,
                goal_pos
            )

        g_cost = 0
        f_cost = g_cost + h_cost

        heapq.heappush(
            frontier,
            (
                f_cost,
                g_cost,
                start_pos,
                []
            )
        )

        reached_states = set()

        while frontier:
            (
                f_cost,
                g_cost,
                current_pos,
                path_taken
            ) = heapq.heappop(frontier)

            if current_pos == goal_pos:
                return path_taken

            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            for action, next_pos in self.get_neighbors(
                current_pos,
                grid_size,
                walls
            ):
                if next_pos in reached_states:
                    continue

                new_g_cost = g_cost + 1

                if heuristic_type == "manhattan":
                    new_h_cost = self.manhattan_distance(
                        next_pos,
                        goal_pos
                    )
                else:
                    new_h_cost = self.euclidean_distance(
                        next_pos,
                        goal_pos
                    )

                new_f_cost = new_g_cost + new_h_cost

                new_path = path_taken + [action]

                heapq.heappush(
                    frontier,
                    (
                        new_f_cost,
                        new_g_cost,
                        next_pos,
                        new_path
                    )
                )

        return []

    def find_closest_food(self, start, foods):
        return min(
            foods,
            key=lambda food:
            abs(start[0] - food[0])
            + abs(start[1] - food[1])
        )

    def sense_and_act(self, percept):
        if not self.plan:
            start = percept["agent_pos"]
            grid_size = percept["grid_size"]
            walls = set(percept["walls"])
            foods = percept["all_food"]

            if not foods:
                return "Up"

            goal = self.find_closest_food(
                start,
                foods
            )

            if self.active_algo == "BFS":
                self.plan = self.bfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == "DFS":
                self.plan = self.dfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == "UCS":
                self.plan = self.ucs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == "AStar":
                self.plan = self.astar_search(
                    start,
                    goal,
                    walls,
                    grid_size,
                    heuristic_type="manhattan"
                )

        if self.plan:
            return self.plan.pop(0)

        return "Up"


if __name__ == "__main__":
    agent = SearchAgent()

    print(
        "Manhattan:",
        agent.manhattan_distance(
            (0, 0),
            (3, 4)
        )
    )

    print(
        "Euclidean:",
        agent.euclidean_distance(
            (0, 0),
            (3, 4)
        )
    )