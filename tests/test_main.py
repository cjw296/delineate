from click.testing import CliRunner

from delineate.main import cli


class TestVersion:

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['version'])
        assert result.exit_code == 0
        assert result.output.strip() == '0.0.0'

    def test_version_with_log_level(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--log-level', 'DEBUG', 'version'])
        assert result.exit_code == 0
        assert result.output.strip() == '0.0.0'
