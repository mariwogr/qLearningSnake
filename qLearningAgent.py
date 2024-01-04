import random
import numpy as np
from snake_game_rl import SnakeGameRL, Point
from helper import plot

class QLearningAgent:
    def __init__(self):
        """
        Sets options, which can be passed in via the Pacman command line using -a alpha=0.5,...
        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - counter of episodes
        
        And initializes Qvalues
        """

        # DISCOMENT WHEN NOT TRAINING
        self.alpha = float(0.)
        self.epsilon = float(0.)

        # DISCOMENT WHEN TRAINING
        # self.alpha = float(0.6)
        # self.epsilon = float(0.3)


        self.discount = float(0.8)
        self.numTraining = int(0)

        # 0: left, 1: right, 2: down, 3: up
        self.actions = [0, 1, 2, 3]

        # qtables for each agent
        self.table_file = open("qtable.txt", "r+")
        self.q_table = self.read_q_table()

    def read_q_table(self):
        "Read qtable from disc"
        table = self.table_file.readlines()
        q_table = []

        for i, line in enumerate(table):
            row = line.split()
            row = [float(x) for x in row]
            q_table.append(row)

        return q_table
    
    def write_q_table(self):
        "Write qtable to disc"
        self.table_file.seek(0)
        self.table_file.truncate()
        for line in self.q_table:
            for item in line:
                self.table_file.write(str(item)+" ")
            self.table_file.write("\n")
    
    def get_state(self, game):

        direction = game.direction

        food_h = 0
        food_v = 0 

        food_h_dif = game.food.x - game.head.x
        food_v_dif = game.food.y - game.head.y

        # Right
        if food_h_dif > 0:
            food_h = 0
        
        # Left
        elif food_h_dif < 0:
            food_h = 1
        
        # Horizontally forward
        else:
            food_h = 2    

        # Down
        if food_v_dif > 0:
            food_v = 0
        
        # Up
        elif food_v_dif < 0:
            food_v = 1
        
        # Vertically forward
        else:
            food_v = 2    

        collision = game.danger()

        wall_x, wall_y = game.is_there_a_wall()

        state = [

            food_h,
            food_v,

            direction,

            collision[0],
            collision[1],
            collision[2],

            # DISCOMENT FOR AGENT1
            wall_x,
            wall_y
            ]

        return np.array(state, dtype=int)
    
    def compute_position(self, game):
        """
        Compute the row of the qtable for a given state.
        For instance, the state (3,1) is the row 7
        """

        q_state = self.get_state(game)

        # It will be computing the position with the possible values of each attribute

        # AGENT1
        #return q_state[0]*32*3+q_state[1]*32+q_state[2]*4+q_state[3]*2+q_state[4]*1

        # AGENT2
        return q_state[0]*128*3+q_state[1]*128+q_state[2]*32+q_state[3]*16+q_state[4]*8+q_state[5]*4+q_state[6]*2+q_state[7]*1

    def get_q_value(self, game, action):

        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        
        position = self.compute_position(game)

        return self.q_table[position][action]

    def get_action(self, game):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """

        legalActions = []
        
        direction = game.direction

        if direction == 0:
            legalActions = [0,2,3]
        elif direction == 1:
            legalActions = [1,2,3]
        elif direction == 2:
            legalActions = [0,1,2]
        else:
            legalActions = [0,1,3]

        flip = random.random() < self.epsilon

        if flip:
            random_move = random.choice(legalActions)
            return random_move
        
        best_actions = [legalActions[0]]
        best_value = self.get_q_value(game, legalActions[0])
        for action in legalActions:
            value = self.get_q_value(game, action)
            if value == best_value and action not in best_actions:
                best_actions.append(action)
            if value > best_value:
                best_actions = [action]
                best_value = value
        return random.choice(best_actions)

    def computeActionFromQValues(self, game):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """

        legalActions = []
        
        direction = game.direction

        if direction == 0:
            legalActions = [0,2,3]
        elif direction == 1:
            legalActions = [1,2,3]
        elif direction == 2:
            legalActions = [0,1,2]
        else:
            legalActions = [0,1,3]

        best_actions = [legalActions[0]]
        best_value = self.get_q_value(game, legalActions[0])
        for action in legalActions:
            value = self.get_q_value(game, action)
            if value == best_value and action not in best_actions:
                best_actions.append(action)
            if value > best_value:
                best_actions = [action]
                best_value = value

        return best_value

    def learn(self, game):

        # Obtain the action and position of the game
        action = self.get_action(game)
        position = self.compute_position(game)

        q_value = self.get_q_value(game, action)

        # Play a step of the game
        reward, end, score = game.play_step(action)
        
        # Obtain the next q max value
        max_q_next = self.computeActionFromQValues(game)

        # Update the Q value of the state
        self.q_table[position][action] = (1 - self.alpha) * q_value + self.alpha * (reward + self.discount * max_q_next)
        self.write_q_table()

        return [end, score]

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0

    agent = QLearningAgent()
    game = SnakeGameRL()

    episodes = 10

    while agent.numTraining < episodes:

        end, score = agent.learn(game)

        if end:
            game.reset()
            agent.numTraining += 1
            
            if score > record:
                record = score

            print("Game: ", agent.numTraining, ", Score: ", score, ", Record: ", record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.numTraining
            plot_mean_scores.append(mean_score)
            fig = plot(plot_scores, plot_mean_scores)
    fig.savefig('plot_1152_50000.png')

if __name__ == '__main__':
    train()