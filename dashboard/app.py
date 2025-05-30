import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from datetime import datetime, timedelta
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import plotly.express as px
import io
import os

def safe_text(text):
    """Sanitize text by replacing unsupported characters with 'replace' strategy"""
    return text.encode('latin-1', 'replace').decode('latin-1')

def create_pdf_report(df, pie_chart_path, line_chart_path):
    # Create a BytesIO buffer to store the PDF data
    pdf_buffer = io.BytesIO()

    # Create a canvas to draw the PDF
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    # Add title and summary text
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, "Market Sentiment Report")
    
    c.drawString(100, 730, "Summary:")
    c.drawString(100, 710, f"Total articles: {len(df)}")
    c.drawString(100, 690, f"Average sentiment: {df['sentiment_score'].mean():.3f}")

    # Add Pie Chart Image
    c.drawImage(pie_chart_path, 100, 500, width=400, height=200)  # Adjust size and position
    c.showPage()  # Start new page for next content

    # Add Time Series Line Chart Image
    c.drawImage(line_chart_path, 100, 500, width=400, height=200)  # Adjust size and position
    c.showPage()  # Start new page for next content

    # Add top positive headlines
    c.drawString(100, 750, "Top 5 Positive Headlines:")
    y_position = 730
    top_pos = df.sort_values('sentiment_score', ascending=False).head(5)
    for _, row in top_pos.iterrows():
        text = f"- [{row['sector']}] {row['title']} ({row['sentiment_score']:.2f})"
        c.drawString(100, y_position, safe_text(text))
        y_position -= 20

    c.showPage()  # Start new page for next content

    # Add top negative headlines
    c.drawString(100, 750, "Top 5 Negative Headlines:")
    y_position = 730
    top_neg = df.sort_values('sentiment_score').head(5)
    for _, row in top_neg.iterrows():
        text = f"- [{row['sector']}] {row['title']} ({row['sentiment_score']:.2f})"
        c.drawString(100, y_position, safe_text(text))
        y_position -= 20

    # Save the PDF to the buffer
    c.save()

    # Move buffer cursor to the beginning for reading
    pdf_buffer.seek(0)

    # Delete the temporary chart images
    os.remove(pie_chart_path)
    os.remove(line_chart_path)

    # Return the PDF buffer for downloading
    return pdf_buffer

# Use correct DB host (update as needed)
engine = create_engine("postgresql://postgres:postgres@sentiment-postgres:5432/newsdb")

@st.cache_data(ttl=1000)
def load_articles(sector=None):
    query = """
    SELECT title, sector, sentiment, sentiment_score, published_at
    FROM articles
    WHERE published_at IS NOT NULL
    """
    if sector:
        query += f" AND sector = '{sector}'"
    query += " ORDER BY published_at DESC LIMIT 1000"
    return pd.read_sql(query, engine)

st.title("Market Sentiment Dashboard")

# Load data
sectors = ['AI', 'EV', 'Green Energy', 'Fashion Tech', 'Healthcare', 'FinTech', 'EdTech', 'Cybersecurity', 
'Gaming', 'Food Tech', 'Real Estate Tech', 'Travel Tech', 'Logistics Tech', 'Biotech', 'Retail Tech', 
'Smart Cities', 'Space Tech', 'Quantum Computing', 'Robotics', 'Blockchain', 'Sustainability', 'Augmented Reality', 
'Virtual Reality', '5G Technology', 'Wearable Tech', 'Cloud Computing', 'Internet of Things', 'Digital Marketing', 
'Content Creation', 'Social Media', 'Data Science', 'Machine Learning', 'Natural Language Processing', 'DevOps']
selected_sector = st.sidebar.selectbox("Select Sector", sectors)

df = load_articles(selected_sector if selected_sector != "All" else None)

# Display articles
st.write(f"Articles for sector: {selected_sector if selected_sector != 'All' else 'All sectors'}")
st.write(df)

if df.empty:
    st.warning("No articles found for the selected filters.")
