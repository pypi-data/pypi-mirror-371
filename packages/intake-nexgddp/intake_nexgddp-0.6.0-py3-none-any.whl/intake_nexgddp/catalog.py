# intake_nexgddp/catalog.py
from datetime import datetime
from typing import Optional, Tuple, Dict, List

import numpy as np
import pandas as pd
import xarray as xr
import OpenVisus as ov
from intake.source.base import DataSource, Schema

# ----------------------------
# Hard-coded domain choices
# ----------------------------
SCENARIO_DATES: Dict[str, Tuple[str, str]] = {
    "historical": ("1950-01-01", "2014-12-31"),
    "ssp126":     ("2015-01-01", "2100-12-31"),
    "ssp245":     ("2015-01-01", "2100-12-31"),
    "ssp370":     ("2015-01-01", "2100-12-31"),
    "ssp585":     ("2015-01-01", "2100-12-31"),
}

AVAILABLE_MODELS: List[str] = [
    "ACCESS-CM2",
    "CanESM5",
    "CESM2",
    "CMCC-CM2-SR5",
    "EC-Earth3",
    "GFDL-ESM4",
    "INM-CM5-0",
    "IPSL-CM6A-LR",
    "MIROC6",
    "MPI-ESM1-2-HR",
    "MRI-ESM2-0",
]

AVAILABLE_VARIABLES: List[str] = [
    "hurs", "huss", "pr", "rlds", "rsds", "sfcWind", "tas", "tasmax", "tasmin"
]

AVAILABLE_SCENARIOS: List[str] = ["historical", "ssp126", "ssp245", "ssp370", "ssp585"]

# ----------------------------
# Helpers
# ----------------------------
def _dataset_url_atlantis(cached: bool) -> str:
    base = "http://atlantis.sci.utah.edu/mod_visus?dataset=nex-gddp-cmip6"
    return base + "&cached=arco" if cached else base
def _dataset_url_fth(cached: bool) -> str:
    base = "https://us-east-2.future-tech-holdings.com:9000/nasa-t0/nex-gddp-cmip6/nex-gddp-cmip6.idx"
    return base 
def calculate_day_of_year(date_str: str) -> int:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return (dt - datetime(dt.year, 1, 1)).days

def get_timestep(date_str: str) -> int:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    day_of_year = calculate_day_of_year(date_str)
    is_leap = (dt.year % 4 == 0 and dt.year % 100 != 0) or (dt.year % 400 == 0)
    total_days = 366 if is_leap else 365
    return dt.year * total_days + day_of_year


class NexGDDPList(DataSource):
    name = "nex_gddp_list"
    version = "1.0"

    def __init__(self, kind: str, **kwargs):
        assert kind in {"models", "variables", "scenarios","timeranges"}
        self.kind = kind
        md = kwargs.pop("metadata", {"kind": kind})
        super().__init__(metadata=md, **kwargs)

    def _load(self) -> pd.DataFrame:
        if self.kind == "models":
            return pd.DataFrame({"model": AVAILABLE_MODELS})
        if self.kind == "variables":
            return pd.DataFrame({"variable": AVAILABLE_VARIABLES})
        if self.kind == "timeranges":
            rows = [{"scenario": s, "start_date": a, "end_date": b}
                    for s, (a, b) in SCENARIO_DATES.items()]
            return pd.DataFrame(rows)
        return pd.DataFrame({"scenario": AVAILABLE_SCENARIOS})

    def read(self) -> pd.DataFrame:
        return self._load()

class NexGDDPTimeline(DataSource):
    name = "nex_gddp_timeranges"
    version = "1.0"

    def __init__(self, **kwargs):
        md = kwargs.pop("metadata", {"source": "scenario_time_ranges"})
        super().__init__(metadata=md, **kwargs)

    def _load(self) -> pd.DataFrame:
        rows = [{"scenario": s, "start_date": a, "end_date": b}
                for s, (a, b) in SCENARIO_DATES.items()]
        return pd.DataFrame(rows)

    def read(self) -> pd.DataFrame:
        return self._load()


