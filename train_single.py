import wandb

wandb.init(project="hr_adaptation", sync_tensorboard=True)
import os
import shutil
import argparse
import gin
import gym
import numpy as np
from single_agent_env import make_single_env
from stable_baselines import PPO2
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import SubprocVecEnv
from stable_baselines.common.vec_env.vec_normalize import VecNormalize

PPO2 = gin.external_configurable(PPO2)
VecNormalize = gin.external_configurable(VecNormalize)


@gin.configurable
def train(logdir, num_envs=1, experiment_name=gin.REQUIRED, timesteps=gin.REQUIRED):
    env = VecNormalize(SubprocVecEnv(num_envs * [make_single_env]))
    model = PPO2(MlpPolicy, env, verbose=1, tensorboard_log=logdir)
    model.learn(total_timesteps=timesteps)
    if os.path.exists(experiment_name):
        shutil.rmtree(experiment_name)
    os.makedirs(experiment_name)
    model.save(os.path.join(experiment_name, "model"))
    env.save_running_average(experiment_name)
    wandb.save(os.path.join(experiment_name, "*.pkl"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=str)
    parser.add_argument("--logdir", type=str, default="/tmp/driving")
    args = parser.parse_args()
    gin.parse_config_file(args.config)
    wandb.save(args.config)
    train(args.logdir)
