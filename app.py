"""
South Sudan Election Monitoring Dashboard
Enhanced with Visualizations & Election Prediction Engine
"""

import os
import sys
import json
import logging
import ssl
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

# Fix SSL for NLTK
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Fix import paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize NLTK
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)
try:
    nltk.data.find('corpora/brown')
except LookupError:
    nltk.download('brown', quiet=True)

# Import custom modules
try:
    from scrapers.news_scraper import NewsScraper
    from utils.data_processor import DataProcessor
except ImportError as e:
    logger.error(f"Import error: {e}")
    # Create dummy classes if import fails
    class NewsScraper:
        def get_all_news(self):
            return []
    class DataProcessor:
        def categorize_articles(self, articles):
            return pd.DataFrame()
        def analyze_sentiment(self, texts):
            return ['Neutral'] * len(texts)
        def get_sentiment_emoji(self, text):
            return "😐"
        def calculate_election_probability(self, articles):
            return {'probability': 50, 'articles_analyzed': 0}

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
)
server = app.server

# Initialize scrapers
news_scraper = NewsScraper()
data_processor = DataProcessor()

# Load sources
def load_sources():
    try:
        sources_path = os.path.join(os.path.dirname(__file__), 'sources.json')
        with open(sources_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading sources: {e}")
        return {"news": [], "government": [], "ngo": []}

SOURCES = load_sources()

# Election Prediction Engine
class ElectionPredictor:
    """Analyze scraped data to predict election likelihood"""
    
    def __init__(self):
        self.target_date = datetime(2026, 12, 22)
        self.current_date = datetime.now()
        self.days_remaining = (self.target_date - self.current_date).days
        self.predictors = {
            'readiness_score': 0.0,
            'stability_score': 0.0,
            'political_will_score': 0.0,
            'international_support_score': 0.0,
            'logistical_readiness_score': 0.0,
            'security_score': 0.0
        }
        self.scores = {}
        
    def calculate_readiness(self, articles_data):
        """Calculate election readiness based on news data"""
        if not articles_data:
            return self._default_scores()
        
        scores = {}
        total_articles = len(articles_data)
        
        if total_articles == 0:
            return self._default_scores()
        
        # Score based on keyword frequency
        readiness_keywords = ['ready', 'prepared', 'progress', 'on track', 'timeline']
        stability_keywords = ['peace', 'stable', 'security', 'calm']
        political_keywords = ['kiir', 'machar', 'agreement', 'dialogue', 'negotiation']
        international_keywords = ['unmiss', 'un', 'au', 'igad', 'support']
        logistics_keywords = ['registration', 'voter', 'logistics', 'budget', 'infrastructure']
        security_keywords = ['violence', 'conflict', 'unrest', 'attack', 'dispute']
        
        def count_keywords(text, keywords):
            text_lower = str(text).lower()
            return sum(1 for keyword in keywords if keyword in text_lower)
        
        # Calculate scores
        readiness_count = sum(count_keywords(article.get('title', '') + article.get('description', ''), 
                          readiness_keywords) for article in articles_data)
        stability_count = sum(count_keywords(article.get('title', '') + article.get('description', ''), 
                         stability_keywords) for article in articles_data)
        political_count = sum(count_keywords(article.get('title', '') + article.get('description', ''), 
                         political_keywords) for article in articles_data)
        international_count = sum(count_keywords(article.get('title', '') + article.get('description', ''), 
                             international_keywords) for article in articles_data)
        logistics_count = sum(count_keywords(article.get('title', '') + article.get('description', ''), 
                         logistics_keywords) for article in articles_data)
        security_count = sum(count_keywords(article.get('title', '') + article.get('description', ''), 
                         security_keywords) for article in articles_data)
        
        # Normalize scores (0-100)
        max_occurrences = max(1, total_articles * 0.3)
        
        scores['readiness'] = min(100, (readiness_count / max_occurrences) * 100)
        scores['stability'] = min(100, (stability_count / max_occurrences) * 100)
        scores['political'] = min(100, (political_count / max_occurrences) * 100)
        scores['international'] = min(100, (international_count / max_occurrences) * 100)
        scores['logistics'] = min(100, (logistics_count / max_occurrences) * 100)
        scores['security'] = min(100, 100 - (security_count / max_occurrences) * 100)
        
        return scores
    
    def _default_scores(self):
        """Return default scores when no data is available"""
        return {
            'readiness': 50,
            'stability': 50,
            'political': 50,
            'international': 50,
            'logistics': 50,
            'security': 50
        }
    
    def predict_election_likelihood(self, articles_data):
        """Predict if elections will be held by Dec 22, 2026"""
        scores = self.calculate_readiness(articles_data)
        self.scores = scores
        
        # Weighted average
        weights = {
            'readiness': 0.25,
            'stability': 0.15,
            'political': 0.20,
            'international': 0.10,
            'logistics': 0.20,
            'security': 0.10
        }
        
        final_score = sum(scores[key] * weights.get(key, 0.1) for key in scores)
        self.final_score = final_score
        
        # Time factor (closer to date = higher urgency)
        days_factor = min(1.0, max(0.0, self.days_remaining / 365))
        adjusted_score = final_score * (0.7 + 0.3 * days_factor)
        
        # Determine prediction
        if adjusted_score >= 70:
            prediction = "YES ✅"
            confidence = "High"
            probability = min(95, adjusted_score)
        elif adjusted_score >= 50:
            prediction = "MAYBE 🤔"
            confidence = "Medium"
            probability = adjusted_score
        else:
            prediction = "NO ❌"
            confidence = "Low"
            probability = max(5, adjusted_score)
        
        # Source reliability adjustment
        reliability_weight = 1.0
        source_count = len(articles_data)
        if source_count > 20:
            reliability_weight = 1.1
        elif source_count > 10:
            reliability_weight = 1.0
        else:
            reliability_weight = 0.8
        
        adjusted_probability = min(100, probability * reliability_weight)
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'probability': round(adjusted_probability, 1),
            'final_score': round(final_score, 1),
            'scores': scores,
            'days_remaining': self.days_remaining,
            'target_date': self.target_date.strftime('%B %d, %Y'),
            'articles_analyzed': len(articles_data)
        }

