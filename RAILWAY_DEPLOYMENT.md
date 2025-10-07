# Environment Variables for Railway Deployment

## Required Environment Variables

### Django Settings
- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts (include your Railway domain)

### Database Configuration
**SQLite3 Database**: No additional database configuration needed!
- SQLite3 database file (`db.sqlite3`) will be created automatically
- No separate database service required
- Database file persists with your deployment

### Email Configuration
- `EMAIL_HOST_USER`: Your Gmail address
- `EMAIL_HOST_PASSWORD`: Gmail app password

### M-Pesa Configuration
- `MPESA_ENVIRONMENT`: `sandbox` or `production`
- `MPESA_CONSUMER_KEY`: M-Pesa consumer key
- `MPESA_CONSUMER_SECRET`: M-Pesa consumer secret
- `MPESA_SHORTCODE`: M-Pesa shortcode
- `MPESA_PASSKEY`: M-Pesa passkey
- `MPESA_CALLBACK_URL`: Your Railway domain + `/api/orders/mpesa-callback/`

## Setting Environment Variables in Railway

1. Go to your Railway project dashboard
2. Click on your service
3. Go to the "Variables" tab
4. Add each environment variable with its value
5. Railway will automatically restart your service

## Database Migration

After deployment, run migrations to set up your database:
```bash
python manage.py migrate
```
