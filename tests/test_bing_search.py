"""
Unit tests for bing_search.py

All Selenium / WebDriver interactions are mocked so no real browser is needed.
Run with:
    pytest --cov=bing_search --cov-report=term-missing
"""

import builtins
import io
import pytest
from unittest.mock import MagicMock, patch, call, mock_open

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

import bing_search


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_driver():
    """Return a fresh MagicMock that mimics a Selenium WebDriver."""
    return MagicMock()


# ===========================================================================
# read_file_to_list
# ===========================================================================

class TestReadFileToList:
    def test_success(self, tmp_path):
        """Happy path: returns stripped lines from the file."""
        f = tmp_path / "topics.txt"
        f.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")

        result = bing_search.read_file_to_list(str(f))

        assert result == ["alpha", "beta", "gamma"]

    def test_empty_file(self, tmp_path):
        """An empty file returns an empty list (not a list with a blank entry)."""
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")

        result = bing_search.read_file_to_list(str(f))

        assert result == []

    def test_strips_whitespace(self, tmp_path):
        """Lines with leading/trailing whitespace are stripped."""
        f = tmp_path / "topics.txt"
        f.write_text("  hello  \n  world  \n", encoding="utf-8")

        result = bing_search.read_file_to_list(str(f))

        assert result == ["hello", "world"]

    def test_file_not_found(self, capsys):
        """Missing file prints an error and returns an empty list."""
        result = bing_search.read_file_to_list("/nonexistent/path/file.txt")

        captured = capsys.readouterr()
        assert result == []
        assert "was not found" in captured.out

    def test_io_error(self, capsys):
        """IOError during read prints an error and returns an empty list."""
        with patch("builtins.open", side_effect=IOError("disk full")):
            result = bing_search.read_file_to_list("anything.txt")

        captured = capsys.readouterr()
        assert result == []
        assert "Error reading file" in captured.out


# ===========================================================================
# login_to_current_user
# ===========================================================================

class TestLoginToCurrentUser:
    def test_prints_message(self, capsys):
        """Function should print the automatic-login message."""
        driver = _make_driver()
        bing_search.login_to_current_user(driver)

        captured = capsys.readouterr()
        assert "automatic login" in captured.out.lower()


# ===========================================================================
# auto_accept_cookies
# ===========================================================================

class TestAutoAcceptCookies:
    def _make_wait(self, side_effects):
        """
        Build a patched WebDriverWait whose .until() raises or returns a mock
        element according to *side_effects* (one entry per selector attempt).
        """
        wait_instance = MagicMock()
        wait_instance.until.side_effect = side_effects
        return wait_instance

    def test_accepts_first_selector(self, capsys):
        """When the first selector succeeds the element is clicked and we break."""
        elem = MagicMock()
        driver = _make_driver()

        with patch("bing_search.WebDriverWait") as MockWait:
            MockWait.return_value.until.return_value = elem
            bing_search.auto_accept_cookies(driver)

        elem.click.assert_called_once()
        assert "Accepted cookies" in capsys.readouterr().out

    def test_accepts_fallback_selector(self, capsys):
        """When earlier selectors fail the function tries the next one."""
        elem = MagicMock()
        driver = _make_driver()

        # First two selectors raise, third succeeds
        with patch("bing_search.WebDriverWait") as MockWait:
            MockWait.return_value.until.side_effect = [
                Exception("no match"),
                Exception("no match"),
                elem,
                Exception("no match"),
            ]
            bing_search.auto_accept_cookies(driver)

        elem.click.assert_called_once()

    def test_no_banner_found(self, capsys):
        """When all selectors fail nothing crashes."""
        driver = _make_driver()

        with patch("bing_search.WebDriverWait") as MockWait:
            MockWait.return_value.until.side_effect = Exception("timeout")
            bing_search.auto_accept_cookies(driver)

        # Should not raise; no output expected when every inner except swallows the error
        capsys.readouterr()  # drain output (may be empty)


# ===========================================================================
# create_driver
# ===========================================================================

class TestCreateDriver:
    def test_returns_edge_driver(self):
        """create_driver() must call webdriver.Edge() and return its result."""
        mock_driver = MagicMock()

        with patch("bing_search.webdriver.Edge", return_value=mock_driver) as MockEdge:
            result = bing_search.create_driver()

        MockEdge.assert_called_once()
        assert result is mock_driver


# ===========================================================================
# perform_search
# ===========================================================================

