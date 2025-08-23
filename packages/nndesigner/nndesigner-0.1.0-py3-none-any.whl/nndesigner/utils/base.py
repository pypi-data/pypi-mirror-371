from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from omegaconf import OmegaConf
import torch
import nndesigner
import os

DEFAULT_CONFIG_DIR = os.path.join(os.path.dirname(nndesigner.__file__), "config")
DEFAULT_NODE_GROUP_CONFIG_PATH = os.path.join(DEFAULT_CONFIG_DIR, "system/node_groups.json")