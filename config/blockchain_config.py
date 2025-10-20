"""Blockchain configuration settings."""


class BlockchainConfig:
    """Blockchain parameters configuration."""
    
    ADJUST_DIFFICULTY_IN_EVERY = 10  # In Blocks
    INIT_DIFFICULTY = 1
    BLOCK_TIME_IN_EVERY = 30  # In Seconds
    MINING_REWARDS = 10.0
    MAX_TRANSACTIONS_IN_BLOCK = 32