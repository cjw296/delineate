from importlib.metadata import version

from click.testing import CliRunner

from delineate.main import cli

expected_version = version('delineate')


class TestVersion:
    def test_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ['version'])
        assert result.exit_code == 0
        assert result.output.strip() == expected_version

    def test_version_with_log_level(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ['--log-level', 'DEBUG', 'version'])
        assert result.exit_code == 0
        assert result.output.strip() == expected_version