else:

    # Convert published_at to datetime
    df['published_at'] = pd.to_datetime(df['published_at'])

    # Sidebar filters
    sectors = sorted(df['sector'].dropna().unique().tolist())
    selected_sector = st.sidebar.selectbox("Select Sector", options=["All"] + sectors)

    # Date filter: last 30 days by default
    # Get min and max dates from data

    min_date = df['published_at'].min().date()
    max_date = df['published_at'].max().date()

    # If only one date available, allow a wider range around it
    if min_date == max_date:
        min_date = min_date - datetime.timedelta(days=7)
        max_date = max_date + datetime.timedelta(days=7)

    default_start = max(max_date - timedelta(days=30), min_date)

    start_date = st.sidebar.date_input(
        "Start date",
        value=default_start,
        min_value=min_date,
        max_value=max_date,
    )

    end_date = st.sidebar.date_input(
        "End date",
        value=max_date if max_date >= start_date else start_date,
        min_value=start_date,
        max_value=max_date,
    )

    # Filter data
    filtered_df = df[(df['published_at'] >= pd.Timestamp(start_date)) & (df['published_at'] <= pd.Timestamp(end_date))]

    st.markdown("### Articles Data Summary")

    total_articles = len(filtered_df)
    unique_sectors = filtered_df['sector'].nunique()
    date_range_start = filtered_df['published_at'].min()
    date_range_end = filtered_df['published_at'].max()

    st.write(f"- Total articles displayed: **{total_articles}**")
    st.write(f"- Number of sectors covered: **{unique_sectors}**")
    st.write(f"- Date range: **{date_range_start.date()}** to **{date_range_end.date()}**")
    avg_sentiment = filtered_df['sentiment_score'].mean()
    st.write(f"- Average sentiment score: **{avg_sentiment:.3f}**")

    if selected_sector != "All":
        filtered_df = filtered_df[filtered_df['sector'] == selected_sector]

    st.subheader(f"Articles count: {len(filtered_df)}")

    # Sentiment distribution pie chart
    sentiment_counts = filtered_df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']

    # Create Pie chart
    fig_pie = px.pie(sentiment_counts, values='Count', names='Sentiment', title="Sentiment Distribution",
                    color='Sentiment', color_discrete_map={"positive": "green", "negative": "red", "neutral": "grey"})

    # Save Pie chart as PNG
    pie_chart_path = "/tmp/sentiment_pie_chart.png"
    fig_pie.write_image(pie_chart_path)

    st.plotly_chart(fig_pie,key='senti_pie')

    # Time series: average sentiment score by day
    if not filtered_df.empty:
        time_series = (
            filtered_df
            .set_index('published_at')
            .resample('D')
            .sentiment_score.mean()
            .reset_index()
        )

        fig_line = px.line(time_series, x='published_at', y='sentiment_score',
                        title="Average Sentiment Score Over Time",
                        labels={"published_at": "Date", "sentiment_score": "Avg Sentiment Score"})
        st.plotly_chart(fig_line,key='senti_line')
        # Save Line chart as PNG
        line_chart_path = "/tmp/sentiment_time_series.png"
        fig_line.write_image(line_chart_path)
    else:
        st.info("No data available for the selected filters.")

    fig_hist = px.histogram(filtered_df, x='sentiment_score', nbins=30, title="Sentiment Score Distribution")
    st.plotly_chart(fig_hist, key="senti_hist")

    # Top 5 positive and negative articles
    st.subheader("Top 5 Positive Headlines")
    top_positive = filtered_df.sort_values('sentiment_score', ascending=False).head(5)
    for _, row in top_positive.iterrows():
        st.markdown(f"**[{row['sector']}]** {row['title']} ({row['sentiment_score']:.2f}) — *{row['published_at'].strftime('%Y-%m-%d')}*")

    st.subheader("Top 5 Negative Headlines")
    top_negative = filtered_df.sort_values('sentiment_score').head(5)
    for _, row in top_negative.iterrows():
        st.markdown(f"**[{row['sector']}]** {row['title']} ({row['sentiment_score']:.2f}) — *{row['published_at'].strftime('%Y-%m-%d')}*")



    summary_text = (
        f"Total articles: {total_articles}\n"
        f"Sectors covered: {unique_sectors}\n"
        f"Date range: {date_range_start.date()} to {date_range_end.date()}\n"
        f"Average sentiment: {avg_sentiment:.3f}"
    )

    # Example of using the function
    pdf_buffer = create_pdf_report(filtered_df, summary_text)

    # Streamlit download button for PDF
    st.download_button(
        label="Download Report as PDF",
        data=pdf_buffer,
        file_name="market_sentiment_report.pdf",
        mime="application/pdf"
    )
