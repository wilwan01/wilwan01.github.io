# 国内GPU与AI架构人物：八位优先研究

审阅日期：2026-10-13。

这是人物研究稿，不是新增人物已入库或网站已发布的记录。[结构化来源、逐人缺口与贡献草稿](2026-10-13-china-gpu-priority8.json)与本文同目录。

## 本轮结果

八位均已建立独立研究记录。其中六位已读到两项不同技术作品的机制正文；彭莉仍缺第二项独立技术作品，刘少礼的两篇论文尚未成功读取原文。所有记录仍需最终身份交叉复核、完整目录去重及现有站点结构校验，不能把“正文已读”理解为“全部入库条件已通过”。

| 人物 | 公司关联 | 贡献卡主线 | 本轮技术证据状态 |
|---|---|---|---|
| 彭莉 / Li Peng | 沐曦 | GPU共享矩阵数据的请求聚合与广播 | 一项机制正文已读；缺第二项不同作品 |
| 杨建 / Jian Yang | 沐曦 | GPU软件生态与存储系统协同 | 两项正文已读；补历史署名身份交叉核对及软件栈作品 |
| 洪洲 / Zhou Hong | 壁仞 | 图像块压缩、寄存器邻域数据复用 | 两项正文已读；明确S3/FutureWei历史作品归属 |
| 刘彦 / Yan Liu | 燧原 | 超越函数计算控制、芯片级互联集群 | 两项正文已读；首席架构师职称只按历史资料处理 |
| 刘少礼 / Shaoli Liu | 寒武纪 | 神经网络ISA、稀疏加速器 | 出版信息与摘要已定位；原文机制待读 |
| 吕坚平 / Jianping Lu | 天数智芯 | 可微硬件反馈、混合光栅化流水线 | 两项正文已读；不推断量产采用 |
| 王平 / Ping Wang | 登临 | 张量寻址解耦、异构单元任务队列 | 两项正文已读；同名与中英文署名交叉复核 |
| 谢威宇 / Weiyu Xie | 趋境科技 | CPU/GPU混合推理、面向微架构的图查询 | 两项论文的署名、机制正文及相关页面图像已核读 |

## 技术来源入口与归属边界

### 彭莉与杨建：共享作品不能成为两项独立证据

[US11609785B2](https://patents.google.com/patent/US11609785B2/en)列Li Peng、Jian Yang、Chi Tang为共同发明人。该作品可以分别支持两位共同贡献者，但对任意一人的“两项作品”门槛只计一次；同族中文文本同样不能再计一次。彭莉第二项技术作品未补齐，不用履历、获奖或访谈简介凑数。

杨建另有MetaX申请的[US12614243B2](https://patents.google.com/patent/US12614243B2/en)，讨论独立显存扩展控制器与跨芯片访问。[上海科技大学2024年讲座](https://sist.shanghaitech.edu.cn/sist_en/2024/0401/c11304a1093468/page.htm)可作软件生态职责和历史经历锚点，但讲座摘要本身不计作已读技术正文。

### 洪洲：历史作品不是壁仞产品说明书

技术入口为S3时期的[US5956431A](https://patents.google.com/patent/US5956431A/en)和FutureWei时期的[US10726516B2](https://patents.google.com/patent/US10726516B2/en)。两项均有共同署名。与当前身份对应的[2026年9月学院活动](https://www.sisi.edu.cn/2026/0923/c17042a1127608/page.htm)确认壁仞联合创始人和CTO身份，不能代替对两段历史任职时间的复核。

### 刘彦：用同一机构的中文署名锁定技术作品

采用燧原申请的[CN109271134A](https://patents.google.com/patent/CN109271134A/zh)与[CN109739802B](https://patents.google.com/patent/CN109739802B/zh)。分别涉及函数迭代计算控制和训练集群连接。其他机构的同名刘彦不并入此人物；不依据专利申请人的今天名称推定今天的个人职务。

### 刘少礼：确定研究方向，但不伪装完成原文核验

作品入口为[Cambricon ISA / ISCA 2016](https://dl.acm.org/doi/10.1145/3007787.3001179)与[Cambricon-X / MICRO 2016](https://dl.acm.org/doi/10.5555/3195638.3195662)。本轮ACM及IEEE PDF读取未成功，因此结构化记录中的mechanismBody为false；未根据二手笔记填写指令编码、寄存器规模或稀疏索引实现。

### 吕坚平：区分专利方案、图形技术与已量产特性

采用[CN115936966A](https://patents.google.com/patent/CN115936966A/zh)和[CN117456070A](https://patents.google.com/patent/CN117456070A/zh)。第一项讨论硬件节点的可微反馈，第二项将专用光栅化覆盖计算与线程执行结合。后者不是完全软件光栅化；也不能凭分析H100的文章声称本人参与了H100设计。

### 王平：具体机制比“GPU+”标签更适合人物卡

采用[CN115658146B](https://patents.google.com/patent/CN115658146B/zh)和[US11789895B2](https://patents.google.com/patent/US11789895B2/en)。研究卡分别围绕张量寻址/执行分离与异构单元任务队列展开。保持共同发明人归属，并在最终人物审计中将常见姓名与登临机构信息联用。

### 谢威宇：系统软件分区，不放入GPU芯片首席架构师名单

已核[个人履历](https://www.xieweiyu.me/about)、[KTransformers原文](https://madsys.cs.tsinghua.edu.cn/publication/ktransformers-unleashing-the-full-potential-of-cpu/gpu-hybrid-inference-for-moe-models/SOSP25-chen.pdf)与[VertexSurge原文](https://madsys.cs.tsinghua.edu.cn/publication/vertexsurge-variable-length-graph-pattern-match-on-billion-edge-graphs/ASPLOS24-Xie.pdf)。KTransformers首页明确前三位作者同等贡献，其中包括Weiyu Xie；VertexSurge列其为第一作者。

贡献卡必须保留一个关键边界：Expert Deferral改变部分专家输出的层间合并时机，涉及模型语义和质量取舍，不是保持结果不变的单纯异步调度；论文将其用于decode而非prefill。不要把KTransformers所有优化混成同一种无损加速。

个人主页明确其为趋境引擎架构师，不是摩尔线程人员；本科为北京理工大学，博士阶段的信息不写成已获得博士学位。

## 整合与发布状态

本分支仅新增这份研究稿及结构化记录，没有修改catalog.json、index.html、人物总数、目录或技能矩阵，也没有修改分析师站点。

八个中文名的GitHub索引搜索未发现明确现有条目，但这不是完整目录去重。当前catalog.json体积超过contents接口可直接返回正文的范围；encoding=none不能解释为空文件。合并人物前仍应读取完整当前版本并检查英文别名，不能直接给总数加八。

后续技术整合应依次完成：身份及去重核对、补齐两位的技术证据缺口、生成现有profile/sourceAudit/challenge字段、运行原站完整校验。只有通过这些步骤的个人记录才应计入正式目录。陈云霁已有条目，不在本批重复新增。
