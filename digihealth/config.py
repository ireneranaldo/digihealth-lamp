import yaml
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
from pathlib import Path

class SensorConfig(BaseModel):
    zph: Dict[str, Any] = Field(default_factory=dict)
    light: Dict[str, Any] = Field(default_factory=dict)
    door: Dict[str, Any] = Field(default_factory=dict)
    window: Dict[str, Any] = Field(default_factory=dict)
    people_counter: Dict[str, Any] = Field(default_factory=dict)
    microphone: Dict[str, Any] = Field(default_factory=dict)

class ProcessorConfig(BaseModel):
    iaqi: Dict[str, Any] = Field(default_factory=dict)
    circadian: Dict[str, Any] = Field(default_factory=dict)
    audio_comfort: Dict[str, Any] = Field(default_factory=dict)

class ActuatorConfig(BaseModel):
    neopixel: Dict[str, Any] = Field(default_factory=dict)
    shelly: Dict[str, Any] = Field(default_factory=dict)
    led_wifi: Dict[str, Any] = Field(default_factory=dict)

class CommunicatorConfig(BaseModel):
    telegraf: Dict[str, Any] = Field(default_factory=dict)
    ipc: Dict[str, Any] = Field(default_factory=dict)

class WebConfig(BaseModel):
    enabled: bool = False
    host: str = "0.0.0.0"
    port: int = 5000

class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: Optional[str] = None

class DigiHealthConfig(BaseModel):
    sensors: SensorConfig = Field(default_factory=SensorConfig)
    processors: ProcessorConfig = Field(default_factory=ProcessorConfig)
    actuators: ActuatorConfig = Field(default_factory=ActuatorConfig)
    communicator: CommunicatorConfig = Field(default_factory=CommunicatorConfig)
    web: WebConfig = Field(default_factory=WebConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

def merge_configs(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    return result

def load_config(config_path: str = "config/default.yaml") -> DigiHealthConfig:
    """Load configuration from YAML files, with local overrides."""
    config_dir = Path("config")
    default_config_path = config_dir / "default.yaml"
    local_config_path = config_dir / "local.yaml"

    # Load default config
    if default_config_path.exists():
        with open(default_config_path, 'r') as f:
            config_data = yaml.safe_load(f) or {}
    else:
        config_data = {}

    # Override with local config if exists
    if local_config_path.exists():
        with open(local_config_path, 'r') as f:
            local_data = yaml.safe_load(f) or {}
            config_data = merge_configs(config_data, local_data)

    # Override with environment variables
    env_overrides = {
        'communicator.telegraf.tags.sensor': os.getenv('DIGIHEALTH_SENSOR'),
        'communicator.telegraf.tags.host': os.getenv('DIGIHEALTH_HOST'),
        'communicator.telegraf.tags.lampada': os.getenv('DIGIHEALTH_LAMPADA'),
        'communicator.telegraf.tags.stanza': os.getenv('DIGIHEALTH_STANZA'),
        'communicator.telegraf.tags.client_id': os.getenv('DIGIHEALTH_CLIENT_ID')
    }

    for key_path, value in env_overrides.items():
        if value is not None:
            keys = key_path.split('.')
            current = config_data
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = value

    return DigiHealthConfig(**config_data)

config = load_config()