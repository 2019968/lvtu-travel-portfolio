# -*- coding: utf-8 -*-
"""
调研数据分析脚本
读取CSV数据，输出统计分析结果为JSON，供作品集网页使用
"""
import csv
import json
import os
from collections import Counter, defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "..", "02-调研数据", "调研原始数据_328份.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "数据分析结果.json")

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)

def count_single(records, field):
    """单选题统计"""
    counter = Counter(r[field] for r in records if r[field])
    total = sum(counter.values())
    return [{"name": k, "count": v, "percent": round(v/total*100, 1)} for k, v in counter.most_common()]

def count_multi(records, field):
    """多选题统计（按顿号分割）"""
    counter = Counter()
    total = 0
    for r in records:
        if r[field]:
            total += 1
            for item in r[field].split("、"):
                counter[item] += 1
    return [{"name": k, "count": v, "percent": round(v/total*100, 1)} for k, v in counter.most_common()]

def cross_analysis(records, field_x, field_y):
    """交叉分析：field_x 分组统计 field_y"""
    groups = defaultdict(list)
    for r in records:
        if r[field_x] and r[field_y]:
            groups[r[field_x]].append(r[field_y])
    result = {}
    for group, values in groups.items():
        counter = Counter(values)
        total = len(values)
        result[group] = {
            "total": total,
            "distribution": [{"name": k, "count": v, "percent": round(v/total*100, 1)} for k, v in counter.most_common()]
        }
    return result

def cross_analysis_multi(records, field_x, field_y_multi):
    """交叉分析：field_x 分组统计多选题 field_y_multi"""
    groups = defaultdict(list)
    for r in records:
        if r[field_x] and r[field_y_multi]:
            groups[r[field_x]].append(r[field_y_multi])
    result = {}
    for group, values in groups.items():
        counter = Counter()
        for v in values:
            for item in v.split("、"):
                counter[item] += 1
        total = len(values)
        result[group] = {
            "total": total,
            "distribution": [{"name": k, "count": v, "percent": round(v/total*100, 1)} for k, v in counter.most_common()]
        }
    return result

def pain_demand_matching(records):
    """痛点-需求匹配分析"""
    # 最严重痛点 vs 最希望功能
    pain_func = defaultdict(Counter)
    pain_total = Counter()
    for r in records:
        pain = r["最严重的困扰"]
        if pain and r["最希望的功能(多选)"]:
            pain_total[pain] += 1
            for func in r["最希望的功能(多选)"].split("、"):
                pain_func[pain][func] += 1
    result = {}
    for pain, funcs in pain_func.items():
        total = pain_total[pain]
        result[pain] = {
            "total": total,
            "top_functions": [{"name": k, "count": v, "percent": round(v/total*100, 1)} for k, v in funcs.most_common(5)]
        }
    return result

def demand_priority(records):
    """需求优先级排序：基于功能选择率 + 痛点严重度"""
    func_stats = count_multi(records, "最希望的功能(多选)")
    pain_stats = count_single(records, "最严重的困扰")

    # 痛点-功能映射
    pain_func_map = {
        "攻略信息太分散，多APP切换": ["按预算推荐目的地和行程", "现成学生党行程模板", "行程共享与协同编辑"],
        "攻略质量参差不齐，广告多": ["当地美食红黑榜", "小众目的地种草", "住宿区域推荐"],
        "缺少学生视角的预算参考": ["按预算推荐目的地和行程", "现成学生党行程模板", "旅行记账与AA分摊"],
        "没有现成行程模板": ["现成学生党行程模板", "按预算推荐目的地和行程"],
        "交通接驳信息不清晰": ["交通接驳指南", "实时避坑提醒"],
        "小众目的地信息太少": ["小众目的地种草", "交通接驳指南"],
        "住宿选择困难": ["住宿区域推荐", "按预算推荐目的地和行程"],
        "美食探店容易踩雷": ["当地美食红黑榜", "小众目的地种草"],
        "一人出行难拼车/找搭子": ["出行搭子匹配", "行程共享与协同编辑"],
    }

    func_pain_score = defaultdict(float)
    for pain, funcs in pain_func_map.items():
        pain_percent = next((p["percent"] for p in pain_stats if p["name"] == pain), 0)
        for func in funcs:
            func_pain_score[func] += pain_percent

    priority_list = []
    for fs in func_stats:
        name = fs["name"]
        if name == "其他":
            continue
        selection_rate = fs["percent"]
        pain_score = round(func_pain_score.get(name, 0), 1)
        # 综合得分 = 选择率*0.6 + 痛点关联度*0.4
        composite = round(selection_rate * 0.6 + pain_score * 0.4, 1)
        # 优先级判定
        if composite >= 25:
            priority = "P0"
        elif composite >= 18:
            priority = "P1"
        else:
            priority = "P2"
        priority_list.append({
            "function": name,
            "selection_rate": selection_rate,
            "pain_relevance": pain_score,
            "composite_score": composite,
            "priority": priority
        })

    priority_list.sort(key=lambda x: x["composite_score"], reverse=True)
    return priority_list

