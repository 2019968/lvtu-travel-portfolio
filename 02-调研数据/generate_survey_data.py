# -*- coding: utf-8 -*-
"""
大学生轻量化文旅出行工具调研 - 模拟数据生成脚本
生成328份有效样本，数据包含合理的逻辑关联，非纯随机
"""
import csv
import random
import os

random.seed(42)  # 固定随机种子，保证可复现

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "调研原始数据_328份.csv")

# ============ 选项定义 ============
GRADES = ["大一", "大二", "大三", "大四", "研一", "研二及以上"]
GRADE_WEIGHTS = [0.18, 0.25, 0.28, 0.15, 0.08, 0.06]

MAJORS = ["经管类", "理工类", "文史哲类", "艺术类", "医学类", "教育类", "旅游/酒店管理类", "其他"]
MAJOR_WEIGHTS = [0.22, 0.20, 0.15, 0.10, 0.08, 0.08, 0.12, 0.05]

LIVING_COSTS = ["1000元以下", "1000-1500元", "1501-2000元", "2001-2500元", "2501-3000元", "3000元以上"]
LIVING_COST_WEIGHTS = [0.08, 0.22, 0.30, 0.20, 0.12, 0.08]

TRIP_FREQS = ["0次", "1-2次", "3-4次", "5-6次", "7次及以上"]
DEST_TYPES = ["城市人文", "自然风景", "主题乐园", "美食探店", "周边乡村/古镇", "网红打卡点", "高校校园参观", "其他"]
COMPANIONS = ["独自一人", "室友/同学(2-3人)", "朋友小团体(4人以上)", "男/女朋友", "家人"]
BUDGETS = ["200元以下", "201-400元", "401-600元", "601-800元", "801-1000元", "1000元以上"]
BUDGET_PARTS = ["交通", "住宿", "餐饮", "门票/体验项目", "购物/伴手礼"]
PLAN_AHEAD = ["说走就走", "提前1-2天", "提前3-7天", "提前1-2周", "提前2周以上"]
INFO_CHANNELS = ["小红书", "抖音", "大众点评", "OTA平台(携程/马蜂窝)", "朋友推荐", "微博", "B站", "知乎", "其他"]

PAIN_POINTS = [
    "攻略信息太分散，多APP切换",
    "攻略质量参差不齐，广告多",
    "缺少学生视角的预算参考",
    "没有现成行程模板",
    "交通接驳信息不清晰",
    "小众目的地信息太少",
    "住宿选择困难",
    "美食探店容易踩雷",
    "一人出行难拼车/找搭子",
    "其他"
]

PLAN_TOOL_USE = ["经常使用", "偶尔使用", "听说过但没用过", "完全没听说过"]
PLAN_TOOL_USE_WEIGHTS = [0.08, 0.25, 0.35, 0.32]

TOOL_COMPLAINTS = ["操作太复杂", "行程模板太少", "不能按预算调整", "交通时间不准", "不能协同编辑", "推荐太商业化", "其他"]

FUNCTIONS = [
    "按预算推荐目的地和行程",
    "现成学生党行程模板",
    "小众目的地种草",
    "交通接驳指南",
    "当地美食红黑榜",
    "住宿区域推荐",
    "出行搭子匹配",
    "行程共享与协同编辑",
    "实时避坑提醒",
    "旅行记账与AA分摊",
    "其他"
]

PAY_WILLING = ["无广告纯净体验", "独家小众目的地攻略", "AI高级行程定制", "都不愿意付费", "其他"]
PRODUCT_FORM = ["微信小程序", "独立APP", "小红书/抖音账号+社群", "网页版", "都可以"]
CONTENT_STYLE = ["真实接地气(学长学姐经验)", "简洁高效(直接给结论)", "图文精美", "有趣好玩有梗", "专业严谨数据详实"]

# 开放题素材
OPEN_ENDED_SAMPLES = [
    "", "", "", "", "",  # 约40%空
    "希望能有大学生优惠门票的汇总信息",
    "周末短途游的推荐能不能更精准一些",
    "一个人旅行的安全问题能不能有提示",
    "高铁票抢票攻略也想要",
    "希望能看到实时的景区人流量",
    "青旅的真实评价太少了",
    "能不能有旅行照片的模板推荐",
    "",
    "当地特色节日活动的信息想要",
    "希望能和同校的人组队出行",
    "",
    "行李寄存的点能不能标注出来",
    "希望有雨天备选方案",
    "",
    "景区学生票需要带什么证件能不能说明",
    "希望能有旅行vlog的模板",
    "",
    "小众景点的交通真的很头疼",
    "希望能看到目的地的天气和穿搭建议",
    "",
    "能不能有毕业旅行的专题",
    "音乐节+旅行的组合攻略想要",
    "",
    "希望能有省钱技巧的汇总",
    "当地菜市场能不能推荐，想吃地道的",
    "",
    "希望能有夜生活安全的提示",
    "拍照机位能不能标注出来",
]


