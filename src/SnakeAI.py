import os
import math
import random
import pygame
import random
import neat

Width = 500   # 画面幅
Height = 500  # 画面高さ

Cols = 25
Rows = 20

WIN = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Snake Game!!")

gen = 0
inversion = False

class Window:
    """ウィンドウの基本クラス"""
    EDGE_WIDTH = 4  # 白枠の幅
    def __init__(self, rect):
        self.rect = rect  # 一番外側の白い矩形
        # 内側の黒い矩形
        self.inner_rect = self.rect.inflate(-self.EDGE_WIDTH * 2,
                                            -self.EDGE_WIDTH * 2)
        self.is_visible = False  # ウィンドウを表示中か？
    def draw(self, screen):
        """ウィンドウを描画"""
        if self.is_visible == False: return
        pygame.draw.rect(screen, (255,255,255), self.rect, 0)
        pygame.draw.rect(screen, (0,0,0), self.inner_rect, 0)
    def show(self):
        """ウィンドウを表示"""
        self.is_visible = True
    def hide(self):
        """ウィンドウを隠す"""
        self.is_visible = False

class Cube():
    """
    Snakeの各体やFruitのオブジェクト
    """
    def __init__(self, start, x=1, y=0, color=(255,0,0)):
        self.rows = 20
        self.w = 500
        self.pos = start # (x, y)
        self.x = x
        self.y = y
        self.color = color
    
    def move(self, x, y):
        self.x = x       # new x
        self.y = y       # new y
        self.pos = (self.pos[0] + self.x, self.pos[1] + self.y)
    
    def draw(self, surface):
        dis = self.w // self.rows
        x, y = self.pos
        pygame.draw.rect(surface, self.color, (x * dis + 1, y * dis + 1, dis - 2, dis - 2))

class Snake():
    def __init__(self, pos, color):
        self.head = Cube(pos)   #頭の位置
        self.color = color
        self.body = [self.head] # 体、最初に頭を追加
        self.turns = {}
        self.x = 0
        self.y = 1
    
    def reset(self, pos):
        """
        Gameoverなどでリセットする際に呼び出される
        """
        self.head = Cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.x = 0
        self.y = 1
        pygame.display.set_caption("Snake Game!!")

    def move(self, surface, best_score):
        self.best_score = best_score
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.font.init()
                wnd = Window(pygame.Rect(70,134,360,140))
                pygame.display.set_caption("Quit option")  
                clock = pygame.time.Clock()
                font = pygame.font.Font(None, 35)
                while True:
                    clock.tick(60)
                    # ウィンドウ表示中は更新を中止
                    if not wnd.is_visible:
                        pygame.display.update()
                    wnd.draw(surface)  # ウィンドウの描画
                    text = font.render("Quit?", True, (255,255,255))   # 描画する文字列の設定
                    best_score = font.render(f"Your best score is {self.best_score}", True, (255,255,255))
                    yes = font.render("Yes: y", True, (255,0,0))
                    no = font.render("No: n", True, (0,255,0))
            
                    surface.blit(text, [180, 150])
                    surface.blit(best_score, [140, 180])
                    surface.blit(yes, [140, 220])
                    surface.blit(no, [280, 220])
                    
                    pygame.display.update()
                    wnd.show()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            exit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            exit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_y:
                            exit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                            wnd.hide()
                            wnd.draw(surface)
                            break
                    else:
                        continue
                    break              
            keys = pygame.key.get_pressed() # keyは押したままにする
            
            for key in keys:
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:       # 左に進む
                    self.x = -1
                    self.y = 0
                elif keys[pygame.K_UP] or keys[pygame.K_w]:       # 上に進む
                    self.x = 0
                    self.y = -1
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:    # 右に進む
                    self.x = 1
                    self.y = 0
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:     # 下に進む
                    self.x = 0
                    self.y = 1
                self.turns[self.head.pos[:]] = [self.x, self.y]
    
        for i, cube in enumerate(self.body):
            posision = cube.pos[:]
            if posision in self.turns:    # 曲がる動作をしていたら
                turn = self.turns[posision]
                cube.move(x=turn[0], y=turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(posision)
            else:
                cube.move(x=cube.x, y=cube.y)
        
    def addTail(self):
        """
        Fruitをとった際にSnakeの末尾にCubeを追加する
        """
        tail = self.body[-1]
        tail_x, tail_y = tail.x, tail.y

        # 右に進んでいるときは左に追加
        if tail_x == 1 and tail_y == 0:
            self.body.append(Cube((tail.pos[0]- 1, tail.pos[1]), x=tail_x, y=tail_y))
        # 上に進んでいるときは下に追加
        elif tail_x == 0 and tail_y == -1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] + 1), x=tail_x, y=tail_y))
        # 左に進んでいるときは右に追加
        elif tail_x == -1 and tail_y == 0:
            self.body.append(Cube((tail.pos[0] + 1, tail.pos[1]), x=tail_x, y=tail_y))
        # 下に進んでいるときは上に追加 
        elif tail_x == 0 and tail_y == 1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] - 1), x=tail_x, y=tail_y))

        
    def draw(self, surface):
        """
        各Cubeを描画
        """
        for cube in self.body:
            cube.draw(surface)

