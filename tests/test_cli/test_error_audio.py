import pytest
from dataset_forge.utils import printing
from dataset_forge.utils.printing import print_error


def test_error_triggers_audio(monkeypatch):
    called = {}

    def fake_play_error_sound(*args, **kwargs):
        called['yes'] = True

    monkeypatch.setattr(printing, "play_error_sound", fake_play_error_sound)
    print_error("This is a test error")
    assert called.get('yes')
