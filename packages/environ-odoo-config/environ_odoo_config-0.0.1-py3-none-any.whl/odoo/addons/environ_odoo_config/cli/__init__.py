from environ_odoo_config import cli, entry
from odoo.cli import Command


def _exec(args):
    """
    Entrypoint of the command

    1. First we parse `args`
    2. Then we load `--profiles` if some are provided
    3. And finaly we execute [odoo_env_config][odoo_env_config.entry.env_to_odoo_args] and save it to the dest file

    Args:
        args: the args provided by Odoo
    """
    ns, sub_args = cli.get_odoo_cmd_parser().parse_known_args(args)
    # Removing blank sub_args
    # Is called with "$ENV_VAR" but ENV_VAR isn't set, then `sub_args` contains `['']
    # So we remove empty string from it
    sub_args = [s for s in sub_args if s.split()]
    entry.direct_run_command(sub_args, ns.config_dest)


class EnvConfig(Command):
    """
    This contains a new OdooCommand named `envconfig`
    This class prupose is to use it inside an Odoo modules
    This command use `environ_odoo_config` to convert the [os.environ][os.environ] to a valid Odoo config
    Args:
        --dest str: The path where we store the result odoo config file.
    Examples:
        >>> /odoo-bin envconfig
    """

    def run(self, args):
        return _exec(args)


class Oenv2config(Command):
    """
    This contains a new OdooCommand named `env2config`
    This class prupose is to use it inside an Odoo modules
    This command use `environ_odoo_config` to convert the [os.environ][os.environ] to a valid Odoo config
    Args:
        --dest str: The path where we store the result odoo config file.
    Examples:
        >>> /odoo-bin env2config
    """

    def run(self, args):
        return _exec(args)
