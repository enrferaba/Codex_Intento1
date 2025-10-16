from core import config


def test_load_settings(tmp_path):
    file = tmp_path / "cfg.toml"
    file.write_text("[section]\nvalue=1\n")
    data = config.load(str(file))
    assert data["section"]["value"] == 1
