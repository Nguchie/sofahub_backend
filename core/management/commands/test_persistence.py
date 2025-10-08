from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Test Railway file persistence'

    def handle(self, *args, **options):
        """Test if files persist on Railway"""
        
        self.stdout.write('🧪 TESTING RAILWAY FILE PERSISTENCE')
        self.stdout.write('=' * 50)
        
        # Test file creation
        test_file_path = os.path.join(settings.MEDIA_ROOT, 'test.txt')
        test_content = "This is a test file created at deployment time"
        
        try:
            # Create test file
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            with open(test_file_path, 'w') as f:
                f.write(test_content)
            
            self.stdout.write(f'✅ Created test file: {test_file_path}')
            
            # Check if it exists
            if os.path.exists(test_file_path):
                with open(test_file_path, 'r') as f:
                    content = f.read()
                self.stdout.write(f'✅ File exists and readable: {content}')
            else:
                self.stdout.write(f'❌ File disappeared immediately')
                
        except Exception as e:
            self.stdout.write(f'❌ Error: {e}')
        
        # Check media directory structure
        self.stdout.write(f'\n📁 MEDIA DIRECTORY STRUCTURE:')
        if os.path.exists(settings.MEDIA_ROOT):
            for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                level = root.replace(settings.MEDIA_ROOT, '').count(os.sep)
                indent = ' ' * 2 * level
                self.stdout.write(f'{indent}{os.path.basename(root)}/')
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    self.stdout.write(f'{subindent}{file}')
        else:
            self.stdout.write(f'❌ Media directory does not exist: {settings.MEDIA_ROOT}')
        
        self.stdout.write('\n' + '=' * 50)
