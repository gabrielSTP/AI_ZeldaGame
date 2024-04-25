import heapq
import time
import tkinter as tk

start_time = time.time()
def draw_map(canvas, map_matrix, color_map):
    rows = len(map_matrix)
    cols = len(map_matrix[0])
    for i in range(rows):
        for j in range(cols):
            color = color_map.get(map_matrix[i][j], "white")  # Mapeia o número da matriz para o código de cor, padrão é branco
            canvas.create_rectangle(j * 10, i * 10, (j + 1) * 10, (i + 1) * 10, fill=color)
def draw_special_points(canvas, special_points, color):
    for coord in special_points:
        x, y = coord
        # Ajusta a orientação em 45 graus
        canvas.create_rectangle(y * 10, x * 10, (y + 1) * 10, (x + 1) * 10, fill=color)
        # Atualiza a tela para exibir o ponto especial imediatamente
        canvas.update()
        
def draw_path(canvas, path, goals, starts):
    # Função para desenhar um único retângulo do caminho
    def draw_rect(coord):
        x, y = coord
        canvas.create_rectangle(y * 10, x * 10, (y + 1) * 10, (x + 1) * 10, fill="#F0B222")
        # Atualiza a tela para que o retângulo seja exibido imediatamente
        canvas.update()

    # Itera sobre as coordenadas do caminho, ignorando a primeira e última coordenada
    for coord in path[1:-1]:
        if coord in goals or coord in starts:
            pass
        else:
            draw_rect(coord)
            canvas.after(1)
        
def heuristic(a, b):# Função heurística para calcular a distância entre dois pontos no grid
    ax, ay = a
    bx, by = b
    return ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5

def get_neighbors(current, grid):# Função para obter os vizinhos de um nó específico no grid
    row, col = current
    neighbors = []
    
    possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]# Lista de possíveis movimentos: esquerda, direita, cima e baixo

    for move in possible_moves:
        new_row, new_col = row + move[0], col + move[1]

        if 0 <= new_row < len(grid) and 0 <= new_col < len(grid[0]) and grid[new_row][new_col] != 0:# Verifica se o novo nó está dentro dos limites do grid e não é um obstáculo
            neighbors.append((new_row, new_col))

    return neighbors

def visualize_path(grid, path, goals, dungeons):# Função para visualizar o caminho encontrado no grid
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            current_point = (row, col)
            if current_point == path[0]:
                print("L ", end='')  # Início
            elif current_point == path[-1]:
                print("E ", end='')  # Fim
            elif current_point in dungeons:
                print("D ", end='')  # Meta
            elif current_point in path and path.index(current_point) != 0:
                print("* ", end='')  # Caminho (excluindo o ponto de início duplicado)
            else:
                print(". ", end='')  # Obstáculo ou terreno
        print()  # Imprima uma nova linha após cada linha interna do loop
        
def dun_visualize_path(grid, path, goals):# Função para visualizar o caminho encontrado no grid(ESPECIFICO PARA AS DUNGEONS)
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            current_point = (row, col)
            if current_point == path[0]:
                print("E ", end='')  # Início
            elif current_point == path[-1]:
                print("P ", end='')  # Fim
            elif current_point in path and path.index(current_point) != 0:
                print("* ", end='')  # Caminho (excluindo o ponto de início duplicado)
            else:
                print(". ", end='')  # Obstáculo ou terreno
        print()  # Imprima uma nova linha após cada linha interna do loop

def calculate_total_cost(path, terrain_costs):# Função para calcular o custo total do caminho
    total_cost = 0
    for node in path:
        total_cost += terrain_costs[node[0]][node[1]]
    return total_cost

