import os
import subprocess
import sys
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Build React frontend components for SSR'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Enable watch mode for development with HMR',
        )
        parser.add_argument(
            '--production',
            action='store_true',
            help='Build for production environment',
        )
    
    def handle(self, *args, **options):
        # Get the frontend directory
        frontend_dir = Path(__file__).parent.parent.parent / 'frontend'
        
        if not frontend_dir.exists():
            raise CommandError(f"Frontend directory not found at {frontend_dir}")
        
        self.stdout.write("Starting React build process...")
        
        # Check if Node.js is installed
        try:
            subprocess.run(['node', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise CommandError(
                "Node.js is not installed. Please install Node.js to build the React frontend."
            )
        
        # Change to frontend directory
        os.chdir(frontend_dir)
        
        # Install npm dependencies if node_modules doesn't exist
        if not (frontend_dir / 'node_modules').exists():
            self.stdout.write("Installing npm dependencies...")
            try:
                subprocess.run(['npm', 'install'], check=True)
                self.stdout.write(
                    self.style.SUCCESS("Dependencies installed successfully")
                )
            except subprocess.CalledProcessError as e:
                raise CommandError(f"Failed to install dependencies: {e}")
        
        # Determine build command
        if options['watch']:
            self.stdout.write("Starting development server with HMR...")
            command = ['npm', 'run', 'dev']
        elif options['production']:
            self.stdout.write("Building for production...")
            command = ['npm', 'run', 'build']
        else:
            self.stdout.write("Building React components...")
            command = ['npm', 'run', 'build']
        
        try:
            if options['watch']:
                # For watch mode, run continuously
                self.stdout.write(
                    self.style.WARNING(
                        "Watch mode started. Press Ctrl+C to stop."
                    )
                )
                subprocess.run(command)
            else:
                # For build mode, run once and exit
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                self.stdout.write(
                    self.style.SUCCESS("React build completed successfully!")
                )
                if result.stdout:
                    self.stdout.write(result.stdout)
                    
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise CommandError(f"Build failed: {error_msg}")
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING("\nBuild process interrupted by user")
            )
