# OakVar
#
# Copyright (c) 2024 Oak Bioinformatics, LLC
#
# All rights reserved.
#
# Do not distribute or use this software without obtaining
# a license from Oak Bioinformatics, LLC.
#
# Do not use this software to develop another software
# which competes with the products by Oak Bioinformatics, LLC,
# without obtaining a license for such use from Oak Bioinformatics, LLC.
#
# For personal use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For research use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For use by commercial entities, you must obtain a commercial license
# from Oak Bioinformatics, LLC. Please write to info@oakbioinformatics.com
# to obtain the commercial license.
# ================
# OpenCRAVAT
#
# MIT License
#
# Copyright (c) 2021 KarchinLab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Any
from typing import List
from typing import Tuple
from typing import Dict
from typing import Optional
from pathlib import Path
import numpy as np
from polars import schema

ov_system_output_columns: Optional[Dict[str, List[Dict[str, Any]]]] = None


def get_ucsc_bins(start, stop=None):
    """get_ucsc_bins.

    Args:
        start:
        stop:
    """
    if stop is None:
        stop = start + 1

    def range_per_level(start, stop):
        """range_per_level.

        Args:
            start:
            stop:
        """
        BIN_OFFSETS = [512 + 64 + 8 + 1, 64 + 8 + 1, 8 + 1, 1, 0]
        SHIFT_FIRST = 17
        SHIFT_NEXT = 3

        start_bin = start
        stop_bin = max(start, stop - 1)

        start_bin >>= SHIFT_FIRST
        stop_bin >>= SHIFT_FIRST

        for offset in BIN_OFFSETS:
            yield offset + start_bin, offset + stop_bin
            start_bin >>= SHIFT_NEXT
            stop_bin >>= SHIFT_NEXT

    return [
        x
        for first, last in range_per_level(start, stop)
        for x in range(first, last + 1)
    ]


def load_module(path):
    from importlib.util import spec_from_file_location, module_from_spec
    from importlib import import_module
    import sys
    from pathlib import Path
    from ..exceptions import ModuleLoadingError

    p = Path(path)
    path_dir = str(p.parent)
    sys.path = [path_dir] + sys.path
    module = None
    module_name = p.stem
    try:
        module = import_module(module_name)
    except Exception:
        import traceback
        traceback.print_exc()
        try:
            spec = spec_from_file_location(module_name, path)
            if spec is not None:
                module = module_from_spec(spec)
                loader = spec.loader
                if loader is not None:
                    loader.exec_module(module)
        except Exception:
            import traceback
            traceback.print_exc()
            raise ModuleLoadingError(module_name=module_name)
    del sys.path[0]
    return module


def load_class(path, class_name=None):
    """load_class.

    Args:
        path:
        class_name:
    """
    import inspect

    module = load_module(path)
    if not module:
        return None
    module_class = None
    if class_name:
        if hasattr(module, class_name):
            module_class = getattr(module, class_name)
            if not inspect.isclass(module_class):
                module_class = None
    else:
        for n in dir(module):
            if n in [
                "Converter",
                "Mapper",
                "Annotator",
                "PostAggregator",
                "Reporter",
                "CommonModule",
                "CravatConverter",
                "CravatMapper",
                "CravatAnnotator",
                "CravatPostAggregator",
                "CravatReporter",
                "CravatCommonModule",
            ]:
                if hasattr(module, n):
                    module_class = getattr(module, n)
                    if not inspect.isclass(module_class):
                        module_class = None
    return module_class


def get_directory_size(start_path):
    """
    Recursively get directory filesize.
    """
    from os import walk
    from os.path import join, getsize
    from ..store.consts import pack_ignore_fnames

    total_size = 0
    for dirpath, _, filenames in walk(start_path):
        for fname in filenames:
            if fname in pack_ignore_fnames:
                continue
            fp = join(dirpath, fname)
            total_size += getsize(fp)
    return total_size


def get_argument_parser_defaults(parser):
    """get_argument_parser_defaults.

    Args:
        parser:
    """
    defaults = {
        action.dest: action.default
        for action in parser._actions
        if action.dest != "help"
    }
    return defaults


def detect_encoding(path):
    """detect_encoding.

    Args:
        path:
    """
    from chardet.universaldetector import UniversalDetector
    from gzip import open as gzipopen

    if " " not in path:
        path = path.strip('"')
    if path.endswith(".gz"):
        f = gzipopen(path)
    else:
        f = open(path, "rb")
    detector = UniversalDetector()
    count = 0
    encoding = None
    for line in f:
        detector.feed(line)
        count += 1
        if detector.done or count == 10000:
            res = detector.result
            if res:
                encoding = res["encoding"]
            break
    detector.close()
    f.close()
    if not encoding:
        encoding = "utf-8"
    if encoding == "ascii":
        return "utf-8"
    else:
        return encoding


