"""
PPT-Translator: AI-powered PowerPoint presentation translator using Amazon Bedrock.

This package provides tools for translating PowerPoint presentations using
Amazon Bedrock's AI models while preserving formatting and layout.
"""

__version__ = "0.1.0"
__author__ = "PPT-Translator Team"
__email__ = "contact@ppt-translator.com"

from .translation_engine import TranslationEngine
from .ppt_handler import PPTHandler

__all__ = ["TranslationEngine", "PPTHandler"]
