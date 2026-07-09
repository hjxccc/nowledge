# 间隔复训 · loop engineering（引擎驱动）

> 理论：遗忘曲线(Ebbinghaus) + 间隔效应(Cepeda 2006)。**忘是正常的**，靠到期回考捡回来。
> 这一件由 `scripts/review.py` 真跑，不是让你自觉——你的"洞"落在 `progress.json`，到期把题推回来考。

## 怎么用（每天/每几天一次）

```bash
# 看今天有没有到期要复训的题（只给题、不给答案，强制自己先答）
python ../../scripts/review.py due --file progress.json

# 合上材料答完，去 answer_ref 对照，然后打分：
python ../../scripts/review.py grade --file progress.json --id 2 --pass   # 答对 → 间隔拉长(1→3→7→16→35天)
python ../../scripts/review.py grade --file progress.json --id 2 --fail --note "还是漏了X"  # 答错 → 打回从头，记下新的洞

# 看整体进度（进度条 = 掌握程度）
python ../../scripts/review.py stats --file progress.json
```

## 现在队列里有什么

3 道 checkpoint 题已入队（见 `progress.json`），首次回考在录入次日。答对一次前进一级，答错归零重来——**直到进度条满级 ▰▰▰▰▰ 才算真记住**。快变量层过 1–2 个月重跑 `ground.py` 刷新。

## 想要它主动提醒你（可选）

review.py 是"你来问它"。要"它到点来找你"，在 Claude Code 里挂个定时：
> "每天上午用 review.py due 检查 loop-engineering-nowledge 有没有到期复训，有就把题推给我。"
> （Claude 用 Cron / ScheduleWakeup 落地——到期主动把你的洞推回来考。）
