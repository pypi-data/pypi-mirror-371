import subprocess
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.loader import get_template

class Command(BaseCommand):
    """
    Initializes Tailwind CSS v4, creating necessary files and
    automatically running `npm install`.
    """
    help = 'Initializes Tailwind CSS v4 and installs node dependencies.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Initializing Tailwind CSS v4..."))
        project_root = Path(settings.BASE_DIR)

        # 1. Create config files from templates
        self.create_files(project_root)

        # 2. Automatically run npm install
        self.run_npm_install(project_root)

        # 3. Print final instructions
        self.print_next_steps()

    def create_files(self, project_root):
        """Creates package.json, tailwind.config.js, and input.css."""
        files_to_create = {
            "package.json": "django_tailwind_v4/package.json",              # Corrected path
            "tailwind.config.js": "django_tailwind_v4/tailwind.config.js",  # Corrected path
        }
        for file, template in files_to_create.items():
            path = project_root / file
            self.create_file_from_template(path, template, file)

        # Handle the CSS file separately as it's in a subdirectory
        input_css_folder = project_root / "static" / "src"
        input_css_path = input_css_folder / "input.css"
        input_css_folder.mkdir(parents=True, exist_ok=True)
        self.create_file_from_template(
            input_css_path, "django_tailwind_v4/input.css", str(input_css_path) # Corrected path
        )

    def run_npm_install(self, project_root):
        """Checks for npm and runs `npm install`."""
        if not shutil.which("npm"):
            raise CommandError(
                "❌ 'npm' command not found. Please install Node.js and npm before running this command."
            )

        self.stdout.write(self.style.HTTP_INFO("\nRunning 'npm install'..."))
        try:
            # Run the command from the project's root directory
            process = subprocess.run(
                ["npm", "install"],
                cwd=project_root,
                check=True,
                capture_output=True,
                text=True,
            )
            self.stdout.write(self.style.SUCCESS("✅ npm dependencies installed successfully!"))
        except subprocess.CalledProcessError as e:
            # If npm install fails, show the error output
            self.stderr.write(self.style.ERROR("npm install failed:"))
            self.stderr.write(e.stdout)
            self.stderr.write(e.stderr)
            raise CommandError("Failed to install npm dependencies.")

    def create_file_from_template(self, path, template_name, file_desc):
        """Helper to create a file from a template if it doesn't exist."""
        if not path.exists():
            template = get_template(template_name)
            content = template.render()
            with open(path, "w") as f:
                f.write(content)
            self.stdout.write(self.style.SUCCESS(f"✅ Created {file_desc}"))
        else:
            self.stdout.write(self.style.WARNING(f"🟡 {file_desc} already exists. Skipping."))

    def print_next_steps(self):
        """Prints the final instructions for the user."""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("🎉 Tailwind CSS setup complete! 🎉"))
        self.stdout.write("\nNext Steps:")
        self.stdout.write(self.style.NOTICE("1. Configure your paths in settings.py (optional but recommended):"))
        self.stdout.write(
            "   # Example settings for django-tailwind-v4\n"
            "   TAILWIND_INPUT_CSS = 'static/src/input.css'\n"
            "   TAILWIND_OUTPUT_CSS = 'static/dist/output.css'"
        )
        self.stdout.write(self.style.NOTICE("\n2. Run the build process (use --watch for development):"))
        self.stdout.write(self.style.HTTP_INFO("   python manage.py tailwind_build --watch"))
        self.stdout.write(self.style.NOTICE("\n3. Include the compiled CSS in your base template:"))
        self.stdout.write(self.style.HTTP_INFO("   {% load static %}\n   <link href=\"{% static 'dist/output.css' %}\" rel=\"stylesheet\">"))
        self.stdout.write("="*50 + "\n")