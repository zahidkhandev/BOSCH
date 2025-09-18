import pandas as pd
import numpy as np
import os

def process_sensor_data(file_path):
    """
    Ingests, cleans, enriches, and saves sensor telemetry data.
    """
    column_names = [
        'Lp', 'V', 'GTT', 'GTn', 'GGn', 'Ts', 'Tp', 'T48', 'T1', 'T2',
        'P48', 'P1', 'P2', 'Pexh', 'TIC', 'mf', 'decay_coeff_comp', 'decay_coeff_turbine'
    ]

    try:
        df = pd.read_csv(file_path, sep=r"\s+", names=column_names, engine='python')
        print("--- 1. Data Ingestion ---")
        print(f"Successfully ingested {len(df)} rows.")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred during data ingestion: {e}")
        return None

    print("\n--- 2. Data Cleaning ---")
    
    # --- Remove Duplicate Rows ---
    initial_rows = len(df)
    df.drop_duplicates(inplace=True)
    rows_after_dedup = len(df)
    print(f"\nRemoved {initial_rows - rows_after_dedup} duplicate rows.")

    # --- Handle Outliers ---
    def handle_outliers_iqr(df_in, col_name):
        Q1 = df_in[col_name].quantile(0.25)
        Q3 = df_in[col_name].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers_count = ((df_in[col_name] < lower_bound) | (df_in[col_name] > upper_bound)).sum()
        if outliers_count > 0:
            print(f"Capping/flooring {outliers_count} outliers for '{col_name}'.")

        df_out = df_in.copy()
        df_out.loc[df_out[col_name] < lower_bound, col_name] = lower_bound
        df_out.loc[df_out[col_name] > upper_bound, col_name] = upper_bound
        return df_out

    # Apply outlier handling to critical columns
    for col in ['GTT', 'GTn', 'T48', 'P48', 'mf']:
        df = handle_outliers_iqr(df, col)

    # --- Comprehensive Data Smoothing (In-Place) ---
    print("\nApplying smoothing to all key sensor signals...")
    window_size = 5
    columns_to_smooth = [
        'GTT', 'GTn', 'GGn', 'Ts', 'Tp', 'T48', 'T1', 'T2',
        'P48', 'P1', 'P2', 'Pexh', 'TIC', 'mf'
    ]
    
    for col in columns_to_smooth:
        df[col] = df[col].rolling(window=window_size, min_periods=1).mean()
    
    print(f"In-place smoothing applied with a window size of {window_size}.")


    print("\n--- 3. Derived Feature Computation ---")

    # Calculations now use the smoothed data from the original columns
    df['T1_P1_ratio'] = df['T1'] / df['P1']
    df['T2_P2_ratio'] = df['T2'] / df['P2']
    df['T48_P48_ratio'] = df['T48'] / df['P48']
    df['Propeller_Torque_Diff'] = df['Ts'] - df['Tp']
    print("Derived Temperature-Pressure Ratios and Torque Differentials created.")

    # --- Calculate Power Output Proxy ---
    # Power (kW) = Torque (kN.m) * Angular Velocity (rad/s)
    # Convert GTn from RPM to rad/s: (RPM * 2 * pi) / 60
    angular_velocity_rad_s = df['GTn'] * (2 * np.pi / 60)
    df['Power_Proxy_kW'] = df['GTT'] * angular_velocity_rad_s
    print("Derived Power Output Proxy (kW) created.")
    
    # --- Calculate Total Decay Score ---
    # A healthy component has a decay coeff of 1. The score represents the sum of deviations from healthy.
    df['total_decay_score'] = (1 - df['decay_coeff_comp']) + (1 - df['decay_coeff_turbine'])
    print("Derived Total Decay Score created.")

    print("\n--- 4. Finalizing DataFrame ---")
    
    print("\nFinal DataFrame head with new features:")
    print(df.head())

    print("\nDescriptive Statistics for key new features:")
    print(df[['Power_Proxy_kW', 'T1_P1_ratio', 'T2_P2_ratio', 'T48_P48_ratio', 'Propeller_Torque_Diff', 'total_decay_score']].describe())
    
    return df

if __name__ == '__main__':
    # Paths are set as per the user's provided code
    input_file_path = 'capstone/code/data/data.txt'
    output_folder_path = 'capstone/code/data'
    output_file_path = os.path.join(output_folder_path, 'processed_data.csv')

    processed_df = process_sensor_data(input_file_path)
    
    if processed_df is not None:
        try:
            os.makedirs(output_folder_path, exist_ok=True)
            
            # Add a verification print statement before saving
            print(f"\nColumns being saved to CSV: {processed_df.columns.tolist()}")
            
            processed_df.to_csv(output_file_path, index=False)
            
            print(f"\n--- 5. Data Export ---")
            print(f"Processed data successfully saved to: {output_file_path}")
            print("\nPhase 2 execution completed successfully.")
        
        except Exception as e:
            print(f"An error occurred while saving the file: {e}")

