"""Tests for BracketOrderMixin (validation and successful flows)."""

from unittest.mock import AsyncMock

import pytest

from project_x_py.exceptions import ProjectXOrderError
from project_x_py.models import BracketOrderResponse, OrderPlaceResponse


@pytest.mark.asyncio
class TestBracketOrderMixin:
    """Unit tests for BracketOrderMixin bracket order placement."""

    @pytest.mark.parametrize(
        "side, entry, stop, target, err",
        [
            (0, 100.0, 101.0, 102.0, "stop loss (101.0) must be below entry (100.0)"),
            (0, 100.0, 99.0, 99.0, "take profit (99.0) must be above entry (100.0)"),
            (1, 100.0, 99.0, 98.0, "stop loss (99.0) must be above entry (100.0)"),
            (1, 100.0, 101.0, 101.0, "take profit (101.0) must be below entry (100.0)"),
        ],
    )
    async def test_bracket_order_validation_fails(self, side, entry, stop, target, err):
        """BracketOrderMixin validates stop/take_profit price relationships."""
        from project_x_py.order_manager.bracket_orders import BracketOrderMixin

        mixin = BracketOrderMixin()
        mixin.place_market_order = AsyncMock()
        mixin.place_limit_order = AsyncMock()
        mixin.place_stop_order = AsyncMock()
        mixin.position_orders = {
            "FOO": {"entry_orders": [], "stop_orders": [], "target_orders": []}
        }
        mixin.stats = {"bracket_orders": 0}
        with pytest.raises(ProjectXOrderError) as exc:
            await mixin.place_bracket_order(
                "FOO", side, 1, entry, stop, target, entry_type="limit"
            )
        assert err in str(exc.value)

    async def test_bracket_order_success_flow(self):
        """Successful bracket order path places all three orders and updates stats/caches."""
        from project_x_py.order_manager.bracket_orders import BracketOrderMixin

        mixin = BracketOrderMixin()
        mixin.place_market_order = AsyncMock(
            return_value=OrderPlaceResponse(
                orderId=1, success=True, errorCode=0, errorMessage=None
            )
        )
        mixin.place_limit_order = AsyncMock(
            side_effect=[
                OrderPlaceResponse(
                    orderId=2, success=True, errorCode=0, errorMessage=None
                ),
                OrderPlaceResponse(
                    orderId=3, success=True, errorCode=0, errorMessage=None
                ),
            ]
        )
        mixin.place_stop_order = AsyncMock(
            return_value=OrderPlaceResponse(
                orderId=4, success=True, errorCode=0, errorMessage=None
            )
        )
        mixin.position_orders = {
            "BAR": {"entry_orders": [], "stop_orders": [], "target_orders": []}
        }
        mixin.stats = {"bracket_orders": 0}
        # Mock the methods that are called from bracket_orders
        mixin._wait_for_order_fill = AsyncMock(return_value=True)
        mixin._link_oco_orders = AsyncMock()

        # Mock the new methods added for race condition fix
        mixin.get_order_by_id = AsyncMock(return_value=None)  # Simulate filled order
        mixin._check_order_fill_status = AsyncMock(
            return_value=(True, 2, 0)
        )  # Fully filled
        mixin._place_protective_orders_with_retry = AsyncMock(
            return_value=(
                OrderPlaceResponse(
                    orderId=4, success=True, errorCode=0, errorMessage=None
                ),
                OrderPlaceResponse(
                    orderId=3, success=True, errorCode=0, errorMessage=None
                ),
            )
        )

        # Create a side effect that updates position_orders
        async def mock_track_order(contract_id, order_id, order_type, account_id=None):
            if contract_id not in mixin.position_orders:
                mixin.position_orders[contract_id] = {
                    "entry_orders": [],
                    "stop_orders": [],
                    "target_orders": [],
                }
            if order_type == "entry":
                mixin.position_orders[contract_id]["entry_orders"].append(order_id)
            elif order_type == "stop":
                mixin.position_orders[contract_id]["stop_orders"].append(order_id)
            elif order_type == "target":
                mixin.position_orders[contract_id]["target_orders"].append(order_id)

        mixin.track_order_for_position = AsyncMock(side_effect=mock_track_order)
        mixin.close_position = AsyncMock()
        mixin.cancel_order = AsyncMock()
        mixin.oco_groups = {}

        # Entry type = limit
        resp = await mixin.place_bracket_order(
            "BAR", 0, 2, 100.0, 99.0, 103.0, entry_type="limit"
        )
        assert isinstance(resp, BracketOrderResponse)
        assert resp.success
        assert resp.entry_order_id == 2
        assert resp.stop_order_id == 4
        assert resp.target_order_id == 3
        assert mixin.position_orders["BAR"]["entry_orders"][-1] == 2
        assert mixin.position_orders["BAR"]["stop_orders"][-1] == 4
        assert mixin.position_orders["BAR"]["target_orders"][-1] == 3
        assert mixin.stats["bracket_orders"] == 1
