"""
Database population script for VAHAD-TMS.
Delegates to safe idempotent seeder.
"""
import os
import sys

if __name__ == "__main__":
    import django
    sys.path.append(os.getcwd())
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vahad_project.settings')
    django.setup()

from vahad_app.management.commands.seed_data import run_seed


def populate():
    run_seed()


if __name__ == "__main__":
    populate()
