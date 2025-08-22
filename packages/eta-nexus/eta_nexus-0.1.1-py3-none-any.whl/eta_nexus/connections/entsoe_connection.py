"""Utility functions for connecting to the ENTSO-E Transparency database and for reading data. This connection
does not have the ability to write data.
"""

from __future__ import annotations

import concurrent.futures
import os
from contextlib import suppress
from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import requests
from lxml import etree
from requests_cache import DO_NOT_CACHE, CachedSession

from eta_nexus.connections.connection import Connection, SeriesReadable
from eta_nexus.nodes import EntsoeNode
from eta_nexus.timeseries import df_resample, df_time_slice
from eta_nexus.util import dict_search, round_timestamp

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any, Final

    from eta_nexus.util.type_annotations import Nodes, TimeStep


log = getLogger(__name__)


class EntsoeConnection(Connection[EntsoeNode], SeriesReadable[EntsoeNode], protocol="entsoe"):
    """ENTSOEConnection is a class to download and upload multiple features from and to the
    ENTSO-E transparency platform database as timeseries.
    The platform contains data about the european electricity markets.

    :param url: Url of the server with scheme (https://web-api.tp.entsoe.eu/)
    :param usr: Username for login to the platform (usually not required - default: None)
    :param pwd: Password for login to the platform (usually not required - default: None)
    :param nodes: Nodes to select in connection
    """

    API_PATH: str = "api"

    def __init__(
        self,
        url: str = "https://web-api.tp.entsoe.eu",
        *,
        nodes: Nodes[EntsoeNode] | None = None,
    ) -> None:
        url = url.rstrip("/") + "/" + self.API_PATH
        super().__init__(url, None, None, nodes=nodes)

        _api_token: str | None = os.getenv("ENTSOE_API_TOKEN")
        if _api_token is None:
            raise ValueError("ENTSOE_API_TOKEN environment variable is not set.")
        self._api_token: str = _api_token

        self._node_ids: str | None = None
        self.config = _ConnectionConfiguration()
        self._session: CachedSession = CachedSession(
            cache_name="eta_nexus/connections/requests_cache/entso_e_cache",
            urls_expire_after={
                url + "/*": timedelta(minutes=15),
                "*": DO_NOT_CACHE,  # Don't cache other URLs
            },
            allowable_codes=(200, 400, 401),
            use_cache_dir=True,
        )

    @classmethod
    def _from_node(cls, node: EntsoeNode, **kwargs: Any) -> EntsoeConnection:
        """Initialize the connection object from an entso-e protocol node object.

        :param node: Node to initialize from
        :return: ENTSOEConnection object
        """

        return super()._from_node(node)

    def _handle_xml(self, xml_content: bytes) -> dict[str, dict[str, list[pd.Series]]]:
        """Transform XML data from request response into dictionary containing resolutions and time series for the node.

        :param xml_content: XML data
        :return: Dictionary with resolutions and time series data
        """
        parser = etree.XMLParser(load_dtd=False, ns_clean=True, remove_pis=True)
        xml_data = etree.XML(xml_content, parser)
        ns = xml_data.nsmap
        data: dict[str, dict[str, list[pd.Series]]] = {}
        request_type = xml_data.find(".//type", namespaces=ns).text

        timeseries = xml_data.findall(".//TimeSeries", namespaces=ns)
        for ts in timeseries:
            # Day-Ahead Price
            if request_type == "A44":
                col_name = "Price"

            # Actual Generation per Type
            if request_type == "A75":
                psr_type = ts.find(".//MktPSRType", namespaces=ns).find("psrType", namespaces=ns).text
                col_name = dict_search(self.config.psr_types, psr_type)

                if ts.find(".//inBiddingZone_Domain.mRID", namespaces=ns) is not None:
                    col_name = col_name + "_Generation"
                elif ts.find(".//outBiddingZone_Domain.mRID", namespaces=ns) is not None:
                    col_name = col_name + "_Consumption"

            # contains the data points
            period = ts.find(".//Period", namespaces=ns)

            # datetime range of the data points
            time_interval = period.find(".//timeInterval", namespaces=ns).getchildren()
            resolution = period.find(".//resolution", namespaces=ns).text[2:4]  # truncating string PR60M
            datetime_range = pd.date_range(
                datetime.strptime(time_interval[0].text, "%Y-%m-%dT%H:%MZ"),
                datetime.strptime(time_interval[1].text, "%Y-%m-%dT%H:%MZ"),
                freq=resolution + "min",
                inclusive="left",
            )

            points = period.findall(".//Point", namespaces=ns)
            ts_data = [point.getchildren()[-1].text for point in points]

            # Handle missing data points
            if len(ts_data) < len(datetime_range):
                indices = set(range(len(datetime_range)))
                for point in points:
                    indices.remove(int(point.getchildren()[0].text) - 1)

                for miss in indices:
                    ts_data.insert(miss, np.nan)

            s = pd.Series(data=ts_data, index=datetime_range, name=col_name)
            s.index = s.index.tz_localize(tz="UTC")  # ENTSO-E returns always UTC

            if resolution not in data:
                data[resolution] = {}

            if col_name not in data[resolution]:
                data[resolution][col_name] = []

            data[resolution][col_name].append(s.astype(float))

        return data

    def read_series(
        self,
        from_time: datetime,
        to_time: datetime,
        nodes: EntsoeNode | Nodes[EntsoeNode] | None = None,
        interval: TimeStep = 1,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Download timeseries data from the ENTSO-E Database.

        :param nodes: Single node or list/set of nodes to read values from
        :param from_time: Starting time to begin reading (included in output)
        :param to_time: Time to stop reading at (not included in output)
        :param interval: interval between time steps. It is interpreted as seconds if given as integer.
        :return: Pandas DataFrame containing the data read from the connection
        """
        from_time, to_time, nodes, interval = super()._preprocess_series_context(
            from_time, to_time, nodes, interval, **kwargs
        )

        def read_node(node: EntsoeNode) -> pd.DataFrame | None:
            params = self.config.create_params(node, from_time, to_time)

            result = self._raw_request(params)
            if result is None:
                log.warning(f"[ENTSO-E] Skipping node {node.name} due to failed HTTP request.")
                return None
            try:
                data = self._handle_xml(result.content)
            except Exception as e:
                log.warning(
                    f"[ENTSO-E] Failed to parse XML for node {node.name}: {e}"
                    f"Response status code: {result.status_code}. "
                    f"This may be due to a preceding HTTP error or an unexpected response format."
                )
                return None

            df_dict = {}
            # All resolutions are resampled separately and concatenated to one dataframe in the end
            for resolution in data:
                data_resolution = {
                    f"{node.name}_{column}": pd.concat(series) for column, series in data[resolution].items()
                }
                df_resolution = pd.DataFrame.from_dict(data_resolution, orient="columns")
                # entsoe always returns a dataframe in UTC time, convert to same time zone as given from_time
                df_resolution.index = df_resolution.index.tz_convert(tz=from_time.tzinfo)
                df_resolution = df_resample(df_resolution, interval, missing_data="ffill")
                df_resolution = df_time_slice(df_resolution, from_time, to_time)
                df_dict[resolution] = df_resolution
            if not df_dict:
                log.warning(f"[ENTSO-E] No valid data for node {node.name}")
                return None
            value_df = pd.concat(df_dict.values(), axis=1, keys=df_dict.keys())
            value_df = value_df.ffill()
            return value_df.swaplevel(axis=1)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            raw_results = executor.map(read_node, nodes)

            results = [r for r in raw_results if r is not None]

            if not results:
                log.error("[ENTSO-E] No valid data retrieved from any node. All requests failed or returned empty.")
                return pd.DataFrame()

        return pd.concat(results, axis=1, sort=False)

    def _raw_request(self, params: Mapping[str, str], **kwargs: Mapping[str, Any]) -> requests.Response | None:
        """Perform ENTSO-E request and handle possibly resulting errors.

        :param params: Parameters to identify the endpoint
        :param kwargs: Additional arguments for the request.
        :return: request response
        """
        # Prepare the basic request for usage in the requests.
        params = dict(params)
        params["securityToken"] = self._api_token  # API token added as a query parameter

        try:
            response = self._session.get(self.url, params=params, **kwargs)  # Send GET request
            if response.status_code == 400:
                with suppress(Exception):
                    parser = etree.XMLParser(load_dtd=False, ns_clean=True, remove_pis=True)

                    e_msg = etree.XML(response.content, parser)
                    ns = e_msg.nsmap
                    e_code = e_msg.find(".//Reason", namespaces=ns).find("code", namespaces=ns).text
                    e_text = e_msg.find(".//Reason", namespaces=ns).find("text", namespaces=ns).text
                    response.reason = f"ENTSO-E Error {response.status_code} ({e_code}: {e_text})"

            response.raise_for_status()

        except requests.exceptions.HTTPError:
            log.exception(f"[ENTSO-E] HTTPError for params {params}")
            return None

        except requests.exceptions.RequestException:
            log.exception(f"[ENTSO-E] Request failed for params {params}")
            return None
        else:
            return response


class _ConnectionConfiguration:
    """Auxiliary class to configure the parameters for establishing a connection to ENTSO-E API.

    Currently, the connection class only supports two types of data requests through the method read_series, they are:
    **Energy price day ahead** and **Actual energy generation per type**. All the data requests available are listed in
    the _doc_type class attribute, but each of them contains a mandatory list of parameters to establish the connection,
    which can be seemed in the ENTSO-E documentation_.

    .. _documentation: https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html
    """

    #: XML Namespace for the API
    _XMLNS: Final[str] = "urn:iec62325.351:tc57wg16:451-5:statusrequestdocument:4:0"
    #: bidding zones is a mapping of three letter iso country codes to bidding zones.
    _BIDDING_ZONES: Final[dict[str, str]] = {
        "DEU": "10Y1001A1001A83F",
        "DEU-AUT-LUX": "10Y1001A1001A63L",
        "ALB": "10YAL-KESH-----5",
        "AUT": "10YAT-APG------L",
        "BLR": "10Y1001A1001A51S",
        "BEL": "10YBE----------2",
        "BIH": "10YBA-JPCC-----D",
        "BGR": "10YCA-BULGARIA-R",
        "CZE-DEU-SVK": "10YDOM-CZ-DE-SKK",
        "HRV": "10YHR-HEP------M",
        "CYP": "10YCY-1001A0003J",
        "CZE": "10YCZ-CEPS-----N",
        "DEU-LUX": "10Y1001A1001A82H",
        "DNK_west": "10YDK-1--------W",
        "DNK_central": "10YDK-2--------M",
        "EST": "10Y1001A1001A39I",
        "FIN": "10YFI-1--------U",
        "MKD": "10YMK-MEPSO----8",
        "FRA": "10YFR-RTE------C",
        "GB": "17Y0000009369493",
        "GRC": "10YGR-HTSO-----Y",
        "HUN": "10YHU-MAVIR----U",
        "IRL": "10Y1001A1001A59C",
        "ITA_brindisi": "10Y1001A1001A699",
        "ITA_calabria": "10Y1001C--00096J",
        "ITA_central_north": "10Y1001A1001A70O",
        "ITA_central_south": "10Y1001A1001A71M",
        "ITA_foggia": "10Y1001A1001A72K",
        "ITA-GRC": "10Y1001A1001A66F",
        "ITA_malta": "10Y1001A1001A877",
        "ITA_north": "10Y1001A1001A73I",
        "ITA-AUT": "10Y1001A1001A80L",
        "ITA-CHE": "10Y1001A1001A68B",
        "ITA-FRA": "10Y1001A1001A81J",
        "ITA-SVN": "10Y1001A1001A67D",
        "ITA_priolo": "10Y1001A1001A76C",
        "ITA_rossano": "10Y1001A1001A77A",
        "ITA_sardinia": "10Y1001A1001A74G",
        "ITA_sicily": "10Y1001A1001A75E",
        "ITA_south": "10Y1001A1001A788",
        "RUS_kaliningrad": "10Y1001A1001A50U",
        "LVA": "10YLV-1001A00074",
        "LTU": "10YLT-1001A0008Q",
        "LUX": "10YLU-CEGEDEL-NQ",
        "MLT": "10Y1001A1001A93C",
        "MNE": "10YCS-CG-TSO---S",
        "GBR": "10YGB----------A",
        "NLD": "10YNL----------L",
        "NOR_1": "10YNO-1--------2",
        "NOR_2": "10YNO-2--------T",
        "NOR_3": "10YNO-3--------J",
        "NOR_4": "10YNO-4--------9",
        "NOR_5": "10Y1001A1001A48H",
        "POL": "10YPL-AREA-----S",
        "PRT": "10YPT-REN------W",
        "MDA": "10Y1001A1001A990",
        "ROU": "10YRO-TEL------P",
        "RUS": "10Y1001A1001A49F",
        "SWE_1": "10Y1001A1001A44P",
        "SWE_2": "10Y1001A1001A45N",
        "SWE_3": "10Y1001A1001A46L",
        "SWE_4": "10Y1001A1001A47J",
        "SRB": "10YCS-SERBIATSOV",
        "SVK": "10YSK-SEPS-----K",
        "SVN": "10YSI-ELES-----O",
        "ESP": "10YES-REE------0",
        "SWE": "10YSE-1--------K",
        "CHE": "10YCH-SWISSGRIDZ",
        "TUR": "10YTR-TEIAS----W",
        "UKR": "10Y1001C--00003F",
    }

    _MARKET_AGREEMENTS: Final[dict[str, str]] = {
        "Daily": "A01",
        "Weekly": "A02",
        "Monthly": "A03",
        "Yearly": "A04",
        "Total": "A05",
        "Long term": "A06",
        "Intraday": "A07",
        "Hourly": "A13",
    }

    _AUCTION_TYPES: Final[dict[str, str]] = {
        "Implicit": "A01",
        "Explicit": "A02",
    }

    _AUCTION_CATEGORIES: Final[dict[str, str]] = {
        "Base": "A01",
        "Peak": "A02",
        "Off Peak": "A03",
        "Hourly": "A04",
    }

    _PSR_TYPES: Final[dict[str, str]] = {
        "Mixed": "A03",
        "Generation": "A04",
        "Load": "A05",
        "Biomass": "B01",
        "Fossil Brown coal/Lignite": "B02",
        "Fossil Coal-derived gas": "B03",
        "Fossil Gas": "B04",
        "Fossil Hard coal": "B05",
        "Fossil Oil": "B06",
        "Fossil Oil shale": "B07",
        "Fossil Peat": "B08",
        "Geothermal": "B09",
        "Hydro Pumped Storage": "B10",
        "Hydro Run-of-river and poundage": "B11",
        "Hydro Water Reservoir": "B12",
        "Marine": "B13",
        "Nuclear": "B14",
        "Other renewable": "B15",
        "Solar": "B16",
        "Waste": "B17",
        "Wind Offshore": "B18",
        "Wind Onshore": "B19",
        "Other": "B20",
        "AC Link": "B21",
        "DC Link": "B22",
        "Substation": "B23",
        "Transformer": "B24",
    }

    _BUSINESS_TYPES: Final[dict[str, str]] = {
        "General Capacity Information": "A25",
        "Already allocated capacity (AAC)": "A29",
        "Requested capacity (without price)": "A43",
        "System Operator redispatching": "A46",
        "Planned maintenance": "A53",
        "Unplanned outage": "A54",
        "Internal redispatch": "A85",
        "Frequency containment reserve": "A95",
        "Automatic frequency restoration reserve": "A96",
        "Manual frequency restoration reserve": "A97",
        "Replacement reserve": "A98",
        "Interconnector network evolution": "B01",
        "Interconnector network dismantling": "B02",
        "Counter trade": "B03",
        "Congestion costs": "B04",
        "Capacity allocated (including price)": "B05",
        "Auction revenue": "B07",
        "Total nominated capacity": "B08",
        "Net position": "B09",
        "Congestion income": "B10",
        "Production unit": "B11",
        "Area Control Error": "B33",
        "Procured capacity": "B95",
        "Shared Balancing Reserve Capacity": "C22",
        "Share of reserve capacity": "C23",
        "Actual reserve capacity": "C24",
    }

    _PROCESS_TYPES: Final[dict[str, str]] = {
        "Day ahead": "A01",
        "Intra day incremental": "A02",
        "Realised": "A16",
        "Intraday total": "A18",
        "Week ahead": "A31",
        "Month ahead": "A32",
        "Year ahead": "A33",
        "Synchronisation process": "A39",
        "Intraday process": "A40",
        "Replacement reserve": "A46",
        "Manual frequency restoration reserve": "A47",
        "Automatic frequency restoration reserve": "A51",
        "Frequency containment reserve": "A52",
        "Frequency restoration reserve": "A56",
    }

    _DOC_STATES: Final[dict[str, str]] = {
        "Intermediate": "A01",
        "Final": "A02",
        "Active": "A05",
        "Cancelled": "A09",
        "Withdrawn": "A13",
        "Estimated": "X01",
    }

    _DOC_TYPES: Final[dict[str, str]] = {
        "FinalisedSchedule": "A09",
        "AggregatedEnergyDataReport": "A11",
        "AcquiringSystemOperatorReserveSchedule": "A15",
        "Bid": "A24",
        "AllocationResult": "A25",
        "Capacity": "A26",
        "AgreedCapacity": "A31",
        "ReserveAllocationResult": "A38",
        "Price": "A44",
        "EstimatedNetTransferCapacity": "A61",
        "RedispatchNotice": "A63",
        "SystemTotalLoad": "A65",
        "InstalledGenerationPerType": "A68",
        "WindAndSolarForecast": "A69",
        "LoadForecastMargin": "A70",
        "GenerationForecast": "A71",
        "ReservoirFillingInformation": "A72",
        "ActualGeneration": "A73",
        "WindAndSolarGeneration": "A74",
        "ActualGenerationPerType": "A75",
        "LoadUnavailability": "A76",
        "ProductionUnavailability": "A77",
        "TransmissionUnavailability": "A78",
        "OffshoreGridInfrastructureUnavailability": "A79",
        "GenerationUnavailability": "A80",
        "ContractedReserves": "A81",
        "AcceptedOffers": "A82",
        "ActivatedBalancingQuantities": "A83",
        "ActivatedBalancingPrices": "A84",
        "ImbalancePrices": "A85",
        "ImbalanceVolume": "A86",
        "FinancialSituation": "A87",
        "CrossBorderBalancing": "A88",
        "ContractedReservePrices": "A89",
        "InterconnectionNetworkExpansion": "A90",
        "CounterTradeNotice": "A91",
        "CongestionCosts": "A92",
        "DCLinkCapacity": "A93",
        "NonEUAllocations": "A94",
        "Configuration": "A95",
        "FlowBasedAllocations": "B11",
    }

    def create_params(self, node: EntsoeNode, from_time: datetime, to_time: datetime) -> dict[str, str]:
        """Create request parameters object according to API specifications
        Handle configuration parameters for each type of connection.

        :param node: ENTSO-E Node
        :param from_time: Starting time
        :param to_time: End time
        :return: Dictionary with parameters
        """
        if node.endpoint not in self._DOC_TYPES:
            raise ValueError(f"Unsupported endpoint for ENTSO-E connection: {node.endpoint}.")

        bidding_zone = self.map_parameter("In_Domain", node.bidding_zone)
        document_type = self.map_parameter("documentType", node.endpoint)

        params = dict([bidding_zone, document_type])

        process_types = {"Price": "A01", "ActualGenerationPerType": "A16"}
        params["processType"] = process_types[node.endpoint]

        # Price endpoints needs an additional bidding zone
        if node.endpoint == "Price":
            params.update({"processType": "A01", "Out_Domain": bidding_zone[1]})
        elif node.endpoint == "ActualGenerationPerType":
            params.update({"processType": "A16"})
        else:
            raise NotImplementedError(f"Endpoint not available: {node.endpoint}")

        # Round down at from_time and up at to_time to receive all necessary values from entsoe
        # entsoe uses always a full hour
        rounded_from_time_utc = round_timestamp(from_time.astimezone(timezone.utc), 3600)
        rounded_to_time_utc = round_timestamp(to_time.astimezone(timezone.utc), 3600)

        if rounded_to_time_utc < to_time.astimezone(timezone.utc):
            rounded_to_time_utc += timedelta(hours=1)

        params["periodStart"] = rounded_from_time_utc.strftime("%Y%m%d%H%M")  # yyyyMMddHHmm
        params["periodEnd"] = rounded_to_time_utc.strftime("%Y%m%d%H%M")  # yyyyMMddHHmm

        return params

    def map_parameter(self, parameter: str, value: str) -> tuple:
        """Map parameters to their corresponding values for the GET request.

        :param parameter: The parameter key
        :param value: The parameter value
        :return: Tuple containing the parameter key and its mapped value
        """
        if parameter in {"Contract_MarketAgreement.Type", "Type_MarketAgreement.Type"}:
            value = self._MARKET_AGREEMENTS[value]
        elif parameter == "Auction.Type":
            value = self._AUCTION_TYPES[value]
        elif parameter == "Auction.Category":
            value = self._AUCTION_CATEGORIES[value]
        elif parameter == "PsrType":
            value = self._PSR_TYPES[value]
        elif parameter == "BusinessType":
            value = self._BUSINESS_TYPES[value]
        elif parameter == "ProcessType":
            value = self._PROCESS_TYPES[value]
        elif parameter == "DocStatus":
            value = self._DOC_STATES[value]
        elif parameter == "documentType":
            value = self._DOC_TYPES[value]
        elif parameter in {"In_Domain", "Out_Domain"}:
            value = self._BIDDING_ZONES[value]

        return parameter, value

    @property
    def psr_types(self) -> dict[str, str]:
        return self._PSR_TYPES

    @property
    def doc_types(self) -> dict[str, str]:
        return self._DOC_TYPES
