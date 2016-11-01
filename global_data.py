from flask import Flask
import os
import git_commands

app = Flask(__name__)
app.config.from_object("config")

ROOT = os.path.dirname(os.path.realpath(__file__))
git = git_commands.Repository(ROOT + "/repository", app.config["MASTER"])


