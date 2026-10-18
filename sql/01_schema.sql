-- ============================================================
-- 大学生轻量化文旅出行问卷 —— 数据库结构
-- 数据库：SQLite
--
-- 设计说明（面试可讲）：
--   问卷原始数据是「一张宽表」——150 个受访者、28 列，
--   多选题挤在一格里用 ┋ 分隔。这种结构没法直接做统计：
--   "多少人选了某个功能"这句话，在宽表里没有对应的字段。
--
--   所以先做一次结构化，拆成 3 张表：
--     respondent     一人一行，放单选类信息（专业/频率/预算/耗时…）
--     answer_choice  一人一选项一行，放多选题的每个选择（★ 核心）
--     dim_option     选项对照表，保证跨答卷的口径统一
--
--   拆完之后，"多少人选了 X" 就变成一句 GROUP BY，
--   "选了 A 困扰的人更想要 B 功能吗" 就变成一次自关联 JOIN。
-- ============================================================

DROP TABLE IF EXISTS respondent;
DROP TABLE IF EXISTS answer_choice;
DROP TABLE IF EXISTS dim_option;

-- ------------------------------------------------------------
-- 1. 受访者表：一人一行
--    只放单选类字段（多选拆到 answer_choice）
-- ------------------------------------------------------------
CREATE TABLE respondent (
    respondent_id INTEGER PRIMARY KEY,   -- 对应问卷星的「序号」
    submit_time   TEXT,                  -- 提交时间
    duration_sec  REAL,                  -- 答题时长（秒）
    ip_region     TEXT,                  -- IP 属地

    q1_role       TEXT,                  -- 身份
    q2_grade      TEXT,                  -- 年级
    q3_major      TEXT,                  -- 专业
    q4_living     TEXT,                  -- 月生活费
    q5_freq       TEXT,                  -- 半年短途出行次数（★ 分层/跳题的依据）
    q7_companion  TEXT,                  -- 通常和谁出行
    q8_budget     TEXT,                  -- 单次预算
    q9_top_cost   TEXT,                  -- 预算占比最大项
    q10_ahead     TEXT,                  -- 提前多久规划
    q12_hours     TEXT,                  -- 做攻略总耗时（★ 行为事实题）
    q13_apps      TEXT,                  -- 打开过几个 App（★ 行为事实题）
    q14_giveup    TEXT,                  -- 是否因嫌麻烦放弃过出行（★ 核心结论）
    q15_prefer    TEXT,                  -- 自己做 vs 用现成的
    q16_tool      TEXT,                  -- 是否用过行程规划工具
    q19_worst     TEXT,                  -- 最严重的一项困扰
    q21_pay       TEXT,                  -- 付费意愿
    q22_form      TEXT,                  -- 偏好的产品形态
    q23_style     TEXT,                  -- 偏好内容风格
    q24_open      TEXT                   -- 开放题原话
);

-- ------------------------------------------------------------
-- 2. 答案选择表：一人一选项一行（多选拆开后的结果）
--    这是最关键的一张表 —— 有了它才能做频次统计和共现分析
-- ------------------------------------------------------------
CREATE TABLE answer_choice (
    respondent_id INTEGER NOT NULL,
    question_id   TEXT    NOT NULL,   -- 'Q6' / 'Q11' / 'Q17' / 'Q18' / 'Q20'
    option_text   TEXT    NOT NULL,   -- 选项文本（已按选项表归一）
    source        TEXT,               -- 'multi' 多选 / 'single' 单选
    PRIMARY KEY (respondent_id, question_id, option_text),
    FOREIGN KEY (respondent_id) REFERENCES respondent(respondent_id)
);

-- ------------------------------------------------------------
-- 3. 选项对照表：问卷每个选项的规范写法
--    作用：同一选项在不同答卷里写法可能有细微差别，
--          用这张表归一后才能跨答卷计数
-- ------------------------------------------------------------
CREATE TABLE dim_option (
    question_id TEXT NOT NULL,
    option_no   TEXT NOT NULL,        -- 'A' / 'B' / 'C' …
    option_text TEXT NOT NULL,        -- 规范选项文本
    PRIMARY KEY (question_id, option_no)
);

CREATE INDEX idx_ac_qid  ON answer_choice(question_id);
CREATE INDEX idx_ac_opt  ON answer_choice(option_text);
CREATE INDEX idx_resp_freq ON respondent(q5_freq);