class Game():
    """
    Game開始時に設定
    """
    def __init__(self, snakes, fruits):
        self.surface = WIN
        # self.surface = pygame.display.set_mode((Width, Height))
        # pygame.display.set_caption("Snake Game!!")
        # self.snake = Snake(pos=(10,10), color=(255,0,0)) # Snakeの初期値、色を決定
        self.snakes = snakes
        # self.snake.addTail()                             # Snakeは最初2つのCubeを持っていることにする
        self.clock = pygame.time.Clock()
        self.fruits = fruits
        # self.fruit = Cube(self.randomFruit(Rows, self.snake), color=(0,255,0)) # フルーツの色を決定、場所はランダム
    
    def drawGrid(self, width, rows, surface):
        """
        Grid線を描画
        """
        sizeBtwn = width // rows
        x = 0
        y = 0
        for line in range(rows):
            x = x + sizeBtwn
            y = y +sizeBtwn

            pygame.draw.line(surface, (255, 255, 255), (x, 0), (x, width))
            pygame.draw.line(surface, (255, 255, 255), (0, y), (width, y))
    
    def randomFruit(self, rows, snake, fruit):
        """
        ランダムにフルーツを決定
        """
        positions = snake.body

        while True:
            x = random.randrange(1, rows-1)
            y = random.randrange(1, rows-1)
            if len(list(filter(lambda z: z.pos == (x, y), positions))) > 0:
                continue
            if x == fruit.pos[0] and y == fruit.pos[1]:
                continue
            else:
                break
        return (x, y)

    def allDraw(self):
        """
        全ての描画処理
        """
        self.surface.fill((0,0,0))
        self.drawGrid(Width, Rows, self.surface) # Grid線描画
        for snake, fruit in zip(self.snakes, self.fruits):
            snake.draw(self.surface)            # Snake描画
            fruit.draw(self.surface)            # Fruit描画
        pygame.display.update()
    
    def gameOver(self):
        self.best_score = max(len(self.snake.body), self.best_score)
        pygame.font.init()
        wnd = Window(pygame.Rect(70,134,360,140))
        pygame.display.set_caption("Game Over")  
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 35)
        while True:
            clock.tick(60)
            if not wnd.is_visible:  # ウィンドウ表示中は更新を中止
                pygame.display.update()
            wnd.draw(self.surface)  # ウィンドウの描画
            text = font.render("Game Over", True, (255,255,255))   # 描画する文字列の設定
            best_score = font.render(f"Your best score is {self.best_score}", True, (255,255,255))
            yes = font.render("Quit: y", True, (255,0,0))
            no = font.render("Continue: n", True, (0,255,0))
    
            self.surface.blit(text, [180, 150])
            self.surface.blit(best_score, [140, 180])
            self.surface.blit(yes, [140, 220])
            self.surface.blit(no, [240, 220])
            
            pygame.display.update()
            wnd.show()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_y:
                    exit()
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_n or event.key != pygame.K_y):
                    wnd.hide()
                    wnd.draw(self.surface)
                    break
            else:
                continue
            break
        self.snake.reset((10,10))

    def play(self):
        self.best_score = 0
        while True:
            pygame.time.delay(50)
            self.clock.tick(10)
            self.snake.move(self.surface, self.best_score)
            headPos = self.snake.head.pos
            if headPos[0] >= 20 or headPos[0] < 0 or headPos[1] >= 20 or headPos[1] < 0:
                self.gameOver()

            if self.snake.body[0].pos == self.fruit.pos:
                self.snake.addTail()
                self.fruit = Cube(self.randomFruit(Rows, self.snake), color=(0,255,0))
                
            for x in range(len(self.snake.body)):
                if self.snake.body[x].pos in list(map(lambda z: z.pos, self.snake.body[x+1:])):
                    self.gameOver()
                    break
                        
            self.allDraw()