def get_job_version(dbpath, platform_name):
    """get_job_version.

    Args:
        dbpath:
        platform_name:
    """
    from packaging.version import Version
    import sqlite3

    db = sqlite3.connect(dbpath)
    c = db.cursor()
    sql = f'select colval from info where colkey="{platform_name}"'
    c.execute(sql)
    r = c.fetchone()
    db_version = None
    if r is not None:
        db_version = Version(r[0])
    return db_version


def is_compatible_version(dbpath):
    """is_compatible_version.

    Args:
        dbpath:
    """
    from .admin_util import get_max_version_supported_for_migration
    from packaging.version import Version
    from importlib import metadata

    max_version_supported_for_migration = get_max_version_supported_for_migration()
    try:
        ov_version = Version(metadata.version("oakvar"))
    except Exception:
        ov_version = None
    try:
        oc_version = Version(metadata.version("open-cravat"))
    except Exception:
        oc_version = None
    job_version_ov = get_job_version(dbpath, "oakvar")
    job_version_oc = get_job_version(dbpath, "open-cravat")
    if job_version_ov is None:
        if job_version_oc is None:
            compatible = False
        else:
            if job_version_oc < max_version_supported_for_migration:
                compatible = False
            else:
                compatible = True
        return compatible, job_version_oc, oc_version
    else:
        if job_version_ov < max_version_supported_for_migration:
            compatible = False
        else:
            compatible = True
        return compatible, job_version_ov, ov_version


def is_url(s: str) -> bool:
    """is_url.

    Args:
        s (str): s

    Returns:
        bool:
    """
    if s.startswith("http://") or s.startswith("https://"):
        return True
    else:
        return False


def get_current_time_str():
    """get_current_time_str."""
    from datetime import datetime

    t = datetime.now()
    return t.strftime("%Y:%m:%d %H:%M:%S")


def get_args_conf(args: dict) -> Dict:
    """get_args_conf.

    Args:
        args (dict): args

    Returns:
        Dict:
    """
    if not args:
        return {}
    # fill with run_conf dict
    run_conf = args.get("run_conf")
    if run_conf and type(run_conf) is dict:
        for k, v in run_conf.items():
            if k not in args or not args[k]:
                args[k] = v
    # fill with conf
    conf_path = args.get("confpath")
    if conf_path:
        conf = load_yml_conf(conf_path).get("run", {})
        args["conf"] = conf
        if conf:
            for k, v in conf.items():
                if k not in args or not args[k]:
                    args[k] = v
    return args


def get_args_package(args: dict) -> Dict:
    """get_args_package.

    Args:
        args (dict): args

    Returns:
        Dict:
    """
    if not args:
        return {}
    package = args.get("package")
    if package:
        from ..module.local import get_local_module_info

        m_info = get_local_module_info(package)
        if m_info:
            package_conf = m_info.conf
            package_conf_run = package_conf.get("run")
            if package_conf_run:
                for k, v in package_conf_run.items():
                    if k not in args or not args[k]:
                        args[k] = v
    return args


def get_args(parser, inargs, inkwargs) -> dict:
    """get_args.

    Args:
        parser:
        inargs:
        inkwargs:

    Returns:
        dict:
    """
    from types import SimpleNamespace
    from argparse import Namespace

    # given args. Combines arguments in various formats.
    inarg_dict = {}
    if inargs is not None:
        for inarg in inargs:
            if isinstance(inarg, list):  # ['-t', 'text']
                inarg_dict.update(**vars(parser.parse_args(inarg)))
            elif isinstance(inarg, Namespace):  # already parsed by a parser.
                inarg_dict.update(**vars(inarg))
            elif isinstance(inarg, SimpleNamespace):
                inarg_dict.update(**vars(inarg))
            elif isinstance(inarg, dict):  # {'output_dir': '/rt'}
                inarg_dict.update(inarg)
    if inkwargs is not None:
        inarg_dict.update(inkwargs)
    # conf
    inarg_dict = get_args_conf(inarg_dict)
    # package
    inarg_dict = get_args_package(inarg_dict)
    # defaults
    default_args = get_argument_parser_defaults(parser)
    for k, v in default_args.items():
        if k not in inarg_dict or inarg_dict[k] is None:
            inarg_dict[k] = v
    # convert value to list if needed.
    for action in parser._actions:
        if action.dest == "help":
            continue
        if action.nargs in ["+", "*"]:
            key = action.dest
            value = inarg_dict[key]
            if value and not isinstance(value, list) and not isinstance(value, dict):
                inarg_dict[key] = [value]
    return inarg_dict


