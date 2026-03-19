"""Tests for batch geocoding functions."""

import csv
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from geoclient.batch_geocode import (
    batch_geocode_addresses,
    geocode_csv,
    load_addresses_from_csv,
    save_results_to_csv,
)
from geoclient.exceptions import GeoClientError


class TestLoadAddressesFromCsv:
    """Tests for load_addresses_from_csv."""

    def test_basic_load(self, tmp_path):
        csv_file = tmp_path / "addresses.csv"
        csv_file.write_text(
            "house_number,street,borough\n"
            "314,west 100 st,manhattan\n"
            "350,5th ave,manhattan\n",
            encoding="utf-8",
        )
        addresses = load_addresses_from_csv(str(csv_file))
        assert len(addresses) == 2
        assert addresses[0] == {"house_number": "314", "street": "west 100 st", "borough": "manhattan"}
        assert addresses[1] == {"house_number": "350", "street": "5th ave", "borough": "manhattan"}

    def test_column_names_with_spaces(self, tmp_path):
        csv_file = tmp_path / "addresses.csv"
        csv_file.write_text(
            "house number,street,borough\n"
            "120,broadway,manhattan\n",
            encoding="utf-8",
        )
        addresses = load_addresses_from_csv(str(csv_file))
        assert len(addresses) == 1
        assert addresses[0]["house_number"] == "120"

    def test_column_names_case_insensitive(self, tmp_path):
        csv_file = tmp_path / "addresses.csv"
        csv_file.write_text(
            "House_Number,STREET,Borough\n"
            "1,wall st,manhattan\n",
            encoding="utf-8",
        )
        addresses = load_addresses_from_csv(str(csv_file))
        assert addresses[0] == {"house_number": "1", "street": "wall st", "borough": "manhattan"}

    def test_strips_whitespace(self, tmp_path):
        csv_file = tmp_path / "addresses.csv"
        csv_file.write_text(
            "house_number,street,borough\n"
            "  314 , west 100 st , manhattan \n",
            encoding="utf-8",
        )
        addresses = load_addresses_from_csv(str(csv_file))
        assert addresses[0] == {"house_number": "314", "street": "west 100 st", "borough": "manhattan"}

    def test_empty_csv(self, tmp_path):
        csv_file = tmp_path / "addresses.csv"
        csv_file.write_text("house_number,street,borough\n", encoding="utf-8")
        addresses = load_addresses_from_csv(str(csv_file))
        assert addresses == []

    def test_missing_column_raises_error(self, tmp_path):
        csv_file = tmp_path / "addresses.csv"
        csv_file.write_text(
            "house_number,street\n"
            "314,west 100 st\n",
            encoding="utf-8",
        )
        with pytest.raises(KeyError):
            load_addresses_from_csv(str(csv_file))

    def test_null_house_number_column_missing(self, tmp_path):
        """Missing house_number column produces None, not a KeyError."""
        csv_file = tmp_path / "addresses.csv"
        csv_file.write_text(
            "street,borough\n"
            "broadway,manhattan\n",
            encoding="utf-8",
        )
        addresses = load_addresses_from_csv(str(csv_file))
        assert len(addresses) == 1
        assert addresses[0]["house_number"] is None
        assert addresses[0]["street"] == "broadway"

    def test_empty_house_number_value(self, tmp_path):
        """Empty house_number value in CSV is normalised to None."""
        csv_file = tmp_path / "addresses.csv"
        csv_file.write_text(
            "house_number,street,borough\n"
            ",broadway,manhattan\n",
            encoding="utf-8",
        )
        addresses = load_addresses_from_csv(str(csv_file))
        assert len(addresses) == 1
        assert addresses[0]["house_number"] is None


