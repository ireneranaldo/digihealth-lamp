#!/usr/bin/env python3
"""
Setup script for DigiHealth Lamp configuration.
This script helps configure the installation-specific settings.
"""

import os
import yaml
from pathlib import Path

def load_config():
    """Load existing configuration."""
    config_dir = Path("config")
    default_config = config_dir / "default.yaml"
    local_config = config_dir / "local.yaml"

    # Load default config
    with open(default_config, 'r') as f:
        config = yaml.safe_load(f)

    # Override with local config if exists
    if local_config.exists():
        with open(local_config, 'r') as f:
            local = yaml.safe_load(f)
            # Deep merge
            config = merge_configs(config, local)

    return config

def merge_configs(base, override):
    """Deep merge two dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    return result

def create_local_config():
    """Create local configuration file with installation-specific settings."""
    config_dir = Path("config")
    local_config = config_dir / "local.yaml"

    if local_config.exists():
        print("Local configuration already exists!")
        return

    print("=== DigiHealth Lamp Setup ===")
    print("Configurazione impostazioni specifiche per questa installazione")
    print()

    # Get tag values from environment or user input
    tags = {}

    # Check environment variables first
    env_tags = {
        'sensor': os.getenv('DIGIHEALTH_SENSOR'),
        'host': os.getenv('DIGIHEALTH_HOST'),
        'lampada': os.getenv('DIGIHEALTH_LAMPADA'),
        'stanza': os.getenv('DIGIHEALTH_STANZA'),
        'client_id': os.getenv('DIGIHEALTH_CLIENT_ID')
    }

    print("Configurazione tag InfluxDB:")
    print("(premi Enter per usare valori di default o variabili d'ambiente)")
    print()

    for tag_name, env_value in env_tags.items():
        if env_value:
            default_value = env_value
            print(f"{tag_name}: {env_value} (da variabile d'ambiente)")
        else:
            # Default values based on the user's previous configuration
            defaults = {
                'sensor': 'ZPHS01B',
                'host': 'raspberry01',
                'lampada': '88a29e6f9779',
                'stanza': 'Ufficio1_ProtoDesign',
                'client_id': '57'
            }
            default_value = defaults.get(tag_name, '')

        value = input(f"{tag_name} [{default_value}]: ").strip()
        if not value:
            value = default_value
        tags[tag_name] = value

    # Create local config
    local_config_data = {
        'communicator': {
            'telegraf': {
                'tags': tags
            }
        }
    }

    # Ask about optional features
    print()
    print("Configurazione sensori/attuatori opzionali:")
    print()

    # People counter
    enable_people = input("Abilitare conteggio persone via telecamera? (y/N): ").lower().startswith('y')
    if enable_people:
        rtsp_url = input("URL RTSP telecamera [rtsp://admin:password@192.168.1.124/profile2/media.smp]: ").strip()
        if not rtsp_url:
            rtsp_url = "rtsp://admin:password@192.168.1.124/profile2/media.smp"

        local_config_data['sensors'] = local_config_data.get('sensors', {})
        local_config_data['sensors']['people_counter'] = {
            'enabled': True,
            'rtsp_url': rtsp_url,
            'model_path': 'yolov8n.pt',
            'frame_width': 640,
            'frame_height': 480
        }

    # LED WiFi
    enable_led_wifi = input("Abilitare faretti LED WiFi circadiani? (y/N): ").lower().startswith('y')
    if enable_led_wifi:
        led_ip = input("IP del faretto LED WiFi [192.168.1.192]: ").strip()
        if not led_ip:
            led_ip = "192.168.1.192"

        local_config_data['actuators'] = local_config_data.get('actuators', {})
        local_config_data['actuators']['led_wifi'] = {
            'enabled': True,
            'ip': led_ip,
            'mode': 'circadian',
            'min_lux': 10,
            'max_lux': 500
        }

    # Save local config
    with open(local_config, 'w') as f:
        yaml.dump(local_config_data, f, default_flow_style=False, sort_keys=False)

    print()
    print("✅ Configurazione locale creata in config/local.yaml")
    print("I valori possono essere modificati direttamente nel file o rieseguendo questo script.")

if __name__ == "__main__":
    create_local_config()