def wallCollide(snake_pos):
    if snake_pos[0] >= 20 or snake_pos[0] < 0 or snake_pos[1] >= 20 or snake_pos[1] < 0:
        return True

def bodyCollide(snake, pos):
    for x in range(len(snake.body)):
        if pos in list(map(lambda z: z.pos, snake.body[x+1:])):
            return True

def withinRadiusOfFood(pos, fruit):
    return math.sqrt((pos[0] - fruit[0]) ** 2 + (pos[1] - fruit[1]) ** 2)

def getDistances(win, snake, fruit):
    # scale = Width // Rows # 1目盛り
    pos = []
    directions = ['NORTH', 'SOUTH', 'WEST', 'EAST', 'NORTHWEST', 'NORTHEAST', 'SOUTHWEST', 'SOUTHEAST']
    distances = []
    for mode in range(3):
        for x, direction in enumerate(directions):
            distance = 0
            pos.clear()
            pos.append(snake.head.x)
            pos.append(snake.head.y)
            while not wallCollide(pos):
                if direction == 'NORTH':
                    pos[1] -= 1
                elif direction == 'SOUTH':
                    pos[1] += 1
                elif direction == 'WEST':
                    pos[0] -= 1
                elif direction == 'EAST':
                    pos[0] += 1
                elif direction == 'NORTHWEST':
                    pos[1] -= 1
                    pos[0] -= 1
                elif direction == 'NORTHEAST':
                    pos[1] -= 1
                    pos[0] += 1
                elif direction == 'SOUTHWEST':
                    pos[1] += 1
                    pos[0] -= 1
                elif direction == 'SOUTHEAST':
                    pos[1] += 1
                    pos[0] += 1
                if withinRadiusOfFood(pos, fruit) == 0 and mode == 1:
                    break
                if bodyCollide(snake, pos) and mode == 2:
                    break
                # if mode == 1:
                #     pygame.draw.rect(win, green, pygame.Rect(pos[0], pos[1], 10, 10))
                # pygame.display.update()
                distance += 1
            distances.append(distance)

    return distances

def move(snake, index, pre_pos):
    # if index == 0:
    #     change_to = 'UP'
    # elif index == 1:
    #     change_to = 'DOWN'
    # elif index == 2:
    #     change_to = 'LEFT'
    # elif index == 3:
    #     change_to = 'RIGHT'
    
    # if change_to == 'UP' and direction != 'DOWN':
    #     direction = 'UP'
    # if change_to == 'DOWN' and direction != 'UP':
    #     direction = 'DOWN'
    # if change_to == 'LEFT' and direction != 'RIGHT':
    #     direction = 'LEFT'
    # if change_to == 'RIGHT' and direction != 'LEFT':
    #     direction = 'RIGHT'

    # if direction == 'UP':     # 上に進む
    #     snake.x = 0
    #     snake.y = -1
    # elif direction == 'DOWN':     # 下に進む
    #     snake.x = 0
    #     snake.y = 1
    # elif direction == 'LEFT':       # 左に進む
    #     snake.x = -1
    #     snake.y = 0
    # elif direction == 'RIGHT':     # 右に進む
    #     snake.x = 1
    #     snake.y = 0
    global inversion
    inversion = False
    if index == 0:
        if pre_pos == (0, 1):
            inversion = True     # 上に進む
        snake.x = 0
        snake.y = -1
    elif index == 1:
        if pre_pos != (0, -1):
            inversion = True     # 下に進む
        snake.x = 0
        snake.y = 1
    elif index == 2:
        if pre_pos != (1, 0):
            inversion = True      # 左に進む
        snake.x = -1
        snake.y = 0
    elif index == 3:
        if pre_pos != (-1, 0):
            inversion = True     # 右に進む
        snake.x = 1
        snake.y = 0
    # else:
    #     snake.x = 0
    #     snake.y = 0
    snake.turns[snake.head.pos[:]] = [snake.x, snake.y]
    
    for i, cube in enumerate(snake.body):
        posision = cube.pos[:]
        if posision in snake.turns:    # 曲がる動作をしていたら
            turn = snake.turns[posision]
            cube.move(x=turn[0], y=turn[1])
            if i == len(snake.body) - 1:
                snake.turns.pop(posision)
        else:
            cube.move(x=cube.x, y=cube.y)


