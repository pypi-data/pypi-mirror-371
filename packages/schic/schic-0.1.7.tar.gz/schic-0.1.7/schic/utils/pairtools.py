# -*- coding: utf-8 -*-
__author__ = "legendzdy@dingtalk.com"
"""
Author: legendzdy@dingtalk.com
Data: 20250725
Description:
pairtools.
"""
import os, gzip, shutil
import pandas as pd
import numpy as np
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
from basebio import run_command, check_path_exists

def mkpairs(input_pairs, output_pairs):
    """
    unzip pairs file and extract only the first 8 columns

    Args:
        input_pairs: input pairs file.
        output_pairs: output pairs file.
    
    Example:
        mkpairs('input.pairs.gz', 'output.pairs')
    """
    
    if not os.path.exists(input_pairs):
        raise FileNotFoundError(f"Pairs file not found: {input_pairs}")
    
    with gzip.open(input_pairs, 'rt') as f_in, open(output_pairs, 'w') as f_out:
        for line in f_in:
            if not line.startswith('#'):
                cols = line.strip().split('\t')
                if len(cols) >= 8:
                    f_out.write('\t'.join(cols[:8]) + '\n')

def mkstats(input_stats, output_stats):
    """
    Parse stats file and extract only the required columns and rename them.

    Args:
        input_stats: input stats file.
        output_stats: output stats file.
    
    Example:
        mkstats('input.stats', 'output.stats')
    """
    stats_dict = {}
    with open(input_stats, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                stats_dict[parts[0]] = parts[1]
    
    total = int(stats_dict.get("total", 0))
    unmapped = int(stats_dict.get("total_unmapped", 0))
    mapped = int(stats_dict.get("total_mapped", 0))
    dups = int(stats_dict.get("total_dups", 0))
    nodups = int(stats_dict.get("total_nodups", 0))
    cis = int(stats_dict.get("cis", 0))
    trans = int(stats_dict.get("trans", 0))
    cis_gt1kb = int(stats_dict.get("cis_1kb+", 0))
    cis_lt1kb = cis - cis_gt1kb
    cis_gt10kb = int(stats_dict.get("cis_10kb+", 0))
    valid_pairs = trans + cis_gt1kb
    
    with open(output_stats, 'w') as f_out:
        f_out.write(f"""Total_Reads\t{total}
Unmapped_Read_Pairs\t{unmapped}
Mapped_Read_Pairs\t{mapped}
PCR_Dup_Read_Pairs\t{dups}
No-Dup_Read_Pairs\t{nodups}
Cis_Read_Pairs\t{cis}
Trans_Read_Pairs\t{trans}
Valid_Read_Pairs\t{valid_pairs}
Cis1kb\t{cis_lt1kb}
Cis1kb+\t{cis_gt1kb}
Cis10kb+\t{cis_gt10kb}
""")

def qc_plots(input_path, output_path, prefix):
    # 设置matplotlib参数
    plt.rcParams.update({
        'font.size': 15,
    })
    
    # 读取数据
    raw_data = pd.read_csv(input_path, sep='\t', header=None)
    raw_data[0] = raw_data[0].str.replace('_', ' ')
    
    # 处理第一个图的数据
    raw1 = raw_data.iloc[0:5].copy()
    total_reads = raw1.iloc[0, 1]
    raw1[2] = (raw1[1] / total_reads * 100).round(3).astype(str) + '%' # type: ignore
    
    # 插入Low MAPQ行
    low_mapq_val = total_reads - raw1.iloc[1, 1] - raw1.iloc[2, 1] # type: ignore
    low_mapq_row = pd.DataFrame({
        0: ['Low MAPQ'],
        1: [low_mapq_val],
        2: [f'{(low_mapq_val/total_reads*100).round(2)}%'] # type: ignore
    })
    raw1 = pd.concat([raw1.iloc[:1], low_mapq_row, raw1.iloc[1:]]).reset_index(drop=True)
    
    # 添加分类列
    sub_group_categories = ["Total Reads", "Unmapped Read Pairs", "Low MAPQ", 
                           "Mapped Read Pairs", "PCR Dup Read Pairs", "No-Dup Read Pairs"]
    
    raw1['sub_group'] = pd.Categorical(raw1[0], categories=sub_group_categories)
    group_categories = ["Total", "Alignment", "Dup/NO-Dup"]
    raw1['group'] = pd.Categorical(
        ["Total", "Alignment", "Alignment", "Alignment", "Dup/NO-Dup", "Dup/NO-Dup"],
        categories=group_categories
    )
    raw1['values'] = raw1[1] / 1e6
    raw1['label'] = raw1['values'].round(3).astype(str) + 'M\n' + raw1[2]
    
    # 保存CSV
    raw1[[0, 1, 2]].rename(columns={0: 'Group', 1: 'Reads Number', 2: 'Mapping rate'})\
        .to_csv(os.path.join(output_path, f'{prefix}.QC1.csv'), index=False)
    
    # 绘制第一个图
    color_set1 = {
        "Total Reads": "#686464",
        "Low MAPQ": "#404491",
        "Unmapped Read Pairs": "#a48784",
        "Mapped Read Pairs": "#829fd2",
        "PCR Dup Read Pairs": "#cc4a4e",
        "No-Dup Read Pairs": "#b5d6f0"
    }
    
    fig, ax = plt.subplots(figsize=(12, 9))
    
    # 确保所有类别都在颜色字典中
    for category in raw1['sub_group'].unique():
        if category not in color_set1:
            print(f"警告: 类别 '{category}' 不在颜色字典中")
    
    # 手动创建堆叠条形图
    groups = ["Total", "Alignment", "Dup/NO-Dup"]
    bottom = np.zeros(len(groups))
    
    for category in sub_group_categories:
        if category in raw1['sub_group'].values:
            values = []
            for group in groups:
                group_data = raw1[(raw1['group'] == group) & (raw1['sub_group'] == category)]
                values.append(group_data['values'].sum() if not group_data.empty else 0)
            
            ax.bar(groups, values, bottom=bottom, label=category, color=color_set1[category])
            bottom += values
    
    # 添加标签
    for i, group in enumerate(groups):
        group_data = raw1[raw1['group'] == group]
        cumulative = 0
        for _, row in group_data.iterrows():
            if row['values'] > 0:  # 只为非零值添加标签
                ax.text(i, cumulative + row['values']/2, row['label'], 
                       ha='center', va='center', fontsize=15)
            cumulative += row['values']
    
    ax.set_xlabel('')
    ax.set_ylabel('Number of reads (millions)')
    ax.legend(title='', bbox_to_anchor=(1.05, 0.5), loc='center left')
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_path, f'{prefix}.QC1.pdf'))
    plt.savefig(os.path.join(output_path, f'{prefix}.QC1.png'))
    plt.close()
    
    # 处理第二个图的数据
    raw2 = raw_data.iloc[4:10].copy()
    no_dup_reads = raw2.iloc[0, 1]
    
    raw2[2] = (raw2[1] / no_dup_reads * 100).round(2).astype(str) + '%' # type: ignore
    
    sub_group_categories2 = [
    "No-Dup Read Pairs", "Cis Read Pairs", "Trans Read Pairs", "Valid Read Pairs",
    "Cis1kb", "Cis1kb+"
    ]
    group_categories2 = ["No-Dup reads", "cis/trans", "cis", "Valid Pairs\n(trans+cis≥1Kb)"]
    
    raw2['sub_group'] = pd.Categorical(raw2[0], categories=sub_group_categories2)
    raw2['group'] = pd.Categorical(
        ["No-Dup reads", "cis/trans", "cis/trans", "Valid Pairs\n(trans+cis≥1Kb)", "cis", "cis"],
        categories=group_categories2
    )
    raw2['values'] = raw2[1] / 1e6
    raw2['label'] = raw2['values'].round(3).astype(str) + 'M\n' + raw2[2]
    
    # 保存CSV
    raw2[[0, 1, 2]].rename(columns={0: 'Group', 1: 'Reads Number', 2: 'Mapping rate'})\
        .to_csv(os.path.join(output_path, f'{prefix}.QC2.csv'), index=False, quotechar='"')
    
    # 绘制第二个图
    color_set2 = {
        "No-Dup Read Pairs": "#b5d6f0",
        "Cis Read Pairs": "#9f356a",
        "Trans Read Pairs": "#f0623c",
        "Valid Read Pairs": "#2b9551",
        "Cis1kb": "#fe9295",
        "Cis1kb+": "#9cc9a6"
    }
    
    fig, ax = plt.subplots(figsize=(12, 9))
    
    # 手动创建堆叠条形图
    groups = ["No-Dup reads", "cis/trans", "cis", "Valid Pairs\n(trans+cis≥1Kb)"]
    bottom = np.zeros(len(groups))
    
    for category in sub_group_categories2:
        if category in raw2['sub_group'].values:
            values = []
            for group in groups:
                group_data = raw2[(raw2['group'] == group) & (raw2['sub_group'] == category)]
                values.append(group_data['values'].sum() if not group_data.empty else 0)
            
            ax.bar(groups, values, bottom=bottom, label=category, color=color_set2[category])
            bottom += values
    
    # 添加标签
    for i, group in enumerate(groups):
        group_data = raw2[raw2['group'] == group]
        cumulative = 0
        for _, row in group_data.iterrows():
            if row['values'] > 0:  # 只为非零值添加标签
                ax.text(i, cumulative + row['values']/2, row['label'], 
                       ha='center', va='center', fontsize=15)
            cumulative += row['values']
    
    ax.set_xlabel('')
    ax.set_ylabel('Number of reads (millions)')
    ax.legend(title='', bbox_to_anchor=(1.05, 0.5), loc='center left')
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_path, f'{prefix}.QC2.pdf'))
    plt.savefig(os.path.join(output_path, f'{prefix}.QC2.png'))
    plt.close()

