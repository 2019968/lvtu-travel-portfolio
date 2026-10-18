-- ============================================================
-- 查询 3：生成需求池（含优先级 / 功能模块 / 关联痛点）
--
-- 业务问题：
--   把「哪些功能多人想要」变成一张能交给开发的需求池表 ——
--   每条需求都要写清：多少人要、属于哪个模块、对应哪个痛点、优先级。
--
-- 用到的 SQL 知识点（面试可讲）：
--   · 三段 CTE 串起来     —— 每一步只做一件事，可读性优先
--   · LEFT JOIN 共现表    —— 有些需求可能没有明显关联痛点，用 LEFT 不丢行
--   · GROUP_CONCAT        —— 把多行痛点拼成一格（相当于 Excel 的 TEXTJOIN）
--   · CASE WHEN           —— 按选择率划分优先级（规则写死在 SQL 里，不是我拍脑袋）
--   · 字符串函数          —— SUBSTR 截断长选项名
-- ============================================================

WITH func_rate AS (          -- 第一步：每个功能的选择率
    SELECT option_text AS func_text,
           COUNT(*)    AS cnt,
           ROUND(COUNT(*) * 100.0 /
                 (SELECT COUNT(DISTINCT respondent_id)
                    FROM answer_choice WHERE question_id = 'Q20'), 1) AS rate
    FROM answer_choice
    WHERE question_id = 'Q20'
      AND option_text <> '其他'          -- 「其他」不进需求池
    GROUP BY option_text
),
pair AS (                    -- 第二步：每个功能关联到的痛点（共现 >= 25 人才算）
    SELECT f.option_text AS func_text,
           p.option_text AS pain_text,
           COUNT(*)      AS together
    FROM answer_choice f
    JOIN answer_choice p
      ON p.respondent_id = f.respondent_id
     AND p.question_id   = 'Q18'
    WHERE f.question_id = 'Q20'
    GROUP BY f.option_text, p.option_text
),
pain_agg AS (                -- 第三步：每个功能只保留共现最多的 3 个痛点，拼成一格
    SELECT func_text,
           GROUP_CONCAT(pain_text, '；') AS pains
    FROM (
        SELECT func_text, pain_text,
               ROW_NUMBER() OVER (PARTITION BY func_text
                                  ORDER BY together DESC, pain_text) AS rn
        FROM pair
        WHERE together >= 25
    )
    WHERE rn <= 3                -- 只留 Top 3，避免一格塞 8 个痛点反而看不出重点
    GROUP BY func_text
)
SELECT
    'REQ-' || SUBSTR('00' || ROW_NUMBER() OVER (ORDER BY fr.cnt DESC), -3)   AS 需求ID,
    fr.func_text                                                             AS 需求名称,
    fr.cnt                                                                   AS 选择人数,
    fr.rate || '%'                                                           AS 用户选择率,
    CASE                                                                     -- 优先级规则
        WHEN fr.rate >= 45 THEN 'P0'
        WHEN fr.rate >= 35 THEN 'P1'
        WHEN fr.rate >= 25 THEN 'P2'
        ELSE 'P3'
    END                                                                      AS 优先级,
    CASE                                       -- ⚠️ 判断顺序有讲究，见下方说明
        WHEN fr.func_text LIKE '%搭子%'   THEN '社交匹配'
        WHEN fr.func_text LIKE '%记账%'   THEN '记账工具'
        WHEN fr.func_text LIKE '%住宿%'   THEN '住宿推荐'
        WHEN fr.func_text LIKE '%美食%'   THEN '美食推荐'
        WHEN fr.func_text LIKE '%避坑%'   THEN '实时提醒'
        WHEN fr.func_text LIKE '%交通%'   THEN '交通指南'
        WHEN fr.func_text LIKE '%模板%'   THEN '行程模板'
        WHEN fr.func_text LIKE '%预算%'   THEN '智能推荐'
        WHEN fr.func_text LIKE '%小众%'   THEN '内容种草'
        WHEN fr.func_text LIKE '%协同%'   THEN '协同编辑'
        ELSE '其他'
    END                                                                      AS 功能模块,
    COALESCE(pa.pains, '—')                                                  AS 关联痛点
FROM func_rate fr
LEFT JOIN pain_agg pa ON pa.func_text = fr.func_text
ORDER BY fr.cnt DESC;

-- ============================================================
-- 优先级规则说明（面试如果被问「优先级怎么定的」）：
--   规则完全由「用户选择率」单一口径决定，写死在 SQL 里：
--      选择率 >= 45%  → P0（近半数人明确要，必须做）
--      35% ~ 45%      → P1（超过三分之一，应该做）
--      25% ~ 35%      → P2（有明确需求，可以排期）
--      < 25%          → P3（需求存在但不紧迫）
--   为什么不用加权打分：
--     「选择率 × 0.6 + 痛点强度 × 0.4」这类权重没有依据，
--     而单一选择率口径虽然简单，但**每个人的数字都能追溯**。
--
-- ⚠️ 功能模块的 CASE WHEN 判断顺序（踩过的坑）：
--   「实时避坑提醒（排队、天气、交通延误）」这个选项文本里**含"交通"二字**，
--   如果把 `LIKE '%交通%'` 写在前面，它会被误归到「交通指南」模块。
--   所以判断顺序必须**从更具体的特征词开始**：
--     搭子/记账/住宿/美食/避坑 → 交通/模板/预算/小众/协同
--   面试如果被问"这段有什么讲究"，这就是一个能答的细节：
--   **多分支条件判断时，具体的模式要排在宽泛的模式前面。**
-- ============================================================