def dungeon(grid, start, goal, terrain_costs):# Função A* para encontrar o caminho (ESPECIFICO PARA DUNGEONS)
    final_path = []# Lista para armazenar o caminho final
    total_cost = 0 # Variável para armazenar o custo total do caminho
    heap = [(0, start)]# Inicializa uma fila de prioridade com o ponto de partida
    came_from = {}# Dicionário para rastrear o caminho percorrido
    cost_so_far = {start: 0}# Dicionário para armazenar o custo acumulado até o momento para cada nó

    while heap:
            current_cost, current_node = heapq.heappop(heap) # Remove e retorna o nó com menor custo da fila
            if current_node == goal:# Verifica se chegou ao objetivo
                path = []
                while current_node in came_from:
                    path.append(current_node)
                    current_node = came_from[current_node]
                path.append(start)
                path = path[::-1]

                final_path.extend(path)  # Evita a duplicação do ponto de início
                total_cost += calculate_total_cost(path, terrain_costs)
                total_cost += total_cost #Duplica o custo, para considerar a volta pelo mesmo caminho
                start = goal  # Atualiza o ponto de partida para o próximo objetivo
                break

            for next_node in get_neighbors(current_node, grid):# Itera sobre os vizinhos do nó atual
                new_cost = cost_so_far[current_node] + terrain_costs[next_node[0]][next_node[1]]
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + heuristic(goal, next_node) # Calcula a prioridade do próximo nó
                    heapq.heappush(heap, (priority, next_node))# Adiciona o próximo nó à fila de prioridade
                    came_from[next_node] = current_node# Registra o caminho até o próximo nó

    if path:
        print("Caminho encontrado:", path)
        dun_visualize_path(terrain_costs, path, goal_nodes)
        print("Custo total do caminho da Dungeon:", total_cost)
        print("\n")
    else:
        print("Não foi possível encontrar um caminho.")
    return final_path, total_cost

def a_star(grid, start, goals, finalgoal, terrain_costs, dungeons, dun_grids, dun_goals, dun_start):
    final_path = []
    total_cost = 0
    dun_done = 0
    
    while goals:
        distances = [(goal, heuristic(start, goal)) for goal in goals]  # Calcula as distâncias de todos os objetivos
        distances.sort(key=lambda x: x[1])  # Ordena os objetivos com base nas distâncias
        closest_goal, _ = distances[0]  # Pega o objetivo mais próximo
        goals.remove(closest_goal)  # Remove o objetivo mais próximo da lista de objetivos
        
        heap = [(0, start)]
        came_from = {}
        cost_so_far = {start: 0}
        
        while heap:
            current_cost, current_node = heapq.heappop(heap)
            if current_node == closest_goal:
                if current_node in dungeons:
                    print("DUNGEON: ", current_node)
                    if current_node == dungeons[0]:
                        id = 0
                        dun_done += 1
                    elif current_node == dungeons[1]:
                        id = 1
                        dun_done += 1
                    elif current_node == dungeons[2]:
                        id = 2
                        dun_done += 1

                    dungeon_path, dungeon_cost = dungeon(dun_grids[id], dun_start[id], dun_goals[id], dun_grids[id])
                    total_cost += dungeon_cost

                    # Mostra a interface gráfica para a dungeon concluída
                    color_map = {
                        0: "#697060",#Verde escuro
                        10: "#F2D680",#Verde claro
                    }
                    teste = id
                    root = tk.Tk()
                    root.title("DUNGEON: "+ str(dun_done))

                    canvas = tk.Canvas(root, width=280, height=280, bg="white")
                    canvas.pack()
                    
                    draw_map(canvas, dun_grids[id], color_map)  # Desenhe o mapa da dungeon
                    draw_special_points(canvas, [dun_start[id]], "#5EB670")
                    draw_special_points(canvas, [dun_goals[id]], "red")
                    draw_path(canvas, dungeon_path, dun_goals[id], dun_start[id])  # Desenhe o caminho encontrado na dungeon
                    

                    root.mainloop()  # Inicie o loop principal da interface gráfica

                    if dun_done == 3:
                        goals.append(finalgoal)
                    
                path = []
                while current_node in came_from:
                    path.append(current_node)
                    current_node = came_from[current_node]
                path.append(start)
                path = path[::-1]

                final_path.extend(path)
                total_cost += calculate_total_cost(path, terrain_costs)
                start = closest_goal
                break

            for next_node in get_neighbors(current_node, grid):
                new_cost = cost_so_far[current_node] + terrain_costs[next_node[0]][next_node[1]]
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + heuristic(closest_goal, next_node)
                    heapq.heappush(heap, (priority, next_node))
                    came_from[next_node] = current_node
            
    return final_path, total_cost

