-- ============================================================
-- 查询 4：按出行频率 / 预算 看需求差异
--
-- 业务问题：
--   常出行的人和偶尔出行的人，想要的东西一样吗？
--   如果不一样，就说明功能要分优先级批次做，而不是一锅端。
--
-- 用到的 SQL 知识点（面试可讲）：
--   · 两个 JOIN          —— answer_choice 同时关联 respondent（拿频率）和 dim_option
--   · CASE WHEN 打标签    —— 把频次/预算区间映射成可分组的分层
--   · GROUP BY 多列       —— 按「分层 × 功能」交叉
--   · 条件聚合 COUNT(DISTINCT) —— 每个分层里有多少人选了该功能
-- ============================================================

-- ------------------------------------------------------------
-- 4-A：不同出行频率的人，最想要的功能各是什么？
-- ------------------------------------------------------------
WITH labeled AS (
    SELECT
        r.respondent_id,
        CASE                                   -- 频率 → 分层
            WHEN r.q5_freq LIKE '0%'         THEN '0次（未出行）'
            WHEN r.q5_freq LIKE '1–2%'       THEN '低频(1-2次)'
            WHEN r.q5_freq LIKE '3–4%'       THEN '中频(3-4次)'
            WHEN r.q5_freq LIKE '5–6%'       THEN '中高频(5-6次)'
            WHEN r.q5_freq LIKE '7%'         THEN '高频(7次+)'
            ELSE '未识别'
        END AS freq_tier,
        ac.option_text AS func_text
    FROM respondent r
    JOIN answer_choice ac
      ON ac.respondent_id = r.respondent_id
     AND ac.question_id   = 'Q20'
),
grp AS (
    SELECT freq_tier, func_text,
           COUNT(DISTINCT respondent_id) AS sel_cnt
    FROM labeled
    WHERE freq_tier <> '未识别'
    GROUP BY freq_tier, func_text
),
den AS (                                       -- 每个分层有多少人（分母）
    SELECT freq_tier, COUNT(*) AS tier_total
    FROM (SELECT DISTINCT respondent_id, freq_tier FROM labeled) GROUP BY freq_tier
)
SELECT
    g.freq_tier                                  AS 出行频率分层,
    d.tier_total                                 AS 该层人数,
    g.func_text                                  AS 想要的功能,
    g.sel_cnt                                    AS 选择人数,
    ROUND(g.sel_cnt * 100.0 / d.tier_total, 1)   AS 层内选择率
FROM grp g
JOIN den d ON d.freq_tier = g.freq_tier
WHERE g.sel_cnt >= 5                           -- 少于 5 人的不展示，避免小样本误导
ORDER BY d.tier_total DESC, g.sel_cnt DESC;

-- ------------------------------------------------------------
-- 4-B：核心结论 —— 有多少人因「嫌规划麻烦」而放弃过出行？
--      （这条是整个项目的立论依据，用一条 SQL 直接算出来）
-- ------------------------------------------------------------
SELECT
    CASE
        WHEN q14_giveup LIKE '有过%' THEN '有过（被麻烦劝退过）'
        WHEN q14_giveup = '没有过'   THEN '没有过'
        ELSE '记不清了'
    END                                                  AS 分组,
    COUNT(*)                                             AS 人数,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM respondent), 1) AS 占全样本比例,
    ROUND(COUNT(*) * 100.0 /
          (SELECT COUNT(*) FROM respondent
            WHERE q14_giveup LIKE '有过%' OR q14_giveup = '没有过'), 1) AS 剔除记不清后占比
FROM respondent
GROUP BY 分组
ORDER BY 人数 DESC;
