import os
import sqlite3
from typing import Any, Dict, List, Tuple, Optional


class DbOperations:
    def __init__(self, db_file: Optional[str] = None) -> None:
        # Resolve DB path
        self.db_file = db_file or os.environ.get("OPUSAPI_DB")
        if not self.db_file:
            raise ValueError("OPUSAPI_DB environment variable or db_file must be set")

        # Single, reusable connection
        # check_same_thread=False allows usage from different threads if your app does that
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        # Performance/safety PRAGMAs – run once per connection
        self._configure_connection()

    def _configure_connection(self) -> None:
        # WAL improves concurrency and often speed
        self.conn.execute("PRAGMA journal_mode = WAL;")
        # Good balance of durability and performance
        self.conn.execute("PRAGMA synchronous = NORMAL;")
        # Keep temp structures in memory
        self.conn.execute("PRAGMA temp_store = MEMORY;")
        # Enforce FK constraints
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def close(self) -> None:
        if getattr(self, "conn", None) is not None:
            self.conn.close()
            self.conn = None

    def __enter__(self) -> "DbOperations":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        # Best-effort cleanup
        try:
            self.close()
        except Exception:
            pass

    # -------------------------
    # Utility helpers
    # -------------------------

    def clean_up_parameters(self, parameters: Dict[str, str]) -> Dict[str, str]:
        """
        Keep only allowed keys, strip quote characters from values.
        """
        remove: List[str] = []
        valid_keys = [
            "corpus",
            "id",
            "latest",
            "preprocessing",
            "source",
            "target",
            "version",
            "corpora",
            "languages",
        ]
        for key, value in parameters.items():
            if key not in valid_keys:
                remove.append(key)
                continue
            # These replacements are mostly unnecessary with parameterized queries,
            # but kept for backward-compatibility.
            value = value.replace('"', "")
            value = value.replace("'", "")
            parameters[key] = value
        for key in remove:
            del parameters[key]
        return parameters

    def _build_where(
        self, parameters: Dict[str, Any]
    ) -> Tuple[str, List[Any]]:
        """
        Build a WHERE clause and parameter list from a dict like {"source": "en", "target": "de"}.
        Returns (clause_string, values_list), e.g. ("source = ? AND target = ?", ["en", "de"])
        """
        clauses: List[str] = []
        values: List[Any] = []
        for k, v in parameters.items():
            clauses.append(f"{k} = ?")
            values.append(v)
        return " AND ".join(clauses), values

    def run_query(
        self, sql_command: str, params: Optional[List[Any]] = None
    ) -> Tuple[List[str], List[sqlite3.Row]]:
        """
        Execute a query and return (column_names, list_of_rows).
        """
        cur = self.conn.execute(sql_command, params or [])
        rows = cur.fetchall()
        keys = [d[0] for d in cur.description]
        return keys, rows

    # -------------------------
    # Public query helpers
    # -------------------------

    def sort_source_target(self, parameters: Dict[str, str]) -> Dict[str, str]:
        source = parameters.get("source")
        target = parameters.get("target")
        if source and target:
            sou_tar = sorted([source, target])
            parameters["source"] = sou_tar[0]
            parameters["target"] = sou_tar[1]
        return parameters

    def convert_latest(self, parameters: Dict[str, str]) -> Dict[str, str]:
        version = parameters.get("version")
        if version and version == "latest":
            parameters["latest"] = "True"
            del parameters["version"]
        return parameters

    def run_default_query(
        self, parameters: Dict[str, str], suffix: str = ""
    ) -> List[Dict[str, Any]]:
        columns = [
            "alignment_pairs",
            "corpus",
            "documents",
            "id",
            "latest",
            "preprocessing",
            "size",
            "source",
            "source_tokens",
            "target",
            "target_tokens",
            "url",
            "version",
        ]

        # We mutate parameters in this method, so work on a local copy
        parameters = dict(parameters)
        parameters = self.sort_source_target(parameters)

        where_clause, values = self._build_where(parameters)

        sql_command = f"SELECT {', '.join(columns)} FROM opusfile"
        if where_clause:
            sql_command += " WHERE " + where_clause
        if suffix:
            # suffix usually like " AND target != ''" or " AND source != ''"
            sql_command += suffix

        keys, rows = self.run_query(sql_command, values)
        ret = [{k: row[idx] for idx, k in enumerate(keys)} for row in rows]

        # Monolingual fetches when target is present but preprocessing not specified
        if "preprocessing" not in parameters.keys() and parameters.get("target"):
            # 1) Mono source: target = ''
            param_mono_src = dict(parameters)
            param_mono_src["target"] = ""
            where_clause, values = self._build_where(param_mono_src)
            sql_command = (
                f"SELECT {', '.join(columns)} FROM opusfile WHERE {where_clause}"
            ) + suffix
            keys, rows = self.run_query(sql_command, values)
            ret.extend({k: row[idx] for idx, k in enumerate(keys)} for row in rows)

            # 2) Mono target: swap source/target, then set target = ''
            param_mono_trg = dict(parameters)
            param_mono_trg["source"] = parameters["target"]
            param_mono_trg["target"] = ""
            where_clause, values = self._build_where(param_mono_trg)
            sql_command = (
                f"SELECT {', '.join(columns)} FROM opusfile WHERE {where_clause}"
            ) + suffix
            keys, rows = self.run_query(sql_command, values)
            ret.extend({k: row[idx] for idx, k in enumerate(keys)} for row in rows)

        return ret

    def run_corpora_query(self, parameters: Dict[str, str]) -> List[str]:
        # Work on a copy to avoid side effects
        parameters = dict(parameters)
        parameters = self.convert_latest(parameters)
        parameters = self.sort_source_target(parameters)
        parameters.pop("corpora", None)

        sql_command = "SELECT DISTINCT corpus FROM opusfile"
        where_clause, values = self._build_where(parameters)

        if where_clause:
            sql_command += " WHERE " + where_clause

        _, rows = self.run_query(sql_command, values)
        return [row[0] for row in rows]

    def run_languages_query(self, parameters: Dict[str, str]) -> List[str]:
        # Work on a copy to avoid mutating caller's dict
        parameters = dict(parameters)
        parameters = self.convert_latest(parameters)
        parameters = self.sort_source_target(parameters)
        parameters.pop("languages", None)

        # If there are no filters, just list sources
        if not parameters:
            sql_command = "SELECT DISTINCT source FROM opusfile"
            _, rows = self.run_query(sql_command)
            return [row[0] for row in rows]

        base_params = dict(parameters)
        source = base_params.get("source")

        # Case 1: source specified -> UNION of target and source
        if source:
            # First part: DISTINCT target with filters + target != source/''

            where1_clause_parts: List[str] = []
            where1_values: List[Any] = []
            for k, v in base_params.items():
                where1_clause_parts.append(f"{k} = ?")
                where1_values.append(v)
            where1_clause = " AND ".join(where1_clause_parts)

            sql1 = (
                "SELECT DISTINCT target FROM opusfile WHERE "
                + where1_clause
                + " AND target != ? AND target != ''"
            )
            where1_values.extend([source])

            # Second part: DISTINCT source with source/target swapped
            swapped = dict(base_params)
            swapped["target"] = swapped["source"]
            del swapped["source"]
            where2_clause, where2_values = self._build_where(swapped)

            sql2 = "SELECT DISTINCT source FROM opusfile"
            if where2_clause:
                sql2 += " WHERE " + where2_clause

            # Combine UNION query and parameters
            sql_command = sql1 + " UNION " + sql2
            params_list = where1_values + where2_values

            _, rows = self.run_query(sql_command, params_list)
            return [row[0] for row in rows]

        # Case 2: no 'source' filter → basic DISTINCT source with other filters
        where_clause, values = self._build_where(base_params)
        sql_command = "SELECT DISTINCT source FROM opusfile"
        if where_clause:
            sql_command += " WHERE " + where_clause

        _, rows = self.run_query(sql_command, values)
        return [row[0] for row in rows]

    def get_corpora(self, parameters: Dict[str, str]) -> List[Dict[str, Any]]:
        # Work on a copy
        parameters = dict(parameters)
        parameters = self.convert_latest(parameters)

        a_parameters = dict(parameters)
        preprocessing = parameters.get("preprocessing")
        suffix = ""

        if preprocessing in ["xml", "raw", "parsed"]:
            # Get xml alignment files
            a_parameters["preprocessing"] = "xml"
            # Don't get the sentence file
            suffix = ' AND target != ""'

        ret = self.run_default_query(a_parameters, suffix=suffix)

        source = parameters.get("source")
        target = parameters.get("target")

        if source and not target:
            # Get items where the queried language is on the target side
            a_parameters = dict(parameters)
            a_parameters["target"] = parameters["source"]
            a_parameters.pop("source", None)
            ret = (
                self.run_default_query(a_parameters, suffix=" AND source != ''")
                + ret
            )

        if preprocessing in ["xml", "raw", "parsed"]:
            # Get sentence files
            languages = set()
            for item in ret:
                languages.add(item.get("source", ""))
                languages.add(item.get("target", ""))

            parameters["target"] = ""
            for language in sorted(languages):
                if not language:
                    continue
                parameters["source"] = language
                ret.extend(self.run_default_query(parameters))

        return ret

    # -------------------------
    # Optional: index helper
    # -------------------------

    def ensure_indexes(self) -> None:
        """
        Create indexes that match the query patterns used in this class.
        Call this once (e.g. from a migration or admin script).
        """
        self.conn.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_opusfile_src_trg_pre_latest
                ON opusfile(source, target, preprocessing, latest);

            CREATE INDEX IF NOT EXISTS idx_opusfile_corpus_latest_pre
                ON opusfile(corpus, latest, preprocessing);

            CREATE INDEX IF NOT EXISTS idx_opusfile_source_pre_latest
                ON opusfile(source, preprocessing, latest);

            CREATE INDEX IF NOT EXISTS idx_opusfile_target_pre_latest
                ON opusfile(target, preprocessing, latest);
            """
        )
        # Update statistics so the query planner can use the new indexes optimally
        self.conn.execute("ANALYZE;")
        self.conn.commit()
