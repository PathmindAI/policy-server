import os
import shutil
import fire
import config
import subprocess


class CLI:
    """Simple wrapper class to expose to "fire" to auto-generate a command line
    interface for this project.
    """

    @staticmethod
    def schema(schema_file, title="Pathmind Policy Server", version=config.API_VERSION,
               template_file=config.SWAGGER_TEMPLATE, out_file=config.SWAGGER_FILE):
        with open(template_file, 'r') as template:
            template_str = template.read()
        with open(schema_file, 'r') as schema:
            schema_lines = schema.readlines()
        template_str = template_str.replace("{{title}}", title)
        template_str = template_str.replace("{{version}}", f"\"{version}\"")

        template_str = template_str.replace("{{prediction}}", config.get_prediction_schema())

        # Increase indentation by one level
        schema_lines = [f'  {line}' for line in schema_lines]
        observation = "".join(schema_lines)
        template_str = template_str.replace("{{observation}}", observation)
        if os.path.exists(out_file):
            os.remove(out_file)
        with open(out_file, 'w') as out:
            out.write(template_str)
        # When creating a new schema, regenerate clients as well.
        CLI.clients()

    @staticmethod
    def clients():
        shutil.rmtree("clients")
        os.makedirs("clients")
        generate_client_for("python")
        generate_client_for("java")
        generate_client_for("scala")
        generate_client_for("r")

    @staticmethod
    def clean():
        save_remove(config.OUTPUT_MAPPER_FILE)
        save_remove(config.PREPROCESSOR_FILE)
        save_remove(config.SCHEMA_FILE)
        save_remove(config.SWAGGER_FILE)
        shutil.rmtree(config.MODEL_FOLDER)
        os.makedirs(config.MODEL_FOLDER)


def save_remove(file_name):
    """Pythonic remove-if-exists."""
    try:
        os.remove(file_name)
    except OSError:
        pass


def generate_client_for(lang):
    os.makedirs(f"./clients/{lang}")
    subprocess.run(["swagger-codegen", "generate", "-i", config.SWAGGER_FILE, "-l", lang, "-o", f"clients/{lang}"])


if __name__ == '__main__':
    fire.Fire(CLI)
