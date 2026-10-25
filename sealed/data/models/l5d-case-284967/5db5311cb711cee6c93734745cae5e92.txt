"""一句话主张，写成**能被判错**的那种。一条概念只断言一件事。"""
LEVEL = "L1"        # 地图的哪一块：L1 动作效果 / L2 阻挡 / L4 计数器 / L5 终止 / L6 运动物 / L7 观测
SCOPE = "只看 ACTIONx；换关返回 NA；读不出来返回 NA"
NOTE = ""           # 改版时写清**为什么**改
EVIDENCE = []       # 它所依据的 tid，**不能为空**（硬要求 1）

# from _lib import me, CELL        # 本局词汇：这些是假设，跟着概念一起被重审
# from geo import diff_cells       # 跨局几何：里面没有任何关于世界的断言


def assert_(prev, action, nxt, ctx=None):
    """检查器：让主张可判错。只许返回 "TRUE" / "FALSE" / "NA"。"""
    return "NA"


def apply(prev, action, ctx=None):
    """生成器（可选）：这条概念**敢生成**的那部分下一帧，只填它管得着的格子。

    返回 {(行, 列): 颜色} 或 None。
    不变量式的概念（「墙集合不变」）生成不了就别写 apply，只写 assert_。
    """
    return None