def filter_affected_cols(filter):
    """filter_affected_cols.

    Args:
        filter:
    """
    cols = set()
    if "column" in filter:
        cols.add(filter["column"])
    else:
        for rule in filter["rules"]:
            cols.update(filter_affected_cols(rule))
    return cols


def humanize_bytes(num, binary=False):
    """Human friendly file size"""
    from math import floor, log

    exp2unit_dec = {0: "B", 1: "kB", 2: "MB", 3: "GB"}
    exp2unit_bin = {0: "B", 1: "KiB", 2: "MiB", 3: "GiB"}
    max_exponent = 3
    if binary:
        base = 1024
    else:
        base = 1000
    if num > 0:
        exponent = floor(log(num, base))
        if exponent > max_exponent:
            exponent = max_exponent
    else:
        exponent = 0
    quotient = float(num) / base**exponent
    if binary:
        unit = exp2unit_bin[exponent]
    else:
        unit = exp2unit_dec[exponent]
    quot_str = "{:.1f}".format(quotient)
    # No decimal for byte level sizes
    if exponent == 0:
        quot_str = quot_str.rstrip("0").rstrip(".")
    return "{quotient} {unit}".format(quotient=quot_str, unit=unit)


def email_is_valid(email: Optional[str]) -> bool:
    """email_is_valid.

    Args:
        email (Optional[str]): email

    Returns:
        bool:
    """
    from re import fullmatch

    if not email:
        return False
    if fullmatch(
        r"([A-Za-z0-9]+[.\-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+", email
    ):
        return True
    else:
        return False


def pw_is_valid(pw: Optional[str]) -> bool:
    """pw_is_valid.

    Args:
        pw (Optional[str]): pw

    Returns:
        bool:
    """
    from re import fullmatch

    if not pw:
        return False
    if fullmatch(r"[a-zA-Z0-9!?$@*&\-\+]+", pw):
        return True
    else:
        return False


def load_yml_conf(yml_conf_path: Path) -> Dict[str, Any]:
    """load_yml_conf.

    Args:
        yml_conf_path (Path): yml_conf_path
    """
    from oyaml import safe_load

    if not Path(yml_conf_path).exists():
        return {}
    with open(yml_conf_path, encoding="utf-8") as f:
        conf = safe_load(f)
        return conf


def compare_version(v1: str, v2: str) -> int:
    """compare_version.

    Args:
        v1:
        v2:
    """
    from packaging.version import Version

    sv1 = Version(v1)
    sv2 = Version(v2)
    if sv1 == sv2:
        return 0
    elif sv1 > sv2:
        return 1
    else:
        return -1


def version_requirement_met(version, target_version) -> bool:
    """version_requirement_met.

    Args:
        version:
        target_version:

    Returns:
        bool:
    """
    from packaging.version import Version

    if not target_version:
        return True
    return Version(version) >= Version(target_version)


def get_latest_version(versions, target_version=None):
    """get_latest_version.

    Args:
        versions:
        target_version:
    """
    from packaging.version import Version

    latest_version = ""
    for version in versions:
        if not version_requirement_met(version, target_version):
            continue
        if not latest_version or Version(version) > Version(latest_version):
            latest_version = version
    return latest_version


def escape_glob_pattern(pattern):
    """escape_glob_pattern.

    Args:
        pattern:
    """
    new_pattern = "[[]".join(["[]]".join(v.split("]")) for v in pattern.split("[")])
    return new_pattern.replace("*", "[*]").replace("?", "[?]")


def get_random_string(k=16):
    """get_random_string.

    Args:
        k:
    """
    from random import choices
    from string import ascii_lowercase

    return "".join(choices(ascii_lowercase, k=k))


def get_result_dbpath(output_dir: str, run_name: str):
    """get_result_dbpath.

    Args:
        output_dir (str): output_dir
        run_name (str): run_name
    """
    from pathlib import Path
    from ..consts import result_db_suffix

    return str(Path(output_dir) / (run_name + result_db_suffix))


def get_unique_path(path: str):
    """get_unique_path.

    Args:
        path (str): path
    """
    from pathlib import Path

    count = 1
    p = Path(path)
    stem = p.stem
    suffix = p.suffix
    while p.exists():
        p = Path(f"{stem}_{count}{suffix}")
    return str(p)