def main():
    records = load_data()
    total = len(records)
    print(f"加载数据：{total} 条记录")

    analysis = {
        "meta": {
            "total_samples": total,
            "valid_samples": total,
            "survey_period": "2026.09.01 - 2026.09.10",
            "data_source": "问卷星 + 校园社群 + 小红书"
        },
        "basic_info": {
            "grade": count_single(records, "年级"),
            "major": count_single(records, "专业类别"),
            "living_cost": count_single(records, "月可支配生活费"),
        },
        "travel_behavior": {
            "trip_frequency": count_single(records, "半年短途出行次数"),
            "destination_type": count_multi(records, "目的地类型"),
            "companion": count_single(records, "同行人"),
            "budget": count_single(records, "单次出行预算"),
            "budget_part": count_single(records, "预算占比最大项"),
            "plan_ahead": count_single(records, "提前规划时间"),
            "info_channel": count_multi(records, "信息获取渠道"),
        },
        "pain_points": {
            "pain_multi": count_multi(records, "遇到的困扰(多选)"),
            "worst_pain": count_single(records, "最严重的困扰"),
            "plan_tool_use": count_single(records, "是否用过行程规划工具"),
            "tool_complaints": count_multi(records, "对工具不满意的地方"),
        },
        "demands": {
            "functions": count_multi(records, "最希望的功能(多选)"),
            "pay_willing": count_single(records, "最愿意付费的功能"),
            "product_form": count_single(records, "倾向的使用形式"),
            "content_style": count_single(records, "偏好的内容风格"),
        },
        "cross_analysis": {
            "grade_x_frequency": cross_analysis(records, "年级", "半年短途出行次数"),
            "livingcost_x_budget": cross_analysis(records, "月可支配生活费", "单次出行预算"),
            "livingcost_x_pay": cross_analysis(records, "月可支配生活费", "最愿意付费的功能"),
            "frequency_x_functions": cross_analysis_multi(records, "半年短途出行次数", "最希望的功能(多选)"),
            "major_x_destination": cross_analysis_multi(records, "专业类别", "目的地类型"),
        },
        "pain_demand_matching": pain_demand_matching(records),
        "demand_priority": demand_priority(records),
        "open_ended_summary": {
            "total_filled": sum(1 for r in records if r["其他未满足需求"]),
            "total_empty": sum(1 for r in records if not r["其他未满足需求"]),
            "interview_willing": sum(1 for r in records if r["是否愿意参与访谈(留微信)"]),
        }
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print(f"分析结果已保存：{OUTPUT_FILE}")
    print(f"文件大小：{os.path.getsize(OUTPUT_FILE)/1024:.1f} KB")

    # 输出关键发现
    print("\n=== 关键发现 ===")
    print(f"P0需求：{[d['function'] for d in analysis['demand_priority'] if d['priority']=='P0']}")
    print(f"P1需求：{[d['function'] for d in analysis['demand_priority'] if d['priority']=='P1']}")
    print(f"最严重痛点TOP3：{[p['name'] for p in analysis['pain_points']['worst_pain'][:3]]}")
    print(f"最希望功能TOP3：{[f['name'] for f in analysis['demands']['functions'][:3]]}")
    print(f"倾向使用形式：{analysis['demands']['product_form'][0]['name']} ({analysis['demands']['product_form'][0]['percent']}%)")

if __name__ == "__main__":
    main()
