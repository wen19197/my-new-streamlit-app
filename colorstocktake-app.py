import streamlit as st
import re
from collections import Counter

# 页面配置
st.set_page_config(page_title="库存 AI 计算器", layout="centered")

# 初始化状态
if 'counter' not in st.session_state:
    st.session_state.counter = Counter()
if 'history' not in st.session_state:
    st.session_state.history = []
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""
if 'search_code' not in st.session_state:
    st.session_state.search_code = ""

st.title("📊 累计库存 AI 计算器（任意 code + 小数数量 & 智能排序）")
st.markdown("""
- 支持任意长度、任意字符的 code（非空白即可）  
- 数量可为整数或小数，例如 `5.35`、`6.3`、`.75`  
- 每次“添加”或“清空”操作前自动记录历史，支持撤回  
- 可随时查询某个 code 的当前累计数量  
- 展示结果时：  
  1. 纯数字 code 按数值大小排序  
  2. 其他 code 按字典序排序  
""")

# 添加回调
def add_to_total():
    text = st.session_state.input_text
    matches = re.findall(r"(\S+)\s*([\d]*\.?\d+)", text)
    if not matches:
        st.warning("❗ 未检测到符合格式的 code+数量，请检查输入。")
        return
    st.session_state.history.append(st.session_state.counter.copy())
    for code, qty in matches:
        st.session_state.counter[code] += float(qty)
    st.session_state.input_text = ""
    st.success("✅ 本轮数据已累计")

# 清空回调
def clear_all():
    if st.session_state.counter:
        st.session_state.history.append(st.session_state.counter.copy())
    st.session_state.counter = Counter()
    st.success("🗑️ 已清空所有累计数据")

# 撤回回调
def undo():
    if st.session_state.history:
        st.session_state.counter = st.session_state.history.pop()
        st.success("⏪ 已撤回上一步操作")
    else:
        st.warning("⚠️ 无可撤回的操作")

# 文本输入
st.text_area(
    "📋 输入本轮库存列表",
    key="input_text",
    height=150,
    placeholder="格式：<code> <数量>\n示例：\nABC-123 5\nXYZ 6.3\nN11 .75\n3020021 2"
)

# 操作按钮
col1, col2, col3 = st.columns(3)
with col1:
    st.button("✅ 添加到总数", on_click=add_to_total)
with col2:
    st.button("🗑️ 清空所有数据", on_click=clear_all)
with col3:
    st.button("⏪ 撤回上一步", on_click=undo)

st.markdown("---")

# 搜索功能
st.text_input(
    "🔍 查询某个 code 的数量",
    key="search_code",
    placeholder="在此输入 code"
)
if st.session_state.search_code:
    code = st.session_state.search_code.strip()
    qty = st.session_state.counter.get(code, 0.0)
    display_qty = int(qty) if qty == int(qty) else qty
    st.info(f"🔎 Code **{code}** 的当前累计数量：**{display_qty}**")

# 智能排序函数
def sort_key(item):
    code, _ = item
    if re.fullmatch(r'\d+', code):
        return (0, int(code))
    else:
        return (1, code)

# 展示结果
if st.session_state.counter:
    st.subheader("📈 当前累计库存总览（智能排序）")
    result = []
    for k, v in sorted(st.session_state.counter.items(), key=sort_key):
        display_v = int(v) if v == int(v) else v
        result.append({"产品 code": k, "总数量": display_v})
    st.table(result)
