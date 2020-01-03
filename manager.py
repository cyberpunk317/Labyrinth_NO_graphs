from SimpleAgents import Agent
import sys
import numpy as np
import matplotlib.pyplot as plt
import pprint
import seaborn as sns
import pandas as pd
from Trainers import *
from abc import ABC, abstractmethod
pp = pprint.PrettyPrinter(indent=4)


class AbstractProductA(ABC):
    @abstractmethod
    def useful_function_a(self) -> str:
        pass


class AbstractProductB(ABC):
    @abstractmethod
    def useful_function_b(self) -> None:
        pass

    @abstractmethod
    def another_useful_function_b(self, collaborator: AbstractProductA) -> None:
        pass


class AbstractFactory(ABC):

    @abstractmethod
    def create_trainer_std(self, env, agent, epochs) -> AbstractProductA:
        pass

    @abstractmethod
    def create_trainer_dqn(self, env, agent, epochs) -> AbstractProductB:
        pass


class ConcreteFactoryCustom(AbstractFactory):
    def create_trainer_std(self, env, agent, epochs) -> CustomTrainerStd:
        return CustomTrainerStd(env, agent, epochs)

    def create_trainer_dqn(self, env, agent, epochs) -> CustomTrainerDQN:
        return CustomTrainerDQN(env, agent, epochs)


class ConcreteFactoryGym(AbstractFactory):
    def create_trainer_std(self, env, agent, epochs) -> GymTrainerStd:
        return GymTrainerStd(env, agent, epochs)

    def create_trainer_dqn(self, env, agent, epochs) -> GymTrainerDQN:
        return GymTrainerDQN(env, agent, epochs)


class Manager:
    __instance = None
    
    def __init__(self, env_size, strategy, num_episodes, num_actions):
        if not Manager.__instance:
            self._num_episodes = num_episodes
            self._env = self.init_env(env_size)
            self._agent = self.init_agent(strategy, num_actions)
            self._history = []
        else:
            print("Instance already created:", self.get_instance(strategy, env_size, num_episodes, num_actions))

    @classmethod
    def get_instance(cls, env_size, strategy, num_episodes, num_actions):
        if not cls.__instance:
            cls.__instance = Manager(env_size, strategy, num_episodes, num_actions)
        return cls.__instance

    def init_agent(self, strategy, num_actions):
        agent = Agent(strategy, num_actions)
        return agent

    def init_env(self, env_size):
        env = Environment(env_size)
        return env

    @staticmethod
    def run(strategy_type, factory, env, agent, epochs):
        if strategy_type == 'std':
            trainer = factory.create_trainer_std(env, agent, epochs)
        else:
            trainer = factory.create_trainer_dqn(env, agent, epochs)
        return trainer

    def start_learning(self, plot_every=100):
        pass
        
    def display_current_policy(self, parameter_list):
        pass


def main(strategy, epochs, env, env_size=(10, 10), n_actions=4, seed=42):

    if env == 'Custom':
        factory = ConcreteFactoryCustom()
        if 'Sarsa' in strategy:
            manager = Manager.get_instance(env_size, strategy, epochs, 4)
            strategy_type = 'std'
            cts = manager.run(strategy_type, factory, manager._env, manager._agent, epochs)
            Q = cts.train()
            print('Resulting table of (state, action) value-pairs: ')
            pp.pprint(Q)
            df = pd.DataFrame.from_dict(Q)

            plt.plot(np.linspace(0, cts.n_episodes, len(cts._history), endpoint=False),
                     np.asarray(cts._history))
            plt.xlabel('Episode Number')
            plt.ylabel('Average Reward (Over Next %d Episodes)' % 300)
            fig = plt.figure(figsize=(11, 6))
            ax1 = fig.add_subplot(2, 2, 1)
            ax2 = fig.add_subplot(2, 2, 2)
            ax3 = fig.add_subplot(3, 1, 3)
            cts.env.display_env(ax1)
            cts.env.plot_optimal_path(Q, ax2)
            ax3.set_title('Learned Q-table')
            sns.heatmap(df, cmap='coolwarm',  annot=False, fmt='g', ax=ax3)

            plt.show()
        else:
            strategy_type = 'dqn'
            torch.cuda.current_device()
            agent = AdvAgents.DQNAgent(state_size=len(env_size), action_size=n_actions, seed=seed)
            env = Environment(env_size)
            ct = Manager.run(strategy_type, factory, env, agent, epochs)
            scores = ct.train()
            fgr = plt.figure()
            ax = plt.subplot(111)
            plt.plot(np.arange(len(scores)), scores)
            plt.xlabel('Episodes')
            plt.ylabel('Scores')
            plt.show()
    else:
        factory = ConcreteFactoryGym()
        if 'Sarsa' in strategy:
            manager = Manager.get_instance(env_size, strategy, epochs, 4)
            strategy_type = 'std'
            env = gym.make('maze-random-5x5-v0')
            gt = manager.run(strategy_type, factory, env, manager._agent, epochs)
        else:
            strategy_type = 'dqn'
            torch.cuda.current_device()
            agent = AdvAgents.DQNAgent(state_size=len(env_size), action_size=n_actions, seed=seed)
            env = Environment(env_size)
            gt = Manager.run(strategy_type, factory, env, agent, epochs)
            # gt = GymTrainerDQN(env, agent, epochs)
        Q = gt.train()
        print('Resulting table of (state, action) value-pairs: ')
        pp.pprint(Q)
        df = pd.DataFrame.from_dict(Q)

        plt.plot(np.linspace(0, gt.n_episodes, len(gt._history), endpoint=False),
                 np.asarray(gt._history))
        plt.xlabel('Episode Number')
        plt.ylabel('Average Reward (Over Next %d Episodes)' % 300)
        fig = plt.figure(figsize=(11, 6))
        ax1 = fig.add_subplot(2, 2, 1)
        ax2 = fig.add_subplot(2, 2, 2)
        ax3 = fig.add_subplot(3, 1, 3)
        ax1 = gt.env.render()
        ax3.set_title('Learned Q-table')
        sns.heatmap(df, cmap='coolwarm', annot=False, fmt='g', ax=ax3)

        plt.show()


