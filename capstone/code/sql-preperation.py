import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def setup_database(conn: sqlite3.Connection, df: pd.DataFrame):
    """
    Creates SQL tables and populates them with sensor and metadata.
    """
    print("--- 1. Setting up the SQLite Database ---")
    cursor = conn.cursor()

    # a. Create turbine_metadata table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS turbine_metadata (
            turbine_id INTEGER PRIMARY KEY,
            model_name TEXT NOT NULL,
            install_date DATE
        )
    ''')
    # Insert some sample metadata
    cursor.execute("INSERT OR IGNORE INTO turbine_metadata VALUES (101, 'Frigate-GT-7B', '2020-01-15')")
    print("  - 'turbine_metadata' table created and populated.")

    # b. Load the DataFrame into the sensor_readings table
    # Add a turbine_id for joining and a simulated timestamp for time-series analysis
    df['turbine_id'] = 101
    df['timestamp'] = pd.to_datetime(pd.to_datetime('2023-01-01') + pd.to_timedelta(df.index, unit='h'))
    
    # Rename columns to be more SQL-friendly
    df.columns = [col.lower() for col in df.columns]
    
    df.to_sql('sensor_readings', conn, if_exists='replace', index=False)
    print("  - 'sensor_readings' table created and populated from CSV.")

    # c. Create and populate the alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reading_timestamp DATETIME,
            alert_type TEXT NOT NULL,
            description TEXT,
            severity TEXT
        )
    ''')
    
    # Populate alerts based on rules (e.g., high exit temp or severe decay)
    cursor.execute('''
        INSERT INTO alerts (reading_timestamp, alert_type, description, severity)
        SELECT 
            timestamp,
            'High Exit Temperature',
            'HP Turbine exit temperature (T48) is above 800 C',
            'Warning'
        FROM sensor_readings
        WHERE t48 > 800
    ''')
    
    cursor.execute('''
        INSERT INTO alerts (reading_timestamp, alert_type, description, severity)
        SELECT 
            timestamp,
            'Severe Decay Detected',
            'Total decay score is critically high (> 0.06)',
            'Critical'
        FROM sensor_readings
        WHERE total_decay_score > 0.06
    ''')
    print("  - 'alerts' table created and populated based on operational rules.")
    conn.commit()

def analyze_fuel_patterns(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Analyzes fuel usage patterns using SQL aggregations.
    """
    print("\n--- 2. Analyzing Fuel Usage Patterns with SQL ---")
    query = """
        SELECT
            strftime('%Y-%m-%d', timestamp) as reading_day,
            AVG(mf) as average_fuel_flow,
            MAX(power_proxy_kw) as peak_power_output
        FROM
            sensor_readings
        GROUP BY
            reading_day
        ORDER BY
            reading_day;
    """
    df_fuel = pd.read_sql_query(query, conn)
    print("  - Successfully aggregated daily fuel usage and peak power.")
    return df_fuel

def analyze_efficiency(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Analyzes how turbine efficiency changes with component decay.
    """
    print("\n--- 3. Analyzing Turbine Efficiency vs. Decay with SQL ---")
    query = """
        WITH EfficiencyData AS (
            SELECT
                -- Calculate efficiency: Power output per unit of fuel. Add 1e-6 to avoid division by zero.
                (power_proxy_kw / (mf + 1e-6)) as efficiency_metric,
                total_decay_score
            FROM
                sensor_readings
            WHERE
                mf > 0.1 -- Exclude low/zero fuel flow readings for stable efficiency calculation
        )
        SELECT
            -- Group decay scores into bins for clearer visualization
            CASE
                WHEN total_decay_score < 0.01 THEN '01_Healthy'
                WHEN total_decay_score < 0.03 THEN '02_Minor_Decay'
                WHEN total_decay_score < 0.05 THEN '03_Moderate_Decay'
                ELSE '04_Severe_Decay'
            END as decay_level,
            AVG(efficiency_metric) as average_efficiency
        FROM
            EfficiencyData
        GROUP BY
            decay_level
        ORDER BY
            decay_level;
    """
    df_efficiency = pd.read_sql_query(query, conn)
    print("  - Successfully calculated and grouped efficiency by decay level.")
    return df_efficiency

def visualize_results(df_fuel: pd.DataFrame, df_efficiency: pd.DataFrame, output_folder: str):
    """
    Generates and saves visualizations of the analysis results.
    """
    print("\n--- 4. Visualizing Core Analysis ---")
    sns.set_theme(style="whitegrid")
    
    # a. Plot Fuel Usage and Power Output Over Time
    fig, ax1 = plt.subplots(figsize=(14, 7))
    
    ax1.set_title('Average Fuel Usage and Peak Power Over Time', fontsize=16, pad=20)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Average Fuel Flow (mf)', color='tab:blue')
    sns.lineplot(data=df_fuel, x='reading_day', y='average_fuel_flow', ax=ax1, color='tab:blue', marker='o', label='Avg Fuel Flow')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.tick_params(axis='x', rotation=45)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Peak Power Output (kW)', color='tab:green')
    sns.lineplot(data=df_fuel, x='reading_day', y='peak_power_output', ax=ax2, color='tab:green', marker='x', linestyle='--', label='Peak Power')
    ax2.tick_params(axis='y', labelcolor='tab:green')
    
    fig.tight_layout()
    plt.savefig(os.path.join(output_folder, 'fuel_usage_over_time.png'))
    print(f"  - Saved 'fuel_usage_over_time.png' to {output_folder}")
    plt.close()

    # b. Plot Turbine Efficiency vs. Decay Level
    plt.figure(figsize=(12, 7))
    ax = sns.barplot(data=df_efficiency, x='decay_level', y='average_efficiency', palette='viridis_r', hue='decay_level', dodge=False)
    
    plt.title('Turbine Efficiency vs. Component Decay', fontsize=16, pad=20)
    plt.xlabel('Turbine Health (Decay Level)', fontsize=12)
    plt.ylabel('Average Efficiency (Power / Fuel Flow)', fontsize=12)
    plt.xticks(ticks=np.arange(len(df_efficiency['decay_level'])), labels=[label.split('_', 1)[1].replace('_', ' ') for label in df_efficiency['decay_level']])
    plt.legend([],[], frameon=False)
    
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.1f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=11, color='black', xytext=(0, 5), textcoords='offset points')
                    
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'efficiency_vs_decay.png'))
    print(f"  - Saved 'efficiency_vs_decay.png' to {output_folder}")
    plt.close()

