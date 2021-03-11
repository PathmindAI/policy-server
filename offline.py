class EpisodeCache:
    t = 0
    episode = 1
    prev_action = None
    prev_reward = None
    prev_obs = None

    def is_empty(self):
        return self.prev_obs is None

    def store(self, t, prev_action, prev_reward, prev_obs):
        self.t = t
        self.prev_action = prev_action
        self.prev_reward = prev_reward
        self.prev_obs = prev_obs

    def reset(self):
        self.episode += 1
        self.t = 0
        self.prev_action = None
        self.prev_reward = None
        self.prev_obs = None
