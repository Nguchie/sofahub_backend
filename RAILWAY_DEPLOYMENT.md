# Environment Variables for Railway Deployment

## Required Environment Variables

### Django Settings
- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts (include your Railway domain)

### Database Configuration
Railway will automatically provide `DATABASE_URL`. If you prefer individual settings:
- `DB_NAME`: Database name
- `DB_USER`: Database username  
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port (default: 3306)

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
