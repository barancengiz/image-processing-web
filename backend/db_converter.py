import sqlite3
import pandas as pd

def convert_csv_to_sqlite(csv_file: str, db_file: str, table_name: str) -> None:
    # Read the CSV file
    df = pd.read_csv(csv_file)
    # Create a connection to the SQLite database
    conn = sqlite3.connect(db_file)
    # Get only DMC_COLOR, R, G, B columns
    df = df[["DMC_COLOR", "RGB_COLOR", "R", "G", "B"]]
    # Change DMC_COLOR column to DMC_CODE, RGB_COLOR to HEX
    df = df.rename(columns={"DMC_COLOR": "DMC_CODE", "RGB_COLOR": "HEX"})
    # Write the data to the database
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    # Close the connection
    conn.close()
    print(f"CSV file '{csv_file}' converted to SQLite database '{db_file}' with table '{table_name}'")

if __name__ == "__main__":
    csv_file = "/app/assets/dmc_colors.csv"
    db_file = "/app/assets/dmc_colors.db"
    table_name = "dmc_colors"
    convert_csv_to_sqlite(csv_file, db_file, table_name)