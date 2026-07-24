"""
South Sudan Election Monitoring Dashboard
Main Dash Application
"""

import os
import json
import logging
from datetime import datetime
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

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

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
)
server = app.server  # For gunicorn deployment

# Load sources configuration
def load_sources():
    """Load sources from JSON file"""
    try:
        with open('sources.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("sources.json not found!")
        return {"news": [], "government": [], "ngo": []}
    except json.JSONDecodeError:
        logger.error("Invalid JSON in sources.json!")
        return {"news": [], "government": [], "ngo": []}

SOURCES = load_sources()

# App Layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(
            html.Div([
                html.H1("🗳️ South Sudan Election Monitor", 
                       className="text-center text-primary mb-0"),
                html.P("Real-time election monitoring dashboard", 
                       className="text-center text-muted")
            ]),
            width=12
        )
    ], className="mb-4"),
    
    # Stats Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Total Sources", className="card-title"),
                html.H2(len(SOURCES.get('news', [])) + 
                       len(SOURCES.get('government', [])) + 
                       len(SOURCES.get('ngo', [])), 
                       className="text-primary")
            ])
        ]), md=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("News Sources", className="card-title"),
                html.H2(len(SOURCES.get('news', [])), className="text-success")
            ])
        ]), md=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Official Sources", className="card-title"),
                html.H2(len(SOURCES.get('government', [])), className="text-warning")
            ])
        ]), md=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("NGO Sources", className="card-title"),
                html.H2(len(SOURCES.get('ngo', [])), className="text-info")
            ])
        ]), md=3)
    ], className="mb-4"),
    
    # Tabs
    dbc.Tabs([
        dbc.Tab(label="News Sources", tab_id="tab-news", children=[
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("South Sudan News Sources", className="mt-3"),
                        html.Ul([
                            html.Li([
                                html.A(source['name'], href=source['url'], target="_blank"),
                                " - ",
                                html.Small(source.get('country', 'Unknown'), 
                                         className="badge badge-secondary"),
                                html.Br(),
                                html.Small(f"RSS: {source.get('rss', 'N/A')}", 
                                         className="text-muted")
                            ])
                            for source in SOURCES.get('news', [])
                        ], className="list-group list-group-flush")
                    ])
                ], md=8),
                dbc.Col([
                    html.Div([
                        html.H4("Source Distribution", className="mt-3"),
                        dcc.Graph(
                            figure=px.pie(
                                names=['News', 'Government', 'NGO'],
                                values=[
                                    len(SOURCES.get('news', [])),
                                    len(SOURCES.get('government', [])),
                                    len(SOURCES.get('ngo', []))
                                ],
                                title="Source Type Distribution"
                            )
                        )
                    ])
                ], md=4)
            ])
        ]),
        
        dbc.Tab(label="Official Sources", tab_id="tab-official", children=[
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("Government & Electoral Bodies", className="mt-3"),
                        html.Ul([
                            html.Li([
                                html.A(source['name'], href=source['url'], target="_blank"),
                                " - ",
                                html.Span(source.get('category', ''), 
                                        className="badge badge-info")
                            ])
                            for source in SOURCES.get('government', [])
                        ], className="list-group list-group-flush")
                    ])
                ], md=6),
                dbc.Col([
                    html.Div([
                        html.H4("NGOs & Organizations", className="mt-3"),
                        html.Ul([
                            html.Li([
                                html.A(source['name'], href=source['url'], target="_blank"),
                                " - ",
                                html.Span(source.get('category', ''), 
                                        className="badge badge-success")
                            ])
                            for source in SOURCES.get('ngo', [])
                        ], className="list-group list-group-flush")
                    ])
                ], md=6)
            ])
        ]),
        
        dbc.Tab(label="Reliability Analysis", tab_id="tab-reliability", children=[
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("Source Reliability Ratings", className="mt-3"),
                        dcc.Graph(
                            figure=px.bar(
                                x=list(SOURCES.get('reliability_ratings', {}).keys()),
                                y=[{'high': 3, 'medium': 2, 'low': 1}
                                   .get(v, 0) for v in SOURCES.get('reliability_ratings', {}).values()],
                                labels={'x': 'Source', 'y': 'Reliability Score'},
                                title="Source Reliability"
                            )
                        )
                    ])
                ], md=12),
                dbc.Col([
                    html.Div([
                        html.H4("Keyword Categories", className="mt-3"),
                        html.Div([
                            html.H6("Election Terms"),
                            html.P(", ".join(SOURCES.get('keywords', {})
                                           .get('election_related', [])[:10]))
                        ], className="mb-2"),
                        html.Div([
                            html.H6("Political Terms"),
                            html.P(", ".join(SOURCES.get('keywords', {})
                                           .get('political_related', [])[:10]))
                        ], className="mb-2"),
                        html.Div([
                            html.H6("Security Terms"),
                            html.P(", ".join(SOURCES.get('keywords', {})
                                           .get('security_related', [])[:10]))
                        ], className="mb-2")
                    ])
                ], md=12)
            ])
        ]),
        
        dbc.Tab(label="About", tab_id="tab-about", children=[
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("About This Dashboard", className="mt-3"),
                        html.P("""
                            The South Sudan Election Monitoring Dashboard aggregates news, 
                            official statements, and NGO reports to provide comprehensive 
                            coverage of the electoral process in South Sudan.
                        """),
                        html.H5("Features:"),
                        html.Ul([
                            html.Li("Real-time news aggregation from South Sudanese sources"),
                            html.Li("Official government and electoral body monitoring"),
                            html.Li("NGO and international organization reports"),
                            html.Li("Reliability scoring for different source types"),
                            html.Li("Keyword tracking for election-related terms")
                        ]),
                        html.H5("Data Sources:"),
                        html.P("Sources are curated from verified news outlets, "
                              "government websites, and reputable NGOs operating in South Sudan."),
                        html.Hr(),
                        html.P("Last Updated: " + 
                              datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                              className="text-muted")
                    ])
                ], md=12)
            ])
        ])
    ], id="tabs", active_tab="tab-news"),
    
    # Footer
    dbc.Row([
        dbc.Col(
            html.P("© 2026 South Sudan Election Monitor | Data refreshed hourly", 
                   className="text-center text-muted mt-4"),
            width=12
        )
    ])
], fluid=True, className="p-3")

# Callbacks
@callback(
    Output("tabs", "active_tab"),
    Input("tabs", "active_tab")
)
def update_tab(tab):
    """Handle tab switching"""
    logger.info(f"Tab changed to: {tab}")
    return tab

# Main entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    debug = os.environ.get('ENVIRONMENT', 'development') == 'development'
    
    logger.info(f"Starting app on port {port}")
    app.run(
        debug=debug,
        host='0.0.0.0',
        port=port
    )