class NexGDDPCatalog(DataSource):
    name = "nex_gddp_cmip6"
    version = "1.0"

    def __init__(
        self,
        model: str,
        variable: str,
        scenario: str,
        timestamp: str,
        quality = 0,
        cached = False,
        backup = False,
        lat_range = None,
        lon_range = None,
        **kwargs,
    ):
        self.model = model
        self.variable = variable
        self.scenario = scenario
        self.timestamp = timestamp
        self.quality = quality
        self.lat_range = lat_range
        self.lon_range = lon_range
        self.cached = cached
        self.backup = backup


        md = kwargs.pop("metadata", {
            "source": "NEX-GDDP-CMIP6",
            "spatial_resolution": "0.25°",
            "temporal_resolution": "daily"
        })
        super().__init__(metadata=md, **kwargs)

    def _get_schema(self) -> Schema:
        return Schema(
            datashape=None, dtype=None, shape=None, npartitions=1,
            extra_metadata={
                "models": AVAILABLE_MODELS,
                "variables": AVAILABLE_VARIABLES,
                "scenarios": AVAILABLE_SCENARIOS,
                "time_ranges": SCENARIO_DATES,
            }
        )
    def list_models(self):
        """Return all available models"""
        return list(AVAILABLE_MODELS)

    def list_variables(self):
        """Return variables for a given model, or all if None"""
  
        return list(AVAILABLE_MODELS)
    def list_scenarios(self):
        """Return scenarios """
  
        return list(AVAILABLE_SCENARIOS)

    def list_timeranges(self):
        """Return timestamps for all scenarios"""
        return SCENARIO_DATES
    
    def _validate_inputs(self):
        if self.model not in AVAILABLE_MODELS:
            raise ValueError(f"Invalid model {self.model}")
        if self.variable not in AVAILABLE_VARIABLES:
            raise ValueError(f"Invalid variable {self.variable}")
        if self.scenario not in AVAILABLE_SCENARIOS:
            raise ValueError(f"Invalid scenario {self.scenario}")
        t0, t1 = SCENARIO_DATES[self.scenario]
        if not (t0 <= self.timestamp <= t1):
            raise ValueError(f"Date {self.timestamp} outside {t0}..{t1}")

    def _load(self) -> xr.DataArray:
        self._validate_inputs()
        try:
            url = _dataset_url_fth(self.cached)
        except:
            print("Using Utah Atlantis URL as FTH is not available. Continue...")        
            url = _dataset_url_atlantis(self.cached)

        if self.model=="CESM2":
            field = f"{self.variable}_day_{self.model}_{self.scenario}_r4i1p1f1_gn"
        else:
            field = f"{self.variable}_day_{self.model}_{self.scenario}_r1i1p1f1_gn"
        tidx = int(get_timestep(self.timestamp))

        db = ov.LoadDataset(url)
        full_nx, full_ny = db.getLogicBox()[1]  # full resolution shape
        lat_start, lat_end = -59.88, 90.0
        lon_start, lon_end = 0.125, 360.0
        lat_full = np.linspace(lat_start, lat_end, full_ny, endpoint=False)
        lon_full = np.linspace(lon_start, lon_end, full_nx, endpoint=False)

        y1, y2 = 0, full_ny
        x1, x2 = 0, full_nx
        if self.lat_range:
            lat_min, lat_max = self.lat_range
            y1 = int(np.searchsorted(lat_full, lat_min, side="left"))
            y2 = int(np.searchsorted(lat_full, lat_max, side="right"))

        if self.lon_range:
            lon_min, lon_max = self.lon_range
            x1 = int(np.searchsorted(lon_full, lon_min, side="left"))
            x2 = int(np.searchsorted(lon_full, lon_max, side="right"))

        logic_box = [[x1, y1], [x2, y2]]
        data = db.read(time=tidx, field=field, quality=self.quality, logic_box=logic_box)

        returned_ny, returned_nx = data.shape

        lat_pix = lat_full[1] - lat_full[0]
        lon_pix = lon_full[1] - lon_full[0]

        span_y = max(1, y2 - y1)   # rows requested
        span_x = max(1, x2 - x1)   # cols requested

        # how many full-res pixels per returned pixel (handles quality<0 decimation)
        stride_y = span_y / float(returned_ny)
        stride_x = span_x / float(returned_nx)

        # build coordinates using scaled steps
        lat0 = lat_full[y1]
        lon0 = lon_full[x1]

        lat = lat0 + (np.arange(returned_ny) * stride_y * lat_pix)
        lon = lon0 + (np.arange(returned_nx) * stride_x * lon_pix)

        return xr.DataArray(data, coords=[("lat", lat), ("lon", lon)])

    def read(self) -> xr.DataArray:
        return self._load()
