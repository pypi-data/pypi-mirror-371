from __future__ import annotations

import contextlib
import logging
import os
from typing import Dict, List

from . import api
from .converters import apply_converter, load_converter
from .mappers import apply_mapper

_logger = logging.getLogger(__name__)


def env_to_dict(extra_env: Dict[str, str] = None) -> api.OdooCliFlag:
    """
    Convert [environnement variables][os.environ] to a dict, with odoo compatible args, by applying a mapper and
     converter.
    Args:
        extra_env: A dict to update environnement variables
    Returns:
        A dict with converted environnement variables
    """
    return apply_converter(api.Env({**os.environ, **(extra_env or {})}).apply_mapper())


def env_to_odoo_args(extra_env: Dict[str, str] = None) -> List[str]:
    """
    Entrypoint of this library
    Convert [environnement variable][os.environ] to a odoo args valid.
    See Also
         The env to args [converter][odoo_env_config.api.EnvConfigSection]
         The speccific cloud [env mapper][odoo_env_config.mappers]
    Examples
         >>> import odoo
         >>> odoo.tools.config.parse_args(env_to_odoo_args())
         >>> odoo.tools.config.save()
    Returns:
         A list with args created from Env
    """
    curr_env = api.Env(os.environ)
    curr_env.update(extra_env or {})
    curr_env = apply_mapper(env=curr_env)
    store_values = apply_converter(curr_env)
    return api.dict_to_odoo_args(store_values)


def env_to_config(config: api.OdooConfig, extra_env: Dict[str, str] = None) -> None:
    curr_env = api.Env(os.environ)
    curr_env.update(extra_env or {})
    curr_env = apply_mapper(env=curr_env)
    for c in load_converter():
        with contextlib.suppress(NotImplementedError):
            c().init(curr_env).write_to_config(config)


def _reset_odoo_tools(odoo_module):
    odoo_module.tools.config.casts = {}
    odoo_module.tools.config.misc = {}
    odoo_module.tools.config.options = {}
    odoo_module.tools.config.config_file = None
    # Copy all optparse options (i.e. MyOption) into self.options.
    for group in odoo_module.tools.config.parser.option_groups:
        for option in group.option_list:
            if option.dest not in odoo_module.tools.config.options:
                odoo_module.tools.config.options[option.dest] = option.my_default
                odoo_module.tools.config.casts[option.dest] = option

    # generate default config
    odoo_module.tools.config._parse_config()


def direct_run_command(
    odoo_args: List[str],
    config_dest: str,
    other_env: api.Env = None,
):
    """
    Entrypoint of the command

    1. First we parse `args`
    2. Then we load `--profiles` if some are provided
    3. And finaly we execute [odoo_env_config][odoo_env_config.entry.env_to_odoo_args] and save it to the dest file

    Args:
        odoo_module: The Odoo module imported
        force_odoo_args: Other args to pass to odoo_module config
        config_dest: The dest file to store the config generated
        other_env: The environment where the config is extracted
    """
    import odoo as odoo_module

    with contextlib.suppress(Exception):
        odoo_module.netsvc.init_logger()

    _reset_odoo_tools(odoo_module)
    odoo_module.tools.config.config_file = config_dest

    print(other_env)
    env_args = env_to_odoo_args(other_env)
    _logger.info("exec Odoo with args: %s", env_args)
    odoo_module.tools.config._parse_config(env_args)
    _logger.info("exec Odoo with args: %s", odoo_args)
    odoo_module.tools.config._parse_config(odoo_args)
    env_to_config(odoo_module.tools.config, other_env)
    odoo_module.tools.config.save()
