from dataset_forge.menus import session_state


def test_user_preferences_update():
    """Test updating and reading user_preferences in session_state."""
    orig = session_state.user_preferences.get("play_audio")
    session_state.user_preferences["play_audio"] = False
    assert session_state.user_preferences["play_audio"] is False
    session_state.user_preferences["play_audio"] = orig


def test_parallel_config_update():
    """Test updating and reading parallel_config in session_state."""
    orig = session_state.parallel_config.get("max_workers")
    session_state.parallel_config["max_workers"] = 7
    assert session_state.parallel_config["max_workers"] == 7
    session_state.parallel_config["max_workers"] = orig
