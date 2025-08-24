import os
import json

try:
    import yaml
except ImportError:
    yaml = None

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import toml
    except ImportError:
        toml = None
        tomllib = None

import configparser
import xml.etree.ElementTree as ET

def generate_schema(env_file=".env", schema_file="schema.json"):
    schema = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            schema[key] = {"required": True, "default": value}
    with open(schema_file, "w") as f:
        json.dump(schema, f, indent=2)
    print(f"Schema saved to {schema_file}")

# def validate_schema(schema_file="schema.json", env_file=".env"):
#     with open(schema_file) as f:
#         schema = json.load(f)
#     with open(env_file) as f:
#         env_vars = dict(line.strip().split("=", 1) for line in f if "=" in line and not line.startswith("#"))
#     missing = [key for key, props in schema.items() if props.get("required") and key not in env_vars]
#     if missing:
#         print(f"Missing variables: {', '.join(missing)}")
#     else:
#         print("All required variables are present")

def load_schema(schema_file):
    ext = os.path.splitext(schema_file)[1].lower()

    with open(schema_file, "rb") as f:
        if ext in (".json", ""):
            return json.load(f)

        elif ext in (".yaml", ".yml"):
            if not yaml:
                raise ImportError("PyYAML not installed. Install with `pip install pyyaml`.")
            return yaml.safe_load(f)

        elif ext in (".toml",):
            if tomllib:
                return tomllib.load(f)
            elif toml:
                return toml.load(f)
            else:
                raise ImportError("No TOML parser available. Install `toml` or use Python 3.11+.")

        elif ext in (".ini",):
            config = configparser.ConfigParser()
            config.read_file(f)
            # Convert ConfigParser to a dict
            return {section: dict(config[section]) for section in config.sections()}

        elif ext in (".xml",):
            tree = ET.parse(f)
            root = tree.getroot()

            def xml_to_dict(element):
                return {
                    "tag": element.tag,
                    "attributes": element.attrib,
                    "text": element.text.strip() if element.text else None,
                    "children": [xml_to_dict(e) for e in element]
                }

            return xml_to_dict(root)

        else:
            raise ValueError(f"Unsupported schema format: {ext}")


def validate_schema(schema_file="schema.json", env_file=".env"):
    schema = load_schema(schema_file)

    with open(env_file) as f:
        env_vars = dict(
            line.strip().split("=", 1)
            for line in f
            if "=" in line and not line.startswith("#")
        )

    missing = [
        key for key, props in schema.items()
        if isinstance(props, dict) and props.get("required") and key not in env_vars
    ]

    if missing:
        print(f"Missing variables: {', '.join(missing)}")
    else:
        print("All required variables are present")

# def check_unused(env_file=".env", project_path="."):
#     with open(env_file) as f:
#         env_vars = [line.strip().split("=")[0] for line in f if "=" in line and not line.startswith("#")]
#     unused = []
#     for var in env_vars:
#         found = False
#         for root, _, files in os.walk(project_path):
#             for file in files:
#                 if file.endswith((".py", ".txt", ".md")):
#                     with open(os.path.join(root, file)) as f:
#                         if var in f.read():
#                             found = True
#                             break
#             if found:
#                 break
#         if not found:
#             unused.append(var)
#     if unused:
#         print(f"Unused variables: {', '.join(unused)}")
#     else:
#         print("No unused variables found")

import os
import locale

def check_unused(env_file=".env", project_path="."):
    # Detect system default encoding (e.g., cp1252 on Windows)
    system_encoding = locale.getpreferredencoding(False)
    encodings_to_try = ["utf-8", system_encoding, "latin-1", "utf-16"]

    # Read environment variables
    with open(env_file, encoding="utf-8") as f:  # .env files are usually utf-8
        env_vars = [line.strip().split("=")[0] for line in f if "=" in line and not line.startswith("#")]

    unused = []
    for var in env_vars:
        found = False
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith((".py", ".txt", ".md")):
                    file_path = os.path.join(root, file)

                    # Try multiple encodings
                    for enc in encodings_to_try:
                        try:
                            with open(file_path, encoding=enc) as f:
                                if var in f.read():
                                    found = True
                                    break
                        except UnicodeDecodeError:
                            continue  # try next encoding
                    if found:
                        break
            if found:
                break
        if not found:
            unused.append(var)

    if unused:
        print(f"Unused variables: {', '.join(unused)}")
    else:
        print("No unused variables found")

