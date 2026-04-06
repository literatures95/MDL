"""MDL 解释器 - 执行 MDL 脚本的核心引擎"""

import os
import re
from ast_nodes import *
from mdl_builtins import Environment, BuiltinFunctions, BUILTINS
from md_parser import parse_markdown
from md_generator import generate_markdown, generate_node, MarkdownGenerator
from storage import storage as _storage
from analyzer import DocumentAnalyzer


class MDLRuntimeError(Exception):
    """MDL 运行时错误"""
    pass


class ReturnException(Exception):
    """函数返回异常"""
    def __init__(self, value=None):
        self.value = value


class Interpreter:
    """MDL 脚本解释器"""

    def __init__(self, env: Environment = None):
        self.env = env or Environment()
        self.generator = MarkdownGenerator()

    def execute(self, program: MDLProgramNode):
        """执行 MDL 程序"""
        result = None
        for stmt in program.body:
            result = self._execute_statement(stmt)
        return result

    def _execute_statement(self, stmt):
        """执行语句"""
        if isinstance(stmt, MDLLoadNode):
            return self._exec_load(stmt)
        elif isinstance(stmt, MDLSaveNode):
            return self._exec_save(stmt)
        elif isinstance(stmt, MDLPrintNode):
            return self._exec_print(stmt)
        elif isinstance(stmt, MDLSetNode):
            return self._exec_set(stmt)
        elif isinstance(stmt, MDLInsertNode):
            return self._exec_insert(stmt)
        elif isinstance(stmt, MDLAppendNode):
            return self._exec_append(stmt)
        elif isinstance(stmt, MDLRemoveNode):
            return self._exec_remove(stmt)
        elif isinstance(stmt, MDLConvertNode):
            return self._exec_convert(stmt)
        elif isinstance(stmt, MDLForNode):
            return self._exec_for(stmt)
        elif isinstance(stmt, MDLIfNode):
            return self._exec_if(stmt)
        elif isinstance(stmt, MDLFuncDefNode):
            return self._exec_func_def(stmt)
        elif isinstance(stmt, MDLAssignNode):
            return self._exec_assign(stmt)
        elif isinstance(stmt, MDLPrintNode):
            return self._exec_print(stmt)
        elif isinstance(stmt, MDLFuncCallNode):
            return self._call_function(stmt.name, stmt.args)
        elif isinstance(stmt, MDLBatchNode):
            return self._exec_batch(stmt)
        elif isinstance(stmt, MDLCleanNode):
            return self._exec_clean(stmt)
        elif isinstance(stmt, MDLExtractNode):
            return self._exec_extract(stmt)
        elif isinstance(stmt, MDLTransformNode):
            return self._exec_transform(stmt)
        else:
            expr_result = self._evaluate(stmt)
            if expr_result is not None:
                print(expr_result)
            return expr_result

    def _exec_load(self, stmt: MDLLoadNode) -> DocumentNode:
        """执行 load 语句"""
        path = self._resolve_string(stmt.path)
        alias = stmt.alias or "doc"
        doc = BuiltinFunctions.load(self.env, path, alias)
        return doc

    def _exec_save(self, stmt: MDLSaveNode):
        """执行 save 语句"""
        target = stmt.target or "doc"
        path = self._resolve_string(stmt.path)
        BuiltinFunctions.save(self.env, target, path)

    def _exec_print(self, stmt: MDLPrintNode):
        """执行 print 语句"""
        value = self._evaluate(stmt.expression)
        return BuiltinFunctions.print_value(value)

    def _exec_set(self, stmt: MDLSetNode):
        """执行 set 语句"""
        target = self._evaluate(stmt.target)
        value = self._evaluate(stmt.value)
        property_name = stmt.property_name
        if isinstance(target, (HeadingNode, ParagraphNode, CodeBlockNode, ListItemNode, TaskItemNode)):
            BuiltinFunctions.set_property(self.env, target, property_name, value)
        elif isinstance(target, str):
            self.env.set_var(target, value)
        print(f"[MDL] 属性已更新: {property_name} = {value}")

    def _exec_insert(self, stmt: MDLInsertNode):
        """执行 insert 语句"""
        target = self._evaluate(stmt.target)
        position = stmt.position
        content = self._prepare_md_content(stmt.content)
        doc = self._get_target_doc(target)
        if doc and isinstance(content, list):
            for elem in content:
                index = self._find_element_index(doc, target)
                BuiltinFunctions.insert_element(self.env, doc, position, index, elem)
            print(f"[MDL] 已在 {position} 插入 {len(content)} 个元素")

    def _exec_append(self, stmt: MDLAppendNode):
        """执行 append 语句"""
        target_name = stmt.target or "doc"
        doc = self.env.get_doc(target_name)
        if not doc:
            raise MDLRuntimeError(f"文档 '{target_name}' 不存在")
        content = self._prepare_md_content(stmt.content)
        if isinstance(content, list):
            for elem in content:
                BuiltinFunctions.append_element(self.env, doc, elem)
            print(f"[MDL] 已追加 {len(content)} 个元素")
        elif content:
            BuiltinFunctions.append_element(self.env, doc, content)
            print("[MDL] 已追加 1 个元素")

    def _exec_remove(self, stmt: MDLRemoveNode):
        """执行 remove 语句"""
        target = self._evaluate(stmt.target)
        doc = self._get_target_doc(target)
        if doc:
            index = self._find_element_index(doc, target)
            BuiltinFunctions.remove_element(self.env, doc, index)

    def _exec_convert(self, stmt: MDLConvertNode):
        """执行 convert 语句"""
        source = self._evaluate(stmt.source)
        fmt = stmt.target_format.lower()
        output_path = stmt.output_path
        BuiltinFunctions.convert_format(self.env, source, fmt, output_path)

    def _exec_for(self, stmt: MDLForNode):
        """执行 for 循环"""
        iterable = self._evaluate(stmt.iterable)
        if isinstance(iterable, list):
            for item in iterable:
                self.env.set_var(stmt.var_name, item)
                for s in stmt.body:
                    self._execute_statement(s)
        elif isinstance(iterable, str):
            for char in iterable:
                self.env.set_var(stmt.var_name, char)
                for s in stmt.body:
                    self._execute_statement(s)
        else:
            raise MDLRuntimeError("for 循环需要可迭代对象")

    def _exec_if(self, stmt: MDLIfNode):
        """执行 if 条件"""
        condition = self._evaluate(stmt.condition)
        if self._is_truthy(condition):
            for s in stmt.then_body:
                self._execute_statement(s)
        elif stmt.else_body:
            for s in stmt.else_body:
                self._execute_statement(s)

    def _exec_func_def(self, stmt: MDLFuncDefNode):
        """执行函数定义"""
        self.env.define_function(stmt.name, stmt.params, stmt.body)
        print(f"[MDL] 函数 '{stmt.name}' 已定义 (参数: {stmt.params})")

    def _exec_assign(self, stmt: MDLAssignNode):
        """执行变量赋值"""
        value = self._evaluate(stmt.value)
        self.env.set_var(stmt.name, value)

    def _evaluate(self, expr):
        """求值表达式"""
        if expr is None:
            return None
        if isinstance(expr, MDLStringNode):
            return expr.value
        elif isinstance(expr, MDLNumberNode):
            return expr.value
        elif isinstance(expr, MDLBooleanNode):
            return expr.value
        elif isinstance(expr, MDLIdentifierNode):
            name = expr.name
            if name == "null" or name == "None":
                return None
            if name == "true":
                return True
            if name == "false":
                return False
            if self.env.has_var(name):
                return self.env.get_var(name)
            doc = self.env.get_doc(name)
            if doc:
                return doc
            raise MDLRuntimeError(f"未定义的变量或文档: {name}")
        elif isinstance(expr, MDLSelectorNode):
            return self._eval_selector(expr)
        elif isinstance(expr, MDLPropertyNode):
            return self._eval_property(expr)
        elif isinstance(expr, MDLIndexNode):
            return self._eval_index(expr)
        elif isinstance(expr, MDLBinaryOpNode):
            return self._eval_binary_op(expr)
        elif isinstance(expr, MDLUnaryOpNode):
            return self._eval_unary_op(expr)
        elif isinstance(expr, MDLComparisonNode):
            return self._eval_comparison(expr)
        elif isinstance(expr, MDLFuncCallNode):
            args = [self._evaluate(a) for a in expr.args]
            return self._call_function(expr.name, args)
        elif isinstance(expr, list):
            return [self._evaluate(e) for e in expr]
        return expr

    def _eval_selector(self, selector: MDLSelectorNode) -> list:
        """评估选择器表达式"""
        doc = self.env.get_doc("doc")
        if not doc:
            raise MDLRuntimeError("没有加载任何文档，请先使用 load 命令加载文件")
        results = BuiltinFunctions.select_elements(
            doc, selector.element_type,
            selector.index
        )
        if selector.index is not None and len(results) == 1:
            return results[0]
        return results

    def _eval_property(self, prop: MDLPropertyNode):
        """评估属性访问"""
        obj = self._evaluate(prop.object_node)
        if obj is None:
            return None
        prop_name = prop.property_name
        if isinstance(obj, HeadingNode):
            if prop_name == "text":
                return obj.raw_text
            if prop_name == "level":
                return obj.level
            if prop_name == "content":
                return obj.content
        elif isinstance(obj, ParagraphNode):
            if prop_name in ("text", "raw_text"):
                return obj.raw_text
            if prop_name == "content":
                return obj.content
        elif isinstance(obj, CodeBlockNode):
            if prop_name == "code":
                return obj.code
            if prop_name == "language":
                return obj.language
        elif isinstance(obj, (UnorderedListNode, OrderedListNode)):
            if prop_name == "items":
                return obj.items
            if prop_name == "count":
                return len(obj.items)
        elif isinstance(obj, TableNode):
            if prop_name == "rows":
                return obj.rows
            if prop_name == "headers":
                return obj.headers
        elif isinstance(obj, ListItemNode):
            if prop_name == "content":
                return obj.content
            if prop_name == "checked":
                return obj.checked
        elif isinstance(obj, TaskItemNode):
            if prop_name == "checked":
                return obj.checked
            if prop_name == "content":
                return obj.content
        elif isinstance(obj, LinkNode):
            if prop_name == "text":
                return obj.text
            if prop_name == "url":
                return obj.url
        elif isinstance(obj, ImageNode):
            if prop_name == "src":
                return obj.src
            if prop_name == "alt":
                return obj.alt
        elif isinstance(obj, DocumentNode):
            if prop_name == "children":
                return obj.children
            if prop_name == "length" or prop_name == "len":
                return len(obj.children)
            if prop_name == "metadata":
                return obj.metadata
        elif isinstance(obj, dict):
            return obj.get(prop_name)
        elif isinstance(obj, list) and prop_name == "length":
            return len(obj)
        raise MDLRuntimeError(f"对象类型 {type(obj).__name__} 没有属性 '{prop_name}'")

    def _eval_index(self, index_expr: MDLIndexNode):
        """评估索引访问"""
        obj = self._evaluate(index_expr.object_node)
        idx = self._evaluate(index_expr.index)
        if isinstance(obj, list):
            if isinstance(idx, int):
                if 0 <= idx < len(obj):
                    return obj[idx]
                raise MDLRuntimeError(f"列表索引越界: {idx} (长度: {len(obj)})")
            if isinstance(idx, MDLNumberNode):
                i = int(idx.value)
                if 0 <= i < len(obj):
                    return obj[i]
        if isinstance(obj, DocumentNode):
            if isinstance(idx, int):
                if 0 <= idx < len(obj.children):
                    return obj.children[idx]
        if isinstance(obj, str):
            return obj[int(idx)]
        raise MDLRuntimeError(f"不支持的索引访问类型: {type(obj).__name__}")

    def _eval_binary_op(self, op: MDLBinaryOpNode):
        """评估二元运算"""
        left = self._evaluate(op.left)
        right = self._evaluate(op.right)
        ops = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b if b != 0 else 0,
            "%": lambda a, b: a % b,
            "^": lambda a, b: a ** b,
            "and": lambda a, b: a and b,
            "or": lambda a, b: a or b,
        }
        if op.operator in ops:
            try:
                return ops[op.operator](left, right)
            except TypeError:
                if op.operator == "+":
                    return str(left) + str(right)
                raise MDLRuntimeError(f"运算符 {op.operator} 不支持类型 {type(left).__name__} 和 {type(right).__name__}")
        raise MDLRuntimeError(f"未知运算符: {op.operator}")

    def _eval_unary_op(self, op: MDLUnaryOpNode):
        """评估一元运算"""
        operand = self._evaluate(op.operand)
        if op.operator == "-":
            return -operand
        if op.operator == "not":
            return not operand
        raise MDLRuntimeError(f"未知一元运算符: {op.operator}")

    def _eval_comparison(self, comp: MDLComparisonNode):
        """评估比较运算"""
        left = self._evaluate(comp.left)
        right = self._evaluate(comp.right)
        ops = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            "<": lambda a, b: a < b,
            ">": lambda a, b: a > b,
            "<=": lambda a, b: a <= b,
            ">=": lambda a, b: a >= b,
        }
        if comp.operator in ops:
            return ops[comp.operator](left, right)
        raise MDLRuntimeError(f"未知比较运算符: {comp.operator}")

    def _call_function(self, name: str, args: list):
        """调用函数（内置/用户定义）"""
        builtin = BUILTINS.get(name.lower())
        if builtin:
            try:
                if name.lower() in ("load", "save", "print", "analyze", "select"):
                    return builtin(self.env, *args)
                return builtin(*args)
            except Exception as e:
                raise MDLRuntimeError(f"调用函数 '{name}' 时出错: {e}")
        func_def = self.env.functions.get(name)
        if func_def:
            return self._call_user_function(name, func_def, args)
        raise MDLRuntimeError(f"未定义的函数: {name}")

    def _call_user_function(self, name: str, func_def: dict, args: list):
        """调用用户定义函数"""
        params = func_def["params"]
        body = func_def["body"]
        old_values = {}
        for i, param in enumerate(params):
            if i < len(args):
                old_values[param] = self.env.get_var(param)
                self.env.set_var(param, args[i])
        try:
            result = None
            for stmt in body:
                result = self._execute_statement(stmt)
            return result
        except ReturnException as ret:
            return ret.value
        finally:
            for param in params:
                if param in old_values:
                    self.env.set_var(param, old_values[param])

    def _resolve_string(self, value) -> str:
        """解析字符串值"""
        if isinstance(value, str):
            return value
        if isinstance(value, MDLStringNode):
            return value.value
        return str(value) if value else ""

    def _prepare_md_content(self, content):
        """准备 Markdown 内容为 AST 节点"""
        if content is None:
            return None
        if isinstance(content, MDLStringNode):
            text = content.value.strip()
            if text.startswith("- ") or text.startswith("* "):
                return self._parse_inline_list(text)
            lines = text.split("\n")
            if len(lines) > 1:
                nodes = []
                for line in lines:
                    line = line.strip()
                    if line:
                        nodes.append(ParagraphNode(content=[TextNode(value=line)], raw_text=line))
                return nodes
            return ParagraphNode(content=[TextNode(value=text)], raw_text=text)
        if isinstance(content, str):
            return ParagraphNode(content=[TextNode(value=content)], raw_text=content)
        if isinstance(content, list):
            items = []
            for item in content:
                prepared = self._prepare_md_content(item)
                if isinstance(prepared, list):
                    items.extend(prepared)
                elif prepared:
                    items.append(prepared)
            return items
        if isinstance(content, (ParagraphNode, HeadingNode, CodeBlockNode, ListNode)):
            return content
        return ParagraphNode(content=[TextNode(value=str(content))], raw_text=str(content))

    def _parse_inline_list(self, text: str) -> UnorderedListNode:
        """解析内联列表文本"""
        items = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith(("- ", "* ", "+ ")):
                item_text = line[2:].strip()
                task_match = re.match(r"\[[ xX]\]\s*(.*)", item_text)
                if task_match:
                    checked = task_match.group(1).lower() != " "
                    items.append(TaskItemNode(content=[TextNode(value=task_match.group(2))], checked=checked))
                else:
                    items.append(ListItemNode(content=[TextNode(value=item_text)]))
        return UnorderedListNode(items=items)

    def _get_target_doc(self, target) -> DocumentNode:
        """获取目标所属文档"""
        if isinstance(target, DocumentNode):
            return target
        return self.env.get_doc("doc")

    def _find_element_index(self, doc: DocumentNode, element) -> int:
        """查找元素在文档中的位置"""
        for i, child in enumerate(doc.children):
            if child is element:
                return i
        return -1

    def _is_truthy(self, value) -> bool:
        """判断值的真假性"""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, list):
            return len(value) > 0
        return True

    def _exec_batch(self, stmt: MDLBatchNode):
        """执行 batch 语句"""
        from batch import batch_convert
        patterns = stmt.input_patterns
        output_dir = stmt.output_dir
        output_format = stmt.output_format
        if not patterns:
            print("[MDL] 错误: batch 需要指定输入模式")
            return None
        if not output_dir:
            print("[MDL] 错误: batch 需要指定输出目录")
            return None
        print(f"[MDL] 批量处理: {len(patterns)} 个模式")
        report = batch_convert(patterns, output_dir, output_format)
        report.print_summary()
        return report.to_dict()

    def _exec_clean(self, stmt: MDLCleanNode):
        """执行 clean 语句"""
        from cleaner import clean_document
        target = self._evaluate(stmt.target)
        if isinstance(target, DocumentNode):
            md = generate_markdown(target)
            cleaned = clean_document(md)
            new_doc = parse_markdown(cleaned)
            alias = self._get_doc_alias(target)
            self.env.set_doc(alias, new_doc)
            print(f"[MDL] 文档已清理")
            return new_doc
        elif isinstance(target, str):
            cleaned = clean_document(target)
            return cleaned
        else:
            print("[MDL] 错误: clean 目标必须是文档或字符串")
            return None

    def _get_doc_alias(self, doc: DocumentNode) -> str:
        """获取文档别名"""
        for alias, d in self.env.documents.items():
            if d is doc:
                return alias
        return "doc"

    def _exec_extract(self, stmt: MDLExtractNode):
        """执行 extract 语句"""
        from extractor import extract_structured
        import json
        target = self._evaluate(stmt.target)
        if isinstance(target, DocumentNode):
            md = generate_markdown(target)
        elif isinstance(target, str):
            md = target
        else:
            print("[MDL] 错误: extract 目标必须是文档或字符串")
            return None
        schema = stmt.schema or "basic"
        result = extract_structured(md, schema)
        if stmt.output_path:
            with open(stmt.output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"[MDL] 提取结果已保存到: {stmt.output_path}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return result

    def _exec_transform(self, stmt: MDLTransformNode):
        """执行 transform 语句"""
        from formats import convert_to_markdown
        source = self._evaluate(stmt.source)
        if isinstance(source, str):
            if os.path.exists(source):
                result = convert_to_markdown(source)
                print(f"[MDL] 已转换: {source}")
                return result
            else:
                print(f"[MDL] 错误: 文件不存在: {source}")
                return None
        else:
            print("[MDL] 错误: transform 需要文件路径")
            return None

    def run_script(self, source: str):
        """运行 MDL 脚本源代码"""
        from parser import parse
        program = parse(source)
        return self.execute(program)

    def run_file(self, filepath: str):
        """运行 MDL 脚本文件"""
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        return self.run_script(source)
