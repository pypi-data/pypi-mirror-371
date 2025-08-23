import pickle

import numpy as np
import pytest

import healpix_geo


class TestRangeMOCIndex:
    @pytest.mark.parametrize("level", [0, 3, 6])
    def test_full_domain(self, level):
        index = healpix_geo.nested.RangeMOCIndex.full_domain(level)

        expected = np.arange(12 * 4**level, dtype="uint64")

        assert index.nbytes == 16
        assert index.size == expected.size
        assert index.depth == level

    @pytest.mark.parametrize(
        ["level", "cell_ids"],
        (
            (0, np.array([1, 2, 5], dtype="uint64")),
            (3, np.array([12, 16, 17, 19, 22, 23, 71, 72, 73, 79], dtype="uint64")),
            (6, np.arange(3 * 4**6, 5 * 4**6, dtype="uint64")),
        ),
    )
    def test_from_cell_ids(self, level, cell_ids):
        index = healpix_geo.nested.RangeMOCIndex.from_cell_ids(level, cell_ids)

        assert index.size == cell_ids.size
        assert index.depth == level

    @pytest.mark.parametrize(
        ["level", "cell_ids1", "cell_ids2", "expected"],
        (
            (
                4,
                np.arange(0, 6 * 4**4, dtype="uint64"),
                np.arange(6 * 4**4, 12 * 4**4, dtype="uint64"),
                np.arange(12 * 4**4, dtype="uint64"),
            ),
            (
                1,
                np.array([1, 2, 3, 4, 21, 22], dtype="uint64"),
                np.array([23, 25, 26, 32, 33, 34, 35], dtype="uint64"),
                np.array(
                    [1, 2, 3, 4, 21, 22, 23, 25, 26, 32, 33, 34, 35], dtype="uint64"
                ),
            ),
        ),
    )
    def test_union(self, level, cell_ids1, cell_ids2, expected):
        index1 = healpix_geo.nested.RangeMOCIndex.from_cell_ids(level, cell_ids1)
        index2 = healpix_geo.nested.RangeMOCIndex.from_cell_ids(level, cell_ids2)

        actual = index1.union(index2)

        isinstance(actual, healpix_geo.nested.RangeMOCIndex)
        np.testing.assert_equal(actual.cell_ids(), expected)

    @pytest.mark.parametrize(
        ["level", "cell_ids1", "cell_ids2", "expected"],
        (
            (
                4,
                np.arange(2 * 4**4, 4 * 4**4, dtype="uint64"),
                np.arange(3 * 4**4, 5 * 4**4, dtype="uint64"),
                np.arange(3 * 4**4, 4 * 4**4, dtype="uint64"),
            ),
            (
                1,
                np.array([1, 2, 3, 4, 21, 22, 23, 24, 25], dtype="uint64"),
                np.array([21, 22, 23, 25, 26, 32, 33, 34, 35], dtype="uint64"),
                np.array([21, 22, 23, 25], dtype="uint64"),
            ),
        ),
    )
    def test_intersection(self, level, cell_ids1, cell_ids2, expected):
        index1 = healpix_geo.nested.RangeMOCIndex.from_cell_ids(level, cell_ids1)
        index2 = healpix_geo.nested.RangeMOCIndex.from_cell_ids(level, cell_ids2)

        actual = index1.intersection(index2)

        assert isinstance(actual, healpix_geo.nested.RangeMOCIndex)
        np.testing.assert_equal(actual.cell_ids(), expected)

    @pytest.mark.parametrize(
        ["level", "cell_ids"],
        (
            pytest.param(0, np.arange(12, dtype="uint64"), id="base cells"),
            pytest.param(
                1,
                np.array([0, 1, 2, 4, 5, 11, 12, 13, 25, 26, 27], dtype="uint64"),
                id="list of level 1 cells",
            ),
            pytest.param(
                4,
                np.arange(1 * 4**4, 2 * 4**4, dtype="uint64"),
                id="single level 4 base cell",
            ),
        ),
    )
    @pytest.mark.parametrize(
        "indexer",
        [
            slice(None),
            slice(None, 4),
            slice(2, None),
            slice(3, 7),
            np.arange(5, dtype="uint64"),
            np.array([1, 2, 4, 6, 8], dtype="uint64"),
        ],
    )
    def test_isel(self, level, cell_ids, indexer):
        expected = cell_ids[indexer]

        index = healpix_geo.nested.RangeMOCIndex.from_cell_ids(level, cell_ids)

        actual = index.isel(indexer)

        np.testing.assert_equal(actual.cell_ids(), expected)

    @pytest.mark.parametrize(
        ["level", "cell_ids", "indexer"],
        (
            pytest.param(
                0,
                np.arange(12, dtype="uint64"),
                slice(None),
                id="base cells-slice-full",
            ),
            pytest.param(
                0,
                np.arange(12, dtype="uint64"),
                slice(None, 6),
                id="base cells-slice-left_open",
            ),
            pytest.param(
                0,
                np.arange(12, dtype="uint64"),
                slice(2, None),
                id="base cells-slice-right_open",
            ),
            pytest.param(
                0,
                np.arange(12, dtype="uint64"),
                slice(2, 7),
                id="base cells-slice-domain",
            ),
            pytest.param(
                0,
                np.arange(12, dtype="uint64"),
                np.arange(12, dtype="uint64"),
                id="base cells-array-full",
            ),
            pytest.param(
                0,
                np.arange(12, dtype="uint64"),
                np.arange(2, 7, dtype="uint64"),
                id="base cells-array-domain",
            ),
            pytest.param(
                0,
                np.arange(12, dtype="uint64"),
                np.array([1, 2, 3, 7, 8, 9, 10], dtype="uint64"),
                id="base cells-array-disconnected",
            ),
            pytest.param(
                3,
                np.arange(12 * 4**3, dtype="uint64"),
                slice(None, 15),
                id="level 3 cells-slice-left_open",
            ),
            pytest.param(
                1,
                np.array([0, 1, 2, 4, 5, 11, 12, 13, 25, 26, 27], dtype="uint64"),
                np.array([2, 5, 11, 12, 25, 27], dtype="uint64"),
                id="list of level 1 cells-array-disconnected",
            ),
            pytest.param(
                4,
                np.arange(1 * 4**4, 2 * 4**4, dtype="uint64"),
                slice(260, 280),
                id="single level 4 base cell-slice-domain",
            ),
        ),
    )
    def test_sel(self, level, cell_ids, indexer):
        if isinstance(indexer, slice):
            n = slice(
                indexer.start if indexer.start is not None else 0,
                (
                    indexer.stop + 1
                    if indexer.stop is not None
                    else int(np.max(cell_ids)) + 1
                ),
                indexer.step if indexer.step is not None else 1,
            )
            range_ = np.arange(n.start, n.stop, n.step, dtype="uint64")
            condition = np.isin(cell_ids, range_)
        else:
            condition = np.isin(cell_ids, indexer)
        expected_cell_ids = cell_ids[condition]

        index = healpix_geo.nested.RangeMOCIndex.from_cell_ids(level, cell_ids)

        actual_indexer, actual_moc = index.sel(indexer)

        np.testing.assert_equal(cell_ids[actual_indexer], expected_cell_ids)
        np.testing.assert_equal(actual_moc.cell_ids(), expected_cell_ids)

    @pytest.mark.parametrize(
        ["depth", "cell_ids"],
        (
            (2, np.arange(1 * 4**2, 3 * 4**2, dtype="uint64")),
            (5, np.arange(12 * 4**5, dtype="uint64")),
        ),
    )
    def test_pickle_roundtrip(self, depth, cell_ids):
        index = healpix_geo.nested.RangeMOCIndex.from_cell_ids(depth, cell_ids)

        pickled = pickle.dumps(index)
        assert isinstance(pickled, bytes)
        unpickled = pickle.loads(pickled)

        assert isinstance(unpickled, healpix_geo.nested.RangeMOCIndex)
        assert index.depth == unpickled.depth
        np.testing.assert_equal(unpickled.cell_ids(), index.cell_ids())
