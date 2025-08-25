import pandas as pd
import numpy as np
from numba import njit, prange
from scipy import stats, optimize, linalg
from scipy.stats import norm
from sklearn.decomposition import PCA
from sklearn.covariance import LedoitWolf
import warnings
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import logging
from scipy.optimize import minimize

warnings.filterwarnings('ignore')


@dataclass
class RiskLimits:
    """Risk limit configuration"""
    max_position_size: float = 0.05  # 5% max per position
    max_sector_exposure: float = 0.20  # 20% max per sector
    max_beta_exposure: float = 0.15  # Net beta limit
    max_daily_var: float = 0.02  # 2% daily VaR
    max_drawdown: float = 0.10  # 10% max drawdown
    max_leverage: float = 1.0  # Net leverage limit


@njit
def fast_softmax(x):
    """Numerically stable softmax with numba acceleration"""
    x_shifted = x - np.max(x)
    exp_x = np.exp(x_shifted)
    return exp_x / np.sum(exp_x)


@njit
def fast_sharpe_ratio(returns, risk_free_rate=0.0):
    """Fast Sharpe ratio calculation"""
    excess_returns = returns - risk_free_rate
    if np.std(excess_returns) == 0:
        return 0.0
    return np.mean(excess_returns) / np.std(excess_returns)


@njit
def exponential_decay(values, half_life):
    """Apply exponential decay to signal values"""
    decay_factor = np.log(0.5) / half_life
    n = len(values)
    weights = np.exp(decay_factor * np.arange(n - 1, -1, -1))
    return values * weights


class SignalProcessor:
    """Advanced signal processing with decay, orthogonalization, and quality metrics"""

    def __init__(self, half_life_days=5, min_ic_threshold=0.02):
        self.half_life_days = half_life_days
        self.min_ic_threshold = min_ic_threshold
        self.signal_history = defaultdict(deque)
        self.ic_history = defaultdict(deque)

    def decay_signals(self, signals_df):
        """Apply exponential decay to signals based on age"""
        decayed_signals = signals_df.copy()

        for ticker in signals_df['ticker'].unique():
            ticker_data = signals_df[signals_df['ticker'] == ticker].sort_values('date')
            if len(ticker_data) > 1:
                signal_values = ticker_data['signal_descriptor'].values
                decayed_values = exponential_decay(signal_values, self.half_life_days)
                decayed_signals.loc[decayed_signals['ticker'] == ticker, 'signal_descriptor'] = decayed_values

        return decayed_signals

    def calculate_information_coefficient(self, signals, forward_returns, periods=20):
        """Calculate rolling information coefficient"""
        if len(signals) != len(forward_returns) or len(signals) < periods:
            return 0.0

        ic_values = []
        for i in range(periods, len(signals)):
            window_signals = signals[i - periods:i]
            window_returns = forward_returns[i - periods:i]

            if len(window_signals) > 5:  # Minimum sample size
                ic, _ = stats.spearmanr(window_signals, window_returns)
                if not np.isnan(ic):
                    ic_values.append(ic)

        return np.mean(ic_values) if ic_values else 0.0

    def orthogonalize_signals(self, signal_matrix):
        """Orthogonalize signals using Gram-Schmidt process"""
        if signal_matrix.shape[1] < 2:
            return signal_matrix

        # Handle NaN values
        signal_matrix = np.nan_to_num(signal_matrix, nan=0.0)

        # Apply Gram-Schmidt orthogonalization
        orthogonal_signals = np.zeros_like(signal_matrix)

        for i in range(signal_matrix.shape[1]):
            vector = signal_matrix[:, i].copy()

            for j in range(i):
                projection = np.dot(vector, orthogonal_signals[:, j]) / np.dot(orthogonal_signals[:, j],
                                                                               orthogonal_signals[:, j])
                if not np.isnan(projection):
                    vector -= projection * orthogonal_signals[:, j]

            norm = np.linalg.norm(vector)
            orthogonal_signals[:, i] = vector / norm if norm > 1e-10 else vector

        return orthogonal_signals


class MarketImpactModel:
    """Almgren-Chriss execution model with market impact"""

    def __init__(self, permanent_impact=0.1, temporary_impact=0.01, volatility_adjustment=True):
        self.permanent_impact = permanent_impact
        self.temporary_impact = temporary_impact
        self.volatility_adjustment = volatility_adjustment

    def calculate_market_impact(self, shares, avg_volume, volatility, participation_rate=0.1):
        """Calculate market impact cost using Almgren-Chriss model"""
        if avg_volume <= 0 or shares == 0:
            return 0.0

        # Market impact parameters
        volume_ratio = abs(shares) / avg_volume

        # Permanent impact (linear in volume)
        permanent_cost = self.permanent_impact * volume_ratio

        # Temporary impact (square-root law)
        temporary_cost = self.temporary_impact * np.sqrt(volume_ratio)

        # Volatility adjustment
        if self.volatility_adjustment and volatility > 0:
            vol_multiplier = volatility / 0.02  # Normalize to 2% daily vol
            permanent_cost *= vol_multiplier
            temporary_cost *= vol_multiplier

        total_impact = permanent_cost + temporary_cost
        return min(total_impact, 0.05)  # Cap at 5%

    def optimal_execution_schedule(self, total_shares, time_horizon_days, risk_aversion=1e-6):
        """Calculate optimal execution schedule"""
        if time_horizon_days <= 0:
            return [total_shares]

        # Simple arithmetic schedule for now (can be enhanced with more complex optimization)
        shares_per_period = total_shares / time_horizon_days
        return [shares_per_period] * int(time_horizon_days)


