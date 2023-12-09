# 2023.12.05 - update


from enum import Enum
from typing import List, NamedTuple, Callable, Optional
import random
from math import sqrt
from generic_search import dfs, bfs, node_to_path, astar, Node


class Cell(str, Enum):
    EMPTY = " "
    BLOCKED = "X"
    START = "S"
    GOAL = "G"
    PATH = "*"



class MazeLocation(NamedTuple): #maybe change to plane location, might not need though
    row: int
    column: int


   
 
class Maze:
    def __init__(self, rows: int, columns: int, sparseness: float = 0.2, start: MazeLocation = MazeLocation(0, 0), goal: MazeLocation = MazeLocation(9, 9)) -> None:
        # initialize basic instance variables
        # a parameter here, would be more elegant if I could avoid
        self._rows: int = rows
        self._columns: int = columns
        self.start: MazeLocation = start
        self.goal: MazeLocation = goal
        # fill the grid with empty cells
        self._grid: List[List[Cell]] = [[Cell.EMPTY for c in range(columns)] for r in range(rows)]
        # populate the grid with blocked cells
        self._randomly_fill(rows, columns, sparseness)
        # fill the start and goal locations in
        self._grid[start.row][start.column] = Cell.START
        self._grid[goal.row][goal.column] = Cell.GOAL
    

    def _randomly_fill(self, rows: int, columns: int, sparseness: float):
        for row in range(rows):
            for column in range(columns):
                if random.uniform(0, 1.0) < sparseness:
                    self._grid[row][column] = Cell.BLOCKED

    # return a nicely formatted version of the maze for printing
    def __str__(self) -> str:
        output: str = ""
        for row in self._grid:
            output += "".join([c.value for c in row]) + "\n"
        return output

    def goal_test(self, ml: MazeLocation) -> bool:
        return ml == self.goal

    def successors(self, ml: MazeLocation) -> List[MazeLocation]:
        locations: List[MazeLocation] = []
        if ml.row + 1 < self._rows and self._grid[ml.row + 1][ml.column] != Cell.BLOCKED:
            locations.append(MazeLocation(ml.row + 1, ml.column))
        if ml.row - 1 >= 0 and self._grid[ml.row - 1][ml.column] != Cell.BLOCKED:
            locations.append(MazeLocation(ml.row - 1, ml.column))
        if ml.column + 1 < self._columns and self._grid[ml.row][ml.column + 1] != Cell.BLOCKED:
            locations.append(MazeLocation(ml.row, ml.column + 1))
        if ml.column - 1 >= 0 and self._grid[ml.row][ml.column - 1] != Cell.BLOCKED:
            locations.append(MazeLocation(ml.row, ml.column - 1))
        return locations

    def mark(self, path: List[MazeLocation]):
        for maze_location in path:
            self._grid[maze_location.row][maze_location.column] = Cell.PATH
        self._grid[self.start.row][self.start.column] = Cell.START
        self._grid[self.goal.row][self.goal.column] = Cell.GOAL
    
    def clear(self, path: List[MazeLocation]):
        for maze_location in path:
            self._grid[maze_location.row][maze_location.column] = Cell.EMPTY
        self._grid[self.start.row][self.start.column] = Cell.START
        self._grid[self.goal.row][self.goal.column] = Cell.GOAL

        self.movement = MazeMovement(self, self.start)

    def mark_cell(self, location: MazeLocation):
        self._grid[location.row][location.column] = Cell.PATH

