import numpy as np
from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Dict, Any, Tuple, Union
import logging
from Backtester_Tushar.Feature_Generator.feature_gen import FeatureGenerator


class Strategy(ABC):
    """Abstract base class for trading strategies."""

    def __init__(self, name, timeframe="daily", atr_period=14, feature_configs=None, base_risk=150000, atr_threshold=5):
        self.name = name
        self.timeframe = timeframe
        self.atr_period = atr_period
        self.atr_cache = {}
        self.feature_generator = FeatureGenerator(feature_configs)
        self.base_risk = base_risk
        self.atr_threshold = atr_threshold

    def base_risk_allocation(self, row):
        if row["Signal"] == 0:
            return np.nan
        atr_percent = row["ATR_percent"] if "ATR_percent" in row else np.inf
        volatility = row["1_Volatility"] if "1_Volatility" in row else np.inf
        if atr_percent <= self.atr_threshold and volatility < 0.02:
            return self.base_risk * 1.33
        return self.base_risk

    @abstractmethod
    def risk_allocation(self, row):
        pass

    @abstractmethod
    def generate_signals(self, df):
        """Generate signals for single ticker DataFrame."""
        pass

    def generate_signals_multi_ticker(self, df):
        """
        Generate signals for master DataFrame containing multiple tickers.

        Args:
            df: Master DataFrame with 'ticker' column and OHLCV data

        Returns:
            DataFrame with signals generated for each ticker
        """
        if 'ticker' not in df.columns:
            raise ValueError("DataFrame must contain 'ticker' column for multi-ticker processing")

        results = []

        # Group by ticker and process each group
        for ticker, group_df in df.groupby('ticker'):
            try:
                # Generate signals for this ticker
                ticker_signals = self.generate_signals(group_df.copy())

                # Ensure ticker column is preserved
                ticker_signals['ticker'] = ticker

                results.append(ticker_signals)

            except Exception as e:
                print(f"Error processing ticker {ticker}: {str(e)}")
                # Optionally, you can choose to skip errored tickers or raise the error
                continue

        if not results:
            raise ValueError("No tickers were successfully processed")

        # Concatenate all results
        final_df = pd.concat(results, ignore_index=True)

        # Restore original order if possible (assuming df has a date/datetime column)
        date_cols = [col for col in df.columns if
                     'date' in col.lower() or df[col].dtype in ['datetime64[ns]', 'object']]
        if date_cols and 'ticker' in final_df.columns:
            try:
                final_df = final_df.sort_values(['ticker', date_cols[0]]).reset_index(drop=True)
            except:
                # If sorting fails, just return as-is
                pass

        return final_df

    def atr(self, high, low, close):
        key = (tuple(high), tuple(low), tuple(close), self.atr_period)
        if key not in self.atr_cache:
            tr = np.amax(
                np.vstack(((high - low).to_numpy(), (abs(high - close)).to_numpy(), (abs(low - close)).to_numpy())).T,
                axis=1)
            self.atr_cache[key] = pd.Series(tr).rolling(self.atr_period).mean().to_numpy()
        return self.atr_cache[key]

    def normalize_signals_industry_neutral(self, signals_df):
        """Two-step normalization: industry-neutral then cross-sectional"""
        signals_df = signals_df.copy()

        # Sector column should always be present in the input data
        if 'sector' not in signals_df.columns:
            raise ValueError("Sector column is required for industry-neutral normalization")

        # Step 1: Industry-neutral normalization within each date
        for date in signals_df['date'].unique():
            date_data = signals_df[signals_df['date'] == date].copy()

            # Normalize within each sector first
            for sector in date_data['sector'].unique():
                sector_mask = (signals_df['date'] == date) & (signals_df['sector'] == sector)
                sector_descriptors = signals_df.loc[sector_mask, 'signal_descriptor']

                if len(sector_descriptors) > 1:
                    # Sector-neutral z-score
                    sector_mean = sector_descriptors.mean()
                    sector_std = sector_descriptors.std()

                    if sector_std > 0:
                        sector_normalized = (sector_descriptors - sector_mean) / sector_std
                        signals_df.loc[sector_mask, 'signal_descriptor'] = sector_normalized
                    else:
                        # If no variation within sector, set to zero
                        signals_df.loc[sector_mask, 'signal_descriptor'] = 0.0
                elif len(sector_descriptors) == 1:
                    # Single stock in sector - set to zero (neutral)
                    signals_df.loc[sector_mask, 'signal_descriptor'] = 0.0

            # Step 2: Cross-sectional normalization across all sectors
            date_mask = signals_df['date'] == date
            all_descriptors = signals_df.loc[date_mask, 'signal_descriptor']

            if len(all_descriptors) > 1:
                # Final cross-sectional z-score normalization
                cross_mean = all_descriptors.mean()
                cross_std = all_descriptors.std()

                if cross_std > 0:
                    final_normalized = (all_descriptors - cross_mean) / cross_std
                    signals_df.loc[date_mask, 'signal_descriptor'] = final_normalized
                else:
                    # If no variation across entire universe, set all to zero
                    signals_df.loc[date_mask, 'signal_descriptor'] = 0.0

        return signals_df
