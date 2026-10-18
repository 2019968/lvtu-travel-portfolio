-- ============================================================
-- 查询 1：各功能需求的选择率与排名
--
-- 业务问题：150 个学生里，每个功能有多少人想要？谁排第一？
--
-- 用到的 SQL 知识点（面试可讲）：
--   · JOIN          —— answer_choice 关联 dim_option，用规范选项文本
--   · GROUP BY      —— 按选项分组计数
--   · 子查询         —— 分母（本题实际作答人数）
--   · ROW_NUMBER()  —— 窗口函数做排名
--   · ROUND()       —— 百分比保留 1 位
--
-- ⚠️ 分母为什么不用 150：
--   Q5 选「0 次」的人跳过了 Q6–Q13。用总样本 150 做分母会低估这些题的占比。
--   所以分母取「本题实际有选择记录的人数」。
-- ============================================================

SELECT
    ac.option_text                                       AS 功能,
    COUNT(*)                                             AS 选择人数,
    (SELECT COUNT(DISTINCT respondent_id)
       FROM answer_choice WHERE question_id = 'Q20')     AS 本题作答人数,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(DISTINCT respondent_id)
           FROM answer_choice WHERE question_id = 'Q20'), 1) AS 选择率百分比,
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC)           AS 排名
FROM answer_choice ac
JOIN dim_option d
  ON d.question_id = ac.question_id
 AND d.option_text = ac.option_text
WHERE ac.question_id = 'Q20'
GROUP BY ac.option_text
ORDER BY 选择人数 DESC;
