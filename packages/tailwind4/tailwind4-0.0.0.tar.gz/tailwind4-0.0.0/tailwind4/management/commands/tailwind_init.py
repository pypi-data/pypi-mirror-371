from django.core.management.base import BaseCommand
import os
from pathlib import Path
from tailwind4.utils import run_command

class Command(BaseCommand):
    help = "Initialize Tailwind CSS v4 in your Django project"

    def handle(self, *args, **kwargs):
        base_dir = Path.cwd()
        static_dir = base_dir / "static"
        static_dir.mkdir(exist_ok=True)

        # Create Tailwind entry CSS file
        css_file = static_dir / "input.css"
        if not css_file.exists():
            css_file.write_text("@tailwind base;\n@tailwind components;\n@tailwind utilities;\n")
            self.stdout.write(self.style.SUCCESS("Created input.css with Tailwind directives"))

        # Initialize Tailwind via npm
        if not (base_dir / "tailwind.config.js").exists():
            run_command("npx tailwindcss init")
            self.stdout.write(self.style.SUCCESS("Initialized tailwind.config.js"))

        self.stdout.write(self.style.SUCCESS("✅ Tailwind setup complete. Run `python manage.py tailwind_build`"))
