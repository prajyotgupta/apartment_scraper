# 🤖 PB-bot: Your Friendly Neighborhood Apartment Scanner

*beep boop* Hello humans! I'm PB-bot, your automated apartment-hunting companion! 

## 🎯 My Mission
I tirelessly scan configured apartments to find the perfect 2 bed/2 bath home for my friend Hedge and his companions. I'm like a ninja 🥷, but for apartments!

## 🔍 What I Do
- Scout for 2 bed/2 bath units
- Filter by your preferred price range ($3,000-$4,200; can be configured)
- Send beautiful HTML emails with apartment details
- Include random jokes about Hedge (because why not? 😄)
- Attach CSV files for the spreadsheet lovers

## 🛠️ How to Make Me Work

### Prerequisites
```bash
# I run on Python 3.8+ and need these packages to function:
python3 -m pip install pandas selenium python-dotenv beautifulsoup4 webdriver-manager
```

### 🔐 Configuration (Shhh... it's a secret!)

1. First, clone my repository:
```bash
git clone https://github.com/yourusername/apartment_scraper.git
cd apartment_scraper
```

2. Create my secret files:
```bash
cp config/config.template.json config/config.json
cp .env.template .env
```

3. Update `.env` with your email settings:
```bash
EMAIL_APP_PASSWORD=your_gmail_app_password
EMAIL_SENDER=your-email@gmail.com
EMAIL_RECEIVERS=email1@gmail.com,email2@gmail.com
```

To get your Gmail App Password:
1. Go to Google Account settings
2. Enable 2-Step Verification
3. Go to Security → App Passwords
4. Generate new App Password for "Mail"

### 🚀 Running Me

```bash
# One-time scan:
python3 irvine_scraper.py  # First, get the apartment data
python3 email_alert.py     # Then, I'll send my report!

# Or set me up as a cron job (I love working 24/7!):
*/30 * * * * cd /path/to/apartment_scraper && python3 irvine_scraper.py && python3 email_alert.py
```

## 📧 What You'll Get
- Regular email updates with available apartments
- Prices sorted for easy viewing
- Fun bot messages (I'm quite charming! 🤖)
- Random Hedge jokes (I'm also quite funny!)
- CSV attachments for data analysis

## 🎛️ Customization
Edit `config/config.json` to modify:
- Price range filters
- Apartment configurations
- Scan interval
- URL and selectors

## 🛟 Troubleshooting

If I'm not working properly:
1. Check if `.env` has correct email credentials
2. Ensure all packages are installed
3. Verify internet connection
4. Make sure Gmail's "Less secure app access" is enabled
5. If I'm still misbehaving, check the error messages (I try to be descriptive!)

## 🤝 Contributing
Found a way to make me smarter? Create a pull request! Just remember:
- Keep sensitive data out of the repository
- Use the template files for configuration
- Test your changes before submitting

## 📝 License
I'm free to help anyone! (MIT License)

---
*Beep boop* - Made with ❤️ by PB-bot 🤖
"Helping Hedge find his dream apartment, one scan at a time!"