def hist_plot(input_file, output_path, prefix):
    lengths = []
    with open(input_file, 'r') as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 2:
                continue
            count = parts[1]
            lengths.append(int(count))

    # 设置中文字体支持
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    # 创建图形
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 绘制密度图
    sns.kdeplot(lengths, ax=ax1, fill=True, color='skyblue', linewidth=2)
    ax1.set_xlabel('barcodes', fontsize=12)
    ax1.set_ylabel('distribution', fontsize=12)
    ax1.set_title('contact distribution', fontsize=14)
    ax1.grid(True, linestyle='--', alpha=0.7)

    # 绘制直方图
    sns.histplot(lengths, ax=ax2, kde=True, color='lightcoral', bins=15)
    ax2.set_xlabel('barcodes', fontsize=12)
    ax2.set_ylabel('frequency', fontsize=12)
    ax2.set_title('contact frequency', fontsize=14)
    ax2.grid(True, linestyle='--', alpha=0.7)

    # 添加统计信息文本框
    stats_text = f"""statistics:
    - barcode count: {len(lengths)}
    - contact mean: {np.mean(lengths):.2f}
    - contact min: {np.min(lengths)}
    - contact max: {np.max(lengths)}
"""
    fig.text(0.85, 0.8, stats_text, ha='left', va='center', fontsize=10,
         bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.5),
         transform=fig.transFigure)

    # 调整布局
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_path, f'{prefix}.contacts_dist.pdf'))
    plt.savefig(os.path.join(output_path, f'{prefix}.contacts_dist.png'))
    plt.close()
    