class TestPerformSearch:
    def _setup_wait(self, mock_wait_cls, search_box, results_elem=None):
        """
        Wire up WebDriverWait so that:
          - First .until() call → returns *search_box*
          - Second .until() call → returns *results_elem* (or a new MagicMock)
        """
        results_elem = results_elem or MagicMock()
        mock_wait_cls.return_value.until.side_effect = [search_box, results_elem]

    def test_success(self, capsys):
        """Happy path: clears box, types keyword, presses Enter, waits for results."""
        driver = _make_driver()
        search_box = MagicMock()

        with patch("bing_search.WebDriverWait") as MockWait, \
             patch("bing_search.auto_accept_cookies") as mock_cookies:
            self._setup_wait(MockWait, search_box)
            bing_search.perform_search(driver, "python testing", timeout=5)

        search_box.clear.assert_called_once()
        search_box.send_keys.assert_any_call("python testing")
        search_box.send_keys.assert_any_call(Keys.RETURN)
        mock_cookies.assert_called_once_with(driver)
        assert "loaded" in capsys.readouterr().out

    def test_timeout_exception(self, capsys):
        """TimeoutException is caught and an error message is printed."""
        driver = _make_driver()

        with patch("bing_search.WebDriverWait") as MockWait:
            MockWait.return_value.until.side_effect = TimeoutException("timed out")
            bing_search.perform_search(driver, "slow query", timeout=1)

        assert "An error occurred while searching for 'slow query'" in capsys.readouterr().out

    def test_generic_exception(self, capsys):
        """Any other exception is caught and an error message is printed."""
        driver = _make_driver()

        with patch("bing_search.WebDriverWait") as MockWait:
            MockWait.return_value.until.side_effect = RuntimeError("network down")
            bing_search.perform_search(driver, "bad query", timeout=1)

        assert "An error occurred while searching for 'bad query'" in capsys.readouterr().out


# ===========================================================================
# run_searches
# ===========================================================================

class TestRunSearches:
    def test_single_keyword_no_sleep(self, capsys):
        """With a single keyword perform_search is called once and sleep is not called."""
        driver = _make_driver()

        with patch("bing_search.perform_search") as mock_search, \
             patch("bing_search.time.sleep") as mock_sleep:
            bing_search.run_searches(driver, ["only one"], timeout=5,
                                     min_delay=1, max_delay=2)

        mock_search.assert_called_once_with(driver, "only one", 5)
        mock_sleep.assert_not_called()
        assert "All keywords have been searched" in capsys.readouterr().out

    def test_multiple_keywords_sleep_between(self, capsys):
        """Sleep is called exactly N-1 times for N keywords."""
        driver = _make_driver()
        keywords = ["alpha", "beta", "gamma"]

        with patch("bing_search.perform_search") as mock_search, \
             patch("bing_search.time.sleep") as mock_sleep, \
             patch("bing_search.random.randint", return_value=7):
            bing_search.run_searches(driver, keywords, timeout=5,
                                     min_delay=3, max_delay=10)

        assert mock_search.call_count == 3
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(7)

    def test_empty_keywords(self, capsys):
        """Empty keyword list → perform_search never called, completion message still printed."""
        driver = _make_driver()

        with patch("bing_search.perform_search") as mock_search, \
             patch("bing_search.time.sleep") as mock_sleep:
            bing_search.run_searches(driver, [], timeout=5, min_delay=1, max_delay=2)

        mock_search.assert_not_called()
        mock_sleep.assert_not_called()
        assert "All keywords have been searched" in capsys.readouterr().out


# ===========================================================================
# main
# ===========================================================================

class TestMain:
    def test_driver_init_fails(self, capsys):
        """If create_driver() raises, main() prints the error and returns early."""
        with patch("bing_search.create_driver", side_effect=Exception("no edge")):
            bing_search.main()

        out = capsys.readouterr().out
        assert "Could not start Microsoft Edge WebDriver" in out

    def test_no_keywords_quits_driver(self, capsys):
        """If topics.txt is empty, the driver is quit and main() returns."""
        mock_driver = MagicMock()

        with patch("bing_search.create_driver", return_value=mock_driver), \
             patch("bing_search.read_file_to_list", return_value=[]):
            bing_search.main()

        mock_driver.quit.assert_called()
        assert "No topics found" in capsys.readouterr().out

    def test_success_full_flow(self, capsys):
        """Happy path: driver is created, Bing is opened, searches run, browser closed."""
        mock_driver = MagicMock()
        keywords = ["topic one", "topic two"]

        with patch("bing_search.create_driver", return_value=mock_driver), \
             patch("bing_search.read_file_to_list", return_value=keywords), \
             patch("bing_search.login_to_current_user") as mock_login, \
             patch("bing_search.auto_accept_cookies") as mock_cookies, \
             patch("bing_search.run_searches") as mock_run:
            bing_search.main()

        mock_driver.maximize_window.assert_called_once()
        mock_driver.get.assert_called_once_with(bing_search.BING_URL)
        mock_login.assert_called_once_with(mock_driver)
        mock_cookies.assert_called_once_with(mock_driver)
        mock_run.assert_called_once_with(mock_driver, keywords)
        # Browser must be closed in the finally block
        mock_driver.quit.assert_called()
        assert "Browser closed" in capsys.readouterr().out

    def test_unexpected_exception_in_main(self, capsys):
        """An unexpected exception inside main() is caught, driver is quit."""
        mock_driver = MagicMock()

        with patch("bing_search.create_driver", return_value=mock_driver), \
             patch("bing_search.read_file_to_list", return_value=["kw"]), \
             patch("bing_search.login_to_current_user", side_effect=RuntimeError("crash")):
            bing_search.main()

        out = capsys.readouterr().out
        assert "An unexpected error occurred" in out
        mock_driver.quit.assert_called()

