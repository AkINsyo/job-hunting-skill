# SKILL 书写指南

> 基于 Anthropic Claude、Vercel、OpenAI 及 GitHub 高星项目的技能结构调研
> 调研日期：2026-06-04

---

## 目录

- [调研概述](#调研概述)
- [一、主流平台技能架构对比](#一主流平台技能架构对比)
- [二、SKILL.md 标准结构规范](#二skillmd-标准结构规范)
- [三、YAML Frontmatter 规范](#三yaml-frontmatter-规范)
- [四、内容编写原则](#四内容编写原则)
- [五、驱动方式详解](#五驱动方式详解)
- [六、文件组织结构](#六文件组织结构)
- [七、实战模板](#七实战模板)
- [八、反模式与避坑指南](#八反模式与避坑指南)
- [九、参考资源](#九参考资源)

---

## 调研概述

本次调研覆盖以下平台和项目：

| 来源 | 代表项目 | Stars | 特点 |
|------|---------|-------|------|
| **Anthropic 官方** | anthropics/claude-plugins-official | 29K+ | Claude Code 插件生态 |
| **Vercel 官方** | vercel-labs/agent-skills | 27K+ | 生产级工程技能 |
| **社区精选** | addyosmani/agent-skills | 48K+ | 完整开发生命周期 |
| **提示词库** | f/prompts.chat | 163K+ | 最大的开源提示词库 |
| **技能目录** | VoltAgent/awesome-agent-skills | 24K+ | 1000+ 技能集合 |

---

## 一、主流平台技能架构对比

### 1.1 Anthropic Claude Plugins

**目录结构：**
```
plugins/
  plugin-name/
    .claude-plugin/
      plugin.json          # 插件元数据
    commands/
      command-name.md      # 斜杠命令定义
    README.md              # 详细文档
```

**plugin.json 格式：**
```json
{
  "name": "code-review",
  "description": "Automated code review for pull requests",
  "author": {
    "name": "Anthropic",
    "email": "support@anthropic.com"
  }
}
```

**特点：**
- 使用斜杠命令触发（如 `/code-review`）
- 支持多 Agent 并行协作
- 基于置信度评分过滤误报
- 强调 CLAUDE.md 规范集成

---

### 1.2 Vercel Agent Skills

**目录结构：**
```
skills/
  skill-name/
    SKILL.md               # 技能定义（必需）
    metadata.json          # 元数据（可选）
    rules/                 # 规则文件（可选）
      rule-name.md
```

**SKILL.md 格式：**
```markdown
---
name: vercel-react-best-practices
description: React and Next.js performance optimization guidelines...
metadata:
  author: vercel
  version: "1.0.0"
---

# 技能标题

## When to Apply
...

## Rule Categories by Priority
...
```

**metadata.json 格式：**
```json
{
  "version": "1.0.0",
  "organization": "Vercel Engineering",
  "date": "January 2026",
  "abstract": "...",
  "references": ["https://react.dev", "..."]
}
```

**特点：**
- 按优先级分类规则（CRITICAL → LOW）
- 提供 Quick Reference 快速查阅
- 丰富的代码示例（正确 vs 错误）
- 支持 ZIP 打包分发

---

### 1.3 Addy Osmani Agent Skills

**目录结构：**
```
skills/
  skill-name/
    SKILL.md               # 技能定义（必需）
    scripts/               # 辅助脚本（可选）
    supporting-file.md     # 补充材料（可选）
```

**SKILL.md 标准结构：**
```markdown
---
name: skill-name-with-hyphens
description: Guides agents through [task/workflow]. Use when [trigger conditions].
---

# Skill Title

## Overview
1-2 句话说明技能用途

## When to Use
- 触发条件列表
- 不适用场景

## Core Process
详细的工作流程步骤

## Common Rationalizations
| 借口 | 现实 |
|------|------|
| Agent 常用的跳过理由 | 为什么这个理由不成立 |

## Red Flags
- 违规行为的信号

## Verification
- [ ] 完成检查清单
```

**核心原则：**
1. **Process over knowledge** - 技能是工作流，不是参考文档
2. **Specific over general** - "运行 `npm test`" 优于 "验证测试"
3. **Evidence over assumption** - 每个验证项需要证据
4. **Anti-rationalization** - 防止 Agent 跳过步骤
5. **Token-conscious** - 每个部分必须证明其价值

---

### 1.4 OpenAI GPTs

**配置结构：**
```json
{
  "name": "Skill Name",
  "description": "一句话描述",
  "instructions": "详细的系统指令...",
  "conversation_starters": ["开场白1", "开场白2"],
  "capabilities": {
    "web_browsing": true,
    "code_interpreter": true,
    "image_generation": false
  }
}
```

**Actions（API 集成）：**
```yaml
openapi: 3.0.0
info:
  title: Skill API
  version: 1.0.0
paths:
  /endpoint:
    get:
      summary: 描述
      operationId: operationName
      parameters: [...]
```

**特点：**
- JSON 配置驱动
- 支持外部 API 集成（Actions）
- 内置能力开关（代码解释器、DALL·E 等）
- 对话启动器（Conversation Starters）

---

### 1.5 对比总结

| 维度 | Anthropic | Vercel | Addy Osmani | OpenAI |
|------|-----------|--------|-------------|--------|
| **文件格式** | JSON + MD | YAML + MD | YAML + MD | JSON |
| **核心文件** | plugin.json | SKILL.md | SKILL.md | instructions |
| **触发方式** | 斜杠命令 | 自动检测 | 自动/命令 | 对话触发 |
| **扩展性** | 插件系统 | 规则文件 | 脚本目录 | Actions API |
| **适用场景** | Claude Code | 通用 Agent | 通用 Agent | ChatGPT |

---

## 二、SKILL.md 标准结构规范

基于调研，推荐以下标准结构：

```markdown
---
name: skill-name
description: [做什么]. Use when [何时用].
---

# 技能标题

> 一句话概述（可选）

## Overview / 概述

简要说明技能的目的和价值。

## When to Use / 使用场景

### 适用场景
- ✅ 场景 1
- ✅ 场景 2

### 不适用场景
- ❌ 场景 A
- ❌ 场景 B

## Core Process / 核心流程

### 阶段 1：[阶段名称]

**触发条件：** 何时进入此阶段

**执行步骤：**
1. 步骤 1
2. 步骤 2
3. 步骤 3

**输出格式：**
```markdown
期望的输出格式
```

**完成条件：**
- [ ] 条件 1
- [ ] 条件 2

### 阶段 2：[阶段名称]
...

## Rules / 规则

### 必须遵守
- ✅ 规则 1
- ✅ 规则 2

### 禁止事项
- ❌ 禁止 1
- ❌ 禁止 2

## Common Rationalizations / 常见借口

| 借口 | 现实 | 应对 |
|------|------|------|
| "这个太简单了，跳过吧" | 简单任务也容易出错 | 坚持流程 |
| "我之后再补测试" | 没有测试就没有信心 | 先写测试 |

## Red Flags / 危险信号

- 🚩 信号 1：说明
- 🚩 信号 2：说明

## Verification / 验证清单

完成技能流程后，确认：
- [ ] 检查项 1（证据：xxx）
- [ ] 检查项 2（证据：xxx）

## Examples / 示例（可选）

### 示例 1：[场景名称]

**输入：**
> 用户输入示例

**输出：**
> 期望输出示例

## References / 参考（可选）

- [链接 1](url)
- [链接 2](url)

## Changelog / 变更日志（可选）

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-06-04 | 初始版本 |
```

---

## 三、YAML Frontmatter 规范

### 3.1 必需字段

```yaml
---
name: skill-name-with-hyphens
description: [做什么]. Use when [何时用].
---
```

**name 规则：**
- 小写字母
- 连字符分隔
- 必须与目录名匹配
- 示例：`code-review-and-quality`

**description 规则：**
- 以第三人称说明技能做什么
- 包含一个或多个 "Use when" 触发条件
- 最大 1024 字符
- 不要包含工作流步骤（Agent 会读取摘要而非完整技能）

**好的描述：**
```yaml
description: Guides agents through multi-axis code review. Use when reviewing code before merging, after completing features, or when evaluating code quality.
```

**差的描述：**
```yaml
description: Code review tool
# 问题：太简短，没有触发条件
```

**差的描述：**
```yaml
description: First check the code, then run tests, then review for security issues, then...
# 问题：包含工作流步骤
```

### 3.2 可选字段

```yaml
---
name: skill-name
description: ...
license: MIT
metadata:
  author: author-name
  version: "1.0.0"
  date: "2026-06"
  organization: "Organization Name"
  tags: ["react", "performance", "nextjs"]
  model_compatibility: ["claude-3.5-sonnet", "gpt-4o"]
---
```

---

## 四、内容编写原则

### 4.1 流程优于知识

**✅ 好的写法：**
```markdown
1. 运行 `npm test` 确保所有测试通过
2. 如果测试失败，查看错误信息并修复
3. 修复后重新运行测试直到全部通过
```

**❌ 差的写法：**
```markdown
测试是代码质量的重要保障，应该确保测试覆盖率达到 80% 以上...
```

**原因：** 技能是工作流，不是教程。Agent 需要明确的步骤，不是知识讲解。

---

### 4.2 具体优于笼统

**✅ 好的写法：**
```markdown
运行以下命令检查 TypeScript 类型：
\`\`\`bash
npx tsc --noEmit
\`\`\`
```

**❌ 差的写法：**
```markdown
检查代码是否有类型错误。
```

**原因：** 具体的命令让 Agent 可以直接执行，笼统的描述会导致不确定性。

---

### 4.3 证据优于假设

**✅ 好的写法：**
```markdown
- [ ] 所有测试通过（证据：粘贴 `npm test` 输出）
- [ ] 无 TypeScript 错误（证据：粘贴 `tsc --noEmit` 输出）
```

**❌ 差的写法：**
```markdown
- [ ] 代码质量良好
- [ ] 没有明显问题
```

**原因：** 可验证的证据防止 Agent 自我欺骗。

---

### 4.4 反合理化

Agent 倾向于找借口跳过步骤。在技能中预设反驳：

```markdown
## Common Rationalizations

| Agent 的借口 | 现实 | 应对 |
|-------------|------|------|
| "这个改动很小，不需要测试" | 小改动也可能引入 bug | 所有改动都需要测试 |
| "我确信这是对的" | 确信不等于正确 | 运行测试验证 |
| "测试环境有问题" | 环境问题也需要解决 | 记录问题并寻找解决方案 |
```

---

### 4.5 Token 意识

每个部分必须证明其价值。如果删除某部分不会改变 Agent 行为，就删除它。

**检查清单：**
- [ ] 这个部分会影响 Agent 的决策吗？
- [ ] 这个信息可以放到补充文件中吗？
- [ ] 这个例子足够典型吗？

---

## 五、驱动方式详解

### 5.1 Prompt-driven（提示驱动）

**原理：** 通过自然语言指令控制行为

**适用场景：**
- 通用对话任务
- 创意写作
- 简单问答

**示例：**
```markdown
请帮我写一封邮件给客户，语气要专业但友好。
```

**优点：** 灵活、易于编写
**缺点：** 行为不稳定、难以精确控制

---

### 5.2 Tool-driven（工具驱动）

**原理：** 定义可调用的工具/函数

**适用场景：**
- 调用外部 API
- 执行代码
- 访问文件系统

**示例：**
```yaml
tools:
  - name: "web_search"
    description: "搜索网页"
    parameters:
      query:
        type: string
        description: "搜索关键词"
```

**优点：** 可扩展、可复用
**缺点：** 需要额外实现

---

### 5.3 Flow-driven（流程驱动）

**原理：** 定义明确的状态机和转换规则

**适用场景：**
- 多步骤任务
- 严格顺序执行
- 条件分支

**示例：**
```yaml
workflow:
  start: "collect_info"
  
  states:
    collect_info:
      prompt: "请提供以下信息..."
      transitions:
        - on: "info_complete"
          goto: "analyze"
    
    analyze:
      tool: "analyze_data"
      transitions:
        - on: "success"
          goto: "report"
```

**优点：** 行为可预测、易于测试
**缺点：** 灵活性低、编写复杂

---

### 5.4 Agent-driven（代理驱动）

**原理：** 赋予 Agent 自主决策能力

**适用场景：**
- 复杂探索性任务
- 动态调整策略
- 多工具组合

**示例：**
```yaml
agent:
  goal: "完成用户请求的任务"
  
  loop:
    - think: "分析当前状态"
    - act: "执行动作"
    - observe: "观察结果"
    - reflect: "评估是否达成目标"
  
  termination:
    - goal_achieved
    - max_iterations: 10
```

**优点：** 灵活、能处理复杂情况
**缺点：** 成本高、行为不可预测

---

### 5.5 混合驱动（推荐）

实际应用中通常采用混合方式：

```markdown
# 技能：代码审查助手

## 工作流程 (Flow-driven)
1. 收集代码 → 2. 静态分析 → 3. AI 审查 → 4. 生成报告

## 阶段 3：AI 审查 (Prompt-driven)
请从以下维度审查代码：
- 安全性
- 性能
- 可读性

## 工具 (Tool-driven)
- lint_code: 执行静态检查
- run_tests: 运行测试用例
```

---

## 六、文件组织结构

### 6.1 最小结构（必需）

```
skill-name/
  SKILL.md
```

### 6.2 标准结构

```
skill-name/
  SKILL.md
  metadata.json          # 元数据
  README.md              # 用户文档
```

### 6.3 完整结构

```
skill-name/
  SKILL.md               # 核心技能定义
  metadata.json          # 元数据
  README.md              # 用户文档
  rules/                 # 规则文件
    rule-1.md
    rule-2.md
  scripts/               # 辅助脚本
    helper.sh
    helper.py
  examples/              # 示例
    example-1.md
    example-2.md
  references/            # 参考资料
    doc-1.md
```

### 6.4 跨技能引用

```markdown
# 在技能中引用其他技能

遵循 `test-driven-development` 技能编写测试。
如果构建失败，使用 `debugging-and-error-recovery` 技能。
```

**原则：** 不要复制内容，引用和链接即可。

---

## 七、实战模板

### 7.1 代码审查技能模板

```markdown
---
name: code-review
description: Conducts multi-axis code review with quality gates. Use before merging any change, after completing features, or when evaluating code quality.
---

# Code Review

## Overview

多维度代码审查，每个变更在合并前都必须经过审查。审查覆盖五个维度：正确性、可读性、架构、安全性和性能。

**审批标准：** 当变更 definitely 改善整体代码健康状况时批准，即使它不完美。完美代码不存在——目标是持续改进。

## When to Use

- 合并任何 PR 或变更前
- 完成功能实现后
- 评估其他 Agent 或模型生成的代码时
- 重构现有代码时
- 任何 bug 修复后

## The Five-Axis Review

### 1. Correctness（正确性）

代码是否做了它声称的事情？

- [ ] 是否匹配规格或任务要求？
- [ ] 边界情况是否处理（null、空值、边界值）？
- [ ] 错误路径是否处理（不只是 happy path）？
- [ ] 是否通过所有测试？测试是否真的测试了正确的东西？

### 2. Readability & Simplicity（可读性）

其他工程师能否无需作者解释就理解这段代码？

- [ ] 名称是否描述性和一致性？
- [ ] 控制流是否直截了当？
- [ ] 代码是否逻辑组织？
- [ ] 能否用更少的行数实现？

### 3. Architecture（架构）

变更是否符合系统设计？

- [ ] 是否遵循现有模式或引入新模式？
- [ ] 是否保持清晰的模块边界？
- [ ] 是否有应该共享的代码重复？

### 4. Security（安全性）

变更是否引入漏洞？

- [ ] 用户输入是否验证和清理？
- [ ] 密钥是否远离代码、日志和版本控制？
- [ ] SQL 查询是否参数化？

### 5. Performance（性能）

变更是否引入性能问题？

- [ ] 是否有 N+1 查询模式？
- [ ] 是否有无界循环或无约束数据获取？
- [ ] 是否有不必要的 UI 重渲染？

## Common Rationalizations

| 借口 | 现实 |
|------|------|
| "代码能运行就行" | 能运行不等于正确 |
| "我之后再优化" | 之后永远不会来 |
| "这是别人的代码" | 代码质量是团队责任 |

## Verification

完成审查后确认：
- [ ] 所有五个维度都已评估
- [ ] 每个问题都有具体位置和建议
- [ ] 优先级已标注（🔴 必须修复 / 🟡 建议改进 / 🟢 可选优化）
```

---

### 7.2 研究助手技能模板

```markdown
---
name: research-assistant
description: Guides agents through systematic research and information synthesis. Use when conducting literature reviews, fact-checking, or gathering information from multiple sources.
---

# Research Assistant

## Overview

系统性研究和信息综合助手。善于提炼关键信息、交叉验证多个来源、结构化呈现发现。

**原则：**
1. 所有信息必须注明来源
2. 区分事实和推测
3. 承认不确定性

## When to Use

- 进行文献综述时
- 事实核查时
- 从多个来源收集信息时
- 需要结构化研究报告时

## Core Process

### Phase 1: Understand the Research Question

**规则：**
- 如果问题模糊，追问澄清
- 如果问题太大，建议拆分
- 确认研究范围和深度

### Phase 2: Information Collection

**策略：**
1. 优先使用权威来源
2. 多角度交叉验证
3. 记录所有来源

**输出格式：**
```markdown
## Information Sources

| # | Source | Type | Credibility | Link |
|---|--------|------|-------------|------|
| 1 | Official Docs | Primary | ⭐⭐⭐⭐⭐ | [link] |
| 2 | Academic Paper | Primary | ⭐⭐⭐⭐⭐ | [link] |
| 3 | Tech Blog | Secondary | ⭐⭐⭐ | [link] |
```

### Phase 3: Analysis & Synthesis

**处理：**
1. 对比不同来源的说法
2. 识别共识和分歧
3. 评估证据强度

### Phase 4: Present Results

**格式：**
```markdown
# Research Report: [Topic]

## Summary
[2-3 sentences summarizing core findings]

## Key Findings
1. **Finding 1**: [Conclusion]
   - Evidence: [Supporting material]
   - Confidence: High/Medium/Low

2. **Finding 2**: ...

## Controversies
- **Controversy 1**: [Different viewpoints]
  - Supporters: ...
  - Opponents: ...

## Limitations
- Data not obtained
- Possible biases

## Suggested Next Steps
- Questions for further research
```

## Common Rationalizations

| 借口 | 现实 |
|------|------|
| "这个来源看起来可靠" | 看起来可靠不等于可靠 |
| "我找不到反对意见" | 找不到不等于不存在 |
| "这个信息足够了" | 足够需要明确定义 |

## Verification

完成研究后确认：
- [ ] 所有来源已记录并评估可信度
- [ ] 事实和推测已区分
- [ ] 不确定性已承认
- [ ] 多角度已考虑
```

---

## 八、反模式与避坑指南

### ❌ 反模式 1：指令模糊

```markdown
# 差的写法
帮助用户解决问题，给出好的建议。
```

**问题：** 没有定义什么是"好的建议"，行为完全随机。

**修正：**
```markdown
# 好的写法
每个建议必须包含：
1. **问题描述**：具体是什么问题
2. **解决方案**：如何解决
3. **实施步骤**：具体怎么做
4. **预期效果**：做完后会怎样
```

---

### ❌ 反模式 2：缺少边界

```markdown
# 差的写法
你可以处理任何文件格式。
```

**问题：** 没有定义不能处理的情况，会导致意外行为。

**修正：**
```markdown
# 好的写法
## 支持的格式
- ✅ PDF、DOCX、MD、TXT
- ❌ 加密 PDF、损坏文件、二进制文件

## 不支持时的处理
1. 明确告知用户不支持
2. 建议转换为支持的格式
3. 不要尝试猜测内容
```

---

### ❌ 反模式 3：过度承诺

```markdown
# 差的写法
我能完美解决你的所有编程问题，保证代码没有 bug。
```

**问题：** 不切实际的承诺会导致用户失望。

**修正：**
```markdown
# 好的写法
## 能力范围
- ✅ 代码审查和优化建议
- ✅ 常见 bug 检测
- ❌ 保证代码无 bug（这是不现实的）
- ❌ 运行时错误检测（需要实际执行）
```

---

### ❌ 反模式 4：忽略用户体验

```markdown
# 差的写法
输入数据后等待处理。
```

**问题：** 没有进度反馈，用户不知道发生了什么。

**修正：**
```markdown
# 好的写法
## 进度反馈

处理耗时任务时，主动告知进度：

> 正在分析代码，预计需要 30 秒...

> 已完成 3/5 个文件，继续处理中...

> 分析完成！发现 12 个潜在问题。
```

---

### ❌ 反模式 5：硬编码假设

```markdown
# 差的写法
用户使用 VS Code，所以快捷键是 Ctrl+Shift+P。
```

**问题：** 假设用户的环境，忽略了其他可能性。

**修正：**
```markdown
# 好的写法
## 编辑器适配

根据用户使用的编辑器提供对应指令：

| 编辑器 | 命令面板快捷键 |
|--------|---------------|
| VS Code | Ctrl+Shift+P / Cmd+Shift+P |
| JetBrains | Ctrl+Shift+A / Cmd+Shift+A |
| Vim | :CommandName |
```

---

### ❌ 反模式 6：过度使用 Token

```markdown
# 差的写法
[500 行的背景知识，Agent 根本不会读完]
```

**问题：** 浪费 Token，Agent 可能跳过重要部分。

**修正：**
```markdown
# 好的写法
## Quick Reference

[精简的核心规则，10-20 行]

## Detailed Guide

[详见 rules/detailed-guide.md]
```

---

## 九、参考资源

### 官方仓库

| 仓库 | Stars | 链接 |
|------|-------|------|
| addyosmani/agent-skills | 48K+ | https://github.com/addyosmani/agent-skills |
| vercel-labs/agent-skills | 27K+ | https://github.com/vercel-labs/agent-skills |
| anthropics/claude-plugins-official | 29K+ | https://github.com/anthropics/claude-plugins-official |
| f/prompts.chat | 163K+ | https://github.com/f/prompts.chat |
| VoltAgent/awesome-agent-skills | 24K+ | https://github.com/VoltAgent/awesome-agent-skills |

### 文档

| 资源 | 链接 |
|------|------|
| Agent Skills 规范 | https://agentskills.io |
| Skills 目录 | https://skills.sh |
| Claude Code 文档 | https://docs.anthropic.com/claude-code |
| OpenAI GPTs 文档 | https://platform.openai.com/docs/guides/gpts |

### 学术论文

1. **Chain-of-Thought Prompting** (Wei et al., 2022)
2. **ReAct: Synergizing Reasoning and Acting** (Yao et al., 2022)
3. **Constitutional AI** (Anthropic, 2022)

---

## 附录：快速检查清单

在发布技能前，检查以下要点：

### 结构完整性
- [ ] 有清晰的角色定义
- [ ] 有明确的工作流程
- [ ] 有输出格式规范
- [ ] 有边界处理说明
- [ ] 有禁止事项列表

### 内容质量
- [ ] 指令具体、可执行
- [ ] 没有模糊的表述
- [ ] 考虑了异常情况
- [ ] 提供了示例（如有必要）

### 用户体验
- [ ] 进度反馈机制
- [ ] 错误提示友好
- [ ] 输出格式清晰
- [ ] 支持中断和恢复

### 可维护性
- [ ] 模块化组织
- [ ] 版本号管理
- [ ] 变更日志记录
- [ ] 测试用例覆盖

### Token 效率
- [ ] 每个部分都有明确价值
- [ ] 详细内容放在补充文件
- [ ] 提供 Quick Reference
- [ ] 避免重复内容

---

> **文档版本**：1.0.0
> **最后更新**：2026-06-04
> **调研来源**：GitHub API、官方文档、社区最佳实践
