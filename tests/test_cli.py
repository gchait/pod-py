from click.testing import CliRunner

from pod_py.cli import cli


def test_cli_dummy():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit." in result.output
