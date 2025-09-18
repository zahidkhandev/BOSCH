import pandas as pd
import numpy as np
import os

def process_sensor_data(file_path):
    column_names = [
        'Lp', 'V', 'GTT', 'GTn', 'GGn', 'Ts', 'Tp', 'T48', 'T1', 'T2',
        'P48', 'P1', 'P2', 'Pexh', 'TIC', 'mf', 'decay_coeff_comp', 'decay_coeff_turbine'
    ]

    try:
        df = pd.read_csv(file_path, sep=r"\s+", names=column_names, engine='python')
        print("--- 1. Data Ingestion ---")
        print("CSV sensor logs ingested successfully.")
        print("DataFrame head:\n", df.head())
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred during data ingestion: {e}")
        return None

    print("\n--- 2. Data Cleaning ---")
    
    print("\nChecking for null values:")
    print(df.isnull().sum())
    
    def handle_outliers_iqr(df_in, col_name):
        Q1 = df_in[col_name].quantile(0.25)
        Q3 = df_in[col_name].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers_count = ((df_in[col_name] < lower_bound) | (df_in[col_name] > upper_bound)).sum()
        print(f"Column '{col_name}': {outliers_count} outliers detected.")

        df_out = df_in.copy()
        df_out.loc[df_out[col_name] < lower_bound, col_name] = lower_bound
        df_out.loc[df_out[col_name] > upper_bound, col_name] = upper_bound
        return df_out

    print("\nHandling outliers for 'GTT':")
    print("GTT stats before outlier handling:\n", df['GTT'].describe())
    df = handle_outliers_iqr(df, 'GTT')
    print("GTT stats after outlier handling (capping/flooring):\n", df['GTT'].describe())

    window_size = 5
    df['T48_smoothed'] = df['T48'].rolling(window=window_size, min_periods=1).mean()
    print(f"\nData smoothing performed for 'T48' with window size {window_size}.")
    print(df[['T48', 'T48_smoothed']].head(10))

    print("\n--- 3. Derived Feature Computation ---")

    df['T48_P48_ratio'] = df['T48'] / df['P48']
    df['T1_P1_ratio'] = df['T1'] / df['P1']
    df['T2_P2_ratio'] = df['T2'] / df['P2']
    print("\nDerived Temperature-Pressure Ratios created.")
    print(df[['T48', 'P48', 'T48_P48_ratio', 'T2', 'P2', 'T2_P2_ratio']].head())

    df['Propeller_Torque_Diff'] = df['Ts'] - df['Tp']
    df['Propeller_GTT_Ratio_Ts'] = df['Ts'] / df['GTT']
    df['Propeller_GTT_Ratio_Tp'] = df['Tp'] / df['GTT']
    print("\nDerived Torque Differentials and Ratios created.")
    print(df[['Ts', 'Tp', 'Propeller_Torque_Diff', 'GTT', 'Propeller_GTT_Ratio_Ts']].head())
    
    print("\n--- 4. Initial Exploratory Data Analysis (EDA) ---")

    print("\nDataFrame Info:")
    df.info()

    print("\nDescriptive Statistics:")
    print(df.describe())

    print("\nData Types:")
    print(df.dtypes)
    
    print("\nUnique values for 'Lp':", df['Lp'].unique())
    print("Unique values for 'V':", df['V'].unique())

    print("\nCorrelation Matrix (sample of original and new features):")
    print(df[['Lp', 'V', 'GTT', 'GTn', 'mf', 'T48_P48_ratio', 'Propeller_Torque_Diff']].corr())
    
    return df

if __name__ == '__main__':
    input_file_path = 'data.txt'
    output_folder_path = 'data'
    output_file_path = os.path.join(output_folder_path, 'processed_data.csv')

    processed_df = process_sensor_data(input_file_path)
    
    if processed_df is not None:
        try:
            # Ensure the output directory exists
            os.makedirs(output_folder_path, exist_ok=True)
            
            # Save the processed DataFrame to a CSV file
            processed_df.to_csv(output_file_path, index=False)
            
            print(f"\n--- 5. Data Export ---")
            print(f"Processed data successfully saved to: {output_file_path}")
            print("\nPhase 2 execution completed successfully.")
        
        except Exception as e:
            print(f"An error occurred while saving the file: {e}")