class RiskManager:
    """Comprehensive risk management with VaR, factor exposure, and compliance"""

    def __init__(self, risk_limits: RiskLimits, lookback_days=252):
        self.risk_limits = risk_limits
        self.lookback_days = lookback_days
        self.factor_loadings = {}
        self.correlation_matrix = None
        self.var_models = {}

    def calculate_portfolio_var(self, positions, returns_covariance, confidence=0.05):
        """Calculate portfolio VaR as % of portfolio value (not absolute dollars)."""
        if not positions or returns_covariance is None:
            return 0.0

        tickers = list(positions.keys())
        position_values = np.array([positions[ticker]['market_value'] for ticker in tickers])

        if len(position_values) == 0:
            return 0.0

        portfolio_value = np.sum(np.abs(position_values))
        if portfolio_value == 0:
            return 0.0

        weights = position_values / portfolio_value

        n_assets = len(weights)
        if returns_covariance.shape[0] != n_assets:
            return 0.0

        # Portfolio variance (in return space)
        portfolio_variance = np.dot(weights.T, np.dot(returns_covariance, weights))
        if portfolio_variance < 0:
            portfolio_variance = 0
        portfolio_std = np.sqrt(portfolio_variance)

        # Parametric VaR (as % of portfolio value)
        z_score = norm.ppf(1 - confidence)  # e.g. 1.645 for 95%
        parametric_var_pct = z_score * portfolio_std  # % loss

        # Historical VaR fallback (also in % terms)
        if hasattr(self, 'historical_returns') and len(self.historical_returns) > 100:
            hist_var_pct = -np.percentile(self.historical_returns, confidence * 100)
            return max(parametric_var_pct, hist_var_pct)

        return parametric_var_pct

    def optimize_with_constraints(self, expected_returns, covariance_matrix, sector_groups, betas=None,
                                  risk_aversion=1.0, is_short=False):
        """
        Mean-variance optimization with position, sector, and beta constraints.
        Args:
            expected_returns (np.array): Expected returns for each asset.
            covariance_matrix (np.array): Covariance matrix of returns.
            sector_groups (dict): Mapping of sector names to indices of assets in that sector.
            betas (np.array, optional): Beta values for each asset, default None.
            risk_aversion (float): Risk aversion factor, default 1.0.
            is_short (bool): Whether optimizing for short positions, default False.
        Returns:
            np.array: Optimized weights.
        """
        n_assets = len(expected_returns)
        if n_assets == 0 or covariance_matrix is None or covariance_matrix.shape[0] != n_assets:
            return np.zeros(n_assets)

        # Validate inputs
        if np.any(np.isnan(expected_returns)) or np.any(np.isnan(covariance_matrix)):
            return np.zeros(n_assets)
        expected_returns = np.nan_to_num(expected_returns, nan=0.0)
        covariance_matrix = np.nan_to_num(covariance_matrix, nan=0.0)

        # Regularize covariance matrix to avoid ill-conditioning
        regularization = 1e-6 * np.eye(n_assets)
        cov_reg = covariance_matrix + regularization

        # Objective function: minimize risk - (1/risk_aversion) * return
        def objective(weights):
            if risk_aversion <= 0:
                return np.inf  # Prevent division by zero or negative risk aversion
            port_var = np.dot(weights.T, np.dot(cov_reg, weights))
            port_ret = np.dot(weights, expected_returns)
            return port_var - (1 / risk_aversion) * port_ret

        # Helper function to create position size constraint
        def create_position_constraint(index):
            def constraint(weights):
                return self.risk_limits.max_position_size - abs(weights[index])

            return constraint

        # Helper function to create sector exposure constraint
        def create_sector_constraint(indices):
            def constraint(weights):
                return self.risk_limits.max_sector_exposure - np.sum(np.abs(weights[indices]))

            return constraint

        # Helper function to create beta constraint
        def create_beta_constraint():
            def constraint(weights):
                return self.risk_limits.max_beta_exposure - abs(np.dot(weights, betas))

            return constraint

        # Build constraints list
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # Weights sum to 1
        ]

        # Add position size constraints
        for i in range(n_assets):
            constraints.append({'type': 'ineq', 'fun': create_position_constraint(i)})

        # Add sector exposure constraints
        for sector, indices in sector_groups.items():
            if not all(0 <= idx < n_assets for idx in indices):  # Validate indices
                continue
            constraints.append({'type': 'ineq', 'fun': create_sector_constraint(indices)})

        # Add beta constraint if betas provided
        if betas is not None and len(betas) == n_assets:
            constraints.append({'type': 'ineq', 'fun': create_beta_constraint()})

        # Bounds: 0 to 1 for longs, -1 to 0 for shorts
        bounds = [(0, 1) if not is_short else (-1, 0) for _ in range(n_assets)]

        # Initial guess
        init_weights = np.ones(n_assets) / n_assets
        if is_short:
            init_weights = -init_weights  # Start with short bias

        # Optimization
        result = minimize(objective, init_weights, method='SLSQP', bounds=bounds, constraints=constraints,
                          options={'maxiter': 1000, 'ftol': 1e-8})

        if result.success:
            weights = result.x
        else:
            # Fallback: equal weights with iterative constraint adjustment
            weights = np.ones(n_assets) / n_assets
            if is_short:
                weights = -weights
            max_iterations = 20
            for _ in range(max_iterations):
                violations = False
                # Check position size
                pos_viol = np.max(np.abs(weights) - self.risk_limits.max_position_size)
                if pos_viol > 0:
                    violations = True
                    weights[np.abs(weights) > self.risk_limits.max_position_size] *= (
                                self.risk_limits.max_position_size / np.abs(
                            weights[np.abs(weights) > self.risk_limits.max_position_size]))

                # Check sector exposure
                for sector, indices in sector_groups.items():
                    sector_sum = np.sum(np.abs(weights[indices]))
                    if sector_sum > self.risk_limits.max_sector_exposure:
                        violations = True
                        scale = self.risk_limits.max_sector_exposure / sector_sum
                        weights[indices] *= scale

                # Check beta if applicable
                if betas is not None and len(betas) == n_assets:
                    beta_exp = abs(np.dot(weights, betas))
                    if beta_exp > self.risk_limits.max_beta_exposure:
                        violations = True
                        weights *= (self.risk_limits.max_beta_exposure / beta_exp)

                if not violations:
                    break
            weights = weights / np.sum(np.abs(weights))  # Renormalize

        return weights


    def calculate_marginal_var(self, ticker, positions, returns_covariance, confidence=0.05):
        """Calculate marginal VaR contribution of a position"""
        if ticker not in positions or returns_covariance is None:
            return 0.0

        # Calculate VaR with and without the position
        full_var = self.calculate_portfolio_var(positions, returns_covariance, confidence)

        # Remove position and recalculate
        positions_without = {k: v for k, v in positions.items() if k != ticker}
        var_without = self.calculate_portfolio_var(positions_without, returns_covariance, confidence)

        return full_var - var_without

    def check_risk_limits(self, positions, portfolio_value, beta_exposure=0.0):
        """Check all risk limits and return violations"""
        violations = []

        if not positions:
            return violations

        # Position size limits
        for ticker, pos in positions.items():
            position_pct = abs(pos['market_value']) / portfolio_value
            if position_pct > self.risk_limits.max_position_size:
                violations.append(f"Position size limit violated for {ticker}: {position_pct:.2%}")

        # Beta exposure limit
        if abs(beta_exposure) > self.risk_limits.max_beta_exposure:
            violations.append(f"Beta exposure limit violated: {beta_exposure:.3f}")

        # Leverage limit
        gross_exposure = sum(abs(pos['market_value']) for pos in positions.values())
        leverage = gross_exposure / portfolio_value
        if leverage > self.risk_limits.max_leverage:
            violations.append(f"Leverage limit violated: {leverage:.2f}")

        return violations

    def calculate_risk_adjusted_weights(self, expected_returns, covariance_matrix, risk_aversion=1.0):
        """Calculate optimal portfolio weights using mean-variance optimization"""
        if len(expected_returns) == 0 or covariance_matrix is None:
            return {}

        try:
            # Regularize covariance matrix
            regularization = 1e-8 * np.eye(covariance_matrix.shape[0])
            reg_cov_matrix = covariance_matrix + regularization

            # Solve for optimal weights: w = (1/lambda) * inv(Sigma) * mu
            inv_cov = linalg.inv(reg_cov_matrix)
            optimal_weights = np.dot(inv_cov, expected_returns) / risk_aversion

            # Normalize weights
            total_weight = np.sum(np.abs(optimal_weights))
            if total_weight > 0:
                optimal_weights = optimal_weights / total_weight

            return optimal_weights

        except (linalg.LinAlgError, np.linalg.LinAlgError):
            # Fall back to equal weights if optimization fails
            n_assets = len(expected_returns)
            return np.ones(n_assets) / n_assets


class PerformanceAnalyzer:
    """Advanced performance analytics with attribution and benchmarking"""

    def __init__(self, benchmark_returns=None):
        self.benchmark_returns = benchmark_returns
        self.performance_history = []
        self.attribution_history = []

    def calculate_performance_metrics(self, returns, benchmark_returns=None):
        """Calculate comprehensive performance metrics"""
        if len(returns) == 0:
            return {}

        returns_array = np.array(returns)
        returns_array = returns_array[~np.isnan(returns_array)]

        if len(returns_array) == 0:
            return {}

        # Basic metrics
        total_return = np.prod(1 + returns_array) - 1
        annualized_return = (np.prod(1 + returns_array)) ** (252 / len(returns_array)) - 1
        annualized_vol = np.std(returns_array) * np.sqrt(252)
        sharpe_ratio = annualized_return / annualized_vol if annualized_vol > 0 else 0

        # Risk metrics
        downside_returns = returns_array[returns_array < 0]
        downside_vol = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = annualized_return / downside_vol if downside_vol > 0 else 0

        # Drawdown metrics
        cumulative_returns = np.cumprod(1 + returns_array)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns)

        # Skewness and Kurtosis
        skewness = stats.skew(returns_array)
        kurtosis = stats.kurtosis(returns_array)

        metrics = {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'annualized_volatility': annualized_vol,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'var_95': np.percentile(returns_array, 5),
            'cvar_95': np.mean(returns_array[returns_array <= np.percentile(returns_array, 5)])
        }

        # Benchmark-relative metrics
        if benchmark_returns is not None and len(benchmark_returns) == len(returns_array):
            excess_returns = returns_array - np.array(benchmark_returns)
            tracking_error = np.std(excess_returns) * np.sqrt(252)
            information_ratio = np.mean(excess_returns) * 252 / tracking_error if tracking_error > 0 else 0

            # Beta calculation
            covariance = np.cov(returns_array, benchmark_returns)[0, 1]
            benchmark_variance = np.var(benchmark_returns)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0

            # Alpha calculation
            risk_free_rate = 0.02 / 252  # Assume 2% annual risk-free rate
            alpha = (annualized_return - risk_free_rate) - beta * (np.mean(benchmark_returns) * 252 - risk_free_rate)

            metrics.update({
                'tracking_error': tracking_error,
                'information_ratio': information_ratio,
                'beta': beta,
                'alpha': alpha
            })

        return metrics


