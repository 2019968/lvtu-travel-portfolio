-- ============================================================
-- 查询 2：困扰 × 功能 的共现分析 ★ 本项目 SQL 的核心
--
-- 业务问题：
--   选了「攻略信息太分散」这个困扰的人，是不是更想要「按预算推荐」？
--   —— 这才是「需求池」里「关联痛点」那一列的**真实依据**，
--      而不是我凭印象写上去的。
--
-- 为什么这道题非用 SQL 不可（面试重点）：
--   困扰（Q18）和功能（Q20）**都是多选题**，各自挤在一个单元格里。
--   在 Excel 里做这个关联，要先把两列都分列拆开、再拉辅助列、
--   再想办法做笛卡尔匹配 —— 又长又容易错。
--   在 SQL 里，因为已经拆成「一人一选项一行」，
--   这就是**同一张表自己关联自己**（self join），一段话就清楚。
--
-- 用到的 SQL 知识点：
--   · 自关联（self join）—— answer_choice 关联自己
--   · 交集条件         —— 同一 respondent_id 同时选了困扰和功能
--   · 条件聚合         —— 用「选了该困扰的总人数」做分母算占比
-- ============================================================

-- ------------------------------------------------------------
-- 2-A：每个困扰 → 最相关的功能（Top 3）
-- ------------------------------------------------------------
WITH pain AS (          -- 每个困扰的总选择人数（分母）
    SELECT option_text AS pain_text, COUNT(*) AS pain_total
    FROM answer_choice
    WHERE question_id = 'Q18'
    GROUP BY option_text
),
pair AS (               -- 困扰与功能的共现次数
    SELECT p.option_text AS pain_text,
           f.option_text AS func_text,
           COUNT(*)      AS together
    FROM answer_choice p
    JOIN answer_choice f
      ON f.respondent_id = p.respondent_id    -- ★ 同一个人
     AND f.question_id   = 'Q20'
    WHERE p.question_id = 'Q18'
    GROUP BY p.option_text, f.option_text
),
ranked AS (
    SELECT
        pair.pain_text                                        AS 困扰,
        pair.func_text                                        AS 相关功能,
        pair.together                                         AS 同时选择人数,
        pain.pain_total                                       AS 有该困扰人数,
        ROUND(pair.together * 100.0 / pain.pain_total, 1)     AS 该困扰人群中选择率,
        ROW_NUMBER() OVER (PARTITION BY pair.pain_text
                           ORDER BY pair.together DESC)       AS 组内排名
    FROM pair
    JOIN pain ON pain.pain_text = pair.pain_text
)
SELECT 困扰, 相关功能, 同时选择人数, 有该困扰人数, 该困扰人群中选择率, 组内排名
FROM ranked
WHERE 组内排名 <= 3
ORDER BY 有该困扰人数 DESC, 组内排名;

-- ------------------------------------------------------------
-- 2-B：反向看 —— 每个功能，是被哪种困扰的人最想要？
--      （用来确认功能与痛点确实对应，而不是巧合）
-- ------------------------------------------------------------
-- WITH func AS (
--     SELECT option_text AS func_text, COUNT(*) AS func_total
--     FROM answer_choice WHERE question_id = 'Q20' GROUP BY option_text
-- ),
-- pair2 AS (
--     SELECT f.option_text AS func_text, p.option_text AS pain_text, COUNT(*) AS together
--     FROM answer_choice f
--     JOIN answer_choice p
--       ON p.respondent_id = f.respondent_id AND p.question_id = 'Q18'
--     WHERE f.question_id = 'Q20'
--     GROUP BY f.option_text, p.option_text
-- )
-- SELECT pair2.func_text AS 功能, pair2.pain_text AS 相关困扰,
--        pair2.together AS 同时选择人数,
--        func.func_total AS 想要该功能人数,
--        ROUND(pair2.together * 100.0 / func.func_total, 1) AS 该功能人群中占比
-- FROM pair2 JOIN func ON func.func_text = pair2.func_text
-- WHERE pair2.together >= 20
-- ORDER BY pair2.func_text, pair2.together DESC;
