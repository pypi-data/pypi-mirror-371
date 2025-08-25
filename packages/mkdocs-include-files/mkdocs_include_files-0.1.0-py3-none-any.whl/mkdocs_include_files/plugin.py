from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.plugins import BasePlugin
from mkdocs.plugins import get_plugin_logger

import os
import fnmatch
import shutil

log = get_plugin_logger(__name__)

class IncludeFilesPluginConfig(Config):
    temp_location = config_options.Type(str, default='includes')
    search_syntax = config_options.Type(str, default='.')
    search_paths = config_options.Type(str, default='.')

class IncludeFilesPlugin(BasePlugin[IncludeFilesPluginConfig]):
    
    def on_pre_build(self, config):
        "runs before files are loaded so its a good time to copy the include files over"

        # get directory containing mkdocs.yml
        mkdocs_yml_dir = os.path.dirname(config.config_file_path)

        # get path to include directory
        include_dir = os.path.join(config.docs_dir, config.plugins['include-files'].config.temp_location)

        # get path to search directory
        search_dir = os.path.join(mkdocs_yml_dir, config.plugins['include-files'].config.search_paths)

        # search the search path for files that match the search syntax
        for root, dirs, files in os.walk(search_dir):
            for filename in fnmatch.filter(files, config.plugins['include-files'].config.search_syntax):
                # copy file to include dir
                src = os.path.join(root, filename)
                dst = os.path.join(include_dir, filename)
                log.info(f"Copying {src} to {dst}")
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