def visualize_additional_analysis(conn: sqlite3.Connection, output_folder: str):
    """Generates and saves additional exploratory visualizations."""
    print("\n--- 5. Visualizing Additional Analysis ---")
    sns.set_theme(style="whitegrid")

    df_all = pd.read_sql_query("SELECT * FROM sensor_readings", conn)
    # Drop non-numeric/identifier columns for correlation
    df_numeric = df_all.drop(columns=['turbine_id', 'timestamp'])
    
    # c. Correlation Heatmap
    plt.figure(figsize=(20, 16))
    sns.heatmap(df_numeric.corr(), annot=True, fmt='.2f', cmap='coolwarm', linewidths=.5)
    plt.title('Feature Correlation Heatmap', fontsize=16, pad=20)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'correlation_heatmap.png'))
    print(f"  - Saved 'correlation_heatmap.png' to {output_folder}")
    plt.close()

    # d. Power Output vs. Fuel Flow Scatter Plot
    plt.figure(figsize=(12, 7))
    sns.scatterplot(data=df_all, x='mf', y='power_proxy_kw', hue='total_decay_score', palette='viridis_r', s=20, alpha=0.7)
    plt.title('Power Output vs. Fuel Flow by Engine Health', fontsize=16, pad=20)
    plt.xlabel('Fuel Flow (mf)', fontsize=12)
    plt.ylabel('Power Output Proxy (kW)', fontsize=12)
    plt.legend(title='Total Decay Score')
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'power_vs_fuel_scatter.png'))
    print(f"  - Saved 'power_vs_fuel_scatter.png' to {output_folder}")
    plt.close()

    # e. Distribution of HP Turbine Exit Temperature (T48)
    plt.figure(figsize=(12, 7))
    sns.histplot(data=df_all, x='t48', kde=True, bins=50)
    plt.title('Distribution of HP Turbine Exit Temperature (T48)', fontsize=16, pad=20)
    plt.xlabel('Temperature (C)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 't48_distribution.png'))
    print(f"  - Saved 't48_distribution.png' to {output_folder}")
    plt.close()
    
    # f. Propeller Load Balance Over Time (Sample)
    df_sample = pd.read_sql_query("SELECT timestamp, ts, tp FROM sensor_readings LIMIT 500", conn)
    plt.figure(figsize=(14, 7))
    sns.lineplot(data=df_sample, x='timestamp', y='ts', label='Starboard Torque (Ts)')
    sns.lineplot(data=df_sample, x='timestamp', y='tp', label='Port Torque (Tp)', linestyle='--')
    plt.title('Propeller Torque Balance Over Time (Sample)', fontsize=16, pad=20)
    plt.xlabel('Timestamp', fontsize=12)
    plt.ylabel('Propeller Torque (kN)', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'propeller_balance.png'))
    print(f"  - Saved 'propeller_balance.png' to {output_folder}")
    plt.close()


if __name__ == '__main__':
    # Define project paths
    input_csv_path = 'capstone/code/data/processed_data.csv'
    output_viz_folder = 'capstone/code/visualizations'

    # Create the output directory if it doesn't exist
    os.makedirs(output_viz_folder, exist_ok=True)

    try:
        processed_df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: '{input_csv_path}' not found. Please run the data processing script first.")
        exit()

    # Use an in-memory SQLite database for the analysis
    conn = sqlite3.connect(':memory:')

    # Run the full pipeline
    setup_database(conn, processed_df)
    df_fuel_analysis = analyze_fuel_patterns(conn)
    df_efficiency_analysis = analyze_efficiency(conn)
    visualize_results(df_fuel_analysis, df_efficiency_analysis, output_viz_folder)
    visualize_additional_analysis(conn, output_viz_folder)

    print("\n--- 6. Sample of Generated Alerts ---")
    alerts_df = pd.read_sql_query("SELECT * FROM alerts LIMIT 5", conn)
    print(alerts_df)

    conn.close()
    print("\n✅ Analysis complete. Check the generated PNG files for all visualizations.")
