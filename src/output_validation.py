"""저장된 분석 산출물을 다시 열어 내용과 파일 상태를 검증하는 공통 함수."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import Mapping, Sequence

import pandas as pd


def _csv_roundtrip(frame: pd.DataFrame, *, index: bool) -> pd.DataFrame:
    """메모리 표를 실제 CSV 저장·재로딩과 같은 형태로 정규화합니다."""
    buffer = StringIO()
    frame.to_csv(buffer, index=index)
    buffer.seek(0)
    return pd.read_csv(buffer, index_col=0 if index else None)


def validate_saved_csv_tables(
    expected_tables: Mapping[
        str,
        tuple[pd.DataFrame, str | Path]
        | tuple[pd.DataFrame, str | Path, bool],
    ],
) -> pd.DataFrame:
    """CSV를 재로딩해 shape·columns·전체 셀 내용이 예상 표와 같은지 확인합니다."""
    rows: list[dict[str, object]] = []
    for label, spec in expected_tables.items():
        expected, path, *index_spec = spec
        include_index = bool(index_spec[0]) if index_spec else False
        output_path = Path(path)

        exists = output_path.is_file()
        shape_match = False
        columns_match = False
        content_match = False
        value = "missing"
        if exists:
            actual = pd.read_csv(
                output_path,
                index_col=0 if include_index else None,
            )
            expected_reloaded = _csv_roundtrip(expected, index=include_index)
            shape_match = actual.shape == expected_reloaded.shape
            columns_match = list(actual.columns) == list(expected_reloaded.columns)
            if shape_match and columns_match:
                try:
                    pd.testing.assert_frame_equal(
                        actual.reset_index(drop=True),
                        expected_reloaded.reset_index(drop=True),
                        check_dtype=False,
                        check_exact=False,
                        rtol=1e-9,
                        atol=1e-9,
                    )
                    content_match = True
                except AssertionError:
                    content_match = False
            value = f"shape={actual.shape}"

        passed = exists and shape_match and columns_match and content_match
        rows.append(
            {
                "artifact": label,
                "value": value,
                "exists": exists,
                "shape_match": shape_match,
                "columns_match": columns_match,
                "content_match": content_match,
                "status": "PASS" if passed else "FAIL",
            }
        )
    return pd.DataFrame(rows)


def validate_saved_files(
    paths: Sequence[str | Path],
    *,
    minimum_bytes: int = 1,
) -> pd.DataFrame:
    """그래프·보고서처럼 표가 아닌 산출물이 실제로 저장됐는지 확인합니다."""
    rows: list[dict[str, object]] = []
    for raw_path in paths:
        path = Path(raw_path)
        size = path.stat().st_size if path.is_file() else 0
        rows.append(
            {
                "artifact": path.name,
                "value": f"bytes={size}",
                "exists": path.is_file(),
                "status": "PASS"
                if path.is_file() and size >= minimum_bytes
                else "FAIL",
            }
        )
    return pd.DataFrame(rows)