def weighted_choice(options, weights):
    return random.choices(options, weights=weights, k=1)[0]


def multi_select(options, min_count=1, max_count=3, weights=None):
    """多选，返回逗号分隔的字符串"""
    count = random.randint(min_count, max_count)
    if weights:
        selected = random.choices(options, weights=weights, k=count)
    else:
        selected = random.sample(options, min(count, len(options)))
    # 去重
    selected = list(dict.fromkeys(selected))
    return "、".join(selected)


def generate_one_record(idx):
    """生成一条调研记录"""
    record = {"样本编号": f"S{idx+1:03d}"}

    # ===== 基本信息 =====
    grade = weighted_choice(GRADES, GRADE_WEIGHTS)
    major = weighted_choice(MAJORS, MAJOR_WEIGHTS)
    living_cost = weighted_choice(LIVING_COSTS, LIVING_COST_WEIGHTS)
    record["年级"] = grade
    record["专业类别"] = major
    record["月可支配生活费"] = living_cost

    # 生活费等级（用于逻辑关联）
    lc_level = LIVING_COSTS.index(living_cost)
    # 年级等级
    grade_level = GRADES.index(grade)
    # 是否旅游相关专业
    is_tourism_major = major in ["旅游/酒店管理类"]

    # ===== 出行行为 =====
    # 出行频率：年级越高、旅游专业、生活费越高 → 频率越高
    freq_weights = [0.05, 0.35, 0.32, 0.18, 0.10]
    # 调整
    if lc_level >= 4:
        freq_weights = [0.02, 0.25, 0.35, 0.23, 0.15]
    if grade_level >= 3:
        freq_weights = [f * 0.8 for f in freq_weights]
        freq_weights[2] += 0.05
        freq_weights[3] += 0.05
        freq_weights[4] += 0.03
    if is_tourism_major:
        freq_weights = [0.01, 0.15, 0.30, 0.30, 0.24]
    # 归一化
    total = sum(freq_weights)
    freq_weights = [f/total for f in freq_weights]
    trip_freq = weighted_choice(TRIP_FREQS, freq_weights)
    record["半年短途出行次数"] = trip_freq

    # 如果0次，跳转到痛点部分（Q12）
    if trip_freq == "0次":
        record["目的地类型"] = ""
        record["同行人"] = ""
        record["单次出行预算"] = ""
        record["预算占比最大项"] = ""
        record["提前规划时间"] = ""
        record["信息获取渠道"] = ""
    else:
        # 目的地类型多选
        dest_weights = [0.25, 0.20, 0.12, 0.15, 0.10, 0.10, 0.05, 0.03]
        if is_tourism_major:
            dest_weights = [0.20, 0.22, 0.08, 0.12, 0.18, 0.12, 0.05, 0.03]
        record["目的地类型"] = multi_select(DEST_TYPES, 1, 3, dest_weights)

        # 同行人
        comp_weights = [0.10, 0.35, 0.20, 0.25, 0.10]
        if grade_level <= 1:
            comp_weights = [0.05, 0.45, 0.25, 0.15, 0.10]
        record["同行人"] = weighted_choice(COMPANIONS, comp_weights)

        # 出行预算：和生活费强相关
        budget_weights = [0.05, 0.15, 0.30, 0.25, 0.15, 0.10]
        if lc_level <= 1:
            budget_weights = [0.15, 0.35, 0.30, 0.12, 0.05, 0.03]
        elif lc_level >= 4:
            budget_weights = [0.02, 0.08, 0.20, 0.28, 0.25, 0.17]
        total = sum(budget_weights)
        budget_weights = [b/total for b in budget_weights]
        budget = weighted_choice(BUDGETS, budget_weights)
        record["单次出行预算"] = budget

        # 预算占比最大项
        budget_level = BUDGETS.index(budget)
        bp_weights = [0.30, 0.25, 0.20, 0.15, 0.10]
        if budget_level <= 1:
            bp_weights = [0.35, 0.15, 0.25, 0.15, 0.10]
        record["预算占比最大项"] = weighted_choice(BUDGET_PARTS, bp_weights)

        # 提前规划时间
        pa_weights = [0.12, 0.28, 0.32, 0.18, 0.10]
        if grade_level >= 3:
            pa_weights = [0.08, 0.20, 0.30, 0.25, 0.17]
        record["提前规划时间"] = weighted_choice(PLAN_AHEAD, pa_weights)

        # 信息渠道多选
        info_weights = [0.28, 0.22, 0.12, 0.10, 0.10, 0.05, 0.06, 0.04, 0.03]
        record["信息获取渠道"] = multi_select(INFO_CHANNELS, 1, 3, info_weights)

    # ===== 痛点 =====
    # 痛点多选（最多5项）
    pain_weights = [0.30, 0.25, 0.22, 0.28, 0.20, 0.18, 0.12, 0.15, 0.08, 0.02]
    # 生活费低的更关注预算
    if lc_level <= 1:
        pain_weights[2] = 0.35
        pain_weights[0] = 0.25
    record["遇到的困扰(多选)"] = multi_select(PAIN_POINTS, 2, 5, pain_weights)

    # 最严重痛点
    worst_pain_weights = [0.20, 0.15, 0.18, 0.15, 0.10, 0.08, 0.05, 0.07, 0.01, 0.01]
    if lc_level <= 1:
        worst_pain_weights[2] = 0.30
        worst_pain_weights[0] = 0.15
    record["最严重的困扰"] = weighted_choice(PAIN_POINTS, worst_pain_weights)

    # 是否使用过行程规划工具
    # 出行频率高的更可能使用
    pt_weights = PLAN_TOOL_USE_WEIGHTS.copy()
    if trip_freq in ["5-6次", "7次及以上"]:
        pt_weights = [0.20, 0.40, 0.25, 0.15]
    elif trip_freq == "0次":
        pt_weights = [0.02, 0.10, 0.35, 0.53]
    record["是否用过行程规划工具"] = weighted_choice(PLAN_TOOL_USE, pt_weights)

    # 不满意点（仅使用过的显示）
    if record["是否用过行程规划工具"] in ["经常使用", "偶尔使用"]:
        tc_weights = [0.20, 0.22, 0.18, 0.12, 0.10, 0.13, 0.05]
        record["对工具不满意的地方"] = multi_select(TOOL_COMPLAINTS, 1, 3, tc_weights)
    else:
        record["对工具不满意的地方"] = ""

    # ===== 需求探索 =====
    # 功能需求多选（最多5项）
    func_weights = [0.32, 0.30, 0.25, 0.20, 0.18, 0.12, 0.10, 0.08, 0.15, 0.06, 0.02]
    # 生活费低的更关注预算推荐
    if lc_level <= 1:
        func_weights[0] = 0.45
        func_weights[1] = 0.35
    # 旅游专业更关注小众目的地
    if is_tourism_major:
        func_weights[2] = 0.40
    record["最希望的功能(多选)"] = multi_select(FUNCTIONS, 2, 5, func_weights)

    # 付费意愿
    pay_weights = [0.10, 0.15, 0.12, 0.58, 0.05]
    if lc_level >= 4:
        pay_weights = [0.15, 0.22, 0.18, 0.40, 0.05]
    record["最愿意付费的功能"] = weighted_choice(PAY_WILLING, pay_weights)

    # 使用形式
    form_weights = [0.45, 0.15, 0.20, 0.08, 0.12]
    record["倾向的使用形式"] = weighted_choice(PRODUCT_FORM, form_weights)

    # 内容风格
    style_weights = [0.35, 0.28, 0.15, 0.12, 0.10]
    record["偏好的内容风格"] = weighted_choice(CONTENT_STYLE, style_weights)

    # ===== 开放题 =====
    record["其他未满足需求"] = random.choice(OPEN_ENDED_SAMPLES)
    # 约15%留下联系方式
    record["是否愿意参与访谈(留微信)"] = "愿意-wx_" + ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8)) if random.random() < 0.15 else ""

    # 答题时长（秒），用于质量控制
    record["答题时长(秒)"] = random.randint(80, 320)
    # 提交时间
    record["提交时间"] = f"2026-09-{random.randint(1,10):02d} {random.randint(9,22):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"

    return record


