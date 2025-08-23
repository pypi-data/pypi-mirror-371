from pathlib import Path
from typing import Any, Optional

import toml

from ..core.roles import RoundtableRole
from .models import AIConfig, ModelConfig


class ConfigManager:
    """Manages loading, saving, and updating configuration."""

    def __init__(self) -> None:
        self._config: Optional[AIConfig] = None
        self._config_path = Path.home() / ".ai-cli" / "config.toml"
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        self._config_path.parent.mkdir(exist_ok=True)

    def load_config(self) -> AIConfig:
        """Load configuration from file or create default."""
        if self._config is not None:
            return self._config

        if self._config_path.exists():
            try:
                with open(self._config_path) as f:
                    config_data = toml.load(f)
                self._config = AIConfig(**config_data)
            except Exception as e:
                print(f"Error: Failed to load config from {self._config_path}: {e}")
                print(
                    "Your configuration file appears to be corrupted or has invalid syntax."
                )

                # Create backup of the problematic config
                backup_path = self._config_path.with_suffix(".toml.backup")
                try:
                    import shutil

                    shutil.copy2(self._config_path, backup_path)
                    print(f"Backed up your current config to: {backup_path}")
                except Exception:
                    pass

                print(
                    "Please fix the configuration file manually, or run 'ai config init' to recreate it."
                )
                print("Using minimal default configuration for this session only...")

                # Don't save defaults automatically - just use them for this session
                self._config = AIConfig()
                return self._config
        else:
            # Only create default config for truly new users
            self._config = AIConfig()
            self.save_config()  # Save default config for new users

        return self._config

    def save_config(self, config: Optional[AIConfig] = None) -> None:
        """Save configuration to file."""
        if config is None:
            config = self._config
        if config is None:
            raise ValueError("No configuration to save")

        # Create backup of existing config before overwriting
        if self._config_path.exists():
            backup_path = self._config_path.with_suffix(".toml.backup")
            try:
                import shutil

                shutil.copy2(self._config_path, backup_path)
            except Exception:
                # Don't fail the save operation if backup fails
                pass

        config_dict = self._config_to_dict(config)

        with open(self._config_path, "w") as f:
            toml.dump(config_dict, f)

    def _config_to_dict(self, config: AIConfig) -> dict[str, Any]:
        """Convert AIConfig to dictionary for TOML serialization."""
        result: dict[str, Any] = {
            "default_model": config.default_model,
            "models": {},
            "roundtable": {
                # New role-centric fields
                "enabled_roles": [
                    role.value for role in config.roundtable.enabled_roles
                ],
                "role_model_mapping": {
                    role.value: model
                    for role, model in config.roundtable.role_model_mapping.items()
                },
                "solo_model": config.roundtable.solo_model,
                # Discussion settings
                "discussion_rounds": config.roundtable.discussion_rounds,
                "parallel_responses": config.roundtable.parallel_responses,
                "timeout_seconds": config.roundtable.timeout_seconds,
                # Custom templates
                "custom_role_templates": {
                    role.value: template
                    for role, template in config.roundtable.custom_role_templates.items()
                },
                # Legacy fields (kept for migration)
                "use_role_based_prompting": config.roundtable.use_role_based_prompting,
                "role_rotation": config.roundtable.role_rotation,
                "role_assignments": {
                    model: [role.value for role in roles]
                    for model, roles in config.roundtable.role_assignments.items()
                },
            },
            "ui": {
                "theme": config.ui.theme,
                "streaming": config.ui.streaming,
                "format": config.ui.format,
                "show_model_icons": config.ui.show_model_icons,
            },
        }

        # Convert model configs to dicts
        for name, model_config in config.models.items():
            model_dict = {
                "provider": model_config.provider,
                "model": model_config.model,
                "max_tokens": model_config.max_tokens,
                "temperature": model_config.temperature,
                "context_window": model_config.context_window,
            }
            # Handle API key storage - save env: references, not resolved keys
            if model_config.api_key:
                # If it looks like a resolved API key or placeholder, convert to env reference
                is_resolved_key = (
                    model_config.api_key.startswith("sk-")
                    or model_config.api_key.startswith("AIzaSy")
                    or len(model_config.api_key) > 50
                )
                is_placeholder = (
                    "your-" in model_config.api_key.lower()
                    and "-key-here" in model_config.api_key.lower()
                )

                if is_resolved_key or is_placeholder:
                    # Try to determine the original env reference
                    if name == "openai/gpt-4" or "openai" in model_config.provider:
                        model_dict["api_key"] = "env:OPENAI_API_KEY"
                    elif (
                        name == "anthropic/claude-3-sonnet"
                        or "anthropic" in model_config.provider
                    ):
                        model_dict["api_key"] = "env:ANTHROPIC_API_KEY"
                    elif (
                        "gemini" in model_config.provider
                        or "google" in model_config.provider
                    ):
                        model_dict["api_key"] = "env:GEMINI_API_KEY"
                else:
                    # It's likely an env: reference, keep it as is
                    model_dict["api_key"] = model_config.api_key

            if model_config.endpoint:
                model_dict["endpoint"] = model_config.endpoint

            result["models"][name] = model_dict

        return result

    def update_model(self, model_name: str, **updates: Any) -> None:
        """Update a specific model configuration."""
        config = self.load_config()

        if model_name not in config.models:
            # Create new model config
            # Ensure model field is set correctly, prioritizing updates over model_name
            model_config_data: dict[str, Any] = {"model": model_name}
            model_config_data.update(
                updates
            )  # This will override model if specified in updates
            config.models[model_name] = ModelConfig(**model_config_data)
        else:
            # Update existing model config
            model_config = config.get_model_config(model_name)
            for key, value in updates.items():
                if hasattr(model_config, key):
                    setattr(model_config, key, value)
            config.models[model_name] = model_config

        self.save_config(config)

    def set_default_model(self, model_name: str) -> None:
        """Set the default model."""
        config = self.load_config()
        if model_name not in config.models:
            raise ValueError(f"Model '{model_name}' not found in configuration")
        config.default_model = model_name
        self.save_config(config)

    def create_default_config(self, minimal: bool = False) -> Path:
        """Create a default configuration file for first-time setup.

        Args:
            minimal: If True, create a minimal config with basic settings only

        Returns:
            Path to the created configuration file
        """
        # Create a default AIConfig
        if minimal:
            # Minimal config with just OpenAI GPT-4
            # Use direct dict creation to bypass ensure_default_models validator
            config_dict = {
                "default_model": "openai/gpt-4",
                "models": {
                    "openai/gpt-4": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "api_key": "env:OPENAI_API_KEY",
                    }
                },
                "roundtable": {
                    "enabled_models": [],
                    "discussion_rounds": 2,
                    "parallel_responses": False,
                    "timeout_seconds": 30,
                    "use_role_based_prompting": True,
                    "role_rotation": True,
                    "role_assignments": {},
                    "custom_role_templates": {},
                },
                "ui": {
                    "theme": "dark",
                    "streaming": True,
                    "format": "markdown",
                    "show_model_icons": True,
                },
            }
            config = AIConfig.model_validate(config_dict)
        else:
            # Full-featured config with roundtable setup
            config = AIConfig(
                default_model="openai/gpt-4",
                models={
                    "openai/gpt-4": ModelConfig(
                        provider="openai", model="gpt-4", api_key="env:OPENAI_API_KEY"
                    ),
                    "anthropic/claude-3-5-sonnet": ModelConfig(
                        provider="anthropic",
                        model="claude-3-5-sonnet-20241022",
                        api_key="env:ANTHROPIC_API_KEY",
                    ),
                    "gemini": ModelConfig(
                        provider="gemini",
                        model="gemini-2.5-flash",
                        api_key="env:GEMINI_API_KEY",
                    ),
                },
            )
            # Roundtable is now role-based and enabled by default

        # Save the config
        self._config = config
        self.save_config(config)

        return self._config_path

    def list_models(self) -> dict[str, ModelConfig]:
        """List all configured models."""
        config = self.load_config()
        return {name: config.get_model_config(name) for name in config.models.keys()}

    def get_config_path(self) -> Path:
        """Get the path to the configuration file."""
        return self._config_path

    def set_role_based_prompting(self, enabled: bool) -> None:
        """Enable or disable role-based prompting."""
        config = self.load_config()
        config.roundtable.use_role_based_prompting = enabled
        self.save_config(config)

    def set_role_rotation(self, enabled: bool) -> None:
        """Enable or disable role rotation."""
        config = self.load_config()
        config.roundtable.role_rotation = enabled
        self.save_config(config)

    def assign_roles_to_model(
        self, model_name: str, roles: list[RoundtableRole]
    ) -> None:
        """Assign specific roles to a model."""
        config = self.load_config()
        if model_name not in config.models:
            raise ValueError(f"Model '{model_name}' not found in configuration")
        config.roundtable.role_assignments[model_name] = roles
        self.save_config(config)

    def remove_role_assignments(self, model_name: str) -> None:
        """Remove role assignments for a model (allow all roles)."""
        config = self.load_config()
        if model_name in config.roundtable.role_assignments:
            del config.roundtable.role_assignments[model_name]
            self.save_config(config)

    def set_custom_role_template(self, role: RoundtableRole, template: str) -> None:
        """Set a custom template for a specific role."""
        config = self.load_config()
        config.roundtable.custom_role_templates[role] = template
        self.save_config(config)

    def remove_custom_role_template(self, role: RoundtableRole) -> None:
        """Remove custom template for a role (use default)."""
        config = self.load_config()
        if role in config.roundtable.custom_role_templates:
            del config.roundtable.custom_role_templates[role]
            self.save_config(config)

    def get_role_assignments(self) -> dict[str, list[RoundtableRole]]:
        """Get all role assignments."""
        config = self.load_config()
        return config.roundtable.role_assignments.copy()

    def get_custom_role_templates(self) -> dict[RoundtableRole, str]:
        """Get all custom role templates."""
        config = self.load_config()
        return config.roundtable.custom_role_templates.copy()

    # New role-centric methods
    def enable_roundtable_role(self, role_str: str) -> None:
        """Enable a role in the roundtable."""
        try:
            role = RoundtableRole(role_str)
        except ValueError as e:
            raise ValueError(
                f"Invalid role: {role_str}. Valid roles: {[r.value for r in RoundtableRole]}"
            ) from e

        config = self.load_config()
        if role not in config.roundtable.enabled_roles:
            config.roundtable.enabled_roles.append(role)
            self.save_config(config)

    def disable_roundtable_role(self, role_str: str) -> None:
        """Disable a role in the roundtable."""
        try:
            role = RoundtableRole(role_str)
        except ValueError as e:
            raise ValueError(
                f"Invalid role: {role_str}. Valid roles: {[r.value for r in RoundtableRole]}"
            ) from e

        config = self.load_config()
        if role in config.roundtable.enabled_roles:
            config.roundtable.enabled_roles.remove(role)
            self.save_config(config)

    def set_role_model_mapping(self, role_str: str, model: str) -> None:
        """Map a role to a specific model."""
        try:
            role = RoundtableRole(role_str)
        except ValueError as e:
            raise ValueError(
                f"Invalid role: {role_str}. Valid roles: {[r.value for r in RoundtableRole]}"
            ) from e

        config = self.load_config()
        if model not in config.models:
            raise ValueError(f"Model '{model}' not found in configuration")

        config.roundtable.role_model_mapping[role] = model
        self.save_config(config)

    def remove_role_model_mapping(self, role_str: str) -> None:
        """Remove role-to-model mapping."""
        try:
            role = RoundtableRole(role_str)
        except ValueError as e:
            raise ValueError(
                f"Invalid role: {role_str}. Valid roles: {[r.value for r in RoundtableRole]}"
            ) from e

        config = self.load_config()
        if role in config.roundtable.role_model_mapping:
            del config.roundtable.role_model_mapping[role]
            self.save_config(config)

    def set_solo_model(self, model: str) -> None:
        """Set solo model for all roles."""
        config = self.load_config()
        if model not in config.models:
            raise ValueError(f"Model '{model}' not found in configuration")

        config.roundtable.solo_model = model
        self.save_config(config)

    def clear_solo_model(self) -> None:
        """Clear solo model setting."""
        config = self.load_config()
        config.roundtable.solo_model = None
        self.save_config(config)
