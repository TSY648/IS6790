from django.core.management import call_command
from django.core.management.base import BaseCommand


SEED_COMMANDS = [
    'seed_level_one',
    'seed_level_two',
    'seed_level_three',
    'seed_level_four',
    'seed_level_five',
    'seed_level_six',
    'seed_level_seven',
]


class Command(BaseCommand):
    help = 'Synchronize all level content into the database.'

    def handle(self, *args, **options):
        for command_name in SEED_COMMANDS:
            self.stdout.write(f'Running {command_name}...')
            call_command(command_name)

        self.stdout.write(self.style.SUCCESS('All game content is synchronized.'))
