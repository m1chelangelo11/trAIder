import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from configs import logger_config

current_dir = Path(__file__).resolve().parent
logger_config.setup_logging()
logger = logger_config.get_logger(__name__)

raw_data_dir = current_dir.parent / "data" / "raw"
df = pd.read_csv(raw_data_dir / "market_data.csv")
logger.info("Loaded raw data")

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(['symbol', 'timestamp'])

# Check for duplicates
duplicates_count = df.duplicated(subset=['timestamp', 'symbol']).sum()
logger.info(f"Found {duplicates_count} duplicate timestamps")

if duplicates_count > 0:
    logger.warning(f"Duplicate timestamps found: {df[df.duplicated(subset=['timestamp', 'symbol'], keep=False)]['timestamp'].unique()}")
    df = df.drop_duplicates(subset=['timestamp', 'symbol'], keep='first')
    logger.info(f"Removed duplicates, remaining records: {len(df)}")

df = df.dropna()
logger.info(f"After dropna: {len(df)} records")

df = df.set_index('timestamp')
logger.info(f"Set timestamp as index")

# Check if timestamps are monotonically increasing within each symbol
for symbol in df['symbol'].unique():
    symbol_df = df[df['symbol'] == symbol]
    if not symbol_df.index.is_monotonic_increasing:
        raise ValueError(f"Timestamps are not monotonically increasing for symbol {symbol}")

processed_dir = current_dir.parent / "data" / "processed"
processed_dir.mkdir(exist_ok=True)
df.to_csv(processed_dir / "preprocessed_data.csv")
logger.info(f"Saved preprocessed data to {processed_dir}")