predictor = ElectionPredictor()

# App Layout (keep existing layout)
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(
            html.Div([
                html.H1("🗳️ South Sudan Election Monitor 2026", 
                       className="text-center text-primary mb-0"),
                html.P(f"Counting down to December 22, 2026 | {predictor.days_remaining} days remaining", 
                       className="text-center text-muted"),
                html.Hr()
            ]),
            width=12
        )
    ]),
    
    # Prediction Dashboard
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Election Prediction", className="mb-0")),
                dbc.CardBody([
                    html.Div(id='prediction-result', className="text-center"),
                    html.P(id='prediction-confidence', className="text-center"),
                    html.Div([
                        dbc.Progress(id='prediction-progress', value=50, 
                                   className="mb-2", style={'height': '30px'}),
                    ]),
                    html.P(id='prediction-details', className="text-center text-muted")
                ])
            ], className="mb-3 shadow")
        ], md=12)
    ]),
    
    # Key Metrics Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Readiness Score", className="text-muted"),
                html.H2(id='metric-readiness', children="--", className="text-primary"),
                dbc.Progress(id='progress-readiness', value=50, className="mb-1")
            ])
        ]), md=2),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Stability Score", className="text-muted"),
                html.H2(id='metric-stability', children="--", className="text-success"),
                dbc.Progress(id='progress-stability', value=50, className="mb-1")
            ])
        ]), md=2),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Political Will", className="text-muted"),
                html.H2(id='metric-political', children="--", className="text-warning"),
                dbc.Progress(id='progress-political', value=50, className="mb-1")
            ])
        ]), md=2),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Logistics", className="text-muted"),
                html.H2(id='metric-logistics', children="--", className="text-info"),
                dbc.Progress(id='progress-logistics', value=50, className="mb-1")
            ])
        ]), md=2),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Security", className="text-muted"),
                html.H2(id='metric-security', children="--", className="text-danger"),
                dbc.Progress(id='progress-security', value=50, className="mb-1")
            ])
        ]), md=2),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Sources Analyzed", className="text-muted"),
                html.H2(id='metric-sources', children="0", className="text-secondary")
            ])
        ]), md=2)
    ], className="mb-4"),
    
    # Charts Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Election Readiness Dashboard", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='readiness-radar')
                ])
            ], className="shadow")
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Category Scores", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='readiness-bar')
                ])
            ], className="shadow")
        ], md=6)
    ], className="mb-4"),
    
    # News Feed with Sentiment
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Latest News & Sentiment Analysis", className="mb-0"),
                    dbc.Button("🔄 Refresh Data", id="refresh-button", 
                              color="primary", size="sm", className="float-end")
                ]),
                dbc.CardBody([
                    html.Div(id='news-feed', style={'maxHeight': '400px', 'overflowY': 'auto'})
                ])
            ], className="shadow")
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Sentiment Analysis", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='sentiment-pie')
                ])
            ], className="shadow"),
            dbc.Card([
                dbc.CardHeader(html.H5("Keyword Frequency", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='keyword-bar')
                ])
            ], className="shadow mt-3")
        ], md=6)
    ], className="mb-4"),
    
    # Data Table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Scraped Data Sample", className="mb-0")),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='data-table',
                        columns=[
                            {"name": "Title", "id": "title"},
                            {"name": "Source", "id": "source"},
                            {"name": "Date", "id": "date"},
                            {"name": "Category", "id": "category"},
                            {"name": "Sentiment", "id": "sentiment"}
                        ],
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left', 'maxWidth': '200px'},
                        style_header={'backgroundColor': '#2c3e50', 'color': 'white'},
                        page_size=10
                    )
                ])
            ], className="shadow")
        ], md=12)
    ], className="mb-4"),
    
    # Sources Overview
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Source Distribution", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='source-pie')
                ])
            ], className="shadow")
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Source Reliability", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id='reliability-chart')
                ])
            ], className="shadow")
        ], md=6)
    ], className="mb-4"),
    
    # Auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=3600000,
        n_intervals=0
    ),
    
    # Hidden store for data
    dcc.Store(id='stored-data', data={}),
    
    # Footer
    dbc.Row([
        dbc.Col(
            html.P(f"© 2026 South Sudan Election Monitor | Data updated hourly | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                   className="text-center text-muted mt-4"),
            width=12
        )
    ])
], fluid=True, className="p-3")

