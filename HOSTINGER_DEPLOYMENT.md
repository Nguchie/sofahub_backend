# Hostinger Django Deployment Guide

## Prerequisites
1. Hostinger hosting account with Python support
2. MySQL database created in Hostinger control panel
3. Domain name configured

## Step 1: Upload Your Code
1. Upload all your Django project files to the `public_html` directory
2. Make sure `passenger_wsgi.py` and `.htaccess` are in the root directory

## Step 2: Configure Environment Variables
1. Create a `.env` file in your project root (copy from `env_template.txt`)
2. Update the following values:
   - `SECRET_KEY`: Generate a new secret key for production
   - `ALLOWED_HOSTS`: Your domain name
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Your MySQL database credentials
   - `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Your email credentials
   - `MPESA_*`: Your M-Pesa API credentials

## Step 3: Update .htaccess File
Update the `.htaccess` file with your actual Hostinger details:
- Replace `u123456789` with your Hostinger username
- Replace `yourdomain.com` with your actual domain
- Update the Python path if needed

## Step 4: Install Dependencies
1. SSH into your Hostinger account
2. Navigate to your project directory
3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Step 5: Database Setup
1. Run migrations:
   ```bash
   python manage.py migrate
   ```
2. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
3. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

## Step 6: Configure Passenger
1. In Hostinger control panel, enable Python support
2. Set the startup file to `passenger_wsgi.py`
3. Set the Python version (3.9 or higher)

## Step 7: Test Your Deployment
1. Visit your domain to test the API
2. Check that static files are being served correctly
3. Test your API endpoints

## Troubleshooting
- Check Hostinger error logs if the site doesn't load
- Ensure all environment variables are set correctly
- Verify database connection settings
- Check that all required packages are installed

## Security Notes
- Never commit `.env` file to version control
- Use strong passwords for database and admin accounts
- Enable HTTPS for production
- Keep Django and all packages updated
