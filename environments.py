import numpy as np
from numpy.random import randint 


class Cell:
    def __init__(self, x, y, color):
        self._x = x
        self._y = y
        self._color = color


class Environment:
    def __init__(self, size):
        self._size = size
        self._action_space = self.init_action_space(size)
        self._start_pos, self._exit_pos = self.init_positions()
        self.state = self._start_pos

    @property
    def action_space(self):
        return self._action_space
    
    @property
    def start_pos(self):
        return self._start_pos
    
    @property
    def exit_pos(self):
        return self._exit_pos
    
    def update_state(self, action):
        """
        
        Inputs:
        - action (int): number in range(0, num_actions)

        Returns:
        - next_state (tuple): agent's position after action
        """
        pass

    def get_state(self):
        return self.state

    @staticmethod
    def init_action_space(shape, complexity=.5, density=.5):
        # Only ODD shapes
        # Adjust complexity and density relative to action_space size
        complexity = int(complexity*(5*(shape[0]+shape[1])))
        density = int(density*(shape[0]//2*shape[1]//2))
        # Build actual action_space
        env = np.zeros(shape, dtype=bool)+255
        # Fill borders
        env[0, :] = env[-1, :] = 0
        env[:, 0] = env[:, -1] = 0
        # Make isles
        for i in range(density):
            x, y = randint(0, shape[1]//2)*2, randint(0, shape[0]//2)*2
            env[y, x] = 1
            for j in range(complexity):
                neighbours = []
                if x > 1:           
                    neighbours.append((y, x-2))
                if x < shape[1]-2:  
                    neighbours.append((y, x+2))
                if y > 1:           
                    neighbours.append((y-2, x))
                if y < shape[0]-2:  
                    neighbours.append((y+2, x))
                if len(neighbours):
                    y_, x_ = neighbours[randint(0, len(neighbours)-1)]
                    if env[y_, x_] == 255:
                        env[y_, x_] = 0
                        env[y_+(y-y_)//2, x_+(x-x_)//2] = 0
                        x, y = x_, y_
        return env.astype('int')

    def render(self, ax=None):
        if ax is None:
            return
        ax.imshow(self.action_space, interpolation='nearest', aspect='auto')
        ax.set_title('Environment')

    def plot_optimal_path(self, q_table, ax):
        opt_path = np.copy(self.action_space)
        for k, v in q_table.items():
            if k is None:
                continue
            opt_path[k] = (opt_path[k] * 5*v.max())
        opt_path[self.exit_pos] = 255
        
        ax.imshow(opt_path, interpolation='nearest', aspect='auto')
        ax.set_title('Learned path')
        
    def init_positions(self):
        indices = np.array(np.argwhere(self.action_space == 255))
        agent_pos = tuple(indices[np.random.randint(0, len(indices))])
        print('Agent pos: ', agent_pos)
        remote_idxs = [a for a in indices if abs(a[0]-agent_pos[0])+abs(a[1]-agent_pos[1]) >= 3]
        exit_pos = tuple(remote_idxs[np.random.randint(0, len(remote_idxs))])
        print('Exit pos: ', exit_pos)
        self.action_space[agent_pos] = 50
        self.action_space[exit_pos] = 225
        return agent_pos, exit_pos

    def step(self, state, action):
        """
            Returns tuple (next_state, reward, done)

            ###################
            #                 #
            #       0         #
            #       /\        #
            #       ||        #
            #   3 <= A => 1   #
            #       ||        #
            #       \/        #
            #       2         #
            ###################
        """
        done = False
        next_state = tuple()
        reward = 0
        if action == 0:
            next_state = state[0]-1, state[1]
        if action == 1:
            next_state = state[0], state[1]+1
        if action == 2:
            next_state = state[0]+1, state[1]
        if action == 3:
            next_state = state[0], state[1]-1

        if self.action_space[next_state] == 0 or \
           self.action_space[next_state] == 1:
            reward = -5
            next_state = state
        elif self.action_space[next_state] == 255 or \
            self.action_space[next_state] == 128 or \
                self.action_space[next_state] == 50:
            reward = -1
        elif next_state == self.exit_pos:
            reward = 10
            done = True

        return next_state, reward, done, {}

    def reset(self):
        return self._start_pos

