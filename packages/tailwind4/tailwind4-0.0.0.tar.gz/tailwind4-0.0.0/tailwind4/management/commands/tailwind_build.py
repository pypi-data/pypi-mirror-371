from django.core.management.base import BaseCommand
from pathlib import Path
from tailwind4.utils import run_command

class Command(BaseCommand):
    help = "Build Tailwind CSS using npx"

    def handle(self, *args, **kwargs):
        base_dir = Path.cwd()
        input_css = base_dir / "static" / "input.css"
        output_css = base_dir / "static" / "output.css"

        if not input_css.exists():
            self.stdout.write(self.style.ERROR("❌ input.css not found. Run `python manage.py tailwind_init` first."))
            return

        run_command(f"npx tailwindcss -i {input_css} -o {output_css} --minify")
        self.stdout.write(self.style.SUCCESS(f"✅ Tailwind CSS built at {output_css}"))