class TestBatchGeocodeAddresses:
    """Tests for batch_geocode_addresses."""

    def _mock_client(self, responses):
        """Create a mock client that returns responses in order."""
        client = MagicMock()
        client.address = MagicMock(side_effect=responses)
        return client

    def _mock_address_response(self, **kwargs):
        defaults = {
            "house_number": "314",
            "street_name": "WEST  100 STREET",
            "borough_name": "MANHATTAN",
            "latitude": 40.798178,
            "longitude": -73.972225,
            "zip_code": "10025",
            "bbl": "1018887502",
            "bin": "1055440",
            "community_district": "107",
            "cross_street_one": "WEST END AVENUE",
            "cross_street_two": "RIVERSIDE DRIVE",
            "geosupport": MagicMock(return_code="00"),
        }
        defaults.update(kwargs)
        mock = MagicMock()
        for key, val in defaults.items():
            setattr(mock, key, val)
        return mock

    def test_all_succeed(self):
        addresses = [
            {"house_number": "314", "street": "west 100 st", "borough": "manhattan"},
            {"house_number": "120", "street": "broadway", "borough": "manhattan"},
        ]
        responses = [self._mock_address_response(), self._mock_address_response(house_number="120")]
        client = self._mock_client(responses)

        results = batch_geocode_addresses(addresses, client, delay=0)
        assert len(results) == 2
        assert all(r["success"] for r in results)
        assert results[0]["input_house_number"] == "314"
        assert results[0]["latitude"] == 40.798178
        assert results[0]["cross_street_one"] == "WEST END AVENUE"
        assert results[0]["cross_street_two"] == "RIVERSIDE DRIVE"
        assert results[0]["error_message"] is None

    def test_one_failure(self):
        addresses = [
            {"house_number": "314", "street": "west 100 st", "borough": "manhattan"},
            {"house_number": "invalid", "street": "fake st", "borough": "manhattan"},
        ]
        responses = [
            self._mock_address_response(),
            GeoClientError("NOT RECOGNIZED"),
        ]
        client = self._mock_client(responses)

        results = batch_geocode_addresses(addresses, client, delay=0)
        assert len(results) == 2
        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert results[1]["error_message"] == "NOT RECOGNIZED"
        assert results[1]["latitude"] is None
        assert results[1]["cross_street_one"] is None
        assert results[1]["cross_street_two"] is None

    def test_all_fail(self):
        addresses = [
            {"house_number": "bad", "street": "fake", "borough": "manhattan"},
        ]
        client = self._mock_client([GeoClientError("FAIL")])

        results = batch_geocode_addresses(addresses, client, delay=0)
        assert len(results) == 1
        assert results[0]["success"] is False

    def test_empty_list(self):
        client = MagicMock()
        results = batch_geocode_addresses([], client, delay=0)
        assert results == []
        client.address.assert_not_called()

    def test_result_keys_consistent(self):
        """Success and failure dicts must have the same keys for CSV output."""
        addresses = [
            {"house_number": "314", "street": "west 100 st", "borough": "manhattan"},
            {"house_number": "bad", "street": "fake", "borough": "manhattan"},
        ]
        responses = [self._mock_address_response(), GeoClientError("FAIL")]
        client = self._mock_client(responses)

        results = batch_geocode_addresses(addresses, client, delay=0)
        assert results[0].keys() == results[1].keys()

    def test_null_house_number_produces_error_result(self):
        """A None house_number is recorded as a failure without raising."""
        addresses = [
            {"house_number": None, "street": "broadway", "borough": "manhattan"},
        ]
        client = MagicMock()

        results = batch_geocode_addresses(addresses, client, delay=0)
        assert len(results) == 1
        assert results[0]["success"] is False
        assert results[0]["input_house_number"] is None
        assert results[0]["latitude"] is None
        assert results[0]["error_message"] is not None
        client.address.assert_not_called()

    def test_empty_string_house_number_produces_error_result(self):
        """An empty-string house_number is recorded as a failure without raising."""
        addresses = [
            {"house_number": "", "street": "broadway", "borough": "manhattan"},
        ]
        client = MagicMock()

        results = batch_geocode_addresses(addresses, client, delay=0)
        assert len(results) == 1
        assert results[0]["success"] is False
        assert results[0]["input_house_number"] == ""
        assert results[0]["error_message"] is not None
        client.address.assert_not_called()

    def test_null_house_number_result_keys_match_success(self):
        """Null-house-number failure dict has the same keys as a success dict."""
        addresses = [
            {"house_number": "314", "street": "west 100 st", "borough": "manhattan"},
            {"house_number": None, "street": "broadway", "borough": "manhattan"},
        ]
        responses = [self._mock_address_response()]
        client = self._mock_client(responses)

        results = batch_geocode_addresses(addresses, client, delay=0)
        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert results[0].keys() == results[1].keys()


class TestSaveResultsToCsv:
    """Tests for save_results_to_csv."""

    def test_saves_correct_content(self, tmp_path):
        output = tmp_path / "results.csv"
        results = [
            {"input_house_number": "314", "success": True, "latitude": 40.798},
            {"input_house_number": "bad", "success": False, "latitude": None},
        ]
        save_results_to_csv(results, str(output))

        with open(output, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2
        assert rows[0]["input_house_number"] == "314"
        assert rows[1]["success"] == "False"

    def test_empty_results(self, tmp_path, capsys):
        output = tmp_path / "results.csv"
        save_results_to_csv([], str(output))
        assert not output.exists()
        assert "No results" in capsys.readouterr().out


class TestGeocodeCsv:
    """Tests for geocode_csv end-to-end."""

    def test_end_to_end(self, tmp_path):
        # Write input CSV
        input_file = tmp_path / "in.csv"
        input_file.write_text(
            "house_number,street,borough\n"
            "314,west 100 st,manhattan\n",
            encoding="utf-8",
        )
        output_file = tmp_path / "out.csv"

        mock_response = MagicMock()
        mock_response.house_number = "314"
        mock_response.street_name = "WEST  100 STREET"
        mock_response.borough_name = "MANHATTAN"
        mock_response.latitude = 40.798178
        mock_response.longitude = -73.972225
        mock_response.zip_code = "10025"
        mock_response.bbl = "1018887502"
        mock_response.bin = "1055440"
        mock_response.community_district = "107"
        mock_response.cross_street_one = "WEST END AVENUE"
        mock_response.cross_street_two = "RIVERSIDE DRIVE"
        mock_response.geosupport = MagicMock(return_code="00")

        with patch("geoclient.batch_geocode.GeoClient") as MockClient:
            instance = MockClient.return_value.__enter__.return_value
            instance.address.return_value = mock_response
            geocode_csv(str(input_file), str(output_file), delay=0)

        with open(output_file, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 1
        assert rows[0]["success"] == "True"
        assert rows[0]["bbl"] == "1018887502"
        assert rows[0]["cross_street_one"] == "WEST END AVENUE"
