"""Config flow for Grok Conversation integration."""

from __future__ import annotations

import logging
from typing import Any
import openai
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_CHAT_MODEL,
    CONF_MAX_TOKENS,
    CONF_PROMPT,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    DOMAIN,
    LOGGER,
    RECOMMENDED_CHAT_MODEL,
    RECOMMENDED_MAX_TOKENS,
    RECOMMENDED_TEMPERATURE,
    RECOMMENDED_TOP_P,
)

API_PROMPT = "Enter your xAI API Key"


class GrokConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Grok Conversation."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1",
            )
            try:
                await client.models.list()
            except openai.AuthenticationError:
                errors["base"] = "invalid_api_key"
            except openai.OpenAIError as err:
                LOGGER.error("Error connecting to Grok API: %s", err)
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="Grok Conversation", data={CONF_API_KEY: api_key}
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            description_placeholders={"api_prompt": API_PROMPT},
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return GrokOptionsFlow(config_entry)


class GrokOptionsFlow(config_entries.OptionsFlow):
    """Handle Grok options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PROMPT,
                        default=self.config_entry.options.get(CONF_PROMPT, ""),
                    ): str,
                    vol.Optional(
                        CONF_CHAT_MODEL,
                        default=self.config_entry.options.get(
                            CONF_CHAT_MODEL, RECOMMENDED_CHAT_MODEL
                        ),
                    ): selector.TextSelector(),
                    vol.Optional(
                        CONF_MAX_TOKENS,
                        default=self.config_entry.options.get(
                            CONF_MAX_TOKENS, RECOMMENDED_MAX_TOKENS
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=2048, unit_of_measurement="tokens"
                        )
                    ),
                    vol.Optional(
                        CONF_TOP_P,
                        default=self.config_entry.options.get(
                            CONF_TOP_P, RECOMMENDED_TOP_P
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(min=0.0, max=1.0)
                    ),
                    vol.Optional(
                        CONF_TEMPERATURE,
                        default=self.config_entry.options.get(
                            CONF_TEMPERATURE, RECOMMENDED_TEMPERATURE
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(min=0.0, max=2.0)
                    ),
                }
            ),
        )