def mkcontacts(input_pairs, output="schic_contacts", prefix="schic", filter=500):
    """
    Process contacts file to extract barcode-specific contacts.

    """
    barcode_contacts = os.path.join(os.path.dirname(output), f"{prefix}_barcode_contacts")
    if os.path.exists(barcode_contacts) and os.path.isdir(barcode_contacts):
        shutil.rmtree(barcode_contacts)
    os.makedirs(output, exist_ok=True)
    os.makedirs("tmp_contacts_pairs", exist_ok=True)

    command = r"""awk -F '[_\t]' '{file="tmp_contacts_pairs/"$2".contacts.pairs"; print ".\t"$4"\t"$5"\t"$6"\t"$7"\t"$8"\t"$9 >> file; close(file)}' """ + input_pairs
    run_command(command, use_shell=True)
    os.rename("tmp_contacts_pairs", barcode_contacts)

    count = 1
    stat_file = f"{prefix}.barcode_contacts.stats"
    with open(stat_file, 'a') as sf:
        for contacts_file in Path(barcode_contacts).glob("*.contacts.pairs"):
            with open(contacts_file, 'r') as f:
                line_count = sum(1 for _ in f)
            
            barcode = os.path.basename(contacts_file).split('.')[0]
            sf.write(f"{barcode}\t{line_count}\n")
            
            if line_count >= int(filter):
                new_count = f"{count:04d}"
                output_file = os.path.join(output, f"schic_{new_count}.contacts.pairs.txt")
                
                with open(contacts_file, 'rb') as f_in:
                    with gzip.open(f"{output_file}.gz", 'wb') as f_out:
                        f_out.write(f_in.read())
                count += 1
    hist_plot(stat_file, os.path.dirname(output), prefix)

