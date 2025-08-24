"""Translator Application class for handling translation operations."""

import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import gemini_srt_translator as gst
from srtify.core.file_encoding import detect_and_fix_encoding
from srtify.core.settings import SettingsManager
from srtify.core.prompts import PromptsManager
from srtify.models.translation import TranslationConfig
from srtify.utils.exceptions import APIKeyError
from srtify.utils.utils import fancy_headline

logger = logging.getLogger(__name__)


class TranslatorApp:
    """ Main Application class for handling translation operations. """
    def __init__(self, settings_manager: SettingsManager, prompts_manager: PromptsManager):
        self.settings = settings_manager
        self.prompts = prompts_manager

    @staticmethod
    def translate_single_file(config: TranslationConfig) -> bool:
        """ Translate a single SRT file. """
        logger.info("Translating %s", config.srt_file)

        print(f"Translating:    {config.srt_file}")
        print(f"Language:       {config.target_language}")
        print(f"Batch Size:     {config.batch_size}")
        if config.prompt:
            print(f"Prompt:         {config.short_prompt}")

        if not config.api_key:
            print("❌ No API key found. Configure settings first.")
            return False

        config.output_file.parent.mkdir(parents=True, exist_ok=True)

        # Configure gemini_srt_translator
        gst.gemini_api_key = config.api_key
        gst.target_language = config.target_language.lower()
        gst.input_file = str(config.input_file)
        gst.output_file = str(config.output_file)
        gst.batch_size = config.batch_size
        if config.prompt:
            gst.description = config.prompt

        try:
            gst.translate()
            print("✅ Translation successful.")
            return True
        except Exception as e:
            print(f"❌ Translation failed for {config.srt_file}: {e}")
            return False

    @staticmethod
    def get_srt_file(input_path: Path, specific_file: Optional[str] = None) -> List[str]:
        """ Get list of SRT files to process. """
        if specific_file:
            file_name = specific_file.strip()
            if not file_name.endswith(".srt"):
                file_name = f"{file_name}.srt"

            file_path = input_path / file_name
            if file_path.exists():
                return [file_name]
            print(f"❌ File {file_name} not found in {input_path}")
            return []

        str_files = [file.name for file in input_path.glob("*.srt")]
        return str_files

    @staticmethod
    def validate_files_encoding(input_path: Path, srt_files: List[str]) -> List[str]:
        """ Validate and fix file encoding for all SRT files. """
        print("Checking file encoding...")
        valid_files = []

        for srt_file in srt_files:
            if detect_and_fix_encoding(input_path, srt_file):
                valid_files.append(srt_file)
            else:
                print(f"❌ Failed to fix encoding for file {srt_file}. Skipping...")

        return valid_files

    def resolve_prompt(self, options: Dict[str, Any]) -> Optional[str]:
        """ Resolve which prompt to use based on options """
        if options.get('custom_prompt'):
            return options['custom_prompt'].strip()
        if options.get('prompt'):
            results = self.prompts.search_prompts(options['prompt'].strip())
            if results:
                if len(results) == 1:
                    return list(results.values())[0]

                print(f"Found {len(results)} prompts matching '{options['prompt']}'")
                for name, desc in results.items():
                    print(f" - {name}: {desc[:100]}{'...' if len(desc) > 100 else ''}")
                return None

            print(f"No prompts found matching '{options['prompt']}'")
            return None
        if options.get('quick'):
            return "Translate naturally and accurately"

        return "Translate naturally and accurately"

    def _get_translation_config(self, options: Dict[str, Any]) -> TranslationConfig:
        """Helper method to create a TranslationConfig object."""
        input_dir, output_dir = self.settings.get_directories()
        input_path = Path(options.get('input_path') or input_dir)
        output_path = Path(options.get('output_path') or output_dir)
        language = options.get('language') or self.settings.get_translation_language()
        batch_size = options.get('batch_size') or self.settings.get_translation_batch_size()
        api_key = self.settings.get_api_key()
        prompt = self.resolve_prompt(options)

        if not api_key:
            raise APIKeyError("API key not found. Use settings to configure.")

        return TranslationConfig(
            input_path=input_path,
            output_path=output_path,
            target_language=language,
            prompt=prompt,
            batch_size=batch_size,
            api_key=api_key
        )

    def run_translation(self, options: Dict[str, Any]) -> None:
        """ Main translation runner. """
        config = self._get_translation_config(options)
        # Print configuration
        print("Translation Settings:")
        print("=" * 30)
        print(f"- Target Language:  {config.target_language}")
        print(f"- Input Directory:  {config.input_path}")
        print(f"- Output Directory: {config.output_path}")
        print(f"- Batch Size:       {config.batch_size}")
        print(f"- API Key:          {'Set' if config.api_key else 'Not Set'}")
        print("=" * 30)

        srt_files = self.get_srt_file(config.input_path, config.srt_file)
        if not srt_files:
            print("❌ No SRT files found. Exiting.")
            return

        print(f"Found {len(srt_files)} SRT files.")

        valid_files = self.validate_files_encoding(config.input_path, srt_files)
        if not valid_files:
            print("❌ No valid SRT files found after encoding check. Exiting.")
            return

        print(f"Found {len(valid_files)} valid SRT files.")
        print(f"\nStarting translation to {config.target_language}...")
        print("=" * shutil.get_terminal_size().columns)

        successful = 0
        failed = 0

        for srt_file in valid_files:
            config.srt_file = srt_file
            if self.translate_single_file(config):
                successful += 1
            else:
                failed += 1

        print("=" * shutil.get_terminal_size().columns)
        print(fancy_headline("TRANSLATION SUMMARY", "rounded"))
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Output Directory: {config.output_path}")