def eval_genomes(genomes, config):
    """
    Snakeのシミュレーションを実行し、壁、フルーツ、自分の体の距離に応じた
    距離を計算
    """
    global WIN, gen
    win = WIN
    gen += 1

    nets = []
    snakes = []
    fruits = []
    ge = []
    pos = (random.randrange(1, Rows-1), random.randrange(1, Rows-1))
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        snakes.append(Snake(pos=(10,10), color=(255,0,0)))
        fruits.append(Cube((5,15), color=(0,255,0)))
        ge.append(genome)
    
    score = 0
    game = Game(snakes, fruits)
    direction = 'LEFT'
    ticks = 0
    max_ticks = 300
    
    run = True
    while run and len(game.snakes) > 0:
        pygame.time.delay(50)
        game.clock.tick(50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        # pipe_ind = 0
        # if len(birds) > 0:
        #     if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second
        #         pipe_ind = 1                                                                 # pipe on the screen for neural network input

        for x, (snake, fruit) in enumerate(zip(game.snakes, game.fruits)):  # give each bird a fitness of 0.1 for each frame it stays alive
            # ge[x].fitness += 0.01

            # fruit = Cube(game.randomFruit(Rows, snake), color=(0,255,0))

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            inputs = getDistances(win, snake, fruit.pos)
            output = nets[game.snakes.index(snake)].activate(inputs)
            softmax_result = neat.math_util.softmax(output)
            index = softmax_result.index(max(softmax_result))

            pre_pos = (snake.x, snake.y)
            move(snake, index, pre_pos)
            if inversion:
                ge[x].fitness -= 20

        for snake, fruit in zip(game.snakes, game.fruits):
            headPos = snake.head.pos
            if headPos[0] >= 20 or headPos[0] < 0 or headPos[1] >= 20 or headPos[1] < 0:
                ge[game.snakes.index(snake)].fitness -= 20
                drop_idx = game.snakes.index(snake)
                ge.pop(drop_idx)
                game.snakes.pop(drop_idx)
                game.fruits.pop(drop_idx)
        
        for snake, fruit in zip(game.snakes, game.fruits):
            if snake.body[0].pos == fruit.pos:
                game.snakes[game.snakes.index(snake)].addTail()
                # snake.addTail()
                game.fruits[game.fruits.index(fruit)] = Cube(game.randomFruit(Rows, snake, fruit), color=(0,255,0))
                ge[game.snakes.index(snake)].fitness += len(snake.body) * 20

            elif withinRadiusOfFood(snake.body[0].pos, fruit.pos) < 3:
                ge[game.snakes.index(snake)].fitness += 10 + withinRadiusOfFood(snake.body[0].pos, fruit.pos)
            else:
                ge[game.snakes.index(snake)].fitness -= withinRadiusOfFood(snake.body[0].pos, fruit.pos)
            # elif withinRadiusOfFood(snake.body[0].pos, fruit.pos) < 5:
            #     ge[game.snakes.index(snake)].fitness += 1

        for snake, fruit in zip(game.snakes, game.fruits):            
            for x in range(len(snake.body)):
                if snake.body[x].pos in list(map(lambda z: z.pos, snake.body[x+1:])):
                    ge[game.snakes.index(snake)].fitness -= 5
                    drop_idx = game.snakes.index(snake)
                    ge.pop(drop_idx)
                    game.snakes.pop(drop_idx)
                    game.fruits.pop(drop_idx)
                    break
        if ticks > max_ticks:
            run = False
            for genome in ge:
                genome.fitness -= 300
        ticks += 1

        game.allDraw()




def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 200)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == "__main__":
    # game = Game()
    # game.play()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)