def main():
    records = []
    for i in range(328):
        records.append(generate_one_record(i))

    # 写入CSV
    fieldnames = list(records[0].keys())
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"数据生成完成！共 {len(records)} 条记录")
    print(f"文件路径：{OUTPUT_FILE}")
    print(f"文件大小：{os.path.getsize(OUTPUT_FILE)/1024:.1f} KB")

    # 简单统计验证
    grade_count = {}
    lc_count = {}
    freq_count = {}
    for r in records:
        grade_count[r["年级"]] = grade_count.get(r["年级"], 0) + 1
        lc_count[r["月可支配生活费"]] = lc_count.get(r["月可支配生活费"], 0) + 1
        freq_count[r["半年短途出行次数"]] = freq_count.get(r["半年短途出行次数"], 0) + 1

    print("\n=== 样本分布验证 ===")
    print("年级分布：", {k: f"{v}人({v/328*100:.1f}%)" for k, v in sorted(grade_count.items(), key=lambda x: GRADES.index(x[0]))})
    print("生活费分布：", {k: f"{v}人({v/328*100:.1f}%)" for k, v in sorted(lc_count.items(), key=lambda x: LIVING_COSTS.index(x[0]))})
    print("出行频率分布：", {k: f"{v}人({v/328*100:.1f}%)" for k, v in sorted(freq_count.items(), key=lambda x: TRIP_FREQS.index(x[0]))})


if __name__ == "__main__":
    main()
