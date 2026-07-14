import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(
    page_title="AI Business Analyst Agent",
    layout="wide"
)

st.title("AI Business Analyst Agent")

st.write(
    "Upload a CSV file to analyze business data, view KPIs, create charts, and ask basic business questions."
)

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    conn=sqlite3.connect("business_data.db")
    df.to_sql("business_data", conn, index=False, if_exists="replace")   

    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    categorical_columns = df.select_dtypes(include=["object"]).columns.tolist()

    st.subheader("Data Preview")
    st.dataframe(df.head())

    st.subheader("Dataset Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Rows", df.shape[0])

    with col2:
        st.metric("Columns", df.shape[1])

    st.subheader("Column Names")
    st.write(list(df.columns))

    st.subheader("Missing Values")
    st.write(df.isnull().sum())

    st.subheader("Basic Statistics")
    st.write(df.describe())

    st.subheader("Business KPI Summary")

    if len(numeric_columns) > 0:
        selected_metric = st.selectbox(
            "Choose a numeric column to analyze",
            numeric_columns,
            key="selected_metric"
        )

        total_value = df[selected_metric].sum()
        average_value = df[selected_metric].mean()
        median_value = df[selected_metric].median()
        max_value = df[selected_metric].max()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total", round(total_value, 2))

        with col2:
            st.metric("Average", round(average_value, 2))

        with col3:
            st.metric("Median", round(median_value, 2))

        with col4:
            st.metric("Highest Value", round(max_value, 2))

        st.subheader("Data Visualization")

        chart_metric = st.selectbox(
            "Choose a numeric column to chart",
            numeric_columns,
            key="chart_metric"
        )

        st.write(f"Distribution of {chart_metric}")
        st.bar_chart(df[chart_metric])

        if len(categorical_columns) > 0:
            category_column = st.selectbox(
                "Choose a category column to compare",
                categorical_columns,
                key="category_chart"
            )

            grouped_data = (
                df.groupby(category_column)[chart_metric]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            st.write(f"Top 10 {category_column} by {chart_metric}")
            st.bar_chart(grouped_data)
        else:
            st.info("No category columns found for comparison charts.")

        st.subheader("Automated Business Insights")

        insight_metric = st.selectbox(
            "Choose a metric for insights",
            numeric_columns,
            key="insight_metric"
        )

        total = df[insight_metric].sum()
        average = df[insight_metric].mean()
        median = df[insight_metric].median()
        highest = df[insight_metric].max()
        lowest = df[insight_metric].min()

        st.write(f"Total {insight_metric}: {round(total, 2)}")
        st.write(f"Average {insight_metric}: {round(average, 2)}")
        st.write(f"Median {insight_metric}: {round(median, 2)}")
        st.write(f"Highest {insight_metric}: {round(highest, 2)}")
        st.write(f"Lowest {insight_metric}: {round(lowest, 2)}")

        if average > median:
            st.success(
                f"The average {insight_metric} is higher than the median, which means a few high values may be pulling the average upward."
            )
        elif average < median:
            st.info(
                f"The average {insight_metric} is lower than the median, which means lower values may be affecting overall performance."
            )
        else:
            st.info(
                f"The average and median for {insight_metric} are close, which means the data is fairly balanced."
            )

        if len(categorical_columns) > 0:
            insight_category = st.selectbox(
                "Choose a category for insight comparison",
                categorical_columns,
                key="insight_category"
            )

            top_category = (
                df.groupby(insight_category)[insight_metric]
                .sum()
                .sort_values(ascending=False)
                .head(1)
            )

            top_name = top_category.index[0]
            top_value = top_category.iloc[0]

            st.success(
                f"The top {insight_category} by {insight_metric} is {top_name}, with a total of {round(top_value, 2)}."
            )

        st.subheader("Ask a Business Question")

        user_question = st.text_input(
            "Ask a question about the dataset",
            placeholder="Example: What is the total Sales?"
        )

        if user_question:
            question_lower = user_question.lower()

            question_metric = insight_metric

            for column in numeric_columns:
                if column.lower() in question_lower:
                    question_metric = column

            if "top" in question_lower and len(categorical_columns) > 0:
                st.write(f"Here are the top categories by {question_metric}:")

                top_result = (
                    df.groupby(categorical_columns[0])[question_metric]
                    .sum()
                    .sort_values(ascending=False)
                    .head(5)
                )

                st.write(top_result)

            elif "average" in question_lower or "mean" in question_lower:
                st.write(
                    f"The average {question_metric} is {round(df[question_metric].mean(), 2)}."
                )

            elif "total" in question_lower or "sum" in question_lower:
                st.write(
                    f"The total {question_metric} is {round(df[question_metric].sum(), 2)}."
                )

            elif "recommend" in question_lower or "focus" in question_lower:
                st.write(
                    f"Based on the data, the business should review low-performing categories by {question_metric}, compare them against top performers, and look for pricing, demand, or operational issues."
                )

            else:
                st.write(
                    "I found your question. This version answers questions about totals, averages, top categories, and recommendations."
                )

        st.subheader("Run a SQL Query")
        st.write("The uploaded CSV is stores as a SQl table named business_data.")
        default_query = "SELECT * FROM business_data LIMIT 5;"
        user_query = st.text_area(
            "Enter a SQL query ",
            value=default_query,
        )
        if st.button("Run SQL Query"):
            try:
                conn = sqlite3.connect("business_data.db")
                query_result = pd.read_sql_query(user_query, conn)  
                st.dataframe(query_result)
            except Exception as e:
                st.error(f"SQL error: {e}")
    else:
        st.warning("No numeric columns found for KPI analysis.")

else:
    st.info("Upload a CSV file to begin.")