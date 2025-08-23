from typing import List, Literal, Optional

from pydantic import BaseModel, Field

# from finter.backtest.config.config import AVAILABLE_MARKETS


class SignalConfig(BaseModel):
    """Signal configuration model"""

    universe: Literal["kr_stock", "us_stock"] = Field(
        ..., description="Trading Universe"
    )
    first_date: int = Field(
        ...,
        description="Data start date (YYYYMMDD) - rebalance anchor",
        ge=19900101,
        le=30000101,
    )
    data_list: List[str] = Field(..., description="Data list")

    data_lookback: int = Field(
        default=0,
        ge=0,
        description="Data lookback point",
    )
    signal_lookback: int = Field(
        default=0,
        ge=0,
        description="Previous signal reference point",
    )

    rebalance: Optional[int] = Field(
        default=None,
        description="Rebalancing period (business days)",
    )
