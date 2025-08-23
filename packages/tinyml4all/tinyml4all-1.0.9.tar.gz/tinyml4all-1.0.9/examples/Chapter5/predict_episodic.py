from tinyml4all.time.episodic.classification import TimeSeries, Chain
from tinyml4all.time.episodic.features import Window
from tinyml4all.time.features import (
    Scale,
    Moments,
    Autocorrelation,
    Peaks,
    CountAboveMean,
    Select,
)
from tinyml4all.time.models.classification import RandomForest

ts = TimeSeries.read_csv_folder("sample_data/media-control")

ts.set_duration("next", "1s")
ts.set_duration("raise", "1s")
ts.set_duration("tap", "1s")

chain = Chain(
    pre=[Scale("minmax")],
    window=Window(
        chunk="250ms",
        features=[Moments(), Autocorrelation(), Peaks(), CountAboveMean()],
    ),
    ovr=[Select(rfe=8), RandomForest(n_estimators=5, max_depth=7)],
)
tables = chain(ts)

# one vs rest classification produces N binary tables
# with classes "<class of interest>" and
# "not <class of interest>"
for table in tables:
    print(table.classification_report())