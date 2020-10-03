import pygame
from queue import PriorityQueue
import math

pygame.init()

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

WIDTH = 900
WINDOW = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("A*")

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.width = width
        self.x = col * width
        self.y = row * width
        self.color = WHITE
        self.neighbors = []
        self.total_rows = total_rows
    def get_pos(self):
        return self.row, self.col
    def is_closed(self):
        return self.color == RED
    def is_open(self):
        return self.color == GREEN
    def is_barrier(self):
        return self.color == BLACK
    def is_start(self):
        return self.color == ORANGE
    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED
    def make_open(self):
        self.color = GREEN
    def make_barrier(self):
        self.color = BLACK
    def make_start(self):
        self.color = ORANGE
    def make_end(self):
        self.color = TURQUOISE
    def make_path(self):
        self.color = PURPLE
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col+1].is_barrier(): # LEFT
            self.neighbors.append(grid[self.row][self.col+1])

        if self.col > 0 and not grid[self.row][self.col-1].is_barrier(): # RIGHT
            self.neighbors.append(grid[self.row][self.col-1])

    def __lt__(self, other):
        return False

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return int(10 * math.hypot(x2-x1,y2-y1))
    # return abs(x2 - x1) + abs(y2 -y1)
def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()
def a_star_search(draw, node_grid, start, end):
    count = 0
    priority_queue = PriorityQueue()
    priority_queue.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in node_grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in node_grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_hash_set = {start}

    while not priority_queue.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = priority_queue.get()[2]
        open_hash_set.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 10

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_hash_set:
                    count += 1
                    priority_queue.put((f_score[neighbor],count,neighbor))
                    open_hash_set.add(neighbor)
                    neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()
    return False

def make_grid_nodes(rows, width):
    grid = []
    gap = width//rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            current_node = Node(i, j, gap, rows)
            grid[i].append(current_node)
    return grid

def draw_grid_lines(win, rows, width):
    gap = width//rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))
        pygame.draw.line(win, GREY, (i*gap, 0), (i*gap,width))

def find_clicked_cube(pos, rows, width):
    pos_x, pos_y = pos
    gap = width//rows
    # also just do pos_x//gap, ,pos_y//gap
    for i in range(rows):
        for j in range(rows):
            if i*gap <= pos_y <= (i+1)*gap and j*gap <= pos_x <= (j+1)*gap:
                return i,j
def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for Node in row:
            Node.draw(win)
    draw_grid_lines(win, rows, width)
    pygame.display.update()

def main(win, width):
    ROWS = 50
    start = None
    end = None
    node_grid = make_grid_nodes(ROWS, width)
    print(node_grid)

    carryOn = True
    started = False
    while carryOn:
        draw(win, node_grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                carryOn = False
            if started:
                continue
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = find_clicked_cube(pos,ROWS,width)
                print(row,col)
                current_node = node_grid[row][col]
                if not start and current_node != end:
                    start = current_node
                    start.make_start()
                elif not end and current_node != start:
                    end = current_node
                    end.make_end()
                elif current_node != end and current_node != start:
                    current_node.make_barrier()
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = find_clicked_cube(pos, ROWS, width)
                current_node = node_grid[row][col]
                current_node.reset()
                if current_node == start:
                    start = None
                if current_node == end:
                    end = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    node_grid = make_grid_nodes(ROWS, width)
                if event.key == pygame.K_SPACE and start and end:
                    for row in node_grid:
                        for Node in row:
                            Node.update_neighbors(node_grid)
                    a_star_search(lambda: draw(win, node_grid, ROWS, width), node_grid, start, end)
        pygame.display.update()

if __name__ == "__main__":
    main(WINDOW, WIDTH)