class InstitutionalPortfolio:
    """Institutional-grade portfolio management system"""

    def __init__(self,
                 initial_capital=10000000,
                 n_long_positions=20,
                 k_short_positions=20,
                 long_capital_pct=0.6,
                 short_capital_pct=0.4,
                 rebalance_frequency=1,
                 risk_limits=None,
                 deployable_capital_pct=1.0,  # NEW: What % of capital can be deployed
                 transaction_cost_bps=5.0,  # Changed from 5.0 to match baseline's 0.0002
                 slippage_factor=0.1):  # Changed from 0.1 to match baseline (no slippage)
        # Core parameters
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.n_long_positions = n_long_positions
        self.k_short_positions = k_short_positions
        self.long_capital_pct = long_capital_pct
        self.short_capital_pct = short_capital_pct
        self.rebalance_frequency = rebalance_frequency
        self.risk_limits = risk_limits or RiskLimits()
        self.risk_manager = RiskManager(self.risk_limits)
        self.signal_processor = SignalProcessor()
        self.market_impact_model = MarketImpactModel()  # Disable market impact

        self.deployable_capital_pct = deployable_capital_pct

        # Store dynamic allocation parameters (can be updated per rebalance)
        self.current_long_pct = long_capital_pct
        self.current_short_pct = short_capital_pct
        self.current_deployable_pct = deployable_capital_pct

        # Rest of existing initialization...
        self.rebalance_frequency = rebalance_frequency
        self.risk_limits = risk_limits or RiskLimits()
        # Update risk limits to enforce no leverage
        self.risk_limits.max_leverage = 1.0  # Strict no-leverage constraint

        self.performance_analyzer = PerformanceAnalyzer()
        self.positions = {}
        self.trade_log = []
        self.performance_log = []
        self.risk_log = []
        self.returns_covariance = None
        self.ticker_order = []
        self.betas = {}
        self.historical_returns = []
        self.portfolio_values = []
        self.returns = []
        self.peak_value = initial_capital
        self.current_drawdown = 0.0
        self.transaction_cost_bps = transaction_cost_bps / 10000
        self.slippage_factor = slippage_factor
        self.trade_id = 1
        self.last_rebalance_date = None
        self.setup_logging()

    def setup_logging(self):
        """Setup comprehensive logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('portfolio_management.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('PortfolioManager')


    def update_allocation_parameters(self, long_pct=None, short_pct=None, deployable_pct=None):
        """
        Update allocation parameters for next rebalancing.
        This can be called before each rebalance to dynamically adjust allocations.
        """
        if long_pct is not None:
            self.current_long_pct = long_pct
        if short_pct is not None:
            self.current_short_pct = short_pct
        if deployable_pct is not None:
            self.current_deployable_pct = deployable_pct

        # Ensure allocations are valid
        total_allocation = self.current_long_pct + self.current_short_pct
        if total_allocation > self.current_deployable_pct:
            self.logger.warning(
                f"Total allocation ({total_allocation:.2%}) exceeds deployable capital ({self.current_deployable_pct:.2%})")
            # Auto-adjust to fit within deployable capital
            scale_factor = self.current_deployable_pct / total_allocation
            self.current_long_pct *= scale_factor
            self.current_short_pct *= scale_factor
            self.logger.info(
                f"Adjusted allocations - Long: {self.current_long_pct:.2%}, Short: {self.current_short_pct:.2%}")

    def validate_no_leverage(self, positions, portfolio_value):
        """Ensure gross exposure never exceeds portfolio value"""
        gross_exposure = sum(abs(pos.get('market_value', 0)) for pos in positions.values())
        return gross_exposure <= portfolio_value * (1 + 1e-6)  # Small tolerance for rounding

    def calculate_available_deployment_capital(self, portfolio_state):
        """Calculate actual cash available for new deployments"""
        total_portfolio_value = portfolio_state['total_portfolio_value']
        available_cash = portfolio_state['cash']
        current_position_value = portfolio_state['total_position_value']

        # Maximum deployment based on target allocation
        max_target_deployment = total_portfolio_value * self.current_deployable_pct

        # Already deployed capital
        current_deployment = abs(current_position_value)

        # Available for new deployments (cannot exceed available cash)
        theoretical_available = max(0, max_target_deployment - current_deployment)
        actual_available = min(available_cash, theoretical_available)

        return {
            'total_portfolio_value': total_portfolio_value,
            'available_cash': available_cash,
            'current_deployment': current_deployment,
            'max_target_deployment': max_target_deployment,
            'theoretical_available': theoretical_available,
            'actual_available': actual_available,
            'deployment_ratio': current_deployment / total_portfolio_value if total_portfolio_value > 0 else 0
        }

    def calculate_target_positions_with_precise_capital(self, long_portfolio, short_portfolio, available_capital,
                                                        market_data):
        """
        Calculate target positions ensuring total allocation never exceeds available capital.
        This is a single-pass calculation that accounts for all execution costs upfront.
        """
        target_positions = {}

        # Separate available capital for longs and shorts
        total_allocation_weight = self.current_long_pct + self.current_short_pct
        if total_allocation_weight <= 0:
            return target_positions

        long_capital = available_capital * (self.current_long_pct / total_allocation_weight)
        short_capital = available_capital * (self.current_short_pct / total_allocation_weight)

        # Process long positions
        if long_portfolio and long_capital > 0:
            target_positions.update(
                self._calculate_positions_for_side(long_portfolio, long_capital, market_data, direction=1)
            )

        # Process short positions
        if short_portfolio and short_capital > 0:
            target_positions.update(
                self._calculate_positions_for_side(short_portfolio, short_capital, market_data, direction=-1)
            )

        return target_positions

    def _calculate_positions_for_side(self, portfolio_weights, available_capital, market_data, direction):
        """
        Calculate positions for one side (long or short) with precise capital allocation.

        Args:
            portfolio_weights: Dict of {ticker: weight} where weights sum to 1.0
            available_capital: Total capital available for this side
            market_data: Market data for execution prices
            direction: 1 for long, -1 for short
        """
        positions = {}

        if not portfolio_weights or available_capital <= 0:
            return positions

        # Normalize weights to ensure they sum to 1.0
        total_weight = sum(portfolio_weights.values())
        if total_weight <= 0:
            return positions

        # Calculate target allocations accounting for ALL execution costs upfront
        remaining_capital = available_capital

        for ticker, weight in portfolio_weights.items():
            if remaining_capital <= 0:
                break

            ticker_data = market_data[market_data['ticker'] == ticker]
            if len(ticker_data) == 0:
                continue

            # Get execution price (next day's open)
            base_price = ticker_data.iloc[0]['Open']
            atr = ticker_data.iloc[0].get('ATR', 0.02)

            # Calculate effective price including slippage
            is_buy = (direction == 1)
            slippage_pct = self.slippage_factor * atr
            effective_price = base_price * (1 + slippage_pct if is_buy else 1 - slippage_pct)

            # Calculate target allocation for this ticker
            normalized_weight = weight / total_weight
            target_capital_allocation = available_capital * normalized_weight

            # Calculate shares that fit within allocated capital INCLUDING transaction costs
            # Solve: shares * effective_price * (1 + transaction_cost_bps) = target_capital_allocation
            cost_multiplier = 1 + self.transaction_cost_bps
            affordable_shares = target_capital_allocation / (effective_price * cost_multiplier)

            # Round down to ensure we don't exceed capital
            final_shares = int(affordable_shares) * direction

            if abs(final_shares) >= 1:  # Only include meaningful positions
                # Calculate actual capital required (for tracking)
                actual_trade_value = abs(final_shares) * effective_price
                actual_transaction_cost = actual_trade_value * self.transaction_cost_bps
                actual_total_cost = actual_trade_value + actual_transaction_cost

                positions[ticker] = {
                    'shares': final_shares,
                    'price': base_price,  # Store base price for reference
                    'effective_price': effective_price,
                    'atr': atr,
                    'direction': direction,
                    'target_notional': target_capital_allocation,
                    'actual_cost': actual_total_cost
                }

                # Track remaining capital
                remaining_capital -= actual_total_cost

        # Log capital utilization
        total_allocated = sum(pos['actual_cost'] for pos in positions.values())
        utilization = total_allocated / available_capital if available_capital > 0 else 0

        side_name = "Long" if direction == 1 else "Short"
        self.logger.info(
            f"{side_name} allocation: ${total_allocated:,.0f} / ${available_capital:,.0f} ({utilization:.1%} utilization)")

        return positions

    def estimate_covariance_matrix(self, returns_data, method='ledoit_wolf'):
        """Estimate returns covariance matrix using advanced methods"""
        if returns_data is None or len(returns_data) < 20:
            return None

        returns_matrix = returns_data.values if hasattr(returns_data, 'values') else returns_data

        # Remove any rows/columns with all NaN values
        valid_data = returns_matrix[~np.isnan(returns_matrix).all(axis=1)]
        if len(valid_data) < 10:
            return None

        try:
            if method == 'ledoit_wolf':
                lw = LedoitWolf().fit(valid_data)
                cov_matrix = lw.covariance_

            elif method == 'sample':
                cov_matrix = np.cov(valid_data.T)
            else:
                # Exponentially weighted covariance
                weights = np.exp(-0.01 * np.arange(len(valid_data))[::-1])
                weights = weights / np.sum(weights)
                weighted_data = valid_data * weights[:, np.newaxis]
                cov_matrix = np.cov(weighted_data.T)

            return cov_matrix

        except Exception as e:
            self.logger.warning(f"Covariance estimation failed: {e}")
            return None

    def select_optimal_portfolio(self, signals_df, returns_data=None):
        """Select optimal portfolio using advanced signal processing and optimization"""
        if len(signals_df) == 0:
            return {}, {}

        # Apply signal decay
        decayed_signals = self.signal_processor.decay_signals(signals_df)

        # Separate long and short signals
        long_signals = decayed_signals[decayed_signals['signal_descriptor'] > 0].copy()
        short_signals = decayed_signals[decayed_signals['signal_descriptor'] < 0].copy()

        # Apply advanced selection logic
        long_portfolio = self._select_long_portfolio(long_signals, returns_data)
        short_portfolio = self._select_short_portfolio(short_signals, returns_data)

        return long_portfolio, short_portfolio

    def _select_long_portfolio(self, long_signals, returns_data):
        """Select optimal long portfolio using risk-adjusted optimization with constraints"""
        if len(long_signals) == 0:
            return {}

        long_signals_sorted = long_signals.nlargest(min(self.n_long_positions * 2, len(long_signals)),
                                                   'signal_descriptor')
        if len(long_signals_sorted) == 0:
            return {}

        scores = []
        tickers = []
        for _, row in long_signals_sorted.iterrows():
            base_score = row['signal_descriptor'] / max(row['ATR'], 0.001)
            market_impact = self.market_impact_model.calculate_market_impact(
                1000, row.get('Volume', 1000000), row['ATR']
            )
            adjusted_score = base_score * (1 - market_impact)
            scores.append(adjusted_score)
            tickers.append(row['ticker'])

        if returns_data is not None and len(scores) > 1:
            try:
                expected_returns = np.array(scores)
                expected_returns = expected_returns / np.sum(np.abs(expected_returns))
                ticker_indices = [self.ticker_order.index(t) for t in tickers if t in self.ticker_order]
                if self.returns_covariance is not None and len(ticker_indices) <= self.returns_covariance.shape[0]:
                    subset_cov = self.returns_covariance[np.ix_(ticker_indices, ticker_indices)]
                    # Build sector groups
                    sector_groups = defaultdict(list)
                    for i, ticker in enumerate(tickers):
                        sector = long_signals[long_signals['ticker'] == ticker]['sector'].iloc[0] if not long_signals[long_signals['ticker'] == ticker].empty else 'Unknown'
                        sector_groups[sector].append(i)
                    # Get betas for these tickers
                    betas = np.array([self.betas.get(t, 1.0) for t in tickers])
                    optimal_weights = self.risk_manager.optimize_with_constraints(expected_returns, subset_cov, sector_groups, betas)
                    portfolio = {}
                    for i, ticker in enumerate(tickers[:len(optimal_weights)]):
                        if abs(optimal_weights[i]) > 0.01:
                            portfolio[ticker] = optimal_weights[i]
                    return portfolio
            except Exception as e:
                self.logger.warning(f"Optimization failed, falling back to softmax: {e}")

        if len(scores) > 0:
            weights = fast_softmax(np.array(scores))
            return dict(zip(tickers[:self.n_long_positions], weights[:self.n_long_positions]))
        return {}

    def _select_short_portfolio(self, short_signals, returns_data):
        """Select optimal short portfolio using risk-adjusted optimization with constraints"""
        if len(short_signals) == 0:
            return {}

        short_signals_sorted = short_signals.nsmallest(min(self.k_short_positions * 2, len(short_signals)),
                                                      'signal_descriptor')
        if len(short_signals_sorted) == 0:
            return {}

        scores = []
        tickers = []
        for _, row in short_signals_sorted.iterrows():
            base_score = abs(row['signal_descriptor']) / max(row['ATR'], 0.001)
            market_impact = self.market_impact_model.calculate_market_impact(
                1000, row.get('Volume', 1000000), row['ATR']
            )
            # Dynamic borrow cost based on ATR (proxy for liquidity)
            borrow_cost = (row['ATR'] / 0.02) * (0.02 / 252)  # Scale by normalized volatility
            adjusted_score = base_score * (1 - market_impact - borrow_cost)
            scores.append(adjusted_score)
            tickers.append(row['ticker'])

        if returns_data is not None and len(scores) > 1:
            try:
                expected_returns = np.array(scores)
                expected_returns = expected_returns / np.sum(np.abs(expected_returns))
                ticker_indices = [self.ticker_order.index(t) for t in tickers if t in self.ticker_order]
                if self.returns_covariance is not None and len(ticker_indices) <= self.returns_covariance.shape[0]:
                    subset_cov = self.returns_covariance[np.ix_(ticker_indices, ticker_indices)]
                    sector_groups = defaultdict(list)
                    for i, ticker in enumerate(tickers):
                        sector = short_signals[short_signals['ticker'] == ticker]['sector'].iloc[0] if not short_signals[short_signals['ticker'] == ticker].empty else 'Unknown'
                        sector_groups[sector].append(i)
                    betas = np.array([self.betas.get(t, 1.0) for t in tickers])
                    optimal_weights = self.risk_manager.optimize_with_constraints(expected_returns, subset_cov, sector_groups, betas)
                    portfolio = {}
                    for i, ticker in enumerate(tickers[:len(optimal_weights)]):
                        if abs(optimal_weights[i]) > 0.01:
                            portfolio[ticker] = optimal_weights[i]
                    return portfolio
            except Exception as e:
                self.logger.warning(f"Short optimization failed, falling back to softmax: {e}")

        if len(scores) > 0:
            weights = fast_softmax(np.array(scores))
            return dict(zip(tickers[:self.k_short_positions], weights[:self.k_short_positions]))
        return {}

    def calculate_portfolio_value_and_cash(self, market_data):
        """Calculate current portfolio value and available cash"""

        cash = self.current_capital
        total_position_value = 0.0
        position_details = {}

        for ticker, pos in self.positions.items():
            ticker_data = market_data[market_data['ticker'] == ticker]
            if len(ticker_data) > 0:
                current_price = ticker_data.iloc[0]['Close']
                market_value = pos['shares'] * current_price
                total_position_value += market_value

                position_details[ticker] = {
                    'shares': pos['shares'],
                    'current_price': current_price,
                    'market_value': market_value,
                    'direction': pos['direction']
                }

        total_portfolio_value = cash + total_position_value

        return {
            'total_portfolio_value': total_portfolio_value,
            'cash': cash,
            'total_position_value': total_position_value,
            'position_details': position_details
        }

    def execute_smart_rebalancing(self, long_portfolio, short_portfolio, current_date, signal_data, market_data):
        """
        Execute portfolio rebalancing with strict no-leverage constraints
        """
        self.logger.info(f"Starting rebalancing for {current_date}")

        trades_executed = []
        total_transaction_costs = 0.0

        # Get current portfolio state
        portfolio_state = self.calculate_portfolio_value_and_cash(market_data)

        # Calculate available deployment capital
        capital_info = self.calculate_available_deployment_capital(portfolio_state)

        self.logger.info(f"Portfolio value: ${capital_info['total_portfolio_value']:,.2f}")
        self.logger.info(f"Available cash: ${capital_info['available_cash']:,.2f}")
        self.logger.info(f"Actual deployable: ${capital_info['actual_available']:,.2f}")

        # Calculate target allocations based on AVAILABLE capital (not theoretical)
        available_for_long = capital_info['actual_available'] * (
                    self.current_long_pct / (self.current_long_pct + self.current_short_pct))
        available_for_short = capital_info['actual_available'] * (
                    self.current_short_pct / (self.current_long_pct + self.current_short_pct))

        self.logger.info(f"Capital allocation - Long: ${available_for_long:,.0f}, Short: ${available_for_short:,.0f}")

        # Calculate target positions
        target_positions = {}
        current_tickers = set(self.positions.keys())
        target_tickers = set()

        # Calculate target positions using precise capital allocation
        target_positions = self.calculate_target_positions_with_precise_capital(
            long_portfolio, short_portfolio, capital_info['actual_available'], market_data
        )

        self.logger.info(f"Calculated {len(target_positions)} target positions with precise capital allocation")

        # Track cash throughout rebalancing
        working_cash = capital_info['available_cash']

        # Phase 1: Close positions not in target portfolio
        positions_to_close = current_tickers - target_tickers

        for ticker in positions_to_close:
            if ticker not in self.positions:
                continue

            pos = self.positions[ticker]
            shares_to_close = -pos['shares']

            ticker_data = market_data[market_data['ticker'] == ticker]
            if len(ticker_data) == 0:
                self.logger.warning(f"No market data for {ticker}, skipping close")
                continue

            execution_price = ticker_data.iloc[0]['Close']
            volatility = pos.get('volatility', ticker_data.iloc[0].get('ATR', 0.02))
            is_buy = shares_to_close > 0
            slippage_pct = self.slippage_factor * volatility
            effective_price = execution_price * (1 + slippage_pct if is_buy else 1 - slippage_pct)

            trade_value = abs(shares_to_close * effective_price)
            transaction_cost = trade_value * self.transaction_cost_bps

            cash_flow = -shares_to_close * effective_price
            working_cash += cash_flow - transaction_cost
            total_transaction_costs += transaction_cost

            trades_executed.append({
                'trade_id': self.trade_id,
                'date': current_date,
                'ticker': ticker,
                'action': 'CLOSE',
                'shares': shares_to_close,
                'execution_price': effective_price,
                'direction': pos['direction'],
                'transaction_cost': transaction_cost,
                'slippage': effective_price - execution_price,
                'cash_flow': cash_flow - transaction_cost
            })

            self.trade_id += 1
            del self.positions[ticker]

            self.logger.debug(f"Closed {ticker}: {shares_to_close:.0f} shares, Cash: ${working_cash:,.2f}")

        self.logger.info(f"Closed {len(positions_to_close)} positions, Working cash: ${working_cash:,.2f}")

        # Phase 2: Open/adjust positions with strict capital validation
        total_deployment_attempted = 0.0
        total_deployment_actual = 0.0

        for ticker, target in target_positions.items():
            current_shares = self.positions.get(ticker, {}).get('shares', 0.0)
            shares_delta = target['shares'] - current_shares

            if abs(shares_delta) < 1:
                continue

            # Calculate required capital with slippage and costs
            volatility = target['atr']
            is_buy = shares_delta > 0
            slippage_pct = self.slippage_factor * volatility
            effective_price = target['price'] * (1 + slippage_pct if is_buy else 1 - slippage_pct)

            trade_value = abs(shares_delta * effective_price)
            transaction_cost = trade_value * self.transaction_cost_bps
            total_required_cash = trade_value + transaction_cost

            total_deployment_attempted += total_required_cash

            # Handle capital constraints by scaling to maximum allocatable amount
            if total_required_cash > working_cash:
                if working_cash > 100:  # Minimum threshold for meaningful trades
                    # Calculate maximum allocatable shares given available cash
                    available_for_trade = working_cash * 0.99  # Leave 1% buffer
                    max_trade_value = available_for_trade / (1 + self.transaction_cost_bps)
                    max_allocatable_shares = max_trade_value / effective_price if effective_price > 0 else 0

                    # Scale to maximum allocatable amount
                    if shares_delta > 0:  # Long position
                        shares_delta = min(shares_delta, max_allocatable_shares)
                    else:  # Short position
                        shares_delta = max(shares_delta, -max_allocatable_shares)

                    # Recalculate costs with scaled shares
                    trade_value = abs(shares_delta * effective_price)
                    transaction_cost = trade_value * self.transaction_cost_bps
                    total_required_cash = trade_value + transaction_cost

                    self.logger.info(
                        f"Scaled {ticker} to max allocatable: {shares_delta:.0f} shares (${trade_value:,.0f})")
                else:
                    self.logger.warning(f"Insufficient cash for {ticker}: ${working_cash:,.0f} available")
                    continue

            if abs(shares_delta) < 1:
                continue

            # Execute trade
            cash_flow = -shares_delta * effective_price
            working_cash += cash_flow - transaction_cost
            total_transaction_costs += transaction_cost
            total_deployment_actual += total_required_cash

            # Update or create position
            if ticker in self.positions:
                old_pos = self.positions[ticker]
                new_total_shares = old_pos['shares'] + shares_delta

                if abs(new_total_shares) > 0.01:
                    old_cost_basis = old_pos['shares'] * old_pos['avg_price']
                    new_cost_basis = shares_delta * effective_price
                    total_cost_basis = old_cost_basis + new_cost_basis
                    avg_price = total_cost_basis / new_total_shares

                    self.positions[ticker].update({
                        'shares': new_total_shares,
                        'avg_price': avg_price,
                        'volatility': volatility
                    })
                else:
                    del self.positions[ticker]
                action = 'ADJUST'
            else:
                self.positions[ticker] = {
                    'shares': shares_delta,
                    'avg_price': effective_price,
                    'direction': target['direction'],
                    'entry_date': current_date,
                    'volatility': volatility
                }
                action = 'OPEN'

            trades_executed.append({
                'trade_id': self.trade_id,
                'date': current_date,
                'ticker': ticker,
                'action': action,
                'shares': shares_delta,
                'execution_price': effective_price,
                'direction': target['direction'],
                'transaction_cost': transaction_cost,
                'slippage': effective_price - target['price'],
                'cash_flow': cash_flow - transaction_cost
            })

            self.trade_id += 1

        # FINAL LEVERAGE VALIDATION
        final_portfolio_state = self.calculate_portfolio_value_and_cash(market_data)
        leverage_compliant = self.validate_no_leverage(
            {ticker: {'market_value': pos['shares'] * market_data[market_data['ticker'] == ticker]['Close'].iloc[0]}
             for ticker, pos in self.positions.items()},
            final_portfolio_state['total_portfolio_value']
        )

        if not leverage_compliant:
            self.logger.error("CRITICAL: Final leverage validation failed!")
            # Emergency position scaling could be implemented here

        # Update current capital
        self.current_capital = working_cash

        # Log comprehensive summary
        deployment_efficiency = (
                    total_deployment_actual / total_deployment_attempted) if total_deployment_attempted > 0 else 1.0
        final_positions = len(self.positions)

        self.logger.info(f"Rebalancing complete:")
        self.logger.info(f"  - Executed {len(trades_executed)} trades")
        self.logger.info(f"  - Transaction costs: ${total_transaction_costs:,.2f}")
        self.logger.info(f"  - Deployment efficiency: {deployment_efficiency:.1%}")
        self.logger.info(f"  - Final positions: {final_positions}")
        self.logger.info(f"  - Remaining cash: ${self.current_capital:,.2f}")
        self.logger.info(f"  - Leverage compliant: {leverage_compliant}")

        self.trade_log.extend(trades_executed)

        return total_transaction_costs, len(trades_executed)

    def calculate_comprehensive_portfolio_metrics(self, market_data, current_date):
        """
        Calculate comprehensive portfolio metrics with enhanced leverage monitoring
        """
        # Get current portfolio state
        portfolio_state = self.calculate_portfolio_value_and_cash(market_data)

        cash = portfolio_state['cash']
        total_position_value = portfolio_state['total_position_value']
        portfolio_value = portfolio_state['total_portfolio_value']
        position_details = portfolio_state['position_details']

        # Calculate position metrics
        total_unrealized_pnl = 0.0
        total_borrow_cost = 0.0
        long_exposure = 0.0
        short_exposure = 0.0
        gross_exposure = 0.0

        for ticker, pos_detail in position_details.items():
            pos = self.positions[ticker]

            cost_basis = pos['shares'] * pos['avg_price']
            market_value = pos_detail['market_value']

            if pos['direction'] == 1:
                unrealized_pnl = market_value - cost_basis
                long_exposure += abs(market_value)
            else:
                unrealized_pnl = cost_basis - market_value
                short_exposure += abs(market_value)

                atr = market_data[market_data['ticker'] == ticker].iloc[0].get('ATR', 0.02)
                borrow_cost = (atr / 0.02) * (0.02 / 252) * abs(market_value)
                total_borrow_cost += borrow_cost

            total_unrealized_pnl += unrealized_pnl
            gross_exposure += abs(market_value)

            position_details[ticker].update({
                'avg_price': pos['avg_price'],
                'cost_basis': cost_basis,
                'unrealized_pnl': unrealized_pnl,
                'weight': market_value / portfolio_value if portfolio_value > 0 else 0,
                'days_held': (pd.to_datetime(current_date) - pd.to_datetime(pos['entry_date'])).days
            })

        # Calculate returns
        if len(self.portfolio_values) > 0:
            daily_return = (portfolio_value - self.portfolio_values[-1]) / self.portfolio_values[-1]
        else:
            daily_return = 0.0

        self.returns.append(daily_return)
        self.historical_returns.append(daily_return)

        # Update drawdown tracking
        if portfolio_value > self.peak_value:
            self.peak_value = portfolio_value
        current_drawdown = (self.peak_value - portfolio_value) / self.peak_value
        self.current_drawdown = current_drawdown

        # Enhanced leverage and deployment metrics
        deployed_capital = gross_exposure
        deployment_ratio = deployed_capital / portfolio_value if portfolio_value > 0 else 0
        cash_ratio = cash / portfolio_value if portfolio_value > 0 else 1.0
        net_exposure = long_exposure - short_exposure
        leverage_ratio = gross_exposure / portfolio_value if portfolio_value > 0 else 0

        # CRITICAL: Leverage compliance check
        leverage_compliant = self.validate_no_leverage(
            {ticker: {'market_value': pos['market_value']} for ticker, pos in position_details.items()},
            portfolio_value
        )

        # Additional compliance checks
        deployment_compliant = deployment_ratio <= self.current_deployable_pct * 1.01
        cash_positive = cash >= 0
        drawdown_compliant = current_drawdown <= self.risk_limits.max_drawdown

        # Calculate sector exposures and beta
        sector_exposures = self._calculate_sector_exposures(position_details, market_data)
        portfolio_beta = self._calculate_portfolio_beta(position_details, market_data)

        # Calculate VaR
        portfolio_var = 0.0
        if self.returns_covariance is not None:
            var_positions = {ticker: {'market_value': pos['market_value']}
                             for ticker, pos in position_details.items()}
            portfolio_var = self.risk_manager.calculate_portfolio_var(var_positions, self.returns_covariance)

        # Performance metrics
        performance_metrics = {}
        if len(self.returns) > 20:
            performance_metrics = self.performance_analyzer.calculate_performance_metrics(
                self.returns[-252:] if len(self.returns) >= 252 else self.returns
            )

        # Compile comprehensive metrics with enhanced compliance monitoring
        comprehensive_metrics = {
            # Basic portfolio metrics
            'date': current_date,
            'portfolio_value': portfolio_value,
            'cash': cash,
            'total_position_value': total_position_value,
            'total_unrealized_pnl': total_unrealized_pnl,
            'daily_return': daily_return,
            'current_drawdown': current_drawdown,

            # Position metrics
            'num_positions': len(self.positions),
            'num_long_positions': len([p for p in self.positions.values() if p['direction'] == 1]),
            'num_short_positions': len([p for p in self.positions.values() if p['direction'] == -1]),

            # Exposure metrics
            'long_exposure': long_exposure,
            'short_exposure': short_exposure,
            'gross_exposure': gross_exposure,
            'net_exposure': net_exposure,
            'deployed_capital': deployed_capital,

            # Critical ratios and compliance
            'deployment_ratio': deployment_ratio,
            'cash_ratio': cash_ratio,
            'leverage_ratio': leverage_ratio,
            'target_deployment_ratio': self.current_deployable_pct,
            'current_long_pct': self.current_long_pct,
            'current_short_pct': self.current_short_pct,

            # Risk metrics
            'portfolio_beta': portfolio_beta,
            'portfolio_var_95': portfolio_var,
            'total_borrow_cost': total_borrow_cost,
            'sector_exposures': sector_exposures,

            # Enhanced compliance flags
            'leverage_compliant': leverage_compliant,
            'deployment_compliant': deployment_compliant,
            'drawdown_compliant': drawdown_compliant,
            'cash_positive': cash_positive,
            'overall_compliant': all([leverage_compliant, deployment_compliant, drawdown_compliant, cash_positive]),

            # Position details
            'position_details': position_details
        }

        # Add performance metrics
        comprehensive_metrics.update(performance_metrics)

        # Store metrics
        self.portfolio_values.append(portfolio_value)
        self.performance_log.append(comprehensive_metrics)

        # Apply daily costs
        self.current_capital -= total_borrow_cost

        # Log critical compliance violations
        if not leverage_compliant:
            self.logger.error(
                f"LEVERAGE VIOLATION: Gross exposure ${gross_exposure:,.2f} > Portfolio value ${portfolio_value:,.2f}")
        if not cash_positive:
            self.logger.error(f"NEGATIVE CASH: ${cash:,.2f}")
        if not deployment_compliant:
            self.logger.warning(f"Deployment breach: {deployment_ratio:.3f} > {self.current_deployable_pct:.3f}")

        return comprehensive_metrics

    def _calculate_portfolio_beta(self, position_details, market_data):
        """Calculate portfolio beta using betas or ATR proxy"""
        total_beta_exposure = 0.0
        total_weight = 0.0
        for ticker, pos in position_details.items():
            beta = self.betas.get(ticker, None)
            if beta is None:
                ticker_data = market_data[market_data['ticker'] == ticker]
                if len(ticker_data) > 0:
                    ticker_atr = ticker_data.iloc[0].get('ATR', 0.02)
                    avg_atr = market_data['ATR'].mean() if 'ATR' in market_data.columns else 0.02
                    beta = ticker_atr / avg_atr if avg_atr > 0 else 1.0
            weight = abs(pos['weight'])
            total_beta_exposure += beta * weight * pos['direction']
            total_weight += weight
        return total_beta_exposure / total_weight if total_weight > 0 else 0.0


    def _calculate_sector_exposures(self, position_details, market_data):
        """Calculate sector exposures (simplified implementation)"""
        # In practice, this would use external sector classification data
        sector_exposures = defaultdict(float)

        for ticker, pos in position_details.items():
            ticker_data = market_data[market_data['ticker'] == ticker]
            if not ticker_data.empty:
                sector = ticker_data['sector'].iloc[0]
            else:
                sector = 'Unknown'
            sector_exposures[sector] += pos['weight']

        return dict(sector_exposures)

    def run_institutional_backtest(self, master_df, allocation_schedule=None):
        """
        Run comprehensive institutional-grade backtest with dynamic allocation management.

        Args:
            master_df: Market data DataFrame
            allocation_schedule: Dict with dates as keys and allocation parameters as values
                               Example: {'2023-01-15': {'long_pct': 0.7, 'short_pct': 0.3, 'deployable_pct': 0.8}}

        Returns:
            Comprehensive results including daily metrics, analytics, and compliance reports
        """

        self.logger.info("=" * 60)
        self.logger.info("STARTING INSTITUTIONAL PORTFOLIO BACKTEST")
        self.logger.info("=" * 60)
        self.logger.info(f"Initial capital: ${self.initial_capital:,.2f}")
        self.logger.info(f"Initial allocation - Long: {self.current_long_pct:.1%}, Short: {self.current_short_pct:.1%}")
        self.logger.info(f"Initial deployable capital: {self.current_deployable_pct:.1%}")
        self.logger.info(f"No-leverage constraint: {self.risk_limits.max_leverage <= 1.0}")

        # Data preprocessing and validation
        self.logger.info("Preprocessing data...")
        master_df = self._preprocess_data(master_df)

        # Initialize risk models
        self.logger.info("Initializing risk models...")
        self._initialize_risk_models(master_df)

        # Backtest execution
        unique_dates = sorted(master_df['date'].unique())
        results = []
        allocation_changes = 0

        self.logger.info(f"Processing {len(unique_dates)} trading days...")

        for i, current_date in enumerate(unique_dates):
            try:
                # Check for allocation parameter updates
                if allocation_schedule and current_date in allocation_schedule:
                    old_params = (self.current_long_pct, self.current_short_pct, self.current_deployable_pct)

                    params = allocation_schedule[current_date]
                    self.update_allocation_parameters(
                        long_pct=params.get('long_pct'),
                        short_pct=params.get('short_pct'),
                        deployable_pct=params.get('deployable_pct')
                    )

                    new_params = (self.current_long_pct, self.current_short_pct, self.current_deployable_pct)

                    if old_params != new_params:
                        allocation_changes += 1
                        self.logger.info(f"ALLOCATION UPDATE on {current_date}:")
                        self.logger.info(f"  Long: {old_params[0]:.1%} → {new_params[0]:.1%}")
                        self.logger.info(f"  Short: {old_params[1]:.1%} → {new_params[1]:.1%}")
                        self.logger.info(f"  Deployable: {old_params[2]:.1%} → {new_params[2]:.1%}")

                # Get current day data for signal generation
                df_day = master_df[master_df['date'] == current_date].copy()

                # Get next day data for trade execution (if available)
                next_day_data = None
                execution_date = current_date

                if i < len(unique_dates) - 1:
                    next_date = unique_dates[i + 1]
                    next_day_data = master_df[master_df['date'] == next_date].copy()
                    execution_date = next_date

                # Handle signal conflicts
                df_day = self._detect_and_handle_conflicts(df_day)

                # Check rebalancing conditions
                should_rebalance = self._should_rebalance(current_date)

                transaction_costs = 0.0
                trades_count = 0

                # Execute rebalancing if conditions met
                if should_rebalance and len(df_day) > 0 and next_day_data is not None:
                    # Get historical returns for analysis
                    returns_window = self._get_returns_window(master_df, current_date, lookback=60)

                    # Select optimal portfolios
                    long_portfolio, short_portfolio = self.select_optimal_portfolio(df_day, returns_window)

                    # Execute rebalancing
                    if len(long_portfolio) > 0 or len(short_portfolio) > 0:
                        transaction_costs, trades_count = self.execute_smart_rebalancing(
                            long_portfolio, short_portfolio, current_date, df_day, next_day_data
                        )
                        self.last_rebalance_date = current_date

                        self.logger.info(
                            f"REBALANCED on {current_date}: {len(long_portfolio)} longs, {len(short_portfolio)} shorts, {trades_count} trades")

                    # Calculate metrics using next day's data
                    daily_metrics = self.calculate_comprehensive_portfolio_metrics(next_day_data, execution_date)
                else:
                    # Non-rebalance day: use current day data for valuation
                    daily_metrics = self.calculate_comprehensive_portfolio_metrics(df_day, current_date)

                # Add trading and execution metadata
                daily_metrics.update({
                    'rebalanced': should_rebalance,
                    'transaction_costs': transaction_costs,
                    'trades_executed': trades_count,
                    'next_day_execution': next_day_data is not None,
                    'execution_date': execution_date,
                    'allocation_changed': allocation_schedule and current_date in allocation_schedule
                })

                results.append(daily_metrics)

                # Monitor risk limits and log warnings
                self._monitor_risk_limits(daily_metrics)

                # Progress reporting
                if i % 50 == 0 or i == len(unique_dates) - 1:
                    progress = (i + 1) / len(unique_dates) * 100
                    self.logger.info(
                        f"Progress: {progress:.1f}% - Date: {current_date} - Portfolio: ${daily_metrics['portfolio_value']:,.2f} - Deployment: {daily_metrics['deployment_ratio']:.1%}")

            except Exception as e:
                self.logger.error(f"Error processing date {current_date}: {str(e)}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                continue

        self.logger.info("=" * 60)
        self.logger.info("BACKTEST COMPLETED")
        self.logger.info("=" * 60)

        # Generate comprehensive results
        results_df = pd.DataFrame(results)
        final_analytics = self._generate_final_analytics(results_df)
        risk_report = self._generate_risk_report(results_df)
        compliance_report = self._generate_compliance_report(results_df)
        allocation_report = self._generate_allocation_report(results_df, allocation_changes)

        # Log final summary
        if len(results_df) > 0:
            final_value = results_df['portfolio_value'].iloc[-1]
            total_return = (final_value - self.initial_capital) / self.initial_capital
            max_dd = results_df['current_drawdown'].max()
            avg_deployment = results_df['deployment_ratio'].mean()

            self.logger.info(f"FINAL RESULTS:")
            self.logger.info(f"  Initial Capital: ${self.initial_capital:,.2f}")
            self.logger.info(f"  Final Value: ${final_value:,.2f}")
            self.logger.info(f"  Total Return: {total_return:.2%}")
            self.logger.info(f"  Max Drawdown: {max_dd:.2%}")
            self.logger.info(f"  Average Deployment: {avg_deployment:.1%}")
            self.logger.info(f"  Total Trades: {len(self.trade_log)}")
            self.logger.info(f"  Allocation Changes: {allocation_changes}")

        return {
            'daily_results': results_df,
            'final_analytics': final_analytics,
            'risk_report': risk_report,
            'compliance_report': compliance_report,
            'allocation_report': allocation_report,
            'trade_log': pd.DataFrame(self.trade_log),
            'position_history': self._generate_position_history(),
            'backtest_summary': {
                'total_days': len(unique_dates),
                'successful_days': len(results),
                'allocation_changes': allocation_changes,
                'rebalance_days': len([r for r in results if r.get('rebalanced', False)]),
                'capital_constrained_days': len([r for r in results if not r.get('deployment_compliant', True)])
            }
        }

    def _generate_compliance_report(self, results_df):
        """Generate detailed compliance and constraint adherence report"""

        if len(results_df) == 0:
            return {}

        # Leverage compliance
        leverage_violations = results_df[results_df['leverage_ratio'] > self.risk_limits.max_leverage]
        leverage_compliant = len(leverage_violations) == 0

        # Deployment compliance
        deployment_violations = results_df[
            results_df['deployment_ratio'] > results_df['target_deployment_ratio'] * 1.01]
        deployment_compliant = len(deployment_violations) == 0

        # Drawdown compliance
        drawdown_violations = results_df[results_df['current_drawdown'] > self.risk_limits.max_drawdown]
        drawdown_compliant = len(drawdown_violations) == 0

        # Cash ratio analysis
        min_cash_ratio = results_df['cash_ratio'].min()
        avg_cash_ratio = results_df['cash_ratio'].mean()
        negative_cash_days = len(results_df[results_df['cash'] < 0])

        # Position size analysis (would need position-level data)
        max_single_position = 0.0
        if 'position_details' in results_df.columns:
            for _, row in results_df.iterrows():
                pos_details = row.get('position_details', {})
                if pos_details:
                    max_weight = max([abs(p.get('weight', 0)) for p in pos_details.values()], default=0)
                    max_single_position = max(max_single_position, max_weight)

        position_size_compliant = max_single_position <= self.risk_limits.max_position_size

        compliance_report = {
            'leverage_compliance': {
                'compliant': leverage_compliant,
                'violations': len(leverage_violations),
                'violation_dates': leverage_violations['date'].tolist() if len(leverage_violations) > 0 else [],
                'max_leverage': results_df['leverage_ratio'].max(),
                'limit': self.risk_limits.max_leverage
            },
            'deployment_compliance': {
                'compliant': deployment_compliant,
                'violations': len(deployment_violations),
                'violation_dates': deployment_violations['date'].tolist() if len(deployment_violations) > 0 else [],
                'max_deployment': results_df['deployment_ratio'].max(),
                'avg_target': results_df['target_deployment_ratio'].mean()
            },
            'drawdown_compliance': {
                'compliant': drawdown_compliant,
                'violations': len(drawdown_violations),
                'violation_dates': drawdown_violations['date'].tolist() if len(drawdown_violations) > 0 else [],
                'max_drawdown': results_df['current_drawdown'].max(),
                'limit': self.risk_limits.max_drawdown
            },
            'cash_management': {
                'min_cash_ratio': min_cash_ratio,
                'avg_cash_ratio': avg_cash_ratio,
                'negative_cash_days': negative_cash_days,
                'cash_compliant': negative_cash_days == 0
            },
            'position_size_compliance': {
                'compliant': position_size_compliant,
                'max_single_position': max_single_position,
                'limit': self.risk_limits.max_position_size
            },
            'overall_compliance': {
                'fully_compliant': all([
                    leverage_compliant, deployment_compliant,
                    drawdown_compliant, negative_cash_days == 0, position_size_compliant
                ]),
                'compliance_score': sum([
                    leverage_compliant, deployment_compliant,
                    drawdown_compliant, negative_cash_days == 0, position_size_compliant
                ]) / 5
            }
        }

        return compliance_report

    def _generate_allocation_report(self, results_df, allocation_changes):
        """Generate report on allocation parameter changes and their impact"""

        if len(results_df) == 0:
            return {}

        # Track allocation parameters over time
        allocation_history = []
        for _, row in results_df.iterrows():
            allocation_history.append({
                'date': row['date'],
                'long_pct': row.get('current_long_pct', self.long_capital_pct),
                'short_pct': row.get('current_short_pct', self.short_capital_pct),
                'deployable_pct': row.get('target_deployment_ratio', self.deployable_capital_pct),
                'actual_deployment': row.get('deployment_ratio', 0),
                'cash_ratio': row.get('cash_ratio', 0)
            })

        allocation_df = pd.DataFrame(allocation_history)

        # Calculate deployment efficiency
        deployment_efficiency = []
        for _, row in allocation_df.iterrows():
            target = row['deployable_pct']
            actual = row['actual_deployment']
            efficiency = actual / target if target > 0 else 0
            deployment_efficiency.append(efficiency)

        avg_efficiency = np.mean(deployment_efficiency)

        # Analyze cash utilization
        target_cash_ratio = 1 - allocation_df['deployable_pct']
        actual_cash_ratio = allocation_df['cash_ratio']
        cash_utilization_gap = actual_cash_ratio - target_cash_ratio

        allocation_report = {
            'allocation_changes': allocation_changes,
            'parameter_ranges': {
                'long_pct_range': (allocation_df['long_pct'].min(), allocation_df['long_pct'].max()),
                'short_pct_range': (allocation_df['short_pct'].min(), allocation_df['short_pct'].max()),
                'deployable_pct_range': (allocation_df['deployable_pct'].min(), allocation_df['deployable_pct'].max())
            },
            'deployment_efficiency': {
                'average': avg_efficiency,
                'min': min(deployment_efficiency),
                'max': max(deployment_efficiency),
                'target_hit_rate': len([e for e in deployment_efficiency if 0.95 <= e <= 1.05]) / len(
                    deployment_efficiency)
            },
            'cash_management': {
                'avg_cash_ratio': allocation_df['cash_ratio'].mean(),
                'target_cash_ratio': target_cash_ratio.mean(),
                'avg_utilization_gap': cash_utilization_gap.mean(),
                'excess_cash_days': len(cash_utilization_gap[cash_utilization_gap > 0.02])
            },
            'allocation_stability': {
                'long_pct_volatility': allocation_df['long_pct'].std(),
                'short_pct_volatility': allocation_df['short_pct'].std(),
                'deployable_pct_volatility': allocation_df['deployable_pct'].std()
            }
        }

        return allocation_report

    def _preprocess_data(self, master_df):
        """Advanced data preprocessing with validation"""

        # Data quality checks
        required_columns = ['date', 'ticker', 'signal_descriptor', 'Close', 'ATR', 'Volume']
        missing_columns = [col for col in required_columns if col not in master_df.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Remove rows with critical missing data
        master_df = master_df.dropna(subset=['Close', 'ATR', 'signal_descriptor'])

        # Handle outliers in ATR (cap at 99th percentile)
        atr_99th = master_df['ATR'].quantile(0.99)
        master_df['ATR'] = master_df['ATR'].clip(upper=atr_99th)

        # Ensure proper data types
        master_df['date'] = pd.to_datetime(master_df['date'])
        master_df = master_df.sort_values(['date', 'ticker']).reset_index(drop=True)

        # Add derived fields
        master_df['returns'] = master_df.groupby('ticker')['Close'].pct_change()

        self.logger.info(f"Data preprocessing complete. {len(master_df)} records processed.")

        return master_df

    def _initialize_risk_models(self, master_df):
        """Initialize risk models and covariance matrices"""

        # Create returns matrix for covariance estimation
        returns_pivot = master_df.pivot_table(
            index='date',
            columns='ticker',
            values='returns',
            fill_value=0
        )
        self.ticker_order = returns_pivot.columns.tolist()
        if len(returns_pivot) > 60:  # Need sufficient history
            self.returns_covariance = self.estimate_covariance_matrix(returns_pivot.values[-252:])  # Use last year
            self.logger.info("Risk models initialized successfully")
        else:
            self.logger.warning("Insufficient data for risk model initialization")

    def _detect_and_handle_conflicts(self, df_day):
        """
        Enhanced conflict detection using `signal_descriptor` column.
        If a ticker has conflicting signals (both positive and negative),
        resolve by keeping only the strongest signal.
        """

        # Add a helper flag column
        df_day['direction_flag'] = 0

        # Group by ticker and check signals
        ticker_groups = df_day.groupby('ticker')

        for ticker, group in ticker_groups:
            signals = group['signal_descriptor'].dropna()

            if len(signals) > 1:
                # Detect both positive and negative signals (conflict)
                has_pos = (signals > 0).any()
                has_neg = (signals < 0).any()

                if has_pos and has_neg:
                    # Mark conflicting entries
                    df_day.loc[df_day['ticker'] == ticker, 'direction_flag'] = 42

                    # Resolution: keep the strongest absolute signal
                    strongest_idx = group['signal_descriptor'].abs().idxmax()
                    df_day.loc[(df_day['ticker'] == ticker) & (df_day.index != strongest_idx),
                    'signal_descriptor'] = 0.0

        return df_day

    def _should_rebalance(self, current_date):
        """Enhanced rebalancing logic with market conditions"""

        if self.last_rebalance_date is None:
            return True

        days_since_rebalance = (pd.to_datetime(current_date) - pd.to_datetime(self.last_rebalance_date)).days

        # Standard frequency-based rebalancing
        if days_since_rebalance >= self.rebalance_frequency:
            return True

        # Emergency rebalancing conditions
        if self.current_drawdown > self.risk_limits.max_drawdown * 0.8:
            self.logger.warning("Emergency rebalancing triggered due to high drawdown")
            return True

        return False

    def _get_returns_window(self, master_df, current_date, lookback=60):
        """Get historical returns window for analysis"""

        current_date_dt = pd.to_datetime(current_date)
        start_date = current_date_dt - pd.Timedelta(days=lookback)

        window_data = master_df[
            (master_df['date'] >= start_date) &
            (master_df['date'] < current_date)
            ]

        return window_data

    def _monitor_risk_limits(self, daily_metrics):
        """Real-time risk monitoring with alerts"""

        # Check critical risk limits
        alerts = []

        if daily_metrics['current_drawdown'] > self.risk_limits.max_drawdown:
            alerts.append(f"CRITICAL: Drawdown limit breached - {daily_metrics['current_drawdown']:.2%}")

        if daily_metrics.get('leverage', 0) > self.risk_limits.max_leverage:
            alerts.append(f"WARNING: Leverage limit exceeded - {daily_metrics['leverage']:.2f}")

        if daily_metrics.get('portfolio_var_95', 0) > self.risk_limits.max_daily_var:
            alerts.append(f"WARNING: VaR limit exceeded - {daily_metrics['portfolio_var_95']:.2%}")

        # Log alerts
        for alert in alerts:
            self.logger.warning(alert)

        # Store risk metrics
        self.risk_log.append({
            'date': daily_metrics['date'],
            'alerts': alerts,
            'risk_metrics': {
                'drawdown': daily_metrics['current_drawdown'],
                'leverage': daily_metrics.get('leverage', 0),
                'var_95': daily_metrics.get('portfolio_var_95', 0),
                'beta': daily_metrics.get('portfolio_beta', 0)
            }
        })

    def _generate_final_analytics(self, results_df):
        """Generate comprehensive final analytics"""

        if len(results_df) == 0:
            return {}

        # Basic performance metrics
        initial_value = self.initial_capital
        final_value = results_df['portfolio_value'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value

        # Risk-adjusted metrics
        returns = results_df['daily_return'].dropna()
        if len(returns) > 0:
            performance_metrics = self.performance_analyzer.calculate_performance_metrics(returns.values)
        else:
            performance_metrics = {}

        # Enhanced trading statistics with slippage analysis
        total_trades = len(self.trade_log)
        total_transaction_costs = sum(trade['transaction_cost'] for trade in self.trade_log)

        # Calculate slippage statistics (difference between signal price and execution price)
        slippage_data = [trade.get('slippage', 0) for trade in self.trade_log if 'slippage' in trade]
        avg_slippage = np.mean(slippage_data) if slippage_data else 0
        slippage_cost = sum(abs(trade.get('slippage', 0)) * abs(trade.get('shares', 0))
                            for trade in self.trade_log if 'slippage' in trade)

        avg_holding_period = np.mean([
            trade.get('days_held', 0) for trade in self.trade_log
            if trade.get('action') == 'CLOSE'
        ]) if self.trade_log else 0

        # Fix: Use 'execution_price' instead of 'price'
        avg_trade_size = np.mean([
            abs(t['shares'] * t.get('execution_price', t.get('price', 0)))
            for t in self.trade_log
            if 'shares' in t and ('execution_price' in t or 'price' in t)
        ]) if self.trade_log else 0

        # Risk statistics
        max_leverage = results_df['leverage'].max() if 'leverage' in results_df.columns else 0
        avg_num_positions = results_df['num_positions'].mean()

        final_analytics = {
            'performance': {
                'initial_capital': initial_value,
                'final_value': final_value,
                'total_return': total_return,
                **performance_metrics
            },
            'risk': {
                'max_drawdown': results_df['current_drawdown'].max(),
                'max_leverage': max_leverage,
                'avg_positions': avg_num_positions,
                'var_breaches': len([r for r in self.risk_log if r['alerts']])
            },
            'trading': {
                'total_trades': total_trades,
                'total_transaction_costs': total_transaction_costs,
                'avg_holding_period': avg_holding_period,
                'turnover_rate': total_transaction_costs / initial_value,
                'avg_slippage': avg_slippage,
                'total_slippage_cost': slippage_cost,
                'avg_trade_size': avg_trade_size,  # Added this metric
                'next_day_execution_rate': len(
                    [t for t in self.trade_log if t.get('execution_date') != t.get('signal_date')]) / max(total_trades,
                                                                                                          1)
            }
        }

        return final_analytics

    def _generate_risk_report(self, results_df):
        """Generate detailed risk analysis report"""

        risk_report = {
            'drawdown_analysis': self._analyze_drawdowns(results_df),
            'var_analysis': self._analyze_var_performance(results_df),
            'concentration_analysis': self._analyze_concentration_risk(results_df),
            'factor_exposures': self._analyze_factor_exposures(results_df)
        }

        return risk_report

    def _analyze_drawdowns(self, results_df):
        """Analyze drawdown characteristics"""

        if 'current_drawdown' not in results_df.columns:
            return {}

        drawdowns = results_df['current_drawdown'].values

        # Find drawdown periods
        drawdown_periods = []
        in_drawdown = False
        start_idx = 0

        for i, dd in enumerate(drawdowns):
            if dd > 0.01 and not in_drawdown:  # Start of drawdown
                in_drawdown = True
                start_idx = i
            elif dd < 0.005 and in_drawdown:  # End of drawdown
                in_drawdown = False
                drawdown_periods.append({
                    'start': results_df.iloc[start_idx]['date'],
                    'end': results_df.iloc[i]['date'],
                    'duration': i - start_idx,
                    'max_drawdown': drawdowns[start_idx:i + 1].max()
                })

        return {
            'max_drawdown': drawdowns.max(),
            'avg_drawdown': drawdowns.mean(),
            'drawdown_periods': len(drawdown_periods),
            'longest_drawdown': max([dd['duration'] for dd in drawdown_periods]) if drawdown_periods else 0,
            'recovery_times': [dd['duration'] for dd in drawdown_periods]
        }

    def _analyze_var_performance(self, results_df):
        """Analyze VaR model performance"""

        if 'portfolio_var_95' not in results_df.columns or 'daily_return' not in results_df.columns:
            return {}

        var_predictions = results_df['portfolio_var_95'].values
        actual_returns = results_df['daily_return'].values

        # VaR exceptions (where actual loss exceeded VaR prediction)
        exceptions = actual_returns < -var_predictions
        exception_rate = np.mean(exceptions)

        return {
            'var_exceptions': np.sum(exceptions),
            'exception_rate': exception_rate,
            'expected_exception_rate': 0.05,
            'var_accuracy': abs(exception_rate - 0.05) < 0.02  # Within reasonable bounds
        }

    def _analyze_concentration_risk(self, results_df):
        """Analyze portfolio concentration risk"""

        concentration_metrics = []

        for _, row in results_df.iterrows():
            position_details = row.get('position_details', {})
            if position_details:
                weights = [abs(pos['weight']) for pos in position_details.values()]
                if weights:
                    # Herfindahl index
                    hhi = sum(w ** 2 for w in weights)
                    max_weight = max(weights)
                    concentration_metrics.append({
                        'date': row['date'],
                        'hhi': hhi,
                        'max_weight': max_weight,
                        'num_positions': len(weights)
                    })

        if not concentration_metrics:
            return {}

        concentration_df = pd.DataFrame(concentration_metrics)

        return {
            'avg_hhi': concentration_df['hhi'].mean(),
            'max_single_position': concentration_df['max_weight'].max(),
            'avg_num_positions': concentration_df['num_positions'].mean()
        }

    def _analyze_factor_exposures(self, results_df):
        """Analyze factor exposures over time"""

        sector_exposures_over_time = []

        for _, row in results_df.iterrows():
            sector_exposures = row.get('sector_exposures', {})
            if sector_exposures:
                sector_exposures_over_time.append({
                    'date': row['date'],
                    **sector_exposures
                })

        if not sector_exposures_over_time:
            return {}

        exposures_df = pd.DataFrame(sector_exposures_over_time)

        # Calculate average and maximum exposures by sector
        factor_analysis = {}
        for col in exposures_df.columns:
            if col != 'date':
                factor_analysis[col] = {
                    'avg_exposure': exposures_df[col].mean(),
                    'max_exposure': exposures_df[col].max(),
                    'volatility': exposures_df[col].std()
                }

        return factor_analysis

    def _generate_position_history(self):
        """Generate detailed position history for analysis"""

        position_history = {
            'current_positions': self.positions,
            'trade_summary': {
                'total_trades': len(self.trade_log),
                'profitable_trades': len([t for t in self.trade_log if t.get('pnl', 0) > 0]),
                'avg_trade_size': np.mean([
                    abs(t['shares'] * t.get('execution_price', t.get('price', 0)))
                    for t in self.trade_log
                    if 'shares' in t and ('execution_price' in t or 'price' in t)
                ]) if self.trade_log else 0
            }
        }

        return position_history
