import subprocess
import shutil
import json
import re
import polars as pl
from .statics import kolumns

# https://peps.python.org/pep-0661/
_DEFAULT_TO_CONFIGURATION = object()

Class Query:

	def __init__(self, configuration, naylib):
		if configuration is None:
			raise ValueError("No configuration was passed to Query class. Ranchero is designed to be initialized with a configuration.")
		else:
			self.cfg = configuration
			self.logging = self.cfg.logger
			self.NeighLib = naylib

	def _default_fallback(self, cfg_var, value):
		if value == _DEFAULT_TO_CONFIGURATION:
			return self.cfg.get_config(cfg_var)
		return value

	def gcloud_storage_objects_describe(uri: str, gs_metadata=_DEFAULT_TO_CONFIGURATION):
		"""
		Requires gcloud is on the path and, if necessary, authenticated.
		"""
		return_fields = self._default_fallback("gs_metadata", gs_metadata)
		if shutil.which("gcloud") is None:
			self.logging.error("Couldn't find gcloud on $PATH")
			exit(1)
		assert type(uri) == str
		cmd = ["gcloud", "storage", "objects", "describe", obj, "--format", "json"]
		result = subprocess.run(cmd, capture_output=True, text=True, check=True)
		meta = json.loads(result.stdout)
		print(meta)
		print(type(meta))
		exit(1)

		return {
			"uri": uri,
			"created": meta.get("timeCreated"),
			"md5": meta.get("md5Hash"),
			"size": int(meta.get("size", 0)),
		}