class MazeMovement:
    def __init__(self, maze: Maze, current_location: MazeLocation):
        self.maze = maze
        self.current_location = current_location
        self.counter = 0

    def move(self):
        self.goal_reached = False  # Flag for reaching the goal
        while True:
            self.maze.mark_cell(self.current_location)  # Mark the current location
            print(self.maze)  # Print the maze with the marked path

            direction = input("Which direction on your compass would you like to go? Remember you want to get to the goal before the algorithm does.: ").lower()
            self.counter += 1
            result = self.go_direction(direction)

            if result != 0:
                # Movement was unsuccessful (blocked or out of bounds)
                break
            if self.current_location == self.maze.goal:
                # Reached the goal
                self.goal_reached = True
                print("Goal reached!")
                break

        print(f"Stopped at {self.current_location}")
        print(f"Total moves by user: {self.counter}")

    def go_direction(self, direction: str):
        new_row = self.current_location.row
        new_column = self.current_location.column

        if direction.lower() == "north":
            new_row -= 1
        elif direction.lower() == "south":
            new_row += 1
        elif direction.lower() == "east":
            new_column += 1
        elif direction.lower() == "west":
            new_column -= 1
        else:
            print("Invalid direction")
            return -1

        # Check if the new location is within bounds and not blocked
        if 0 <= new_row < self.maze._rows and 0 <= new_column < self.maze._columns:
            if self.maze._grid[new_row][new_column] != Cell.BLOCKED:
                self.current_location = MazeLocation(new_row, new_column)
                return 0  # Indicate successful movement
            else:
                print("The way is blocked!")
                return -1  # Indicate blocked path
        else:
            print("Out of bounds!")
            return -1  # Indicate out of bounds

        return 0

   
       
## Interesting so ml isn't recognised
def euclidean_distance(goal: MazeLocation) -> Callable[[MazeLocation], float]:
    def distance(ml: MazeLocation) -> float:
        xdist: int = ml.column - goal.column
        ydist: int = ml.row - goal.row
        return sqrt((xdist * xdist) + (ydist * ydist))
    return distance


def manhattan_distance(goal: MazeLocation) -> Callable[[MazeLocation], float]:
    def distance(ml: MazeLocation) -> float:
        xdist: int = abs(ml.column - goal.column)
        ydist: int = abs(ml.row - goal.row)
        return (xdist + ydist)
    return distance


if __name__ == "__main__":
    m: Maze = Maze(20,20)
    start_location = MazeLocation(0, 0)
    maze_movement = MazeMovement(m, start_location)

    # Run search algorithms
    solution1: Optional[Node[MazeLocation]] = dfs(m.start, m.goal_test, m.successors)
    solution2: Optional[Node[MazeLocation]] = bfs(m.start, m.goal_test, m.successors)
    distance: Callable[[MazeLocation], float] = manhattan_distance(m.goal)
    solution3: Optional[Node[MazeLocation]] = astar(m.start, m.goal_test, m.successors, distance)

    # Calculate path lengths
    dfs_path_length = len(node_to_path(solution1)) if solution1 else None
    bfs_path_length = len(node_to_path(solution2)) if solution2 else None
    a_star_path_length = len(node_to_path(solution3)) if solution3 else None


    # Let the user move through the maze
    goal_reached_by_user = maze_movement.move()

    # Display results of search algorithms
    print("Search Algorithm Results:")
    if dfs_path_length:
        print(f"DFS path length: {dfs_path_length}")
    if bfs_path_length:
        print(f"BFS path length: {bfs_path_length}")
    if a_star_path_length:
        print(f"A* path length: {a_star_path_length}")

    # Compare only if the goal was reached by the user
    if maze_movement.goal_reached:
        user_path_length = maze_movement.counter
        print(f"\nYour path length: {user_path_length}")

        # Compare user's performance with each algorithm
        for algo_name, algo_length in [("DFS", dfs_path_length), ("BFS", bfs_path_length), ("A*", a_star_path_length)]:
            if algo_length:
                if user_path_length < algo_length:
                    print(f"You beat {algo_name} by {algo_length - user_path_length} steps!")
                elif user_path_length == algo_length:
                    print(f"You matched the path length of {algo_name}!")
                else:
                    print(f"{algo_name} was more efficient by {user_path_length - algo_length} steps.")
    else:
        print("As the goal was not reached, we don't know if you beat the algorithm.")