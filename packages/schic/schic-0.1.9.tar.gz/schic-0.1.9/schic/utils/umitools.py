# -*- coding: utf-8 -*-
__author__ = "legendzdy@dingtalk.com"
"""
Author: legendzdy@dingtalk.com
Data: 20250114
Description:
function map.
"""
import re, os, gzip, subprocess
from basebio import clean_read1_name, check_path_exists

def extract_pattern_from_bc_pattern(bc_pattern):
    """
    from bc_pattern string, extract fixed part and build regular expression pattern.
    
    Args:
    bc_pattern: format like '(?P<discard_1>ACATGGCTACGATCCGACTTTCTGCG)(?P<cell_1>.{10})...'
    
    Returns:
    a regular expression pattern object.
    """
    # extract all fixed parts from bc_pattern
    fixed_parts = re.findall(r'\(\?P<[^>]+>([^)]+)\)', bc_pattern)
    
    # build complete regular expression pattern
    # replace variable parts with [ATCG]{length} format
    pattern_str = ""
    for part in fixed_parts:
        # if part is fixed sequence, add directly
        if not re.match(r'^\.\{\d+\}$', part):
            pattern_str += part
        # if part is variable length part, convert to [ATCG]{length} format
        else:
            length = re.search(r'\{(\d+)\}', part).group(1) # type: ignore
            pattern_str += f"[ATCG]{{{length}}}"
    
    return re.compile(pattern_str)

def calculate_link_stats(bc_pattern, r1_path, r2_path):

    pattern = extract_pattern_from_bc_pattern(bc_pattern)

    total_num = 0
    link_r1_num = 0
    with gzip.GzipFile(r1_path, "rb") as fi:
        while True:
            try:
                line1 = next(fi)
                line2 = next(fi).decode().strip()
                line3 = next(fi)
                line4 = next(fi)
                total_num += 1
                if pattern.search(line2):
                    link_r1_num += 1
            except StopIteration:
                break    

    link_r2_num = 0
    with gzip.GzipFile(r2_path, "rb") as fi:
        while True:
            try:
                line1 = next(fi)
                line2 = next(fi).decode().strip()
                line3 = next(fi)
                line4 = next(fi)
                if pattern.search(line2):
                    link_r2_num += 1
            except StopIteration:
                break

    r1_rate = round((link_r1_num * 100) / total_num, 2)
    r2_rate = round((link_r2_num * 100) / total_num, 2)
    rawname = clean_read1_name(os.path.basename(r1_path))
    
    csv_content = f"""sample_R,totalNum,linkNum,linkRate,linkRE
{rawname}_R1,{total_num},{link_r1_num},{r1_rate}%,{pattern.pattern}
{rawname}_R2,{total_num},{link_r2_num},{r2_rate}%,{pattern.pattern}
"""
    with open(f"{rawname}.linkStat.csv", "w") as csv_file:
        csv_file.write(csv_content)


def extract_run(bc_pattern, stdin, stdout, read2_in, read2_out, whitelist, tool, tool_command, parms):
    """
    extract UMI with umitools.
    Args:
        bc-pattern: Barcode pattern for paired reads.
        stdin: input read1 file.
        stdout: output read1 file.
        read2-in: input read2 file.
        read2-out: output read2 file.
        whitelist: whitelist file.
        tool: umitools tool path.
        tool_command: umitools command.
        params: umitools params.
    """
    params_list = parms.split()
    command = [
        tool, tool_command, *params_list, f"--bc-pattern={bc_pattern}", f"--stdin={stdin}", f"--stdout={stdout}", f"--read2-in={read2_in}", f"--read2-out={read2_out}", f"--whitelist={whitelist}"
        ]
    try:
        if not check_path_exists(read2_out):
            subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        exit(1)
    
    rawname = clean_read1_name(os.path.basename(stdin))
    if not check_path_exists(f"{rawname}.linkStat.csv"):
        calculate_link_stats(bc_pattern, stdin, read2_in)

def whitelist_run(bc_pattern, stdin, set_cell_number, plot_prefix, stdout, tool, tool_command, parms):
    """
    extract UMI with umitools.
    Args:
        bc-pattern: Barcode pattern for paired reads.
        stdin: input read1 file.
        set_cell_number: setting cell number.
        plot_prefix: plot prefix.
        stdout: output whitelist file.
        tool: umitools tool path.
        tool: umitools tool path.
        tool_command: umitools command.
        params: umitools params.
    """
    params_list = parms.split()
    command = [
        tool, tool_command, f"--stdin={stdin}", f"--bc-pattern={bc_pattern}", *params_list, f"--set-cell-number={set_cell_number}", f"--plot-prefix={plot_prefix}", f"--stdout={stdout}"
        ]
    try:
        print(f"Running command: {' '.join(command)}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        exit(1)
