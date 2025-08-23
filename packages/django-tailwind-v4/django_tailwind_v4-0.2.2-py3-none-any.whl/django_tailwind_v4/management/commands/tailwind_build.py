import subprocess
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    """
    Builds Tailwind CSS using the @tailwindcss/cli tool.
    """
    help = 'Builds Tailwind CSS using the @tailwindcss/cli tool.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--watch', action='store_true', help='Run in watch mode.'
        )
        parser.add_argument(
            '--minify', action='store_true', help='Minify the output CSS.'
        )

    def handle(self, *args, **options):
        if not shutil.which("npx"):
            raise CommandError("❌ 'npx' not found. Please install Node.js and npm.")

        input_path = Path(settings.BASE_DIR) / getattr(settings, "TAILWIND_INPUT_CSS", "static/src/input.css")
        output_path = Path(settings.BASE_DIR) / getattr(settings, "TAILWIND_OUTPUT_CSS", "static/dist/output.css")

        if not input_path.exists():
            raise CommandError(f"Input CSS file not found at: {input_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # *** THE KEY CHANGE FOR V4 IS HERE ***
        command = [
            "npx",
            "@tailwindcss/cli", # Use the new official CLI package
            "-i", str(input_path),
            "-o", str(output_path),
        ]

        if options['watch']:
            command.append("--watch")
            self.stdout.write(self.style.SUCCESS(f"👀 Watching for changes..."))
        if options['minify']:
            command.append("--minify")
            self.stdout.write(self.style.SUCCESS("📦 Minifying output CSS."))

        try:
            self.stdout.write(self.style.NOTICE(f"Running: {' '.join(command)}"))
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(process.stdout.readline, ''):
                self.stdout.write(line.strip())
            process.stdout.close()
            if process.wait() != 0:
                raise CommandError("Tailwind CSS build failed.")
            if not options['watch']:
                self.stdout.write(self.style.SUCCESS("✅ Tailwind CSS built successfully!"))
        except Exception as e:
            raise CommandError(f"An error occurred: {e}")