def pairtools(input_R1, input_R2, reference, genome_size, prefix, filter=500, threads=8):
    """
    Align and deduplicate paired-end reads using bwa mem and pairtools.

    Args:
        input_R1: input R1 fastq file.
        input_R2: input R2 fastq file.
        reference: bwa index of reference fasta file.
        genome_size: size of the reference genome.
        prefix: output prefix.
        threads: number of threads.
    
    Example:
        pairtools(input_R1="R1.fastq.gz", input_R2="R2.fastq.gz", reference="reference.fasta", genome_size="3.0e9", prefix="output", threads=8)
    """
    out_sam = prefix + ".aligned.sam"
    cmd = ["bwa", "mem", "-5SP", "-T0", "-t", str(threads), reference, input_R1, input_R2, ">", out_sam]
    if not check_path_exists(out_sam):
        run_command(" ".join(cmd), use_shell=True)

    out_pairs = prefix + ".pairs.gz"
    if not check_path_exists(out_pairs):
        run_command(["pairtools", "parse", "-c", genome_size, "-o", out_pairs, out_sam])

    out_sorted = prefix + ".sorted.pairs.gz"
    if not check_path_exists(out_sorted):
        run_command(["pairtools", "sort", "--nproc", str(threads), "-o", out_sorted, out_pairs])

    out_nodups = prefix + ".nodups.pairs.gz"
    out_dups = prefix + ".dups.pairs.gz"
    out_unmapped = prefix + ".unmapped.pairs.gz"
    out_stats = prefix + ".dedup.stats"
    if not check_path_exists(out_nodups):
        run_command(["pairtools", "dedup", "--mark-dups", "--output", out_nodups, "--output-dups", out_dups, "--output-unmapped", out_unmapped, "--output-stats", out_stats, out_sorted])

    mapped_pairs = prefix + ".mapped.pairs"
    if not check_path_exists(mapped_pairs):
        mkpairs(out_nodups, mapped_pairs)

    qc_file = prefix + ".qc.txt"
    if not check_path_exists(qc_file):
        mkstats(out_stats, qc_file)
    
    qc_output = prefix + ".qc_plots"
    os.makedirs(qc_output, exist_ok=True)
    if not os.path.exists(f"{qc_output}/{prefix}_QC1.pdf"):
        qc_plots(qc_file, qc_output, prefix)
    
    contacts_dir = prefix + ".contact_filted_" + str(filter)
    if not os.path.exists(contacts_dir):
        mkcontacts(mapped_pairs, contacts_dir, prefix, filter=filter)