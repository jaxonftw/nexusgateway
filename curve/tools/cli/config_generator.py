import os
from jinja2 import Environment, FileSystemLoader
import yaml
from jsonschema import validate

ENVOY_CONFIG_TEMPLATE_FILE = os.getenv(
    "ENVOY_CONFIG_TEMPLATE_FILE", "envoy.template.yaml"
)
CURVE_CONFIG_FILE = os.getenv("CURVE_CONFIG_FILE", "/config/curve_config.yaml")
ENVOY_CONFIG_FILE_RENDERED = os.getenv(
    "ENVOY_CONFIG_FILE_RENDERED", "/etc/envoy/envoy.yaml"
)
CURVE_CONFIG_SCHEMA_FILE = os.getenv(
    "CURVE_CONFIG_SCHEMA_FILE", "curve_config_schema.yaml"
)


def add_secret_key_to_llm_providers(config_yaml):
    llm_providers = []
    for llm_provider in config_yaml.get("llm_providers", []):
        access_key_env_var = llm_provider.get("access_key", False)
        access_key_value = os.getenv(access_key_env_var, False)
        if access_key_env_var and access_key_value:
            llm_provider["access_key"] = access_key_value
        llm_providers.append(llm_provider)
    config_yaml["llm_providers"] = llm_providers
    return config_yaml


def validate_and_render_schema():
    env = Environment(loader=FileSystemLoader("./"))
    template = env.get_template("envoy.template.yaml")

    try:
        validate_prompt_config(CURVE_CONFIG_FILE, CURVE_CONFIG_SCHEMA_FILE)
    except Exception as e:
        print(str(e))
        exit(1)  # validate_prompt_config failed. Exit

    with open(CURVE_CONFIG_FILE, "r") as file:
        curve_config = file.read()

    with open(CURVE_CONFIG_SCHEMA_FILE, "r") as file:
        curve_config_schema = file.read()

    config_yaml = yaml.safe_load(curve_config)
    config_schema_yaml = yaml.safe_load(curve_config_schema)
    inferred_clusters = {}

    if "prompt_targets" in config_yaml:
        for prompt_target in config_yaml["prompt_targets"]:
            name = prompt_target.get("endpoint", {}).get("name", "")
            if name not in inferred_clusters:
                inferred_clusters[name] = {
                    "name": name,
                    "port": 80,  # default port
                }

    print(inferred_clusters)
    endpoints = config_yaml.get("endpoints", {})

    # override the inferred clusters with the ones defined in the config
    for name, endpoint_details in endpoints.items():
        if name in inferred_clusters:
            print("updating cluster", endpoint_details)
            inferred_clusters[name].update(endpoint_details)
            endpoint = inferred_clusters[name]["endpoint"]
            if len(endpoint.split(":")) > 1:
                inferred_clusters[name]["endpoint"] = endpoint.split(":")[0]
                inferred_clusters[name]["port"] = int(endpoint.split(":")[1])
        else:
            inferred_clusters[name] = endpoint_details

    print("updated clusters", inferred_clusters)

    curve _llm_providers = config_yaml["llm_providers"]
    curve _tracing = config_yaml.get("tracing", {})
    curve_config_string = yaml.dump(config_yaml)
    config_yaml["mode"] = "llm"
    curve _llm_config_string = yaml.dump(config_yaml)

    data = {
        "curve_config": curve_config_string,
        "curve _llm_config": curve _llm_config_string,
        "curve _clusters": inferred_clusters,
        "curve _llm_providers": curve _llm_providers,
        "curve _tracing": curve _tracing,
    }

    rendered = template.render(data)
    print(rendered)
    print(ENVOY_CONFIG_FILE_RENDERED)
    with open(ENVOY_CONFIG_FILE_RENDERED, "w") as file:
        file.write(rendered)


def validate_prompt_config(curve_config_file, curve_config_schema_file):
    with open(curve_config_file, "r") as file:
        curve_config = file.read()

    with open(curve_config_schema_file, "r") as file:
        curve_config_schema = file.read()

    config_yaml = yaml.safe_load(curve_config)
    config_schema_yaml = yaml.safe_load(curve_config_schema)

    try:
        validate(config_yaml, config_schema_yaml)
    except Exception as e:
        print(
            f"Error validating curve_config file: {curve_config_file}, error: {e.message}"
        )
        raise e


if __name__ == "__main__":
    validate_and_render_schema()
