import bisect
import multiprocessing as mp
from abc import abstractmethod
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, cast

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.special import expit
from tqdm import tqdm

from finter.backtest import Simulator
from finter.backtest.config.config import AVAILABLE_MARKETS
from finter.data.manager.adaptor import DataAdapter
from finter.data.manager.type import DataType
from finter.framework_model.alpha import BaseAlpha
from finter.framework_model.signal.process import normalize_signal
from finter.framework_model.signal.schemas import SignalConfig
from finter.framework_model.signal.timeout import timeout


class BaseSignal(BaseAlpha):
    POSITION_SCALE_FACTOR = 1e8
    SIGNAL_SUM_TOLERANCE = 1.01
    TIMEOUT_SECONDS = 300

    def __init__(self):
        super().__init__()

        self._initialized = False
        self.last_date: int = self._get_current_date()
        self.signal_history: deque

        self.configs: SignalConfig
        self.adapter: DataAdapter
        self.simulator: Simulator
        self.signal: pd.DataFrame
        self.position: pd.DataFrame

        self.setup()

    def setup(self):
        self.config()

        self.adapter = DataAdapter(
            self.configs.universe,
            self.configs.first_date,
            self.last_date,
        )
        self.adapter.add(self.configs.data_list)
        self.adapter.info()

        self.simulator = Simulator(
            cast(AVAILABLE_MARKETS, self.configs.universe),
            start=self.configs.first_date,
            end=self.last_date,
        )

        # Initialize signal history - only store if rebalancing is needed
        # Set maxlen to signal_lookback for memory efficiency
        self.signal_history = (
            deque(maxlen=self.configs.signal_lookback)
            if self.configs.signal_lookback > 0
            else deque()
        )

        self._cache_data()
        self._initialized = True

    @abstractmethod
    def config(self):
        """
        self.config_model
        """
        pass

    @abstractmethod
    def step(self, t: datetime) -> np.ndarray:  # (N)
        pass

    @timeout(TIMEOUT_SECONDS)
    def run_step(self, t: datetime, idx: int, first_date_idx: int) -> np.ndarray:
        """
        Rebalancing logic을 적용한 step 실행
        first_date를 anchor로 하여 rebalance 주기에 맞춰 신호를 계산하거나 이전 신호를 재사용
        """
        # 매일 리밸런싱하거나 리밸런스 설정이 없는 경우
        if self._should_calculate_daily():
            signal = self.step(t)
            return signal

        # first_date 이전이면 NaN 배열 반환
        if idx < first_date_idx:
            return self._get_nan_signal()

        # 리밸런싱 날짜 확인 및 신호 처리
        return self._handle_rebalancing(t, idx, first_date_idx)

    def _should_calculate_daily(self) -> bool:
        """매일 신호를 계산해야 하는지 확인"""
        return self.configs.rebalance is None or self.configs.rebalance == 1

    def _needs_history(self) -> bool:
        """신호 히스토리 저장이 필요한지 확인"""
        return not self._should_calculate_daily() and self.signal_history is not None

    def _get_nan_signal(self) -> np.ndarray:
        """NaN으로 채워진 신호 배열 반환"""
        return np.full(len(self.stock_data.N), np.nan)

    def _handle_rebalancing(
        self, t: datetime, idx: int, first_date_idx: int
    ) -> np.ndarray:
        """리밸런싱 로직 처리"""
        days_from_first = idx - first_date_idx

        if self.configs.rebalance and days_from_first % self.configs.rebalance == 0:
            # 리밸런싱 날짜: 새로운 신호 계산
            signal = self.step(t)
            if self._needs_history():
                self.signal_history.append(signal)
            return signal

        # 리밸런싱 날짜가 아님: 이전 신호 사용
        if self._needs_history() and len(self.signal_history) > 0:
            return self.signal_history[-1]
        else:
            return self._get_nan_signal()

    def _create_signal_dataframe(
        self, signal_list: list, date_index: list
    ) -> pd.DataFrame:
        """신호 DataFrame 생성"""
        return pd.DataFrame(
            signal_list,
            index=date_index,
            columns=list(self.stock_data.N),
        )

    def _validate_signal(self):
        """신호 유효성 검증"""
        if (self.signal.abs().sum(axis=1) == 0).all():
            raise ValueError("all signal is 0")
        if self.signal.abs().sum(axis=1).any() > 1.0:
            print("some signal is over exposure")
        if self.signal.abs().sum(axis=1).any() < 1.0:
            print("some signal is under exposure")

    def _create_position_dataframe(self, start: int, end: int) -> pd.DataFrame:
        """포지션 DataFrame 생성"""
        signal = normalize_signal(self.signal)
        return (
            (signal * self.POSITION_SCALE_FACTOR)
            .shift()
            .replace(0, np.nan)
            .dropna(how="all", axis=1)[str(start) : str(end)]
        )

    def _validate_and_adjust_dates(
        self, start: int, start_pos: int, signal_start_pos: int
    ) -> tuple[int, int, int]:
        """날짜 범위 검증 및 조정"""
        if signal_start_pos < self.configs.data_lookback:
            required_lookback = (
                self.configs.data_lookback + 1 + self.configs.signal_lookback
            )
            first_available_date = self.stock_data.T[required_lookback]

            print("-" * 50)
            print(
                f"Warning: Start date {start} requires {self.configs.data_lookback} days of lookback data "
                f"plus 1 day for shift and {self.configs.signal_lookback} days for signal lookback."
            )
            print(
                f"Adjusting start date from {start} to {first_available_date.strftime('%Y%m%d')}"
            )
            print("-" * 50)

            return (
                int(first_available_date.strftime("%Y%m%d")),
                required_lookback,
                self.configs.data_lookback,
            )

        return start, start_pos, signal_start_pos

    def _calculate_signals_batch(
        self, signal_start_pos: int, end_pos: int, start: int, end: int
    ) -> tuple[list[np.ndarray], list[pd.Timestamp]]:
        """신호 계산을 위한 배치 처리 - 메모리 최적화"""
        total_size = min(end_pos, len(self.stock_data.T)) - signal_start_pos

        # 미리 크기를 알고 있으므로 리스트 최적화 (예비 할당)
        signal_list: list[np.ndarray] = [] * total_size if total_size > 0 else []
        date_index: list[pd.Timestamp] = [] * total_size if total_size > 0 else []

        # first_date 인덱스 한 번만 계산
        first_date = self._parse_date(self.configs.first_date)
        first_date_idx = bisect.bisect_left(self.stock_data.T, first_date)

        # 배치 처리로 신호 계산
        for idx in tqdm(
            range(signal_start_pos, min(end_pos, len(self.stock_data.T))),
            desc=f"Calculating signals from {start} to {end}",
            total=total_size,
        ):
            t = self.stock_data.T[idx]
            signal_t = self.run_step(t, idx, first_date_idx)

            # 입력 유효성 검사
            self._validate_signal_shape(signal_t)

            signal_list.append(signal_t)
            date_index.append(pd.Timestamp(t))

        return signal_list, date_index

    def _validate_signal_shape(self, signal: np.ndarray) -> None:
        """신호 배열 모양 검증"""
        if signal.ndim != 1:
            raise ValueError(
                f"run_step() must return 1D array, but got {signal.ndim}D array. shape: {signal.shape}"
            )

    def _cache_data(self):
        if DataType.STOCK in self.adapter.dm.data:
            self.stock_data = self.adapter.stock
        if DataType.MACRO in self.adapter.dm.data:
            self.macro_data = self.adapter.macro
        if DataType.ENTITY in self.adapter.dm.data:
            self.entity_data = self.adapter.entity
        if DataType.STATIC in self.adapter.dm.data:
            self.static_data = self.adapter.static

    def _get_current_date(self) -> int:
        """Get current date as YYYYMMDD integer."""
        return int(datetime.now().strftime("%Y%m%d"))

    def _parse_date(self, date: int) -> pd.Timestamp:
        """Convert YYYYMMDD integer to pandas Timestamp."""
        return pd.Timestamp(datetime.strptime(str(date), "%Y%m%d"))

    def get(self, start: int, end: int) -> pd.DataFrame:
        start_date = self._parse_date(start)
        end_date = self._parse_date(end)

        # start, end 날짜의 인덱스 찾기
        start_pos = bisect.bisect_left(self.stock_data.T, start_date)
        end_pos = bisect.bisect_right(self.stock_data.T, end_date)

        # shift를 위해 하루 전부터 + signal_lookback만큼 더 앞서서 계산
        signal_start_pos = (
            start_pos - 1 - self.configs.signal_lookback if start_pos > 0 else start_pos
        )

        # 날짜 범위 검증 및 조정
        start, start_pos, signal_start_pos = self._validate_and_adjust_dates(
            start, start_pos, signal_start_pos
        )

        # 신호 계산을 위한 최적화된 배치 처리
        signal_list, date_index = self._calculate_signals_batch(
            signal_start_pos, end_pos, start, end
        )

        # DataFrame 생성 및 검증
        self.signal = self._create_signal_dataframe(signal_list, date_index)
        self._validate_signal()

        self.position = self._create_position_dataframe(start, end)
        return self.position

    def backtest(self, start: int, end: int, fee: bool = True) -> Any:
        position = self.get(start, end)
        if not fee:
            simulator = self.simulator.run(
                position, slippage=0, buy_fee_tax=0, sell_fee_tax=0
            )
        else:
            simulator = self.simulator.run(position)

        print(simulator.performance)
        return simulator

    def explore(
        self, start: int, end: int, plot: bool = True, max_workers: int = None
    ) -> dict:
        """시그널 변형들의 성과를 탐색하고 비교"""

        if max_workers is None:
            max_workers = min(mp.cpu_count(), 15)  # 15개의 변형이 있음

        # 기준 백테스트
        base_result = self.backtest(start, end)
        original_signal = self.signal.copy()

        # 변형별 성과 저장
        results = {}
        results["Base"] = base_result.performance.loc["All"]

        # 시그널 변형 함수들
        def apply_rank(signal_df):
            return signal_df.rank(axis=1, pct=True).sub(0.5).mul(2)

        def apply_quantile(signal_df, n_quantiles=5):
            def vectorized_qcut(row):
                valid_mask = ~row.isna()
                if not valid_mask.any():
                    return pd.Series(np.nan, index=row.index)
                result = pd.Series(np.nan, index=row.index)
                valid_data = row[valid_mask]
                try:
                    quantiles = pd.qcut(
                        valid_data.rank(method="first"),
                        q=n_quantiles,
                        labels=False,
                        duplicates="drop",
                    )
                    mapped_values = (2 * quantiles / (n_quantiles - 1)) - 1
                    result[valid_mask] = mapped_values
                except ValueError:
                    pass
                return result

            return signal_df.apply(vectorized_qcut, axis=1)

        def apply_zscore(signal_df):
            return signal_df.sub(signal_df.mean(axis=1), axis=0).div(
                signal_df.std(axis=1), axis=0
            )

        def apply_cut(signal_df, top_pct=0.3, bottom_pct=0.3):
            def vectorized_cut(row):
                valid_mask = ~row.isna()
                if not valid_mask.any():
                    return pd.Series(0.0, index=row.index)
                result = pd.Series(0.0, index=row.index)
                valid_data = row[valid_mask]
                n_stocks = len(valid_data)
                if n_stocks == 0:
                    return result
                n_top = max(1, int(n_stocks * top_pct))
                n_bottom = max(1, int(n_stocks * bottom_pct))
                top_threshold = valid_data.nlargest(n_top).min()
                bottom_threshold = valid_data.nsmallest(n_bottom).max()
                top_mask = (row >= top_threshold) & valid_mask
                bottom_mask = (row <= bottom_threshold) & valid_mask
                if top_mask.sum() > n_top:
                    top_indices = row[top_mask].nlargest(n_top).index
                    top_mask = row.index.isin(top_indices)
                if bottom_mask.sum() > n_bottom:
                    bottom_indices = row[bottom_mask].nsmallest(n_bottom).index
                    bottom_mask = row.index.isin(bottom_indices)
                result[top_mask] = 1.0 / top_mask.sum()
                result[bottom_mask] = -1.0 / bottom_mask.sum()
                return result

            return signal_df.apply(vectorized_cut, axis=1)

        def apply_sigmoid(signal_df, scale=1.0):
            zscore = signal_df.sub(signal_df.mean(axis=1), axis=0).div(
                signal_df.std(axis=1), axis=0
            )
            zscore = zscore.fillna(0)
            return (expit(zscore * scale) - 0.5) * 2

        def apply_smoothing(signal_df, window=3):
            return signal_df.rolling(window=window, min_periods=1).mean()

        def apply_median_norm(signal_df):
            return signal_df.sub(signal_df.median(axis=1), axis=0)

        def apply_middle_select(signal_df, middle_pct=0.4):
            def vectorized_middle(row):
                valid_mask = ~row.isna()
                if not valid_mask.any():
                    return pd.Series(0.0, index=row.index)
                result = pd.Series(0.0, index=row.index)
                valid_data = row[valid_mask]
                n_stocks = len(valid_data)
                if n_stocks == 0:
                    return result
                n_middle = max(1, int(n_stocks * middle_pct))
                median_val = valid_data.median()
                distances = np.abs(valid_data - median_val)
                middle_indices = distances.nsmallest(n_middle).index
                middle_values = row[middle_indices]
                if len(middle_values) > 0:
                    normalized_values = (middle_values - middle_values.mean()) / (
                        middle_values.std() + 1e-8
                    )
                    result[middle_indices] = normalized_values / len(middle_indices)
                return result

            return signal_df.apply(vectorized_middle, axis=1)

        # 변형 정의
        transformations = {
            "Rank": lambda s: apply_rank(s),
            "Quantile_5": lambda s: apply_quantile(s, n_quantiles=5),
            "Quantile_10": lambda s: apply_quantile(s, n_quantiles=10),
            "Zscore": lambda s: apply_zscore(s),
            "Cut_30pct": lambda s: apply_cut(s, top_pct=0.3, bottom_pct=0.3),
            "Cut_20pct": lambda s: apply_cut(s, top_pct=0.2, bottom_pct=0.2),
            "Cut_10pct": lambda s: apply_cut(s, top_pct=0.1, bottom_pct=0.1),
            "Sigmoid_1.0": lambda s: apply_sigmoid(s, scale=1.0),
            "Sigmoid_0.5": lambda s: apply_sigmoid(s, scale=0.5),
            "Smoothing_3d": lambda s: apply_smoothing(s, window=3),
            "Smoothing_5d": lambda s: apply_smoothing(s, window=5),
            "Smoothing_20d": lambda s: apply_smoothing(s, window=20),
            "Smoothing_60d": lambda s: apply_smoothing(s, window=60),
            "Median_Norm": lambda s: apply_median_norm(s),
            "Middle_40pct": lambda s: apply_middle_select(s, middle_pct=0.4),
            "Middle_30pct": lambda s: apply_middle_select(s, middle_pct=0.3),
            "Middle_50pct": lambda s: apply_middle_select(s, middle_pct=0.5),
        }

        # 변형 처리 함수 (병렬 처리용)
        def process_transformation(
            name, transform_func, signal_copy, start, end, simulator
        ):
            try:
                transformed = transform_func(signal_copy)
                if transformed.isna().all().all():
                    return name, None, "All NaN values - skipped"

                # 임시 객체 생성하여 독립적으로 처리
                temp_position = (
                    (normalize_signal(transformed) * self.POSITION_SCALE_FACTOR)
                    .shift()
                    .replace(0, np.nan)
                    .dropna(how="all", axis=1)[str(start) : str(end)]
                )

                if temp_position.empty or temp_position.isna().all().all():
                    return name, None, "Empty position - skipped"

                # 독립적인 simulator로 실행
                result = simulator.run(temp_position)
                return name, result, None
            except Exception as e:
                return name, None, f"Error: {e}"

        print("=" * 80)
        print("Signal Transformation Performance Comparison (Parallel Processing)")
        print("=" * 80)

        # 병렬 처리로 모든 변형 실행
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    process_transformation,
                    name,
                    transform_func,
                    original_signal.copy(),
                    start,
                    end,
                    Simulator(
                        cast(AVAILABLE_MARKETS, self.configs.universe),
                        start=self.configs.first_date,
                        end=self.last_date,
                    ),
                ): name
                for name, transform_func in transformations.items()
            }

            # 결과 수집
            for future in tqdm(
                as_completed(futures),
                total=len(futures),
                desc="Processing transformations",
            ):
                name = futures[future]
                try:
                    name_result, result, error_msg = future.result()

                    if error_msg:
                        print(f"\n{name}: {error_msg}")
                        continue

                    results[name] = result.performance.loc["All"]

                    print(f"\n{name}:")
                    print(
                        f"  Return: {result.performance.loc['All']['annualized_return_pct']:.2f}%"
                    )
                    print(
                        f"  Sharpe: {result.performance.loc['All']['sharpe_ratio']:.3f}"
                    )
                    print(
                        f"  PPT: {result.performance.loc['All']['profit_per_turnover_bp']:.2f}bp"
                    )
                    print(
                        f"  Turnover: {result.performance.loc['All']['total_turnover_pct']:.1f}%"
                    )
                except Exception as e:
                    print(f"\n{name}: Execution error - {e}")

        # 결과 요약
        if len(results) > 1:
            results_df = pd.DataFrame(results).T
            key_metrics = [
                "annualized_return_pct",
                "sharpe_ratio",
                "profit_per_turnover_bp",
                "total_turnover_pct",
                "volatility_annual_pct",
                "max_drawdown_pct",
            ]
            summary_df = results_df[key_metrics]

            print("\n" + "=" * 80)
            print("Summary Table (sorted by Sharpe Ratio)")
            print("=" * 80)
            print(summary_df.sort_values("sharpe_ratio", ascending=False).round(2))

            # Plotly 시각화
            if plot:
                self._create_exploration_plots(summary_df)

            # 원본 시그널 복원
            self.signal = original_signal

            return results_df.to_dict()

        return results

    def _create_exploration_plots(self, summary_df):
        """탐색 결과를 plotly로 시각화"""

        # 1. Efficient Frontier 스타일 Return vs Sharpe
        fig1 = go.Figure()

        fig1.add_trace(
            go.Scatter(
                x=summary_df["annualized_return_pct"],
                y=summary_df["sharpe_ratio"],
                mode="markers+text",
                text=summary_df.index,
                textposition="top center",
                marker=dict(
                    size=10,
                    color=summary_df["sharpe_ratio"],
                    colorscale="RdYlGn",
                    showscale=True,
                    colorbar=dict(title="Sharpe Ratio"),
                ),
                hovertemplate="<b>%{text}</b><br>"
                + "Return: %{x:.2f}%<br>"
                + "Sharpe: %{y:.3f}<extra></extra>",
            )
        )

        fig1.update_layout(
            title="Signal Transformations Efficient Frontier",
            xaxis_title="Annualized Return (%)",
            yaxis_title="Sharpe Ratio",
            height=600,
        )
        fig1.show()

        # 2. 모든 변형 성과 비교 (선 그래프)
        fig2 = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Sharpe Ratio",
                "Annualized Return (%)",
                "Max Drawdown (%)",
                "Profit per Turnover (bp)",
            ),
        )

        # 각 서브플롯에 선 그래프 추가
        metrics = [
            "sharpe_ratio",
            "annualized_return_pct",
            "max_drawdown_pct",
            "profit_per_turnover_bp",
        ]
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

        # 정렬된 인덱스 사용
        sorted_df = summary_df.sort_values("sharpe_ratio", ascending=False)

        for metric, (row, col) in zip(metrics, positions):
            fig2.add_trace(
                go.Scatter(
                    x=list(range(len(sorted_df))),
                    y=sorted_df[metric],
                    mode="lines+markers",
                    name=metric,
                    text=sorted_df.index,
                    hovertemplate="<b>%{text}</b><br>"
                    + f"{metric}: %{{y}}<extra></extra>",
                ),
                row=row,
                col=col,
            )

        # x축에 변형 이름 표시
        fig2.update_xaxes(
            tickvals=list(range(len(sorted_df))), ticktext=sorted_df.index, tickangle=45
        )

        fig2.update_layout(
            height=800,
            title_text="All Signal Transformations Performance",
            showlegend=False,
        )
        fig2.show()

        print("\n" + "=" * 80)
        print("Best Transformations")
        print("=" * 80)
        print(
            f"Best Return: {summary_df['annualized_return_pct'].idxmax()} = {summary_df['annualized_return_pct'].max():.2f}%"
        )
        print(
            f"Best Sharpe: {summary_df['sharpe_ratio'].idxmax()} = {summary_df['sharpe_ratio'].max():.3f}"
        )
        print(
            f"Best PPT: {summary_df['profit_per_turnover_bp'].idxmax()} = {summary_df['profit_per_turnover_bp'].max():.2f}bp"
        )
        print(
            f"Lowest Drawdown: {summary_df['max_drawdown_pct'].idxmin()} = {summary_df['max_drawdown_pct'].min():.2f}%"
        )
