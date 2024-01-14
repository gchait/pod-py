from click.testing import CliRunner

from pod_py.cli import existing_pod, new_pod


def test_new_pod_help():
    runner = CliRunner()
    result = runner.invoke(new_pod, ["--help"])
    assert result.exit_code == 0
    assert "Deploy a Pod" in result.output


def test_existing_pod_help():
    runner = CliRunner()
    result = runner.invoke(existing_pod, ["--help"])
    assert result.exit_code == 0
    assert "Execute a Bash command" in result.output
