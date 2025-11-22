from unittest.mock import patch

from scrapers.utils.rate_limiter import RateLimiter, rate_limit


class TestRateLimiter:
    def test_init(self):
        limiter = RateLimiter(calls_per_second=2.0)
        assert limiter.min_interval == 0.5

        limiter_default = RateLimiter()
        assert limiter_default.min_interval == 1.0 / 5.0  # Default is 5.0

    @patch("time.time")
    @patch("time.sleep")
    def test_wait_no_sleep_needed(self, mock_sleep, mock_time):
        limiter = RateLimiter(calls_per_second=1.0)  # min_interval = 1.0

        # First call, set last_call
        mock_time.side_effect = [
            100.0,
            100.0,
            101.5,
        ]  # time() at start, time() at end (for last_call update), time() at start of next wait

        limiter.wait()  # time() called twice here implicitly (once by elapsed, once by last_call)
        assert limiter.last_call == 100.0
        mock_sleep.assert_not_called()

        # Second call immediately after (elapsed = 0), sleep needed. We control the time precisely here.
        mock_time.side_effect = [100.0, 100.0]  # Subsequent time calls
        limiter.wait()
        assert mock_sleep.called_once_with(
            1.0
        )  # Should sleep for min_interval - (100-100) = 1.0
        assert limiter.last_call == 100.0  # last_call updated

        # Third call after enough time (elapsed = 1.5 from current last_call), no sleep needed
        mock_time.side_effect = [101.5, 101.5]
        mock_sleep.reset_mock()  # Reset mock to check calls from this point
        limiter.wait()
        mock_sleep.assert_not_called()
        assert limiter.last_call == 101.5

    @patch("time.time")
    @patch("time.sleep")
    def test_wait_with_sleep_needed(self, mock_sleep, mock_time):
        limiter = RateLimiter(calls_per_second=2.0)  # min_interval = 0.5

        # Sequence of time.time() calls: [start_wait_1, end_wait_1, start_wait_2, end_wait_2, start_wait_3, end_wait_3]
        mock_time.side_effect = [
            100.0,
            100.0,  # First call: no sleep
            100.2,
            100.2,  # Second call: sleep (0.5 - (100.2-100.0)) = 0.3
            100.3,
            100.3,
        ]  # Third call: sleep (0.5 - (100.3-100.2)) = 0.4

        # First call
        limiter.wait()
        assert limiter.last_call == 100.0
        mock_sleep.assert_not_called()

        # Second call
        limiter.wait()
        assert len(mock_sleep.call_args_list) == 1
        assert abs(mock_sleep.call_args_list[0][0][0] - 0.3) < 1e-9
        assert limiter.last_call == 100.2

        # Third call
        limiter.wait()
        assert len(mock_sleep.call_args_list) == 2
        assert abs(mock_sleep.call_args_list[1][0][0] - 0.4) < 1e-9
        assert limiter.last_call == 100.3


class TestRateLimitDecorator:
    @patch("time.time")
    @patch("time.sleep")
    def test_decorator_applies_limit(self, mock_sleep, mock_time):
        # Each test_func() call will invoke time.time() twice:
        # once at the beginning of wait() (for elapsed)
        # and once at the end of wait() (to update last_call).
        mock_time.side_effect = [
            100.0,
            100.0,  # test_func() 1
            100.1,
            100.1,  # test_func() 2
            100.6,
            100.6,  # test_func() 3
            100.7,
            100.7,  # test_func() 4
        ]

        @rate_limit(calls_per_second=2.0)  # min_interval = 0.5
        def test_func():
            return "executed"

        # First call
        result1 = test_func()
        assert result1 == "executed"
        assert mock_sleep.call_count == 0  # No sleep on first call

        # Second call
        result2 = test_func()
        assert result2 == "executed"
        # Expected sleep: min_interval (0.5) - (current_time (100.1) - last_call (100.0)) = 0.4
        assert len(mock_sleep.call_args_list) == 1
        assert abs(mock_sleep.call_args_list[0][0][0] - 0.4) < 1e-9

        # Third call
        result3 = test_func()
        assert result3 == "executed"
        # Expected sleep: min_interval (0.5) - (current_time (100.6) - last_call (100.1)) = 0.0 (no sleep)
        assert len(mock_sleep.call_args_list) == 1  # No new sleep call

        # Fourth call
        result4 = test_func()
        assert result4 == "executed"
        # Expected sleep: min_interval (0.5) - (current_time (100.7) - last_call (100.6)) = 0.4
        assert len(mock_sleep.call_args_list) == 2  # One new sleep call
        assert abs(mock_sleep.call_args_list[1][0][0] - 0.4) < 1e-9
