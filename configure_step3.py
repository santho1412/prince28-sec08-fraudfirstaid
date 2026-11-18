from pathlib import Path

config = """

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
filterwarnings = ["ignore:Using `httpx` with `starlette.testclient`"]
"""

path = Path("pyproject.toml")
content = path.read_text(encoding="utf-8")

if "[tool.ruff]" in content or "[tool.pytest.ini_options]" in content:
    raise SystemExit(
        "A configuration section already exists. Check pyproject.toml before adding anything."
    )

path.write_text(content.rstrip() + "\n" + config, encoding="utf-8")

print("Ruff and Pytest configuration added successfully!")
