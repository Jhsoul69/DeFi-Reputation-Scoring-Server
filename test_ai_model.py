# test_ai_model.py
import pytest
from app.ai_model import AIModel
import pandas as pd
import numpy as np

# A sample mock DataFrame for testing
SAMPLE_DF = pd.DataFrame([
    {'action': 'swap', 'timestamp': 1672531200},
    {'action': 'swap', 'timestamp': 1672617600},
    {'action': 'add_liquidity', 'timestamp': 1672704000},
    {'action': 'swap', 'timestamp': 1672790400},
    {'action': 'add_liquidity', 'timestamp': 1672876800},
    {'action': 'swap', 'timestamp': 1672963200},
    {'action': 'add_liquidity', 'timestamp': 1673049600},
    {'action': 'swap', 'timestamp': 1673136000},
    {'action': 'add_liquidity', 'timestamp': 1673222400},
    {'action': 'swap', 'timestamp': 1673308800},
])

@pytest.fixture
def ai_model_instance():
    return AIModel()

def test_calculate_active_days(ai_model_instance):
    """Test that active days are calculated correctly."""
    active_days = ai_model_instance._calculate_active_days(SAMPLE_DF)
    assert active_days == 9

def test_process_dex_transactions_with_data(ai_model_instance):
    """Test that LP and Swap scores are calculated with valid data."""
    lp_score, swap_score, user_tags = ai_model_instance._process_dex_transactions(SAMPLE_DF)
    
    # Check if scores are non-zero when data exists
    assert lp_score > 0
    assert swap_score > 0
    
    # Check for correct user tags based on mock data
    assert "consistent_lp" in user_tags
    assert "consistent_trader" in user_tags

def test_calculate_score_with_full_data(ai_model_instance):
    """Test the main calculate_score method with a complete wallet data structure."""
    wallet_data = {
        "wallet_address": "0x123",
        "data": [{"protocolType": "dexes", "transactions": SAMPLE_DF.to_dict('records')}]
    }
    
    final_score, features = ai_model_instance.calculate_score(wallet_data)
    
    assert final_score > 0
    assert features["lp_score"] > 0
    assert features["swap_score"] > 0
    assert "consistent_lp" in features["user_tags"]
    assert "consistent_trader" in features["user_tags"]

def test_calculate_score_with_no_dex_data(ai_model_instance):
    """Test graceful handling when no DEX data is provided."""
    wallet_data = {
        "wallet_address": "0x456",
        "data": [{"protocolType": "lending", "transactions": []}]
    }
    final_score, features = ai_model_instance.calculate_score(wallet_data)
    assert final_score == 0.0
    assert features == {}

def test_calculate_score_with_empty_transactions(ai_model_instance):
    """Test graceful handling with empty transactions list."""
    wallet_data = {
        "wallet_address": "0x789",
        "data": [{"protocolType": "dexes", "transactions": []}]
    }
    final_score, features = ai_model_instance.calculate_score(wallet_data)
    assert final_score == 0.0
    assert "inactive" in features.get("user_tags", [])