def print_list_of_dict(ld: List[Dict], outer=None):
    """print_list_of_dict.

    Args:
        ld (List[Dict]):
        outer:
    """
    from rich.console import Console
    from rich.table import Table
    from rich import box

    if not ld:
        return
    table = Table(show_header=True, title_style="bold", box=box.SQUARE)
    headers = list(ld[0].keys())
    for header in headers:
        table.add_column(header)
    for d in ld:
        row = []
        for header in headers:
            v = d[header]
            if isinstance(v, list):
                v = ", ".join(v)
            else:
                v = str(v)
            row.append(v)
        table.add_row(*row)
    console = Console(file=outer)
    console.print(table)


def log_module(module, logger):
    """log_module.

    Args:
        module:
        logger:
    """
    if logger:
        code_version = None
        if hasattr(module, "conf"):
            code_version = module.conf.get("code_version") or module.conf.get("version")
        if not code_version and hasattr(module, "version"):
            code_version = module.version
        if not code_version:
            code_version = "?"
        logger.info(f"module: {module.name}=={code_version} {module.script_path}")


def get_ov_system_output_columns() -> Dict[str, List[Dict[str, Any]]]:
    """get_ov_system_output_columns.

    Args:

    Returns:
        Dict[str, List[Dict[str, Any]]]:
    """
    from pathlib import Path
    from oyaml import safe_load

    global ov_system_output_columns
    if ov_system_output_columns:
        return ov_system_output_columns
    fp = Path(__file__).parent.parent / "assets" / "output_columns.yml"
    with open(fp) as f:
        ov_system_output_columns = safe_load(f)
    if not ov_system_output_columns:
        return {}
    return ov_system_output_columns


def get_crv_def() -> List[Dict[str, Any]]:
    """get_crv_def.

    Args:

    Returns:
        List[Dict[str, Any]]:
    """
    from ..consts import INPUT_LEVEL_KEY

    output_columns = get_ov_system_output_columns()
    return output_columns[INPUT_LEVEL_KEY]


def get_crx_def() -> List[Dict[str, Any]]:
    """get_crx_def.

    Args:

    Returns:
        List[Dict[str, Any]]:
    """
    from ..consts import VARIANT_LEVEL_KEY

    output_columns: dict = get_ov_system_output_columns()
    return output_columns[VARIANT_LEVEL_KEY]


def get_crg_def() -> List[Dict[str, Any]]:
    """get_crg_def.

    Args:

    Returns:
        List[Dict[str, Any]]:
    """
    from ..consts import GENE_LEVEL_KEY

    output_columns: dict = get_ov_system_output_columns()
    return output_columns[GENE_LEVEL_KEY]


def get_crs_def() -> List[Dict[str, Any]]:
    """get_crs_def.

    Args:

    Returns:
        List[Dict[str, Any]]:
    """
    from ..consts import SAMPLE_LEVEL_KEY

    output_columns: dict = get_ov_system_output_columns()
    return output_columns[SAMPLE_LEVEL_KEY]


def get_crm_def() -> List[Dict[str, Any]]:
    """get_crm_def.

    Args:

    Returns:
        List[Dict[str, Any]]:
    """
    from ..consts import MAPPING_LEVEL_KEY

    output_columns: dict = get_ov_system_output_columns()
    return output_columns[MAPPING_LEVEL_KEY]


def get_crl_def() -> List[Dict[str, Any]]:
    """get_crl_def.

    Args:

    Returns:
        List[Dict[str, Any]]:
    """
    from ..consts import LIFTOVER_LEVEL_KEY

    output_columns: dict = get_ov_system_output_columns()
    return output_columns[LIFTOVER_LEVEL_KEY]


def get_result_db_conn(db_path: str):
    """get_result_db_conn.

    Args:
        db_path (str): db_path
    """
    import sqlite3
    from pathlib import Path

    p = Path(db_path)
    if not p.exists():
        return None
    conn = sqlite3.connect(p)
    return conn