terrain_costs = ([
[100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150],
[100, 10, 10, 100, 10, 100, 10, 100, 10, 10, 10, 10, 10, 10, 10, 150, 150, 150, 150, 150, 150, 150, 20, 20, 20, 20, 20, 150, 150, 150, 150, 150, 150, 20, 20, 20, 20, 150, 150, 150, 150, 150],
[100, 10, 10, 100, 10, 10, 10, 100, 10, 100, 10, 10, 10, 10, 10, 10, 150, 150, 150, 150, 150, 20, 20, 20, 20, 20, 20, 20, 150, 150, 150, 150, 20, 20, 20, 20, 20, 20, 150, 150, 150, 150],
[100, 10, 100, 100, 10, 100, 10, 100, 10, 100, 10, 10, 100, 10, 10, 10, 10, 150, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 150, 150],
[100, 10, 10, 10, 10, 100, 10, 100, 10, 100, 10, 10, 100, 10, 10, 10, 10, 150, 20, 150, 150, 20, 20, 20, 20, 20, 20, 20, 150, 150, 150, 150, 20, 20, 20, 20, 20, 20, 150, 150, 150, 150],
[100, 10, 100, 100, 10, 100, 10, 100, 10, 100, 10, 100, 100, 100, 10, 10, 10, 150, 20, 150, 150, 150, 20, 20, 20, 20, 20, 150, 150, 150, 150, 180, 150, 20, 20, 20, 20, 150, 180, 150, 150, 150],
[100, 10, 100, 100, 10, 100, 10, 10, 10, 100, 10, 10, 10, 10, 10, 10, 10, 150, 20, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 180, 150, 150, 150, 150, 150, 150, 180, 150, 150, 150],
[100, 10, 100, 100, 100, 100, 10, 100, 100, 100, 10, 10, 10, 10, 10, 10, 10, 150, 20, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 180, 150, 150, 150, 150, 150, 150, 180, 150, 10, 150],
[100, 10, 10, 100, 10, 10, 10, 10, 10, 100, 10, 10, 180, 10, 10, 10, 10, 150, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 150, 150, 180, 150, 150, 150, 150, 150, 150, 180, 150, 10, 150],
[100, 100, 100, 100, 10, 100, 100, 100, 10, 10, 10, 180, 180, 180, 10, 10, 10, 150, 20, 150, 150, 150, 150, 150, 20, 150, 150, 150, 20, 150, 150, 180, 150, 150, 150, 150, 150, 150, 180, 150, 10, 150],
[100, 10, 10, 100, 10, 10, 10, 10, 10, 10, 180, 180, 180, 180, 180, 10, 10, 150, 150, 150, 100, 100, 100, 150, 150, 150, 100, 100, 100, 100, 100, 180, 10, 10, 150, 150, 10, 10, 180, 10, 10, 150],
[100, 10, 10, 100, 10, 10, 100, 10, 10, 10, 10, 180, 180, 180, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 180, 180, 180, 180, 180, 180, 180, 180, 180, 10, 10, 150],
[100, 10, 10, 100, 10, 10, 100, 10, 10, 10, 10, 10, 180, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 180, 10, 10, 100, 10, 10, 10, 10, 10, 100, 10, 150],
[100, 10, 10, 100, 10, 10, 100, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 100, 100, 100, 10, 10, 10, 100, 100, 100, 100, 10, 10, 10, 180, 10, 10, 10, 10, 10, 10, 100, 10, 100, 10, 150],
[100, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 180, 10, 100, 10, 100, 10, 100, 100, 10, 100, 10, 150],
[100, 10, 100, 100, 100, 100, 100, 10, 100, 100, 100, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 180, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 150],
[100, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 10, 10, 10, 10, 10, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150],
[100, 10, 10, 10, 10, 10, 10, 10, 10, 180, 10, 10, 100, 10, 100, 10, 10, 180, 10, 10, 10, 10, 10, 10, 10, 10, 180, 10, 10, 10, 180, 10, 150, 20, 20, 20, 20, 20, 20, 20, 20, 150],
[100, 10, 100, 10, 10, 100, 10, 10, 10, 180, 10, 10, 10, 10, 10, 10, 10, 180, 10, 100, 10, 10, 10, 10, 100, 10, 180, 180, 180, 180, 180, 10, 150, 20, 150, 20, 20, 150, 20, 20, 20, 150],
[100, 10, 100, 10, 10, 100, 10, 10, 10, 180, 10, 10, 100, 10, 100, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 180, 10, 10, 10, 10, 10, 150, 20, 150, 150, 150, 150, 150, 150, 150, 150],
[100, 10, 100, 10, 10, 100, 10, 10, 10, 180, 10, 10, 10, 10, 10, 10, 10, 180, 10, 10, 10, 10, 10, 10, 10, 10, 180, 10, 10, 10, 150, 10, 150, 20, 20, 20, 20, 20, 20, 20, 20, 150],
[100, 10, 100, 10, 10, 100, 10, 10, 10, 180, 10, 100, 100, 100, 100, 10, 10, 180, 10, 100, 10, 10, 10, 10, 100, 10, 10, 10, 10, 10, 150, 10, 150, 20, 150, 150, 150, 150, 20, 150, 150, 150],
[100, 10, 10, 10, 10, 10, 10, 10, 10, 180, 10, 10, 10, 10, 10, 10, 10, 180, 10, 10, 10, 10, 10, 10, 10, 10, 180, 10, 150, 10, 150, 10, 150, 20, 20, 20, 20, 20, 20, 20, 20, 150],
[100, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 100, 100, 100, 100, 10, 10, 180, 180, 180, 180, 10, 10, 180, 180, 180, 180, 10, 150, 10, 150, 10, 150, 150, 150, 20, 20, 150, 150, 150, 150, 150],
[100, 100, 100, 100, 100, 100, 100, 10, 10, 100, 100, 100, 100, 100, 100, 100, 100, 100, 10, 10, 10, 10, 10, 10, 10, 10, 180, 10, 150, 10, 150, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 150],
[100, 100, 100, 100, 100, 100, 10, 10, 100, 100, 100, 100, 100, 10, 100, 100, 100, 100, 100, 10, 100, 100, 100, 10, 10, 10, 180, 10, 150, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 150],
[100, 10, 100, 10, 100, 10, 10, 10, 100, 100, 100, 100, 10, 10, 10, 100, 100, 100, 100, 10, 100, 100, 100, 10, 10, 10, 180, 10, 150, 10, 10, 10, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150],
[150, 10, 10, 10, 100, 10, 10, 10, 100, 100, 100, 10, 10, 10, 10, 10, 100, 100, 100, 10, 10, 10, 10, 10, 10, 10, 180, 10, 10, 10, 10, 10, 10, 10, 10, 150, 10, 10, 10, 10, 10, 150],
[150, 10, 10, 10, 100, 10, 10, 10, 100, 100, 100, 100, 10, 10, 10, 100, 100, 100, 100, 10, 100, 10, 10, 10, 10, 10, 180, 10, 10, 10, 10, 10, 10, 10, 10, 150, 10, 10, 10, 10, 10, 150],
[150, 10, 10, 10, 10, 10, 10, 10, 10, 100, 100, 100, 100, 10, 100, 100, 100, 100, 10, 10, 100, 10, 10, 10, 10, 10, 180, 180, 180, 10, 180, 180, 180, 180, 10, 150, 10, 150, 150, 150, 150, 150],
[150, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 180, 10, 10, 10, 10, 10, 10, 10, 150],
[150, 150, 150, 150, 150, 150, 150, 150, 150, 10, 10, 10, 10, 150, 150, 150, 150, 150, 150, 150, 10, 10, 150, 150, 150, 150, 10, 10, 10, 10, 10, 10, 10, 180, 150, 150, 150, 150, 150, 150, 10, 150],
[150, 20, 20, 20, 20, 20, 20, 20, 150, 10, 10, 10, 10, 150, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 150, 10, 10, 10, 10, 10, 10, 10, 180, 150, 150, 150, 150, 150, 150, 150, 150],
[150, 20, 150, 150, 20, 20, 20, 20, 150, 10, 10, 10, 10, 150, 10, 10, 10, 10, 10, 10, 10, 10, 100, 10, 10, 150, 10, 10, 180, 180, 180, 180, 180, 180, 180, 180, 150, 150, 180, 180, 150, 150],
[150, 20, 150, 150, 20, 20, 20, 20, 150, 10, 10, 10, 10, 150, 10, 100, 10, 10, 180, 180, 10, 10, 100, 10, 10, 150, 10, 10, 180, 180, 150, 180, 180, 180, 180, 180, 150, 150, 180, 180, 150, 150],
[150, 20, 20, 20, 20, 20, 20, 20, 150, 10, 10, 150, 10, 150, 10, 10, 10, 10, 180, 180, 10, 10, 100, 10, 10, 150, 10, 10, 180, 180, 180, 180, 150, 150, 180, 180, 150, 150, 180, 180, 150, 150],
[150, 20, 20, 20, 20, 20, 20, 20, 150, 10, 10, 150, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 150, 10, 10, 180, 180, 180, 180, 150, 150, 180, 180, 150, 150, 180, 180, 150, 150],
[150, 20, 20, 20, 20, 20, 20, 150, 150, 150, 150, 150, 10, 10, 100, 10, 10, 10, 10, 10, 100, 100, 100, 10, 10, 150, 10, 10, 180, 180, 180, 180, 180, 180, 180, 180, 150, 150, 180, 180, 150, 150],
[150, 20, 20, 20, 20, 20, 20, 20, 20, 150, 150, 150, 10, 10, 100, 10, 180, 180, 180, 10, 10, 100, 10, 10, 10, 150, 10, 10, 180, 180, 180, 180, 180, 180, 180, 180, 150, 150, 180, 180, 150, 150],
[150, 20, 20, 20, 20, 20, 20, 20, 20, 150, 150, 150, 10, 10, 100, 10, 10, 10, 10, 10, 10, 100, 10, 10, 10, 150, 10, 10, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 150, 150],
[150, 20, 20, 20, 20, 20, 20, 20, 20, 20, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 150, 150, 150, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 150, 150],
[150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150],
 ])

