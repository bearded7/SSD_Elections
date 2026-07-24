# South Sudan Election Monitor

A comprehensive election monitoring dashboard for South Sudan, aggregating news, official statements, and NGO reports.

## Features

- 📰 Real-time news aggregation from South Sudanese sources
- 🏛️ Official government and electoral body monitoring
- 🌍 NGO and international organization reports
- 📊 Source reliability scoring
- 🔍 Keyword tracking for election-related terms
- 📱 Mobile-responsive design

## Technology Stack

- **Framework**: Dash/Plotly
- **Scraping**: BeautifulSoup4, Requests
- **Data Processing**: Pandas, Numpy
- **Deployment**: Render.com
- **Language**: Python 3.9+

## Local Development

### Installation

```bash
# Clone repository
git clone https://github.com/bearded7/SSD_Elections.git
cd SSD_Elections

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run locally
python app.py