def get_sample_uid_variant_arrays(
    db_path: str, variant_criteria=None, use_zygosity: bool = True
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Gets a Polars DataFrame of the presence of variants in samples.

    Rows are samples and columns are variants.

    Args:
        db_path (str): Path to the OakVar result database file
                       from which a Polars DataFrame will be extracted.

    Returns:
        Optional[Tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray]]: If no error, three DataFrames will be returned.
            The first array is a 1D array of sample names.
            The second array is a 1D array of variant UIDs.
            The third array is a 2D array of variant presence in samples.
    """

    import sqlite3
    import numpy as np

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("select distinct(base__sample_id) from sample")
    samples = np.array([r[0] for r in cursor.fetchall()], dtype=str)
    samples.sort()
    if variant_criteria is not None:
        cursor.execute(
            f"select distinct(base__uid) from variant where {variant_criteria} order by base__uid"
        )
    else:
        cursor.execute("select distinct(base__uid) from variant order by base__uid")
    uids = [r[0] for r in cursor.fetchall()]
    num_samples = len(samples)
    num_uids = len(uids)
    arr = np.zeros([num_samples, num_uids])
    for sample_no in range(num_samples):
        if use_zygosity:
            if variant_criteria is not None:
                cursor.execute(
                    "select s.base__uid, s.base__zygosity from (select base__uid, base__zygosity from sample where base__sample_id=?) as s, (select base__uid from variant where "
                    + variant_criteria
                    + ") as v on s.base__uid = v.base__uid order by s.base__uid",
                    (samples[sample_no],),
                )
            else:
                cursor.execute(
                    "select base__uid, base__zygosity from sample where base__sample_id=? order by base__uid",
                    (samples[sample_no],),
                )
        else:
            if variant_criteria is not None:
                cursor.execute(
                    "select s.base__uid from (select base__uid from sample where base__sample_id=?) as s, (select base__uid from variant where "
                    + variant_criteria
                    + ") as v on s.base__uid = v.base__uid order by s.base__uid",
                    (samples[sample_no],),
                )
            else:
                cursor.execute(
                    "select base__uid from sample where base__sample_id=? order by base__uid",
                    (samples[sample_no],),
                )
        for r in cursor.fetchall():
            if variant_criteria is not None:
                pos = uids.index(r[0])
            else:
                pos = r[0] - 1
            if use_zygosity:
                zygosity = r[1]
                if zygosity == "het":
                    arr[sample_no][pos] = 1
                elif zygosity == "hom":
                    arr[sample_no][pos] = 2
                else:
                    raise ValueError(f"Unknown zygosity: {zygosity}")
            else:
                arr[sample_no][pos] = 1
    uids = np.array(uids, dtype=np.uint32)
    return samples, uids, arr


def get_df_from_db(
    db_path: str,
    table_name: str = "variant",
    sql: Optional[str] = None,
    num_cores: int = 1,
    conn=None,
    library: Optional[str] = "polars",
    ):
    """Gets a Polars DataFrame of a table in an OakVar result database.

    Args:
        db_path (str): Path to the OakVar result database file
                       from which a Polars DataFrame will be extracted.
        table_name (str): Table name to dump to the DataFrame
        sql (Optional[str]): Custom SQL to apply before dumping to the DataFrame.
            For example,
            `"select base__uid, base__chrom, base__pos from variant where
            clinvar__sig='Pathogenic'"`.
        num_cores (int): Number of CPU cores to use

    Returns:
        DataFrame of the given or default table of the OakVar result database
    """
    import sys
    from pathlib import Path
    from os import environ
    import polars as pl

    environ["RUST_LOG"] = "connectorx=warn,connectorx_python=warn"
    partition_ons = {
        "variant": "base__uid",
        "gene": "base__hugo",
        "sample": "base__uid",
        "mapping": "base__uid",
    }
    df = None
    db_path_to_use = str(Path(db_path).absolute())
    partition_on = partition_ons.get(table_name)
    if conn is not None:
        db_conn = conn
    else:
        db_conn = get_result_db_conn(db_path_to_use)
        if not db_conn:
            return None
    if partition_on and table_name:
        c = db_conn.cursor()
        c.execute(f"select {partition_on} from {table_name} limit 1")
        ret = c.fetchone()
        if not ret:
            sys.stderr.write(f"{partition_on} does not exist in {table_name}")
            c.close()
            return None
        else:
            c.close()
    c = db_conn.cursor()
    c.execute("select sql from sqlite_master where type='table' and tbl_name='variant'")
    ret = c.fetchone()
    if not ret:
        return None
    col_defs = ret[0].split("(")[1].rstrip(")").split(", ")
    schema_overrides = {}
    for col_def in col_defs:
        parts = col_def.split(" ")
        col_name = parts[0]
        col_type = parts[1]
        if col_type == "text":
            pl_type = pl.String
        elif col_type == "integer":
            pl_type = pl.Int32
        elif col_type == "float":
            pl_type = pl.Float32
        else:
            sys.stderr.write("Unknown column type: " + col_type)
            return None
        schema_overrides[col_name] = pl_type
    c.close()
    if not sql:
        sql = f"select * from {table_name}"
    df = pl.read_database(sql, db_conn, schema_overrides=schema_overrides)  # type: ignore
    if conn is None:
        db_conn.close()
    return df


def is_in_jupyter_notebook() -> bool:
    import os

    return "JPY_SESSION_NAME" in os.environ