dungeon_matrix1 = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 0, 0, 0, 0],
[0, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 0, 0, 0, 0, 0, 0, 10, 10, 10, 0, 0, 0, 0],
[0, 0, 10, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0, 0, 10, 10, 10, 0, 0, 0, 0],
[0, 0, 10, 0, 0, 0, 0, 10, 0, 0, 0, 0, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0],
[0, 0, 10, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0],
[0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0],
[0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 0, 0],
[0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 0, 0],
[0, 0, 10, 10, 10, 10, 10, 10, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 0, 0],
[0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 0, 0],
[0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0],
[0, 0, 10, 10, 10, 0, 0, 10, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0],
[0, 0, 10, 10, 10, 0, 0, 10, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0],
[0, 0, 10, 10, 10, 0, 0, 10, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 10, 10, 10, 0, 0, 10, 0, 0, 10, 10, 10, 0, 0, 0, 0, 0, 10, 10, 10, 10, 0, 0, 10, 0, 0, 0],
[0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0, 10, 10, 10, 10, 0, 0, 10, 0, 0, 0],
[0, 0, 10, 10, 10, 0, 0, 10, 0, 0, 10, 10, 10, 0, 0, 0, 0, 0, 10, 10, 10, 10, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

dungeon_matrix2 = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 10, 10, 10, 0, 0, 0, 10, 10, 10, 10, 0, 0, 0, 0, 0, 0],
[0, 0, 10, 10, 10, 10, 10, 0, 0, 10, 0, 0, 10, 10, 10, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 10, 0, 0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 10, 0, 10, 10, 10, 10, 0],
[0, 0, 0, 0, 10, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 10, 10, 10, 10, 10, 10, 0],
[0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 10, 0, 0, 0, 0, 10, 10, 10, 10, 0],
[0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 10, 10, 10, 10, 0],
[0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0, 0, 10, 0, 0],
[0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0],
[0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 0, 10, 0, 0],
[0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 0, 10, 0, 0],
[0, 0, 0, 0, 10, 0, 0, 10, 10, 10, 10, 10, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 0, 10, 0, 0],
[0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 10, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 10, 0, 0],
[0, 0, 0, 0, 10, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 0, 10, 0, 0],
[0, 0, 0, 0, 10, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0],
[0, 0, 0, 0, 10, 0, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 0, 10, 0, 0],
[0, 0, 10, 10, 10, 10, 0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 10, 0, 0],
[0, 0, 10, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 10, 0, 0],
[0, 0, 10, 0, 0, 10, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0],
[0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 10, 0, 0, 0, 0],
[0, 0, 10, 10, 10, 10, 10, 10, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 10, 0, 0, 0, 0],
[0, 0, 10, 0, 0, 10, 10, 10, 0, 0, 10, 0, 0, 10, 0, 0, 0, 0, 10, 0, 0, 0, 0, 10, 0, 0, 0, 0],
[0, 0, 10, 0, 0, 10, 10, 10, 0, 0, 10, 0, 0, 10, 0, 0, 0, 0, 10, 0, 0, 10, 10, 10, 10, 10, 0, 0],
[0, 0, 10, 0, 0, 10, 10, 10, 10, 10, 10, 0, 10, 10, 10, 0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

dungeon_matrix3 = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 10, 10, 10, 0, 10, 10, 10, 0, 10, 10, 10, 0, 10, 10, 10, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 10, 10, 10, 10, 10, 10, 10, 0, 10, 10, 10, 0, 10, 10, 10, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 10, 10, 10, 0, 10, 10, 10, 0, 10, 10, 10, 0, 10, 10, 10, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 10, 10, 10, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0, 10, 0, 10, 10, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 10, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, 10, 0, 10, 10, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 10, 10, 10, 0, 10, 10, 10, 0, 10, 10, 10, 0, 10, 10, 10, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 10, 10, 10, 0, 10, 10, 10, 10, 10, 10, 10, 0, 10, 10, 10, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 10, 10, 10, 0, 10, 10, 10, 0, 10, 10, 10, 0, 10, 10, 10, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 10, 10, 10, 0, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 10, 10, 10, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 10, 10, 10, 0, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 10, 10, 10, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 10, 0, 0, 0],
[0, 0, 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 0],
[0, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 0],
[0, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

list_dungeons = [dungeon_matrix1, dungeon_matrix2, dungeon_matrix3]
list_goals_dun = [
    (3, 13),
    (2, 13),
    (19, 15)
]
list_starts_dun = [
    (26, 14),
    (26, 13),
    (25, 14)
]
start_node = (27, 24)
goal_nodes = [(32, 5), (17, 39), (1, 24)]
final_goal = (5, 6)#Objetivo final que só é adicionado no fim quando as 3 dungeons estiverem concluidas
dungeon_loc = [(32, 5), (17, 39), (1, 24)]#Obrigatoriamente deve manter a ordem de Dungeons 1,2,3

path, total_cost = a_star(terrain_costs, start_node, goal_nodes, final_goal, terrain_costs, dungeon_loc, list_dungeons, list_goals_dun, list_starts_dun)

if path:#Verifica se path está vazia
    print("Caminho encontrado:", path)
    visualize_path(terrain_costs, path, goal_nodes, dungeon_loc)
    print("Custo total do caminho:", total_cost)
else:
   print("Não foi possível encontrar um caminho.")

end_time = time.time()
execution_time = end_time - start_time
print(f"\033[94mTempo de execução: {execution_time} segundos\033[0m")

def main():
    color_map = {
        100: "#519548",#Verde escuro
        10: "#88C425",#Verde claro
        150: "#755C3B",#Marrom
        20: "#EFEBA9",#Areia
        180: "#69D2E7"#Azul
    }
    root = tk.Tk()
    root.title("MAPA PRINCIPAL")
    canvas = tk.Canvas(root, width=420, height=420, bg="white")
    canvas.pack()
    draw_map(canvas, terrain_costs, color_map)
    draw_special_points(canvas, [start_node], "#0F0892")#Cor no inicio
    draw_special_points(canvas, goal_nodes, "#FF8A00")#Cor de qualquer objetivo (menos dungeon e final)
    draw_special_points(canvas, [final_goal], "#710FE8")#Cor objetivo final
    draw_special_points(canvas, dungeon_loc, "#A30006")#Cor Dungeon
    draw_path(canvas, path, goal_nodes, start_node)
    draw_special_points(canvas, dungeon_loc, "#A30006")#Cor Dungeon

    root.mainloop()
if __name__ == "__main__":
    main()