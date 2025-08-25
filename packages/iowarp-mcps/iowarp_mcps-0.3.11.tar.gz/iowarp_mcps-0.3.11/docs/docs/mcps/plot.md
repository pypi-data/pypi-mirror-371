---
title: Plot MCP
description: "Plot MCP is a Model Context Protocol server that enables LLMs to create professional data visualizations from CSV and Excel files with intelligent data processing capabilities. The server automatically handles data cleaning, type inference, and missing value processing while supporting multiple v..."
---

import MCPDetail from '@site/src/components/MCPDetail';

<MCPDetail 
  name="Plot"
  icon="📈"
  category="Data Processing"
  description="Plot MCP is a Model Context Protocol server that enables LLMs to create professional data visualizations from CSV and Excel files with intelligent data processing capabilities. The server automatically handles data cleaning, type inference, and missing value processing while supporting multiple visualization types including line plots, bar charts, scatter plots, histograms, and correlation heatmaps."
  version="0.1.0"
  actions={["line_plot", "bar_plot", "scatter_plot", "histogram_plot", "heatmap_plot", "data_info"]}
  platforms={["claude", "cursor", "vscode"]}
  keywords={["MCP", "plotting", "visualization", "analytics", "matplotlib", "seaborn", "data-science"]}
  license="MIT"
  tools={[{"name": "line_plot", "description": "Create line plots from CSV or Excel data with customizable styling and formatting. Supports multiple data series, trend analysis, and time-series visualization with advanced customization options.", "function_name": "line_plot_tool"}, {"name": "bar_plot", "description": "Create bar charts from CSV or Excel data with advanced styling and categorical data visualization. Supports grouped bars, stacked bars, and horizontal orientation with customizable colors and annotations.", "function_name": "bar_plot_tool"}, {"name": "scatter_plot", "description": "Create scatter plots from CSV or Excel data with correlation analysis and trend visualization. Supports multi-dimensional data exploration, regression lines, and statistical annotations for data relationships.", "function_name": "scatter_plot_tool"}, {"name": "histogram_plot", "description": "Create histograms from CSV or Excel data with statistical distribution analysis. Supports density plots, normal distribution overlays, and comprehensive statistical metrics for data distribution visualization.", "function_name": "histogram_plot_tool"}, {"name": "heatmap_plot", "description": "Create heatmaps from CSV or Excel data with correlation matrix analysis and color-coded data visualization. Supports hierarchical clustering, dendrograms, and advanced color mapping for multi-dimensional data exploration.", "function_name": "heatmap_plot_tool"}, {"name": "data_info", "description": "Get comprehensive data file information including detailed schema analysis, data quality assessment, and statistical profiling. Provides thorough data exploration with column types, distributions, and data health metrics.", "function_name": "data_info_tool"}]}
>

### 1. Data Exploration and Analysis
```
I have a CSV file at /data/sales_data.csv with sales information. Can you first analyze the data structure and then create appropriate visualizations to show sales trends over time?
```

**Tools called:**
- `data_info` - Analyze the dataset structure
- `line_plot` - Create time-series plots showing sales trends

This prompt will:
- Use `data_info` to analyze the dataset structure
- Create time-series plots using `line_plot` showing sales trends
- Provide statistical insights about the data

<!-- **Output:** -->
<!-- Add your output images here -->
<!-- ![Data Info Output](images/example1_data_info.png) -->
<!-- ![Sales Trends Line Plot](images/example1_sales_trends.png) -->

### 2. Comparative Analysis with Multiple Charts
```
Using the file /data/survey_results.csv, create a comprehensive analysis showing:
1. Age distribution of respondents (histogram)
2. Correlation between satisfaction scores (heatmap)  
3. Department vs average salary comparison (bar chart)
```

**Tools called:**
- `histogram_plot` - Age distribution of respondents
- `heatmap_plot` - Correlation between satisfaction scores
- `bar_plot` - Department vs average salary comparison

This prompt will:
- Generate multiple complementary visualizations
- Provide statistical analysis for each chart type
- Show data relationships and distributions
- Create professional publication-ready plots

<!-- **Output:** -->
<!-- Add your output images here -->
<!-- ![Age Distribution Histogram](images/example2_age_histogram.png) -->
<!-- ![Satisfaction Scores Heatmap](images/example2_satisfaction_heatmap.png) -->
<!-- ![Department Salary Comparison](images/example2_department_salary.png) -->

### 3. Scientific Data Visualization
```
I have temperature measurement data in /data/temperature.csv. Create a scatter plot showing the relationship between ambient temperature and device performance, and add a trend analysis.
```

**Tools called:**
- `scatter_plot` - Relationship between ambient temperature and device performance

This prompt will:
- Create correlation analysis between variables using `scatter_plot`
- Generate scatter plot with trend lines
- Provide statistical correlation metrics
- Include uncertainty analysis if applicable

<!-- **Output:** -->
<!-- Add your output images here -->
<!-- ![Temperature vs Performance Scatter Plot](images/example3_temperature_scatter.png) -->

### 4. Business Intelligence Dashboard
```
From /data/quarterly_metrics.xlsx, create visualizations showing:
- Revenue trends by quarter (line plot)
- Performance metrics distribution (histogram)
- Regional comparison (bar chart)
```

**Tools called:**
- `line_plot` - Revenue trends by quarter
- `histogram_plot` - Performance metrics distribution
- `bar_plot` - Regional comparison

This prompt will:
- Handle Excel file format automatically
- Create multiple business-focused visualizations
- Provide executive summary statistics
- Generate dashboard-style layouts

<!-- **Output:** -->
<!-- Add your output images here -->
<!-- ![Revenue Trends Line Plot](images/example4_revenue_trends.png) -->
<!-- ![Performance Metrics Histogram](images/example4_performance_histogram.png) -->
<!-- ![Regional Comparison Bar Chart](images/example4_regional_comparison.png) -->

### 5. Research Data Publication
```
Using /data/experiment_results.csv, create publication-quality figures showing experimental conditions vs outcomes with proper error handling and statistical annotations.
```

**Tools called:**
- `data_info` - Analyze experimental data structure and quality
- `scatter_plot` - Show relationship between experimental conditions and outcomes
- `heatmap_plot` - Display correlation matrix of experimental variables

This prompt will:
- Use `data_info` to analyze data structure and handle missing values
- Generate `scatter_plot` for condition-outcome relationships
- Create `heatmap_plot` for correlation analysis
- Generate publication-ready 300 DPI plots
- Include proper statistical annotations

<!-- **Output:** -->
<!-- Add your output images here -->
<!-- ![Data Quality Report](images/example5_data_quality.png) -->
<!-- ![Experimental Conditions vs Outcomes](images/example5_experiment_scatter.png) -->
<!-- ![Correlation Matrix Heatmap](images/example5_correlation_heatmap.png) -->

### 6. Quick Data Quality Check
```
I need to quickly assess the quality of my dataset at /data/customer_data.csv - show me data completeness, distributions, and suggest the best visualization approaches.
```

**Tools called:**
- `data_info` - Comprehensive data quality assessment

This prompt will:
- Use `data_info` to perform comprehensive data quality assessment
- Identify missing values and data issues
- Suggest optimal visualization strategies
- Provide data cleaning recommendations

<!-- **Output:** -->
<!-- Add your output images here -->
<!-- ![Data Quality Assessment](images/example6_data_quality.png) -->
<!-- ![Data Completeness Report](images/example6_completeness_report.png) -->

</MCPDetail>

