import os
import shutil
import fire
import config
import subprocess
from utils import safe_remove, unzip

class CLI:
    """Simple wrapper class to expose to "fire" to auto-generate a command line
    interface for this project.
    """

    @staticmethod
    def clients():
        try:
            shutil.rmtree("clients")
        except:
            pass
        os.makedirs("clients")
        generate_client_for("python")
        generate_client_for("java")
        generate_client_for("scala")
        #generate_client_for("r")

    @staticmethod
    def copy_server_files(path):
        shutil.copyfile(os.path.join(path, "saved_model.zip"), config.PATHMIND_POLICY)
        shutil.copyfile(os.path.join(path, "schema.yaml"), config.PATHMIND_SCHEMA)
        unzip(config.PATHMIND_POLICY)

    @staticmethod
    def unzip():
        unzip(config.PATHMIND_POLICY)

    @staticmethod
    def clean():
        safe_remove(config.PATHMIND_POLICY)
        safe_remove(config.PATHMIND_SCHEMA)
        safe_remove(config.LOCAL_SWAGGER)
        safe_remove(config.CLIENTS_ZIP)
        shutil.rmtree(config.MODEL_FOLDER)
        os.makedirs(config.MODEL_FOLDER)


def generate_client_for(lang):
    os.makedirs(f"./clients/{lang}")
    subprocess.run(["swagger-codegen", "generate", "-i", config.SWAGGER_FILE, "-l", lang, "-o", f"clients/{lang}"])


if __name__ == '__main__':
    fire.Fire(CLI)