# Callbacks
@callback(
    [Output('prediction-result', 'children'),
     Output('prediction-confidence', 'children'),
     Output('prediction-progress', 'value'),
     Output('prediction-progress', 'color'),
     Output('prediction-details', 'children'),
     Output('metric-readiness', 'children'),
     Output('metric-stability', 'children'),
     Output('metric-political', 'children'),
     Output('metric-logistics', 'children'),
     Output('metric-security', 'children'),
     Output('metric-sources', 'children'),
     Output('progress-readiness', 'value'),
     Output('progress-stability', 'value'),
     Output('progress-political', 'value'),
     Output('progress-logistics', 'value'),
     Output('progress-security', 'value'),
     Output('readiness-radar', 'figure'),
     Output('readiness-bar', 'figure'),
     Output('sentiment-pie', 'figure'),
     Output('keyword-bar', 'figure'),
     Output('source-pie', 'figure'),
     Output('reliability-chart', 'figure'),
     Output('news-feed', 'children'),
     Output('data-table', 'data')],
    [Input('interval-component', 'n_intervals'),
     Input('refresh-button', 'n_clicks')]
)
def update_dashboard(n_intervals, n_clicks):
    """Update all dashboard components with scraped data"""
    
    # Scrape news data
    try:
        articles_data = news_scraper.get_all_news()
        logger.info(f"Scraped {len(articles_data)} articles")
    except Exception as e:
        logger.error(f"Error scraping: {e}")
        articles_data = []
    
    # Process data
    if articles_data:
        try:
            df = data_processor.categorize_articles(articles_data)
            sentiments = data_processor.analyze_sentiment(df['title'].tolist() if 'title' in df else [])
            df['sentiment'] = sentiments
            data_dict = df.to_dict('records')
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            df = pd.DataFrame()
            data_dict = []
    else:
        df = pd.DataFrame()
        data_dict = []
    
    # Run prediction
    prediction = predictor.predict_election_likelihood(articles_data)
    
    # Format prediction display
    if prediction['prediction'] == "YES ✅":
        color = "success"
        icon = "✅"
    elif prediction['prediction'] == "MAYBE 🤔":
        color = "warning"
        icon = "🤔"
    else:
        color = "danger"
        icon = "❌"
    
    prediction_text = html.H2([
        html.Span(f"{icon} {prediction['prediction']}", 
                 className=f"text-{color}")
    ])
    
    confidence_text = html.P([
        f"Confidence: {prediction['confidence']} | ",
        f"Probability: {prediction['probability']}% | ",
        f"Score: {prediction['final_score']}/100"
    ], className=f"text-{color}")
    
    progress_value = prediction['probability']
    progress_color = "success" if progress_value >= 70 else "warning" if progress_value >= 50 else "danger"
    
    details_text = html.Small([
        f"Based on {prediction['articles_analyzed']} articles | ",
        f"{prediction['days_remaining']} days until {prediction['target_date']}"
    ])
    
    # Extract scores
    scores = prediction.get('scores', {})
    readiness = scores.get('readiness', 50)
    stability = scores.get('stability', 50)
    political = scores.get('political', 50)
    logistics = scores.get('logistics', 50)
    security = scores.get('security', 50)
    
    # Create Radar Chart
    radar_fig = go.Figure(data=go.Scatterpolar(
        r=[readiness, stability, political, logistics, security, readiness],
        theta=['Readiness', 'Stability', 'Political Will', 'Logistics', 'Security', 'Readiness'],
        fill='toself',
        name='Election Readiness',
        line_color='#3498db'
    ))
    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Election Readiness Radar",
        height=400
    )
    
    # Create Bar Chart
    bar_fig = go.Figure(data=[
        go.Bar(
            x=['Readiness', 'Stability', 'Political Will', 'Logistics', 'Security'],
            y=[readiness, stability, political, logistics, security],
            marker_color=['#3498db', '#2ecc71', '#f39c12', '#1abc9c', '#e74c3c']
        )
    ])
    bar_fig.update_layout(
        title="Category Scores",
        yaxis_title="Score",
        yaxis_range=[0, 100],
        height=400
    )
    
    # Sentiment Analysis
    if not df.empty and 'sentiment' in df.columns:
        sentiment_counts = df['sentiment'].value_counts()
        sentiment_fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Article Sentiment Distribution",
            color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#f39c12'}
        )
    else:
        sentiment_fig = px.pie(values=[1], names=['No Data'], title="No Sentiment Data Available")
    
    # Keyword Frequency
    keyword_data = SOURCES.get('keywords', {})
    election_keywords = keyword_data.get('election_related', [])[:10]
    keyword_counts = []
    for keyword in election_keywords:
        count = sum(1 for article in articles_data 
                   if keyword.lower() in str(article.get('title', '')).lower())
        keyword_counts.append(count)
    
    keyword_fig = go.Figure(data=[
        go.Bar(x=election_keywords, y=keyword_counts, marker_color='#3498db')
    ])
    keyword_fig.update_layout(
        title="Election Keyword Frequency",
        xaxis_title="Keyword",
        yaxis_title="Occurrences",
        height=300
    )
    
    # Source Distribution
    source_types = {
        'News': len(SOURCES.get('news', [])),
        'Government': len(SOURCES.get('government', [])),
        'NGO': len(SOURCES.get('ngo', []))
    }
    source_fig = px.pie(
        values=list(source_types.values()),
        names=list(source_types.keys()),
        title="Source Type Distribution",
        color_discrete_map={'News': '#3498db', 'Government': '#2ecc71', 'NGO': '#f39c12'}
    )
    
    # Reliability Chart
    reliability_data = SOURCES.get('reliability_ratings', {})
    reliability_counts = {'High': 0, 'Medium': 0, 'Low': 0}
    for rating in reliability_data.values():
        if rating in reliability_counts:
            reliability_counts[rating] += 1
    
    reliability_fig = go.Figure(data=[
        go.Bar(
            x=list(reliability_counts.keys()),
            y=list(reliability_counts.values()),
            marker_color=['#2ecc71', '#f39c12', '#e74c3c']
        )
    ])
    reliability_fig.update_layout(
        title="Source Reliability Distribution",
        xaxis_title="Reliability Level",
        yaxis_title="Number of Sources",
        height=300
    )
    
    # News Feed
    news_items = []
    for article in articles_data[:20]:
        title = article.get('title', 'No Title')
        source = article.get('source', 'Unknown')
        try:
            sentiment = data_processor.get_sentiment_emoji(title)
        except:
            sentiment = "😐"
        news_items.append(html.Div([
            html.Small(f"[{source}]", className="text-muted"),
            html.Span(f" {sentiment} ", className="mx-1"),
            html.A(title, href=article.get('link', '#'), target="_blank"),
            html.Br()
        ], className="mb-2"))
    
    if not news_items:
        news_items = [html.P("No news articles available. Please refresh.", className="text-muted")]
    
    # Return all values
    return (
        prediction_text,
        confidence_text,
        progress_value,
        progress_color,
        details_text,
        f"{readiness:.1f}%",
        f"{stability:.1f}%",
        f"{political:.1f}%",
        f"{logistics:.1f}%",
        f"{security:.1f}%",
        len(articles_data),
        readiness,
        stability,
        political,
        logistics,
        security,
        radar_fig,
        bar_fig,
        sentiment_fig,
        keyword_fig,
        source_fig,
        reliability_fig,
        news_items,
        data_dict
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    debug = os.environ.get('ENVIRONMENT', 'development') == 'development'
    
    logger.info(f"Starting app on port {port}")
    app.run(
        debug=debug,
        host='0.0.0.0',
        port=port
    )