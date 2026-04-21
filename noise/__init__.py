"""
Noise mechanisms for trust game experiments.

This module provides:
- TrustGameNoisy: Trust game with configurable noise and asymmetric naming
- PublicGoodsGame: N-player simultaneous contribution game
- experiments_noisy.yaml: Configuration for noise experiments
- run_noisy_batch.py: Batch runner for noise experiments
"""

from noise.trust_game_noisy import TrustGameNoisy, OTHER_PLAYER_NAMES
from noise.public_goods_game import PublicGoodsGame

__all__ = ['TrustGameNoisy', 'OTHER_PLAYER_NAMES', 'PublicGoodsGame']
